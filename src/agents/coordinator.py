"""
조정 에이전트 모듈
규정 검토 에이전트와 감사 에이전트의 결과를 종합하여 최종 권고안을 생성합니다.
"""

import logging
from typing import Dict, Any

from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    """규정 검토 에이전트와 감사 에이전트의 분석 결과를 종합하여 최종 권고안을 도출하는 조정 에이전트"""
    
    def __init__(self):
        """조정 에이전트를 초기화합니다."""
        self._initialize_llm()
        self._setup_prompt_template()
    
    def _initialize_llm(self) -> None:
        """Gemini LLM을 초기화합니다."""
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API 키가 설정되지 않았습니다.")
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                temperature=0.1, 
                google_api_key=GEMINI_API_KEY
            )
            logger.info("조정 에이전트: Gemini 모델을 사용합니다.")
        except Exception as e:
            logger.error(f"LLM 초기화 실패: {e}")
            raise
    
    def _setup_prompt_template(self) -> None:
        """프롬프트 템플릿을 설정합니다."""
        self.prompt_template = PromptTemplate(
            input_variables=["initial_query", "reviewer_analysis", "auditor_analysis"],
            template="""
            당신은 학생회 규정 관련 사안을 종합적으로 분석하는 최고 조정자입니다.
            다음 사용자 질의와 '규정 검토 에이전트', '감사 에이전트'의 분석 결과를 종합하여
            최종 권고안만을 작성하세요.

            **사용자 질의:** {initial_query}

            **규정 검토 에이전트의 분석 결과:**
            {reviewer_analysis}

            **감사 에이전트의 분석 결과:**
            {auditor_analysis}

            위 두 에이전트의 분석을 종합하여, 아래 형식으로 최종 종합 분석 및 권고안만 작성하세요:

            **최종 종합 분석 및 권고안:**
            - **핵심 요약:** (두 에이전트의 분석을 요약하고 핵심 결론을 제시)
            - **의견 조정:** (두 에이전트의 의견이 다르다면, 그 이유를 설명하고 최종 결론을 도출)
            - **최종 권고:** (사용자에게 가장 적합한 행동 방침을 구체적으로 규정을 바탕으로 제안)
            """
        )

        self.chain = self.prompt_template | self.llm

    def synthesize_and_coordinate(self, initial_query, reviewer_analysis, auditor_analysis):
        """두 에이전트의 분석 결과를 종합하여 최종 권고안을 생성"""
        print("에이전트들의 분석 결과를 종합하여 최종 권고안을 도출합니다...")
        
        try:
            final_result = self.chain.invoke(
                {"initial_query": initial_query, "reviewer_analysis": reviewer_analysis, "auditor_analysis": auditor_analysis}
            )

            # LLM 응답 형태에 따른 처리
            if hasattr(final_result, 'content'):
                result_text = final_result.content
            elif isinstance(final_result, str):
                result_text = final_result
            else:
                result_text = str(final_result)

            return {
                "result": result_text
            }
        except Exception as e:
            return {
                "error": f"최종 권고안 도출 중 오류가 발생했습니다: {e}"
            }