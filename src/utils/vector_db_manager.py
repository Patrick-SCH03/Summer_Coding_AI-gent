# src/utils/vector_db_manager.py
# 이 파일은 ChromaDB를 사용하여 문서 임베딩 및 벡터 검색을 관리합니다.

import chromadb
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import GEMINI_API_KEY, CHROMADB_PATH

# ChromaDB 클라이언트와 임베딩 모델을 전역으로 초기화합니다.
client = None
embeddings = None

try:
    # 설정 파일에 지정된 경로를 사용하여 영구적인 DB를 생성합니다.
    client = chromadb.PersistentClient(path=CHROMADB_PATH)
    print("ChromaDB 클라이언트 초기화 성공.")
except Exception as e:
    print(f"ChromaDB 클라이언트 초기화 중 오류 발생: {e}")
    print(e)

try:
    # Gemini 임베딩 모델을 초기화합니다.
    if GEMINI_API_KEY:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
        print("Gemini 임베딩 모델 초기화 성공.")
    else:
        print("경고: GEMINI_API_KEY가 설정되지 않았습니다.")
except Exception as e:
    print(f"임베딩 모델 초기화 중 오류 발생: {e}")
    print(e)

def get_vector_store(collection_name):
    """
    지정된 컬렉션 이름의 Chroma 벡터 저장소를 반환합니다.
    
    Args:
        collection_name (str): 사용할 컬렉션의 이름.

    Returns:
        Chroma: Chroma 벡터 저장소 객체.
    """
    if not client or not embeddings:
        print("에러: 벡터 데이터베이스 또는 임베딩 모델이 유효하지 않습니다.")
        return None
    
    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings
    )

def _split_documents_into_chunks(documents):
    """
    텍스트 문서를 의미 기반의 작은 청크로 분할하고 파일 이름 메타데이터를 추가합니다.
    
    Args:
        documents (list): 텍스트 내용이 담긴 딕셔너리 목록.
        
    Returns:
        list: 분할된 문서 청크 목록 (메타데이터 포함).
    """
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        all_chunks = []
        for doc in documents:
            text_content = doc["text_content"]
            file_name = doc["file_name"]
            
            # 각 문서를 청크로 분할
            chunks = text_splitter.create_documents([text_content])
            
            # 각 청크에 파일 이름 메타데이터 추가
            for chunk in chunks:
                chunk.metadata["source_file"] = file_name
            
            all_chunks.extend(chunks)
            
        return all_chunks
    except Exception as e:
        print(f"문서 분할 중 오류 발생: {e}")
        return []

def add_documents_to_db(documents, collection_name):
    """
    문서를 청크로 분할하고 벡터 데이터베이스에 추가합니다.

    Args:
        documents (list): 텍스트 문서 목록.
        collection_name (str): 문서를 추가할 컬렉션의 이름.
    
    Returns:
        bool: 작업 성공 여부.
    """
    if not client or not embeddings:
        print("벡터 데이터베이스 또는 임베딩 모델이 유효하지 않습니다.")
        return False
        
    try:
        split_documents = _split_documents_into_chunks(documents)
        if not split_documents:
            return False

        vector_store = get_vector_store(collection_name)
        if not vector_store:
            print("벡터 저장소를 가져오는 데 실패했습니다.")
            return False
        
        vector_store.add_documents(split_documents)
        print(f"총 {len(split_documents)}개의 문서 청크가 ChromaDB에 추가되었습니다.")
        return True
            
    except Exception as e:
        print(f"문서 추가 중 오류 발생: {e}")
        return False

def search_documents_from_db(query, collection_name, k=5):
    """
    쿼리와 가장 유사한 문서를 벡터 데이터베이스에서 검색합니다.

    Args:
        query (str): 검색할 쿼리 텍스트.
        collection_name (str): 검색할 컬렉션의 이름.
        k (int): 반환할 문서의 개수.

    Returns:
        list: 검색된 관련 문서 목록.
    """
    if not client or not embeddings:
        print("벡터 데이터베이스 또는 임베딩 모델이 유효하지 않습니다.")
        return []
        
    try:
        vector_store = get_vector_store(collection_name)
        if not vector_store:
            print("벡터 저장소를 가져오는 데 실패했습니다.")
            return []
            
        # 유사도 검색
        retrieved_docs = vector_store.similarity_search(query, k=k)
        print(f"'{query}'에 대한 {len(retrieved_docs)}개의 관련 문서를 찾았습니다.")
        return retrieved_docs
            
    except Exception as e:
        print(f"문서 검색 중 오류 발생: {e}")
        return []