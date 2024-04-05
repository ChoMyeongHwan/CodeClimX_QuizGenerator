# 🚀 CodeClimX_QuizGenerator

CodeClimX_QuizGenerator는 비디오 강의의 내용을 분석하여 자동으로 퀴즈를 생성하는 Python 스크립트입니다. Firebase Firestore에서 비디오 데이터를 불러오고, OpenAI API를 사용하여 비디오 내용 기반의 퀴즈를 생성한 후, 생성된 퀴즈를 다시 Firestore에 저장합니다.

## 📚 목차

- [📝 시작하기 전에](#-시작하기-전에)
- [💾 설치 방법](#-설치-방법)
- [📘 사용 방법](#-사용-방법)
- [🤝 기여하기](#-기여하기)

## 📝 시작하기 전에

프로젝트 사용을 시작하기 전에 아래 조건들이 충족되어야 합니다:

- Python 3.8 이상 설치
- Firebase 프로젝트와 OpenAI API 키 준비

## 💾 설치 방법

1. **프로젝트 클론하기**

    ```bash
    git clone https://github.com/ChoMyeongHwan/CodeClimX_QuizGenerator.git
    ```

2. **프로젝트 디렉토리로 이동하기**

    ```bash
    cd CodeClimX_QuizGenerator
    ```

3. **필요한 Python 라이브러리 설치하기**

    ```bash
    pip install python-dotenv firebase-admin openai asyncio
    ```

## 📘 사용 방법

1. **`.env` 파일 생성 및 설정하기**

    `.env` 파일 안에 Firebase 프로젝트의 서비스 계정 키 파일 경로(`FIREBASE_CREDENTIALS_PATH`)와 OpenAI API 키(`OPENAI_API_KEY`)를 지정합니다.

    ```
    FIREBASE_CREDENTIALS_PATH="path/to/your/firebase-credentials.json"
    OPENAI_API_KEY="your-openai-api-key"
    ```

2. **Firestore 설정하기**

    Firestore에 `videos` 컬렉션을 생성하고, 각 비디오 문서에 `detail` 필드(비디오 내용 설명)와 `quiz_generated` 필드(퀴즈 생성 여부, 초기값 `false`)를 포함시킵니다.

3. **스크립트 실행하여 퀴즈 생성하기**

    ```bash
    python src/quiz.py
    ```

    스크립트는 아직 퀴즈가 생성되지 않은 모든 비디오에 대해 퀴즈를 생성하고, 생성된 퀴즈를 Firestore의 `quizzes` 컬렉션에 저장합니다. 이후, 관련 비디오 문서의 `quiz_generated` 필드를 `true`로 업데이트합니다.

## 🤝 기여하기

이 프로젝트는 오픈 소스이며, 모든 형태의 기여를 환영합니다. 기여 방법은 다음과 같습니다:

- **Pull Request 보내기**: 새로운 기능 추가, 버그 수정, 문서 개선 등의 기여를 위해 PR을 보내주세요.
- **이슈 등록하기**: 버그를 발견하거나 새로운 기능 제안이 있다면, 이슈를 등록해 주세요.
