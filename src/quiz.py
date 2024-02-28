# 필요한 라이브러리 설치
# pip install python-dotenv firebase-admin openai asyncio
import asyncio
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from openai import OpenAI
import os

# .env 파일에서 환경 변수를 로드. 
# 이 파일은 API 키와 같은 중요한 정보를 저장.
load_dotenv()

# OpenAI 클라이언트를 초기화.
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Firebase를 초기화하고 Firestore 클라이언트를 설정.
# Firebase 관련 설정은 .env 파일에 저장된 경로에서 JSON 형태로 불러옴.
cred = credentials.Certificate(os.environ.get("FIREBASE_CREDENTIALS_PATH"))
if not len(firebase_admin._apps):
    initialize_app(cred)  # 이미 초기화되지 않았다면 초기화를 수행.
db = firestore.client()

# 각 문서(여기서는 비디오 정보)를 처리하는 비동기 함수.
async def fetch_and_process_document(doc):
    video_data = doc.to_dict()  # Firestore 문서를 파이썬 딕셔너리로 변환.
    detail = video_data.get('detail', '')  # 'detail' 키의 값을 가져옴. 없을 경우 빈 문자열을 반환.

    if detail:  # 'detail' 필드가 존재할 경우에만 처리를 진행.
        try:
            # 비동기 이벤트 루프를 가져옴.
            loop = asyncio.get_event_loop()

            # 동기 함수인 OpenAI의 API 호출을 비동기적으로 실행.
            # run_in_executor를 사용해 동기 함수를 비동기적으로 처리할 수 있음.
            completion = await loop.run_in_executor(None, lambda: client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "너는 IT 개발 최고 수준의 전문가야"},
                    {"role": "user", "content": f"다음 세부 정보를 바탕으로 객관식 퀴즈를 만들어주세요. 난이도는 쉬움, 보통, 어려움 중에서 선택하고, 각 문제에는 4개의 선택지와 정답을 포함해주세요: {detail}"},
                ]
            ))
            # API 응답에서 퀴즈 생성 결과를 추출.
            response = completion.choices[0].message.content if completion.choices else "응답 없음"
            print(f"비디오 {doc.id}에 대한 응답: {response}")
        except Exception as e:
            # 오류 발생 시 콘솔에 오류 메시지를 출력.
            print(f"비디오 {doc.id} 처리 중 오류 발생: {e}")

# 메인 비동기 함수.
async def main():
    videos_ref = db.collection(u'videos')  # 'videos' 컬렉션에 대한 참조를 가져옴.
    docs = videos_ref.stream()  # 컬렉션의 모든 문서를 스트리밍.

    # 각 문서에 대해 fetch_and_process_document 함수를 비동기적으로 실행하는 태스크를 생성.
    tasks = [fetch_and_process_document(doc) for doc in docs]
    await asyncio.gather(*tasks)  # 모든 태스크가 완료될 때까지 기다림.

if __name__ == "__main__":
    asyncio.run(main())  # 메인 함수를 비동기적으로 실행.
