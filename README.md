# CodeClimX_QuizGenerator

CodeClimX_QuizGenerator는 비디오 강의의 내용을 분석하여 퀴즈를 자동으로 생성하는 파이썬 스크립트입니다. 이 스크립트는 Firebase Firestore에서 비디오 데이터를 불러온 후, OpenAI API를 활용하여 해당 비디오의 내용에 기반한 퀴즈를 생성하고, 생성된 퀴즈를 다시 Firestore에 저장합니다.

## 시작하기 전에

이 프로젝트를 사용하기 전에, 다음 조건들을 충족해야 합니다:

- Python 3.8 이상이 설치되어 있어야 합니다.
- Firebase 프로젝트와 OpenAI API 키가 필요합니다.

## 설치 방법

1. 프로젝트를 클론합니다.

```bash
git clone https://github.com/ChoMyeongHwan/CodeClimX_QuizGenerator.git
```

2. 프로젝트 디렉토리로 이동합니다.

```bash
cd CodeClimX_QuizGenerator
```

3. 필요한 Python 라이브러리를 설치합니다.

```bash
pip install python-dotenv firebase-admin openai asyncio
```

## 사용 방법

1. `.env` 파일을 생성하고, Firebase 프로젝트의 서비스 계정 키 파일 경로(`FIREBASE_CREDENTIALS_PATH`)와 OpenAI API 키(`OPENAI_API_KEY`)를 지정합니다.

```
FIREBASE_CREDENTIALS_PATH="path/to/your/firebase-credentials.json"
OPENAI_API_KEY="your-openai-api-key"
```

2. Firestore에 `videos` 컬렉션을 생성하고, 각 비디오 문서에 `detail` 필드(비디오의 내용을 설명하는 텍스트)와 `quiz_generated` 필드(퀴즈 생성 여부를 나타내는 부울 값, 초기값은 `false`)를 포함시킵니다.

3. 스크립트를 실행하여 퀴즈를 생성합니다.

```bash
python src/main.py
```

스크립트는 아직 퀴즈가 생성되지 않은 모든 비디오에 대해 퀴즈를 생성하고, 생성된 퀴즈를 Firestore의 `quizzes` 컬렉션에 저장합니다. 또한, 관련 비디오 문서의 `quiz_generated` 필드를 `true`로 업데이트하여 퀴즈가 생성되었음을 표시합니다.

## 기여하기

이 프로젝트에 기여하고 싶으신 분들은 언제든지 Pull Request를 보내주시거나, 이슈를 등록해 주세요.
