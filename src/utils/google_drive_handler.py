# src/utils/google_drive_handler.py
import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
from src.config import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_DRIVE_CREDS_FILE

# Google Drive API의 인증 범위를 정의합니다.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_google_drive_service():
    """
    Google Drive API 서비스 객체를 반환합니다.
    인증이 필요한 경우 OAuth 2.0 흐름을 통해 자격 증명을 획득합니다.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_DRIVE_CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def extract_text_from_pdf(file_bytes):
    """PDF 파일에서 텍스트를 추출합니다. 텍스트 기반 PDF와 이미지 기반 PDF 모두 지원합니다."""
    text = ""
    
    try:
        # 1단계: PyPDF2로 텍스트 기반 PDF에서 텍스트 추출 시도
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            text += page_text
        
        # 2단계: 추출된 텍스트가 충분하지 않으면 OCR 사용
        if len(text.strip()) < 50:  # 텍스트가 너무 적으면 이미지 기반 PDF로 간주
            print("텍스트 기반 추출이 불충분합니다. OCR을 사용하여 이미지에서 텍스트를 추출합니다...")
            text = extract_text_with_ocr(file_bytes)
        else:
            print("텍스트 기반 PDF에서 텍스트 추출 완료")
            
    except Exception as e:
        print(f"PyPDF2 텍스트 추출 실패: {e}. OCR로 재시도합니다...")
        text = extract_text_with_ocr(file_bytes)
    
    return text

def extract_text_with_ocr(file_bytes):
    """OCR을 사용하여 PDF 이미지에서 텍스트를 추출합니다."""
    text = ""
    
    try:
        # PDF를 이미지로 변환
        images = convert_from_bytes(file_bytes)
        print(f"PDF를 {len(images)}개의 이미지로 변환했습니다.")
        
        # 각 이미지에서 OCR로 텍스트 추출
        for i, image in enumerate(images):
            print(f"페이지 {i+1} OCR 처리 중...")
            # pytesseract로 한국어 텍스트 추출
            page_text = pytesseract.image_to_string(image, lang='kor+eng')
            text += f"\n--- 페이지 {i+1} ---\n"
            text += page_text
            
    except Exception as e:
        print(f"OCR 텍스트 추출 중 오류 발생: {e}")
        
    return text

def download_documents_from_folder(service, folder_id):
    """
    지정된 폴더에서 지원되는 문서 파일(PDF)을 다운로드하고 텍스트를 추출합니다.
    특정 키워드가 포함된 문서만 처리합니다.

    Args:
        service (googleapiclient.discovery.Resource): Google Drive API 서비스 객체.
        folder_id (str): 문서를 다운로드할 Google Drive 폴더의 ID.

    Returns:
        list: 텍스트 내용과 파일 이름이 포함된 딕셔너리 목록.
    """
    documents = []
    
    # 포함할 파일 이름에 포함된 키워드 목록을 정의합니다.
    include_keywords = ["회칙", "세칙", "감사", "정기감사","보고서"]
    
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/pdf'",
            fields="files(id, name, mimeType)").execute()
        
        items = results.get('files', [])
        
        if not items:
            print(f"폴더 ID '{folder_id}'에 지원되는 문서가 없습니다.")
            return []
        
        print(f"총 {len(items)}개의 문서를 발견했습니다. 텍스트 추출을 시작합니다.")
        for item in items:
            file_name = item['name']
            
            # 포함 키워드가 파일 이름에 포함되어 있는지 확인
            if not any(keyword in file_name for keyword in include_keywords):
                print(f"'{file_name}' 문서는 포함 키워드를 포함하지 않으므로 건너뜁니다.")
                continue
                
            file_id = item['id']
            mime_type = item['mimeType']
            
            request = service.files().get_media(fileId=file_id)
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_stream.seek(0)
            text_content = ""
            if mime_type == 'application/pdf':
                text_content = extract_text_from_pdf(file_stream.getvalue())
            
            if text_content:
                documents.append({"file_name": file_name, "text_content": text_content})
                print(f"'{file_name}' 문서의 텍스트 추출 완료.")
            else:
                print(f"'{file_name}' 문서에서 텍스트를 추출하지 못했습니다.")
                
    except Exception as e:
        print(f"Google Drive API 호출 중 오류 발생: {e}")
        
    return documents

# 동작하는 예시
if __name__ == "__main__":
    drive_service = get_google_drive_service()
    documents_data = download_documents_from_folder(drive_service, GOOGLE_DRIVE_FOLDER_ID)
    
    if documents_data:
        print("\n--- 추출된 문서 내용 예시 ---")
        for doc in documents_data:
            print(f"파일명: {doc['file_name']}")
            print("내용:", doc['text_content'][:200], "...")
            print("-" * 20)
