"""
기본 Gradio 웹 인터페이스
학생회 규정 검토를 위한 멀티에이전트 시스템의 메인 인터페이스
"""

import gradio as gr
import asyncio
import time
import logging
from typing import List, Tuple, Optional, Dict, Any

from src.core.langgraph_pipeline import run_agent_pipeline
from src.config import GOOGLE_DRIVE_FOLDER_ID, ConfigurationError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class QueryValidator:
    """질의 검증을 담당하는 클래스"""
    
    MAX_QUERY_LENGTH = 1000
    
    @staticmethod
    def validate_query(message: str) -> Optional[str]:
        """질의를 검증하고 오류가 있으면 오류 메시지를 반환합니다."""
        if not message or not message.strip():
            return "❌ 오류: 질문을 입력해주세요."
        
        if len(message) > QueryValidator.MAX_QUERY_LENGTH:
            return f"❌ 오류: 질문이 너무 깁니다 (최대 {QueryValidator.MAX_QUERY_LENGTH}자)."
        
        return None


class ResultProcessor:
    """결과 처리를 담당하는 클래스"""
    
    def __init__(self, final_state: Dict[str, Any]):
        self.final_state = final_state
    
    def get_reviewer_analysis(self) -> str:
        """규정 검토 분석 결과를 반환합니다."""
        analysis = self.final_state.get("reviewer_analysis", "").strip()
        return analysis or "⚠️ 규정 검토 분석이 완료되지 않았습니다."
    
    def get_auditor_analysis(self) -> str:
        """감사 분석 결과를 반환합니다."""
        analysis = self.final_state.get("auditor_analysis", "").strip()
        return analysis or "⚠️ 감사 분석이 완료되지 않았습니다."
    
    def get_final_recommendation(self) -> str:
        """최종 권고안을 반환합니다."""
        recommendation = self.final_state.get("final_recommendation", "").strip()
        return recommendation or "⚠️ 최종 권고안을 생성하지 못했습니다."


class ResponseFormatter:
    """응답 포맷팅을 담당하는 클래스"""
    
    @staticmethod
    def format_success_response(reviewer_analysis: str, auditor_analysis: str, 
                              final_recommendation: str, processing_time: float) -> str:
        """성공적인 분석 결과를 포맷팅합니다."""
        return f"""## 📋 **규정 검토 결과**
{reviewer_analysis}

---

## 🔍 **감사 분석 결과**
{auditor_analysis}

---

## ⚖️ **최종 권고안**
{final_recommendation}

---

⏱️ **처리 시간**: {processing_time:.2f}초"""


class ErrorHandler:
    """오류 처리를 담당하는 클래스"""
    
    @staticmethod
    def format_error_response(error_message: str, processing_time: float) -> str:
        """오류 응답을 포맷팅합니다."""
        return f"""❌ **처리 중 오류가 발생했습니다**

**오류 내용**: {error_message}

**해결 방안**:
1. 인터넷 연결 상태를 확인해주세요
2. 잠시 후 다시 시도해주세요
3. 문제가 지속되면 관리자에게 문의해주세요

⏱️ **처리 시간**: {processing_time:.2f}초"""


async def process_chat_query(message: str, history: List) -> str:
    """사용자 질의를 멀티에이전트 파이프라인으로 처리하여 종합 분석 결과 반환"""
    start_time = time.time()
    
    # 입력 검증
    validation_error = QueryValidator.validate_query(message)
    if validation_error:
        return validation_error
    
    # 설정 검증
    try:
        folder_id = GOOGLE_DRIVE_FOLDER_ID
    except ConfigurationError:
        return "❌ 설정 오류: .env 파일에 Google Drive 폴더 ID가 설정되지 않았습니다."
        
    logger.info(f"사용자 질의 수신: '{message[:50]}...'")
    
    try:
        # 멀티에이전트 파이프라인 실행
        final_state = await run_agent_pipeline(message, folder_id)
        processing_time = time.time() - start_time
        
        # 결과 처리 및 검증
        result_processor = ResultProcessor(final_state)
        reviewer_analysis = result_processor.get_reviewer_analysis()
        auditor_analysis = result_processor.get_auditor_analysis()
        final_recommendation = result_processor.get_final_recommendation()
        
        # 응답 포맷팅 및 반환
        return ResponseFormatter.format_success_response(
            reviewer_analysis, auditor_analysis, final_recommendation, processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"처리 중 오류 발생: {str(e)}", exc_info=True)
        return ErrorHandler.format_error_response(str(e), processing_time)


def create_gradio_interface() -> gr.Interface:
    """Gradio 인터페이스를 생성합니다."""
    
    # 예시 질문들
    examples = [
        ["학생회비로 회식비 사용이 가능한가요?"],
        ["동아리 지원금 사용 내역을 공개해야 하는 의무가 있나요?"],
        ["학생회 임원 선거에서 선거 비용 지원 한도는 얼마인가요?"],
        ["예산 변경 시 필요한 승인 절차는 무엇인가요?"],
        ["감사에서 어떤 처분을 받을 수 있는지 궁금합니다"]
    ]
    
    # 인터페이스 생성 (Gradio 4.0+ 호환 버전)
    interface = gr.ChatInterface(
        fn=process_chat_query,
        title="🎓 학생회 규정 검토 AI 어시스턴트",
        description="""
        **학생회 활동과 관련된 규정, 절차, 위험도를 AI가 종합 분석해드립니다.**
        
        📋 **규정 검토**: 관련 규정을 찾아 위반 여부를 판단합니다  
        🔍 **감사 분석**: 감사 기준에 따른 처분 가능성을 분석합니다  
        ⚖️ **종합 권고**: 최종적인 권고안을 제시합니다  
        
        💡 **사용법**: 학생회 활동과 관련된 궁금한 점을 자연어로 질문해주세요.
        """,
        examples=examples,
        cache_examples=False,
        theme=gr.themes.Soft(),
        type="messages"
    )
    
    return interface


def main():
    """메인 함수"""
    try:
        interface = create_gradio_interface()
        
        logger.info("Gradio 인터페이스를 시작합니다...")
        logger.info("브라우저에서 http://localhost:7860 으로 접속하세요")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
        
    except Exception as e:
        logger.error(f"애플리케이션 시작 실패: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()