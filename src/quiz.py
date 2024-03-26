# 필요한 라이브러리 설치
# pip install python-dotenv firebase-admin openai asyncio
import asyncio
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from openai import OpenAI
import os

# .env 파일에서 환경 변수를 로드. 
load_dotenv()

# OpenAI 클라이언트를 초기화.
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Firebase를 초기화하고 Firestore 클라이언트를 설정.
cred = credentials.Certificate(os.environ.get("FIREBASE_CREDENTIALS_PATH"))
if not len(firebase_admin._apps):
    initialize_app(cred)  # 이미 초기화되지 않았다면 초기화를 수행.
db = firestore.client()

async def fetch_and_process_document(doc):
    """
    Fetches video document from Firestore, generates quizzes using OpenAI API,
    and stores them back in Firestore.
    
    Parameters:
        doc: Firestore document representing a video.
    """
    video_data = doc.to_dict()  # Firestore 문서를 파이썬 딕셔너리로 변환.
    video_detail = video_data.get('detail', '')  # 'detail' 키의 값을 가져옴. 없을 경우 빈 문자열을 반환.
    quiz_generated = video_data.get('quiz_generated', False)  # 퀴즈 생성 여부를 확인.

    if video_detail and not quiz_generated:  # 'detail' 필드가 존재하고, 퀴즈가 아직 생성되지 않았을 경우에만 처리.
        try:
            # 비동기 이벤트 루프를 가져옴.
            loop = asyncio.get_event_loop()
            # 동기 함수인 OpenAI의 API 호출을 비동기적으로 실행.
            completion = await loop.run_in_executor(None, lambda: client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a model designed to generate multiple choice quiz questions as complex JSON objects in Korean. "
                            "Based on the input 'video_detail', create a JSON object containing 10 quizzes, "
                            "each with 'question', 'choices', 'answer', and 'difficulty' keys. "
                            "'choices' must contain four options, and 'difficulty' must use one of the following values: 'easy', 'medium', or 'hard'. "
                            "Ensure each quiz is unique, relevant to the input details, and relevant to the IT field."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"video_detail: {video_detail}."
                        )
                    },
                ]
            ))
            
            response = completion.choices[0].message.content if completion.choices else "{}"
            print(f"Response from video {doc.id}: {response}")

            try:
                response_data = json.loads(response)
                quizzes = response_data.get("quizzes", [])
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return

            # Process the quizzes
            quizzes_ref = db.collection('quizzes')
            for quiz in quizzes:
                quiz["video_id"] = doc.id
                quiz["created_at"] = firestore.SERVER_TIMESTAMP
                quiz["type"] = "multiple"
                try:
                    # 선택지에서 정답 인덱스를 찾음
                    answer_index = quiz["choices"].index(quiz["answer"])
                    # 답변을 인덱스로 업데이트
                    quiz["answer"] = answer_index
                except ValueError:
                    print(f"Answer not found in choices for quiz on video {doc.id}")
                    continue  # 정답이 선택지에 없으면 해당 퀴즈를 건너뛰고 계속 진행
                quizzes_ref.add(quiz)

            doc.reference.update({"quiz_generated": True})
            print("Quizzes successfully saved.")
        except Exception as e:
            print(f"Error processing video {doc.id}: {e}")

# 메인 비동기 함수.
async def main():
    videos_ref = db.collection(u'videos')  # 'videos' 컬렉션에 대한 참조를 가져옴.
    docs = videos_ref.where(u'quiz_generated', '==', False).stream()  # 아직 퀴즈가 생성되지 않은 문서만 스트리밍.

    # 각 문서에 대해 fetch_and_process_document 함수를 비동기적으로 실행하는 태스크를 생성.
    tasks = [fetch_and_process_document(doc) for doc in docs]
    await asyncio.gather(*tasks)  # 모든 태스크가 완료될 때까지 기다림.

if __name__ == "__main__":
    asyncio.run(main())  # 메인 함수를 비동기적으로 실행.
