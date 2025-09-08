from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import logging
from src.config import GEMINI_API_KEY

from src.agents.regulation_reviewer import RegulationReviewerAgent
from src.agents.auditor import AuditorAgent
from src.agents.coordinator import CoordinatorAgent
from src.utils.notion_handler import record_result_to_notion

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# LangGraph 워크플로우 상태 정의
class AgentState(TypedDict):
    query: str
    folder_id: str | None
    reviewer_analysis: str
    auditor_analysis: str
    final_recommendation: str
    router_decision: str
    session_id: str

# 에이전트 인스턴스 생성
reviewer_agent = RegulationReviewerAgent()
auditor_agent = AuditorAgent()
coordinator_agent = CoordinatorAgent()

# 질문 라우팅용 LLM 설정
query_router_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=GEMINI_API_KEY)
query_router_prompt = PromptTemplate.from_template(
    """
    다음 질문이 '학생회 업무, 규정, 재정, 감사'와 관련이 있으면 'relevant', 아니면 'irrelevant'라고만 답변하세요.
    질문: {query}
    답변:
    """
)
query_router_chain = query_router_prompt | query_router_llm

def route_query(state: AgentState) -> str:
    """사용자 질의의 학생회 업무 관련성을 판단하는 라우터"""
    print("질문 라우팅 에이전트가 실행됩니다...")
    decision = query_router_chain.invoke({"query": state["query"]}).content.strip().lower()
    print(f"라우터 결정: '{decision}' (질문: '{state['query']}')")
    return {"router_decision": decision}

def handle_irrelevant_query(state: AgentState) -> str:
    """학생회 업무와 관련 없는 질문에 대한 일반적인 응답 처리"""
    print(f"일반 질문 처리 시작: '{state['query']}'")
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    general_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=GEMINI_API_KEY)
    
    try:
        response = general_llm.invoke(state["query"]).content
        print(f"일반 질문 답변 완료")
        return {"final_recommendation": response}
    except Exception as e:
        print(f"일반 질문 답변 오류: {e}")
        return {"final_recommendation": "죄송합니다. 현재 답변을 처리할 수 없습니다."}

def run_reviewer(state: AgentState) -> AgentState:
    """규정 검토 에이전트 실행"""
    print("규정 검토 에이전트가 실행됩니다...")
    
    try:
        reviewer_result = reviewer_agent.review_and_analyze(state["query"], state["folder_id"])
        return {"reviewer_analysis": reviewer_result}
    except Exception as e:
        logging.error(f"규정 검토 에이전트 실행 실패: {e}")
        return {"reviewer_analysis": f"규정 검토 분석 실패: {str(e)}"}

def run_auditor(state: AgentState) -> AgentState:
    """감사 에이전트 실행"""
    print("감사 에이전트가 실행됩니다...")
    
    try:
        auditor_result = auditor_agent.review_and_audit(state["query"], state["folder_id"])
        return {"auditor_analysis": auditor_result}
    except Exception as e:
        logging.error(f"감사 에이전트 실행 실패: {e}")
        return {"auditor_analysis": f"감사 분석 실패: {str(e)}"}

def run_coordinator(state: AgentState) -> AgentState:
    """조정 에이전트 실행 및 Notion 기록"""
    print("조정 에이전트가 실행됩니다...")
    
    try:
        final_result = coordinator_agent.synthesize_and_coordinate(
            initial_query=state["query"],
            reviewer_analysis=state["reviewer_analysis"],
            auditor_analysis=state["auditor_analysis"]
        )
        
        # 위험도 자동 판정
        risk_level = determine_risk_level(state["reviewer_analysis"], state["auditor_analysis"])
        
        # Notion에 분석 결과 기록
        notion_data = {
            "title": f"[{state['query'][:20]}] 분석 결과",
            "content": final_result.get("result", "분석 실패"),
            "risk_level": risk_level
        }
        
        try:
            record_result_to_notion(notion_data)
        except Exception as notion_error:
            logging.warning(f"Notion 기록 실패: {notion_error}")
        
        return {
            "final_recommendation": final_result.get("result", final_result.get("error")), 
            "reviewer_analysis": state["reviewer_analysis"], 
            "auditor_analysis": state["auditor_analysis"]
        }
        
    except Exception as e:
        logging.error(f"조정 에이전트 실행 실패: {e}")
        return {"final_recommendation": f"최종 분석 실패: {str(e)}"}

def determine_risk_level(reviewer_analysis: str, auditor_analysis: str) -> str:
    """규정 검토와 감사 분석 결과를 바탕으로 위험도 자동 판정"""
    
    # 분석 결과가 없는 경우
    if not reviewer_analysis or not auditor_analysis:
        return "분석 불가"
    
    # 키워드 기반 위험도 판정
    high_risk_keywords = [
        "위반 가능성 높음", "위험도: 높음", "위험도 높음",
        "감사 처분 가능성 높음", "처분 가능성 높음", "가능성 높음",
        "중대한 위반", "심각한", "경고", "제재", "처분"
    ]
    
    medium_risk_keywords = [
        "위반 가능성 낮음", "위험도: 보통", "위험도 보통", 
        "감사 처분 가능성 낮음", "처분 가능성 낮음", "가능성 낮음",
        "주의 필요", "검토 필요", "확인 필요"
    ]
    
    low_risk_keywords = [
        "위반 없음", "위험도: 낮음", "위험도 낮음",
        "가능성 없음", "처분 가능성 없음", "문제없음", "준수"
    ]
    
    # 전체 분석 텍스트
    full_text = (reviewer_analysis + " " + auditor_analysis).lower()
    
    # 고위험 키워드 카운트
    high_risk_count = sum(1 for keyword in high_risk_keywords if keyword.lower() in full_text)
    medium_risk_count = sum(1 for keyword in medium_risk_keywords if keyword.lower() in full_text)
    low_risk_count = sum(1 for keyword in low_risk_keywords if keyword.lower() in full_text)
    
    # 위험도 판정 로직
    if high_risk_count >= 2:
        return "높음"
    elif high_risk_count >= 1 and medium_risk_count >= 1:
        return "높음"  
    elif high_risk_count >= 1:
        return "보통"
    elif medium_risk_count >= 2:
        return "보통"
    elif medium_risk_count >= 1:
        return "낮음"
    elif low_risk_count >= 1:
        return "낮음"
    else:
        return "분석 필요"

def route_agents(state: AgentState) -> str:
    """라우터 결정에 따른 워크플로우 분기 처리"""
    decision = state["router_decision"]
    print(f"워크플로우 분기 결정: '{decision}' (타입: {type(decision)})")
    
    if decision == "relevant":
        print("→ relevant_query_branch로 이동")
        return "relevant_query_branch"
    else:
        print("→ irrelevant_query_branch로 이동")  
        return "irrelevant_query_branch"

def run_parallel_agents(state: AgentState) -> AgentState:
    """규정 검토 에이전트와 감사 에이전트를 순차 실행하여 상태 업데이트"""
    print("에이전트 순차적 실행 시작...")
    
    # 두 에이전트 순차 실행
    reviewer_result = run_reviewer(state)
    auditor_result = run_auditor(state)
    
    # 상태 업데이트
    updated_state = {
        **state,
        "reviewer_analysis": reviewer_result.get("reviewer_analysis", ""),
        "auditor_analysis": auditor_result.get("auditor_analysis", "")
    }
    
    return updated_state

def create_graph():
    """LangGraph 워크플로우 생성 및 구성"""
    workflow = StateGraph(AgentState)
    
    # 워크플로우 노드 추가
    workflow.add_node("route_query", route_query)
    workflow.add_node("irrelevant_query_branch", handle_irrelevant_query)
    workflow.add_node("relevant_query_branch", run_parallel_agents)
    workflow.add_node("run_coordinator", run_coordinator)
    
    # 워크플로우 흐름 정의
    workflow.set_entry_point("route_query")
    workflow.add_conditional_edges(
        "route_query",
        route_agents,
        {
            "relevant_query_branch": "relevant_query_branch",
            "irrelevant_query_branch": "irrelevant_query_branch",
        },
    )
    workflow.add_edge("relevant_query_branch", "run_coordinator")
    workflow.add_edge("irrelevant_query_branch", END)
    workflow.add_edge("run_coordinator", END)
    
    app = workflow.compile()
    return app


async def run_agent_pipeline(query: str, folder_id: str | None = None):
    """멀티에이전트 파이프라인 실행"""
    app = create_graph()
    
    initial_state = {
        "query": query,
        "folder_id": folder_id,
        "reviewer_analysis": "",
        "auditor_analysis": "",
        "final_recommendation": "",
        "router_decision": "",
        "session_id": ""
    }

    try:
        final_state = await app.ainvoke(initial_state)
        return final_state
    except Exception as e:
        raise
