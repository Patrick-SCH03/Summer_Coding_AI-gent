# src/utils/notion_handler.py
# 이 파일은 Notion API를 사용하여 데이터를 Notion 데이터베이스에 기록하는 역할을 합니다.

from notion_client import Client
from notion_client.helpers import get_id
from src.config import NOTION_API_KEY, NOTION_DATABASE_ID
from typing import Dict, Any, Optional

# Notion API 클라이언트 초기화
try:
    notion_client = Client(auth=NOTION_API_KEY)
except Exception as e:
    print(f"Notion 클라이언트 초기화 중 오류 발생: {e}")
    notion_client = None

def get_notion_client():
    """
    초기화된 Notion 클라이언트를 반환합니다.
    클라이언트가 유효하지 않으면 None을 반환합니다.
    """
    return notion_client

def record_result_to_notion(result_data: Dict[str, Any]):
    """
    멀티에이전트 시스템의 결과를 Notion 데이터베이스에 기록합니다.

    Args:
        result_data (dict): 기록할 데이터가 담긴 딕셔너리.
                            예: {"title": "제목", "content": "본문 내용", "risk_level": "높음"}
    
    Returns:
        bool: 기록 성공 여부.
    """
    if not notion_client:
        print("Notion 클라이언트가 유효하지 않아 데이터를 기록할 수 없습니다.")
        return False

    # Notion 데이터베이스 ID가 유효한지 확인합니다.
    try:
        # get_id는 URL에서 데이터베이스 ID를 추출합니다.
        database_id = get_id(NOTION_DATABASE_ID)
    except Exception as e:
        print(f"Notion 데이터베이스 ID가 유효하지 않습니다: {e}")
        return False
    
    # 페이지 생성 시 필요한 속성들을 정의합니다.
    properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": result_data.get("title", "분석 결과")
                    }
                }
            ]
        },
        "Risk Level": {
            "select": {
                "name": result_data.get("risk_level", "알 수 없음")
            }
        },
    }
    
    # 본문 내용을 2000자 단위로 분할합니다.
    content_to_record = result_data.get("content", "내용 없음")
    block_size = 2000
    blocks = []
    
    # 제목 블록 추가
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "최종 종합 분석"}}]
        }
    })
    
    # 본문 내용 분할 및 블록 추가
    for i in range(0, len(content_to_record), block_size):
        chunk = content_to_record[i:i + block_size]
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": chunk}
                    }
                ]
            }
        })
    
    try:
        # Notion 데이터베이스에 새로운 페이지를 생성합니다.
        page_response = notion_client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        # 페이지가 성공적으로 생성되면, 본문 내용을 블록으로 추가합니다.
        page_id = page_response["id"]
        if blocks:
            # 모든 블록을 하나의 API 호출로 처리하여 성능을 향상시킵니다.
            notion_client.blocks.children.append(
                block_id=page_id,
                children=blocks
            )
            
        print("Notion 데이터베이스에 결과가 성공적으로 기록되었습니다.")
        return True
    except Exception as e:
        print(f"Notion에 데이터를 기록하는 중 오류 발생: {e}")
        return False

# 동작하는 예시
if __name__ == "__main__":
    # 예시로 기록할 데이터
    example_data = {
        "title": "학생회 예산 집행 규정 분석",
        "content": "2025년 3월 예산안은 재정 규정 제3조 2항 '항목별 예산 초과 금지' 조항에 위배될 가능성이 있습니다." * 1,
        "risk_level": "높음"
    }
    
    # Notion에 데이터 기록 함수 호출
    record_result_to_notion(example_data)