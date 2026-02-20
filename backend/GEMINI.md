# Backend Directory (backend/)

## 프로젝트 개요

`backend/` 디렉토리는 BizTone Converter 애플리케이션의 핵심 로직을 담당하는 Python Flask 서버를 포함합니다. 이 백엔드는 주로 두 가지 역할을 수행합니다:
1.  **AI 기반 텍스트 변환 API 제공**: 사용자의 요청을 받아 Groq AI 서비스를 활용하여 비즈니스 말투로 텍스트를 변환합니다.
2.  **프론트엔드 정적 파일 서빙**: `frontend/` 디렉토리의 HTML, CSS, JavaScript 파일들을 클라이언트에 제공하여 풀스택 애플리케이션을 단일 서버에서 운영할 수 있도록 합니다.

## 설정 및 실행 방법

`backend/` 서버를 로컬에서 개발 모드로 실행하기 위한 단계는 다음과 같습니다.

1.  **백엔드 디렉토리로 이동합니다:**
    ```bash
    cd backend
    ```

2.  **Python 가상 환경을 생성하고 활성화합니다:**
    프로젝트의 의존성을 분리하기 위해 가상 환경을 사용하는 것이 좋습니다.
    ```bash
    # macOS/Linux 용
    python3 -m venv .venv_backend
    source .venv_backend/bin/activate

    # Windows 용
    python -m venv .venv_backend
    .\.venv_backend\Scripts\activate
    ```

3.  **의존성을 설치합니다:**
    필요한 모든 Python 패키지는 `requirements.txt`에 명시되어 있습니다.
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수를 설정합니다:**
    Groq AI 서비스에 접근하기 위한 API 키를 설정해야 합니다. 프로젝트 루트 디렉토리 (`../.env`)에 `.env` 파일을 생성하고 다음 내용을 추가합니다:
    ```
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    ```
    `app.py`는 `python-dotenv` 라이브러리를 사용하여 이 파일을 자동으로 로드합니다.

5.  **개발 서버를 실행합니다:**
    ```bash
    python app.py
    ```
    서버는 기본적으로 `http://localhost:5001`에서 실행됩니다 (`debug=True` 설정).

## API 엔드포인트

백엔드는 다음과 같은 주요 API 엔드포인트를 제공합니다.

### 1. `POST /api/convert`
-   **설명**: 사용자가 입력한 텍스트를 지정된 비즈니스 말투(대상)로 변환하는 핵심 API입니다.
-   **메서드**: `POST`
-   **요청 본문 (JSON)**:
    ```json
    {
        "text": "변환할 일상적인 문장",
        "target": "Upward" | "Lateral" | "External"
    }
    ```
    -   `text`: 변환하고자 하는 원본 텍스트.
    -   `target`: 변환 대상 (상사: `Upward`, 동료: `Lateral`, 고객: `External`).
-   **응답 본문 (JSON)**:
    -   성공 시:
        ```json
        {
            "original_text": "원본 텍스트",
            "converted_text": "변환된 비즈니스 말투 텍스트",
            "target": "변환 대상"
        }
        ```
    -   오류 시:
        ```json
        {
            "error": "오류 메시지"
        }
        ```
        HTTP 상태 코드 400 (Bad Request) 또는 500 (Internal Server Error).
-   **AI 모델**: Groq AI 서비스의 `moonshotai/kimi-k2-instruct-0905` 모델을 사용합니다.
-   **프롬프트 엔지니어링**: 각 `target` 값에 따라 최적화된 한글 시스템 프롬프트가 `app.py` 내 `SYSTEM_PROMPTS` 사전에 정의되어 있습니다.

### 2. `GET /health`
-   **설명**: 서버의 상태를 확인하기 위한 헬스 체크 엔드포인트입니다.
-   **메서드**: `GET`
-   **응답 본문 (JSON)**:
    ```json
    {
        "status": "healthy"
    }
    ```
    HTTP 상태 코드 200 (OK).

## 정적 파일 서빙

`backend/app.py`는 Flask의 `send_from_directory` 함수를 사용하여 `frontend/` 디렉토리의 정적 파일(HTML, CSS, JS)을 제공합니다.
-   `GET /`: `frontend/index.html`을 반환합니다.
-   `GET /<path:path>`: `frontend/` 디렉토리 내의 요청된 파일을 반환합니다. 경로 조작(`..`) 방지를 위한 기본적인 보안 로직이 포함되어 있습니다.

## 주요 기술 스택 및 라이브러리

-   **Python**: 백엔드 프로그래밍 언어.
-   **Flask**: 웹 애플리케이션 프레임워크 (RESTful API 및 정적 파일 서빙).
-   **Groq SDK**: Groq AI 서비스와 연동하기 위한 Python 클라이언트 라이브러리.
-   **python-dotenv**: `.env` 파일에서 환경 변수를 로드하는 데 사용됩니다.
-   **Flask-CORS**: 교차 출처 리소스 공유(CORS)를 활성화하여 프론트엔드와 백엔드 간의 통신을 허용합니다.
-   **Logging**: Python의 내장 `logging` 모듈을 사용하여 서버 동작 및 오류를 기록합니다.

## 개발 규약 및 특징

-   **모듈성**: `app.py`는 모든 백엔드 로직을 포함하는 단일 파일로 구성되어 있습니다.
-   **환경 변수**: `GROQ_API_KEY`와 같은 민감한 정보는 환경 변수를 통해 안전하게 관리됩니다.
-   **로깅**: 중요한 작업(예: API 요청 수신, 오류 발생)에 대한 정보 로깅이 구현되어 개발 및 디버깅에 유용합니다.
-   **프롬프트 엔지니어링**: AI 모델의 효율적인 활용을 위해 각 비즈니스 상황(대상)에 맞춘 상세하고 한국어 기반의 시스템 프롬프트가 정의되어 있습니다.
-   **오류 처리**: API 요청 본문 유효성 검사, Groq API 호출 실패 등 다양한 오류 상황에 대한 기본적인 처리가 구현되어 있습니다.
