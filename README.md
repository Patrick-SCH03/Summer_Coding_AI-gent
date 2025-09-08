# 🏛️ AI 고도화 학생회 규정 관리 멀티에이전트 시스템

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com/)

## 📋 프로젝트 개요

**🚀 AI 기술이 적용된 학생회 규정 분석 시스템**

학생회 업무에서 발생하는 규정 위반 여부와 감사 처분 가능성을 **AI 멀티에이전트**을 통해 자동으로 분석하는 시스템입니다.

**"학생회비로 회식비 사용이 가능한가요?"** 같은 질문을 입력하면, 다음과 같은 고도화된 AI 기능들이 작동합니다:
- 🧠 **의미론적 분석**: 질문의 진짜 의도를 파악
- 🎯 **위험도 예측**: 머신러닝 기반 사전 위험도 예측  
- 🚨 **이상패턴 탐지**: 비정상적인 질의 패턴 자동 감지
- ⚖️ **3개 전문 AI 에이전트**: 협력을 통한 종합적인 분석과 권고안 제공

## 🎯 핵심 기능

### 🚀 **AI 고도화 기능 **
- **🧠 의미론적 분석**: Google Embeddings를 활용한 질문 의도 자동 파악

### 📊 **멀티에이전트 협업 시스템**
- **📋 규정 검토 에이전트**: 규정 위반 여부 및 위험도 분석
- **🔍 감사 에이전트**: 감사 기준 준수 여부 및 처분 가능성 판단     
- **⚖️ 조정 에이전트**: 두 분석을 종합하여 최종 권고안 도출
- **🧠 의미론적 분석 에이전트**: 질의 의도 파악 및 맥락 이해

### 🔍 **지능형 문서 검색 (RAG)**
- Google Drive와 연동하여 관련 규정 문서 자동 검색
- ChromaDB 벡터 데이터베이스를 활용한 semantic search
- 과거 감사 기록과 처분 사례 자동 참조
- 실시간 문서 업데이트 및 동기화

### 📝 **지능형 기록 및 분석 시스템**
- Notion 데이터베이스에 분석 결과 자동 저장
- 처리 이력 및 위험도 추적 관리
- 성능 메트릭 자동 수집 및 분석
- 사용 패턴 기반 인사이트 생성

  ## 🏗️ 시스템 아키텍처

  ![워크플로우]

  [사용자 질문]
      ↓
  [질문 라우팅] ← 학생회 업무 관련성 판단
      ↓
  [병렬 에이전트 실행]
      ├── 📋 규정 검토 에이전트    └── 🔍 감사 에이전트
      ↓
  [⚖️ 조정 에이전트] ← 결과 종합 및 최종 권고
      ↓[📄 최종 분석 결과]

  ## 🚀 실행 결과 예시

  ### 질문: "학생회비로 회식비 사용이 가능한가요?"

  **📋 규정 검토 결과**:
  - 규정 위반 여부: **위반 가능성 높음**
  - 위험도: **높음**
  - 근거: 학생회비 사용 규정 위반 사례 다수 발견

  **🔍 감사 분석 결과**:
  - 감사 기준 준수: **위반 가능성 높음**
  - 감사 처분 가능성: **높음**
  - 근거: 과거 유사 사례에서 중계상처분 기록 확인

  **⚖️ 최종 권고안**:
  - **핵심 요약**: 감사 처분 가능성이 매우 높음
  - **최종 권고**: 회식비 대신 학생회 공식 활동비 사용 권장

  ## 🛠️ 기술 스택

  ### Core Framework
  - LangGraph: 멀티에이전트 워크플로우 오케스트레이션
  - LangChain: LLM 체인 및 프롬프트 관리
  - Google Gemini 2.5 Flash: 고성능 언어모델

  ### Data & Storage
  - ChromaDB: 벡터 데이터베이스 (문서 임베딩)
  - Google Drive API: 규정 문서 저장소 연동
  - Notion API: 분석 결과 자동 기록

  ### Interface
  - Gradio: 웹 UI 프레임워크

## 📦 설치 및 실행

### ⚡ 빠른 시작 (Quick Start)

```bash
# 1. 저장소 클론
git clone <repository-url>
cd Summer_coding

# 2. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. 의존성 설치
pip install -r requirements.txt

# 4. API 키 설정
cp .env.example .env

# 5. 실행 (3가지 옵션)
python gradio_app.py              # 기본 인터페이스
```

### 🔧 상세 설정

#### 1. 환경 변수 설정

`.env` 파일을 생성하고 다음 정보를 입력:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Google Drive 연동
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id_here

# Notion 연동
NOTION_TOKEN=your_notion_token_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

#### 2. API 키 획득 방법

**🔑 Google Gemini API 키:**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 방문
2. "Create API Key" 클릭
3. 생성된 키를 `.env` 파일에 입력

**📁 Google Drive 폴더 ID:**
1. Google Drive에서 규정 문서들을 저장할 폴더 생성
2. 폴더 URL에서 ID 부분 복사 (예: `1abc-def-ghi-2jkl`)
3. `.env` 파일에 입력

**📝 Notion 설정 (선택사항):**
1. [Notion Developers](https://www.notion.so/my-integrations) 에서 새 integration 생성
2. 데이터베이스 생성 후 integration에 권한 부여
3. 토큰과 데이터베이스 ID를 `.env` 파일에 입력

### 🚀 실행 옵션

#### 기본 인터페이스
```bash
python gradio_app.py
# → http://localhost:7860
```
#### 시스템 데모
```bash
python demo_system.py
```

## 🎮 사용 방법

### 💬 기본 사용법

1. **웹 인터페이스 접속**
   - 브라우저에서 해당 포트로 접속

2. **질문 입력**
   ```
   예시 질문:
   - 학생회비로 회식비 사용이 가능한가요?
   - 신규 사업 예산 집행에 대한 감사 규정을 알려주세요.
   - 학생회 임원 선거 비용 지원이 가능한가요?
   ```

3. **결과 확인**
   - AI 분석 과정 실시간 표시
   - 3개 에이전트의 개별 분석 결과
   - 종합적인 최종 권고안

## 📁 프로젝트 구조

```
Summer_coding/
├── src/                          # 소스 코드
│   ├── agents/                   # AI 에이전트들
│   │   ├── coordinator.py        # 조정 에이전트
│   │   ├── regulation_reviewer.py # 규정 검토 에이전트  
│   │   ├── auditor.py           # 감사 에이전트
│   │   └── document_manager.py   # 문서 관리 에이전트
│   ├── core/                    # 핵심 파이프라인
│   │   └── langgraph_pipeline.py # LangGraph 워크플로우
│   ├── utils/                   # 유틸리티
│   │   ├── notion_handler.py    # Notion API 연동
│   │   ├── google_drive_handler.py # Google Drive 연동
│   │   └── vector_db_manager.py  # 벡터 DB 관리
│   └── config.py               # 설정 관리
├── 📱 인터페이스 파일들
│   ├── gradio_app.py           # 기본 웹 인터페이스
├── 📋 문서화
│   ├── README.md               # 프로젝트 개요
│   ├── TECHNICAL_DOCUMENTATION.md # 기술 문서
├── requirements.txt           # 의존성
└── demo_system.py            # 시스템 데모
```

## 🎯 위험도 판정 시스템

### 📊 판정 기준

#### 📈 높음 (고위험)
- **키워드**: "위반 가능성 높음" + "감사 처분 가능성 높음"  
- **위험 표현**: "처분", "제재", "경고" 등 강한 표현 2개 이상

#### 📊 보통 (중위험)  
- **키워드**: 고위험 키워드 1개 + 중위험 키워드 1개
- **주의 표현**: "주의 필요", "검토 필요" 등

#### 📉 낮음 (저위험)
- **안전 표현**: "위반 없음", "문제없음", "준수" 등
- **긍정 지표**: 중위험 키워드만 1개
