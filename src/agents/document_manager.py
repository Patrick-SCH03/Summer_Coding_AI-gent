# src/agents/document_manager.py
# 문서 관리 에이전트
# 사용자가 지정한 Google Drive 폴더에서 규정 문서를 가져와 벡터 DB에 임베딩하고,
# 다른 에이전트의 요청에 따라 관련 조항을 검색하여 제공합니다.

import os
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from src.utils.google_drive_handler import get_google_drive_service, download_documents_from_folder
from src.utils.vector_db_manager import add_documents_to_db, search_documents_from_db, get_vector_store
from src.config import GOOGLE_DRIVE_FOLDER_ID

class DocumentManagerAgent:
    """
    학생회 규정 문서를 관리하는 에이전트입니다.
    """
    def __init__(self, collection_name="student_council_regulations"):
        """
        에이전트를 초기화하고 Google Drive 서비스와 벡터 DB 컬렉션을 설정합니다.

        Args:
            collection_name (str): 문서를 저장할 ChromaDB 컬렉션 이름.
        """
        self.collection_name = collection_name
        self.drive_service = get_google_drive_service()

    def get_relevant_documents(self, query, folder_id=None, k=5):
        """
        주어진 쿼리에 대한 가장 관련성 높은 문서를 벡터 DB에서 검색합니다.
        
        Args:
            query (str): 사용자의 질의 텍스트.
            folder_id (str, optional): 검색할 Google Drive 폴더의 ID.
                                     None이면 기본 컬렉션에서 검색합니다.
            k (int): 반환할 문서의 개수.

        Returns:
            list: 관련 문서 청크 목록.
        """
        if not folder_id:
            # .env 파일에 GOOGLE_DRIVE_FOLDER_ID가 없으면 오류를 발생시킵니다.
            if not GOOGLE_DRIVE_FOLDER_ID:
                raise ValueError("폴더 ID가 제공되지 않았습니다. .env 파일에 GOOGLE_DRIVE_FOLDER_ID를 설정하거나, Gradio UI에 폴더 ID를 입력해야 합니다.")
            folder_id = GOOGLE_DRIVE_FOLDER_ID

        collection_name = f"regulations_{folder_id}"
        
        # 해당 폴더의 컬렉션이 이미 있는지 확인합니다.
        vector_store = get_vector_store(collection_name)
        
        # 컬렉션에 문서가 없으면 새로 처리
        if not vector_store._collection.count():
            print(f"새로운 폴더 ID '{folder_id}'에 대한 문서를 처리합니다.")
            documents = download_documents_from_folder(self.drive_service, folder_id)
            if not documents:
                print(f"폴더 '{folder_id}'에 문서가 없습니다.")
                return []
            else:
                add_documents_to_db(documents, collection_name)
    
        print(f"'{query}'에 대한 관련 규정을 '{collection_name}' 컬렉션에서 검색합니다...")
        return search_documents_from_db(query, collection_name, k=k)