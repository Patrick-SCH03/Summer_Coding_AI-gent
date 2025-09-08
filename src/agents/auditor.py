from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.document_manager import DocumentManagerAgent
from src.config import GEMINI_API_KEY

class AuditorAgent:
    """재정 관련 업무의 감사 기준 준수 여부를 확인하고 감사 처분 가능성을 판단하는 에이전트"""
    
    def __init__(self):
        # Gemini LLM 초기화
        if GEMINI_API_KEY:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=GEMINI_API_KEY)
            print("감사 에이전트: Gemini 모델을 사용합니다.")
        else:
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")

        self.doc_manager = DocumentManagerAgent()

        # 감사 분석을 위한 프롬프트 템플릿
        self.prompt_template = PromptTemplate(
            input_variables=["query", "regulations", "audit_records"],
            template="""
            당신은 학생회 재정 감사 전문가입니다. 다음 재정 관련 질의와 관련 규정, 과거 감사 처분 기록 및 보고서를 종합하여
            질의 내용이 감사 기준을 준수하는지, 그리고 감사 처분 가능성이 있는지 판단하세요.
            
            분석 결과는 아래 형식에 맞춰 명확하게 작성해 주세요.
            
            ---
            **사용자 질의:** {query}
            
            **관련 규정:**
            {regulations}
            
            **과거 감사 기록 (RAG):**
            {audit_records}
            
            **분석 결과:**
            - **감사 기준 준수 여부:** (준수, 위반 가능성 높음, 위반 가능성 낮음)
            - **감사 처분 가능성:** (가능성 높음, 가능성 낮음, 가능성 없음)
            - **근거:** (왜 그렇게 판단했는지 관련 규정 조항과 과거 감사 사례를 바탕으로 구체적으로 설명)
            - **권고사항:** (감사 리스크를 줄이기 위한 대안이나 조치 제안)
            ---
            """
        )

        self.chain = self.prompt_template | self.llm

    def review_and_audit(self, query, folder_id):
        """사용자 질의를 분석하여 감사 기준 준수 여부와 감사 처분 가능성을 평가"""
        # 관련 규정 문서 검색
        relevant_regulations = self.doc_manager.get_relevant_documents(query, folder_id)
        
        # 감사 기록 문서는 보고서 키워드를 추가하여 검색
        audit_query = f"{query}에 대한 감사 보고서 또는 감사 사례"
        relevant_audit_records = self.doc_manager.get_relevant_documents(audit_query, folder_id)

        regulations_text = "\n\n".join([doc.page_content for doc in relevant_regulations])
        audit_records_text = "\n\n".join([doc.page_content for doc in relevant_audit_records])

        if not regulations_text:
            return "관련 규정을 찾을 수 없습니다. 좀 더 구체적인 질의를 해주세요."
        
        # LLM을 통한 감사 분석 실행
        try:
            analysis_result = self.chain.invoke(
                {"query": query, "regulations": regulations_text, "audit_records": audit_records_text}
            )
            return analysis_result.content
        except Exception as e:
            return f"감사 분석 중 오류가 발생했습니다: {e}"