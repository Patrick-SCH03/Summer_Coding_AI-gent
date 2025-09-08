# 🛠️ 기술 문서 (Technical Documentation)

## 📋 목차
- [시스템 아키텍처](#시스템-아키텍처)
- [핵심 컴포넌트](#핵심-컴포넌트)
- [API 레퍼런스](#api-레퍼런스)
- [개발자 가이드](#개발자-가이드)
- [확장 가능성](#확장-가능성)

## 🏗️ 시스템 아키텍처

### 전체 시스템 구조

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   사용자 UI     │    │  AI 분석 엔진    │    │   데이터 저장소 │
│                 │    │                  │    │                 │
│ • Gradio Web    │◄──►│ • LangGraph      │◄──►│ • ChromaDB      │
│ • 채팅 인터페이스│    │ • Multi-Agents   │    │ • Notion        │
│                 │    │ • LLM Pipeline   │    │ • Google Drive  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 컴포넌트별 상세

#### 1. 사용자 인터페이스 레이어
```python
gradio_app.py                 # 포트 7860
├── 기본 채팅 기능
├── 에러 처리 및 검증
└── 결과 포맷팅
```

#### 2. AI 분석 엔진
```python
# 멀티에이전트 워크플로우
src/core/langgraph_pipeline.py
├── StateGraph 기반 워크플로우
├── 병렬 에이전트 실행
├── 상태 관리 및 동기화
└── 에러 처리 및 복구

# AI 에이전트들
src/agents/
├── regulation_reviewer.py   # 규정 검토 에이전트
├── auditor.py              # 감사 에이전트
├── coordinator.py          # 조정 에이전트
└── document_manager.py     # 문서 관리 에이전트
```

#### 3. 데이터 저장소
```python
# 벡터 데이터베이스
ChromaDB
├── 문서 임베딩 저장
├── 유사도 검색
└── 실시간 업데이트

# 외부 서비스 연동
src/utils/
├── google_drive_handler.py  # Google Drive API
├── notion_handler.py        # Notion API
└── vector_db_manager.py     # ChromaDB 관리
```

## 🧠 핵심 컴포넌트

### LangGraph 워크플로우

```python
class AgentState(TypedDict):
    query: str                    # 사용자 질의
    folder_id: str | None         # Google Drive 폴더 ID
    reviewer_analysis: str        # 규정 검토 결과
    auditor_analysis: str         # 감사 분석 결과
    final_recommendation: str     # 최종 권고안
    router_decision: str          # 라우팅 결정
    session_id: str              # 세션 ID
```

### 워크플로우 실행 과정

1. **질의 라우팅**
   ```python
   def route_query(state: AgentState) -> str:
       # 학생회 업무 관련성 판단
       # "relevant_query_branch" 또는 "irrelevant_query_branch" 반환
   ```

2. **병렬 에이전트 실행**
   ```python
   def relevant_query_branch(state: AgentState) -> AgentState:
       # 규정 검토 에이전트와 감사 에이전트 병렬 실행
       # 결과를 state에 저장
   ```

3. **결과 통합**
   ```python
   def run_coordinator(state: AgentState) -> AgentState:
       # 두 에이전트의 결과를 종합하여 최종 권고안 생성
       # Notion에 결과 저장
   ```

### AI 에이전트 상세

#### 규정 검토 에이전트 (RegulationReviewerAgent)
```python
class RegulationReviewerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.doc_manager = DocumentManagerAgent()
        self.chain = self.prompt_template | self.llm
    
    def review_and_analyze(self, query: str, folder_id: str) -> str:
        # 1. 관련 규정 문서 검색
        # 2. LLM을 통한 규정 분석
        # 3. 위험도 평가 및 근거 제시
```

#### 감사 에이전트 (AuditorAgent)
```python
class AuditorAgent:
    def review_and_audit(self, query: str, folder_id: str) -> str:
        # 1. 감사 기록 및 규정 검색
        # 2. 감사 기준 준수 여부 분석
        # 3. 처분 가능성 평가
```

#### 조정 에이전트 (CoordinatorAgent)
```python
class CoordinatorAgent:
    def synthesize_and_coordinate(self, initial_query: str, 
                                reviewer_analysis: str, 
                                auditor_analysis: str) -> Dict[str, Any]:
        # 1. 두 에이전트의 분석 결과 종합
        # 2. 의견 차이 조정
        # 3. 최종 권고안 도출
```

## 📡 API 레퍼런스

### 핵심 함수

#### `run_agent_pipeline(query: str, folder_id: str = None)`
멀티에이전트 파이프라인을 실행하는 메인 함수

**Parameters:**
- `query` (str): 사용자 질의
- `folder_id` (str, optional): Google Drive 폴더 ID

**Returns:**
- `AgentState`: 최종 분석 결과를 포함한 상태 객체

**Example:**
```python
result = await run_agent_pipeline(
    query="학생회비로 회식비 사용이 가능한가요?",
    folder_id="1abc-def-ghi-2jkl"
)
```

#### `determine_risk_level(reviewer_analysis: str, auditor_analysis: str)`
위험도를 자동으로 판정하는 함수

**Parameters:**
- `reviewer_analysis` (str): 규정 검토 결과
- `auditor_analysis` (str): 감사 분석 결과

**Returns:**
- `str`: "높음", "보통", "낮음", "분석 필요" 중 하나

### 위험도 판정 로직

```python
def determine_risk_level(reviewer_analysis: str, auditor_analysis: str) -> str:
    high_risk_keywords = [
        "위반 가능성 높음", "위험도: 높음", "감사 처분 가능성 높음",
        "중대한 위반", "심각한", "경고", "제재", "처분"
    ]
    
    medium_risk_keywords = [
        "주의 필요", "검토 필요", "위험도: 보통", "조건부",
        "신중한", "추가 확인"
    ]
    
    low_risk_keywords = [
        "위반 없음", "문제없음", "준수", "안전", "허용",
        "위험도: 낮음", "적절함"
    ]
```

## 👨‍💻 개발자 가이드

### 환경 설정

#### 필수 요구사항
- Python 3.8+
- Google Gemini API 키
- Google Drive API 액세스
- Notion API 토큰

#### 설치 과정
```bash
# 1. 저장소 클론
git clone <repository-url>
cd Summer_coding

# 2. 가상환경 설정
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 설정
# .env 파일 생성 후 아래 내용 입력
```

#### 환경변수 설정
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id_here
NOTION_API_KEY=your_notion_token_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

### 새로운 에이전트 추가하기

#### 1. 에이전트 클래스 생성
```python
# src/agents/new_agent.py
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GEMINI_API_KEY

class NewAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["query"],
            template="Your prompt template here: {query}"
        )
        
        self.chain = self.prompt_template | self.llm
    
    def process(self, query: str) -> str:
        try:
            result = self.chain.invoke({"query": query})
            return result.content
        except Exception as e:
            return f"에이전트 처리 실패: {str(e)}"
```

#### 2. 워크플로우에 통합
```python
# src/core/langgraph_pipeline.py에 추가
from src.agents.new_agent import NewAgent

# 에이전트 인스턴스 생성
new_agent = NewAgent()

# 노드 함수 정의
def run_new_agent(state: AgentState) -> AgentState:
    try:
        result = new_agent.process(state["query"])
        return {"new_agent_result": result}
    except Exception as e:
        return {"new_agent_result": f"새 에이전트 실패: {str(e)}"}

# 워크플로우에 노드 추가
workflow.add_node("run_new_agent", run_new_agent)
workflow.add_edge("relevant_query_branch", "run_new_agent")
```

### 효과적인 프롬프트 작성

#### 프롬프트 패턴
```python
EFFECTIVE_PROMPT = """
당신은 {role}입니다.

**작업 목표:**
{objective}

**입력 데이터:**
{input_data}

**출력 형식:**
다음 형식으로만 답변하세요:
- **분석 결과:** (핵심 내용)
- **위험도:** (높음/보통/낮음)  
- **근거:** (구체적인 근거)
- **권고사항:** (행동 방침)
"""
```

#### 프롬프트 최적화 팁
1. **명확한 역할 정의**: 에이전트의 전문성 영역 명시
2. **구조화된 출력**: 일관된 형식으로 결과 요구
3. **구체적인 지침**: 모호한 표현 지양
4. **예시 포함**: Few-shot learning 활용

### 테스트 및 디버깅

#### 단위 테스트 예시
```python
import pytest
from src.agents.regulation_reviewer import RegulationReviewerAgent

def test_regulation_reviewer():
    agent = RegulationReviewerAgent()
    
    # 테스트 케이스
    test_query = "학생회비로 회식비 사용이 가능한가요?"
    result = agent.review_and_analyze(test_query, None)
    
    # 검증
    assert result is not None
    assert "위반" in result or "준수" in result
```

#### 로그 설정
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```