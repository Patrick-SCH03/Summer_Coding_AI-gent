"""
애플리케이션 설정 관리 모듈
환경 변수를 로드하고 검증하는 역할을 담당합니다.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional

logger = logging.getLogger(__name__)

load_dotenv()

class ConfigurationError(Exception):
    """설정 오류를 나타내는 사용자 정의 예외"""
    pass

def _get_required_env_var(key: str) -> str:
    """필수 환경 변수를 안전하게 가져옵니다."""
    value = os.getenv(key)
    if not value:
        raise ConfigurationError(f"필수 환경 변수 '{key}'가 설정되지 않았습니다.")
    return value

def _get_optional_env_var(key: str, default: str) -> str:
    """선택적 환경 변수를 가져옵니다."""
    return os.getenv(key, default)

try:
    GEMINI_API_KEY = _get_required_env_var("GEMINI_API_KEY")
    
    NOTION_API_KEY = _get_required_env_var("NOTION_API_KEY")
    NOTION_DATABASE_ID = _get_required_env_var("NOTION_DATABASE_ID")
    
    GOOGLE_DRIVE_FOLDER_ID = _get_required_env_var("GOOGLE_DRIVE_FOLDER_ID")
    GOOGLE_DRIVE_CREDS_FILE = _get_optional_env_var("GOOGLE_DRIVE_CREDS_FILE", "credentials.json")
    
    CHROMADB_PATH = _get_optional_env_var("CHROMADB_PATH", "./chroma_db")
    
    logger.info("모든 환경 변수가 성공적으로 로드되었습니다.")
    
except ConfigurationError as e:
    logger.error(f"설정 오류: {e}")
    raise