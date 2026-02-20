# BizTone Converter 프로젝트

## 프로젝트 개요

이 프로젝트, BizTone Converter는 일상적인 표현을 전문적인 비즈니스 언어로 변환하여 사용자를 돕는 AI 기반 웹 애플리케이션입니다. 비즈니스 커뮤니케이션에 익숙하지 않은 신입사원과 같은 사용자를 주 대상으로 합니다.

애플리케이션은 풀스택 아키텍처로 구축되었습니다.
-   **백엔드**: Python의 Flask 프레임워크를 사용하는 서버입니다. Groq AI 서비스를 활용하여 언어 변환을 수행하는 단일 API 엔드포인트(`/api/convert`)를 제공하며, 프론트엔드 정적 파일도 함께 제공합니다.
-   **프론트엔드**: 순수 HTML, JavaScript로 구축되었으며, 스타일링은 Tailwind CSS(Play CDN을 통해 로드)를 사용합니다.
-   **배포**: Vercel 플랫폼에 쉽게 배포할 수 있도록 구성되어 있습니다.

## 빌드 및 실행 방법

### 1. 백엔드 설정 및 실행
백엔드는 표준 Python Flask 애플리케이션입니다.

1.  **백엔드 디렉토리로 이동합니다:**
    ```bash
    cd backend
    ```

2.  **Python 가상 환경을 생성하고 활성화합니다:**
    ```bash
    # macOS/Linux 용
    python3 -m venv .venv
    source .venv/bin/activate

    # Windows 용
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **의존성을 설치합니다:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수를 설정합니다:**
    프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 Groq API 키를 추가합니다:
    ```
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    ```

5.  **개발 서버를 실행합니다:**
    ```bash
    python app.py
    ```
    서버는 `http://localhost:5001`에서 시작됩니다.

### 2. 프론트엔드 접속
프론트엔드는 Flask 백엔드에 의해 직접 제공됩니다. 백엔드 서버가 실행되면 웹 브라우저를 열고 다음 주소로 이동하여 애플리케이션에 접속할 수 있습니다:
-   **URL**: `http://localhost:5001`

## 개발 규약

-   **API**: 백엔드는 단일 RESTful 엔드포인트 `POST /api/convert`를 제공합니다. 이 엔드포인트는 `text`(원본 텍스트)와 `target`(`Upward`, `Lateral`, 또는 `External`)을 포함하는 JSON 페이로드를 받아 변환된 텍스트를 반환합니다.
-   **스타일링**: 프론트엔드는 Play CDN을 통해 로드된 Tailwind CSS를 사용하여 스타일을 적용합니다. 전역 스타일 및 커스텀 컴포넌트(`@layer components`)는 `frontend/index.html`의 `<style type="text/tailwindcss">` 태그 내에 정의됩니다.
-   **비밀 관리**: API 키 및 기타 비밀 정보는 `python-dotenv`를 사용하여 `.env` 파일로부터 로드된 환경 변수를 통해 관리됩니다. `vercel.json` 파일은 Vercel 배포 시 이러한 변수들이 어떻게 설정되는지 보여줍니다 (예: `"GROQ_API_KEY": "@groq_api_key"`).
-   **배포**: `vercel.json` 파일은 Flask 애플리케이션을 Python 서버리스 함수로 배포하도록 구성되어 있습니다. API 요청은 백엔드로, 그 외 모든 요청(CSS, JS 등 정적 자산 포함)은 프론트엔드 디렉토리로 올바르게 라우팅됩니다.
