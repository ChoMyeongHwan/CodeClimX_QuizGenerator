import asyncio
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from openai import OpenAI
import os

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Firebase 초기화 및 Firestore 클라이언트 설정
cred = credentials.Certificate(os.environ.get("FIREBASE_CREDENTIALS_PATH"))
if not len(firebase_admin._apps):
    initialize_app(cred)
db = firestore.client()

async def fetch_and_process_document(doc):
    video_data = doc.to_dict()
    video_detail = video_data.get('detail', '')
    quiz_generated = video_data.get('descriptive_generated', False)

    if video_detail and not quiz_generated:
        try:
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(None, lambda: client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a model designed to generate descriptive quiz questions as complex JSON objects in Korean. "
                            "Based on the specified focus on IT-related content, create a JSON object containing 3 quizzes, each with 'question', 'hint', and 'difficulty' keys. "
                            "The 'difficulty' key must use one of the following values: 'easy', 'medium', or 'hard'. "
                            "Each quiz should include a 'question' that requires a detailed and descriptive answer from the user and a 'hint' that helps you answer the question. "
                            "Questions should be crafted to reflect a deep understanding and application of IT concepts, encouraging users to elaborate on their responses. "
                            "Ensure each quiz is unique, insightful. "
                            "Additionally, create quizzes based on the given 'video_detail'."
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
            
            response_data = json.loads(response)
            quizzes = response_data.get("quizzes", [])

            quizzes_ref = db.collection('quizzes')
            for quiz in quizzes:
                quiz["video_id"] = doc.id
                quiz["created_at"] = firestore.SERVER_TIMESTAMP
                quiz["type"] = "descriptive"  # 퀴즈 유형 지정
                quizzes_ref.add(quiz)

            doc.reference.update({"descriptive_generated": True})
            print("Descriptive quizzes successfully saved.")
        except Exception as e:
            print(f"Error processing video {doc.id}: {e}")

async def main():
    videos_ref = db.collection(u'videos')
    docs = videos_ref.where(u'descriptive_generated', '==', False).stream()

    tasks = [fetch_and_process_document(doc) for doc in docs]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
