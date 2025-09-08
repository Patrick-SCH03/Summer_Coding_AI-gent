from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.document_manager import DocumentManagerAgent
from src.config import GEMINI_API_KEY

class RegulationReviewerAgent:
    """사용자 질의에 대한 규정 위반 여부와 위험도를 분석하는 에이전트"""
    
    def __init__(self):
        # Gemini LLM 초기화
        if GEMINI_API_KEY:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=GEMINI_API_KEY)
            print("규정 검토 에이전트: Gemini 모델을 사용합니다.")
        else:
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")
        
        self.doc_manager = DocumentManagerAgent()
        
        # 규정 검토 분석을 위한 프롬프트 템플릿
        self.prompt_template = PromptTemplate(
            input_variables=["query", "regulations"],
            template="""
            당신은 학생회 규정 검토 전문가입니다. 다음 질의와 관련 규정을 분석하여 질의에 포함된 내용이 규정 위반에 해당하는지,
            위반 가능성이 있다면 그 위험도는 어느 정도인지 평가해 대안이나 권고사항을 제시하세요.
            답변 시에는 반드시 어떤 문서의 규정을 참고했는지 명시해 주세요. (예: '재정·회계 세칙' 제10조)
            
            분석 결과는 아래 형식에 맞춰서 명확하고 구체적으로 작성해 주세요.
            
            ---
            **사용자 질의: {query}
            
            **관련 규정:
            {regulations}
            
            **분석 결과:
            - **규정 위반 여부:** (위반 가능성 높음, 위반 가능성 낮음, 위반 없음)
            - **위험도: (높음, 보통, 낮음)
            - **근거: (왜 그렇게 판단했는지 관련 규정 조항과 함께 구체적으로 설명)
            - **권고사항: (규정 위반을 막기 위한 대안이나 향후 조치 제안)
            ---
            """
        )
        
        self.chain = self.prompt_template | self.llm

    def review_and_analyze(self, query, folder_id):
        """사용자 질의를 분석하여 규정 위반 여부와 위험도를 평가"""
        # 관련 규정 문서 검색
        relevant_docs = self.doc_manager.get_relevant_documents(query, folder_id)
        
        # 검색된 문서를 파일명과 함께 텍스트로 결합
        regulations_text = "\n\n".join(
            [f"--- 파일명: {doc.metadata.get('source', '알 수 없음')}\n{doc.page_content}" for doc in relevant_docs]
        )

        if not regulations_text:
            return "관련 규정을 찾을 수 없습니다. 좀 더 구체적인 질의를 해주세요."
            
        # LLM을 통한 규정 분석 실행
        try:
            analysis_result = self.chain.invoke({"query": query, "regulations": regulations_text})
            return analysis_result.content
        except Exception as e:
            return f"규정 분석 중 오류가 발생했습니다: {e}"