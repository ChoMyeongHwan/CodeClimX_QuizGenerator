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

# 각 문서(여기서는 비디오 정보)를 처리하는 비동기 함수.
async def fetch_and_process_document(doc):
    video_data = doc.to_dict()  # Firestore 문서를 파이썬 딕셔너리로 변환.
    detail = video_data.get('detail', '')  # 'detail' 키의 값을 가져옴. 없을 경우 빈 문자열을 반환.
    quiz_generated = video_data.get('quiz_generated', False)  # 퀴즈 생성 여부를 확인.

    if detail and not quiz_generated:  # 'detail' 필드가 존재하고, 퀴즈가 아직 생성되지 않았을 경우에만 처리.
        try:
            # 비동기 이벤트 루프를 가져옴.
            loop = asyncio.get_event_loop()
            # 동기 함수인 OpenAI의 API 호출을 비동기적으로 실행.
            completion = await loop.run_in_executor(None, lambda: client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 IT 개발 최고 수준의 전문가입니다."
                    },
                    {
                        "role": "user", 
                        "content": f"다음 세부 정보를 바탕으로 IT 관련 객관식 퀴즈 3개를 만들어주세요. 난이도는 쉬움, 보통, 어려움 중에서 선택하고, 각 문제에는 4개의 선택지와 정답을 포함해주세요. 출력은 다음과 같은 JSON 포맷 형식으로 출력해주세요: {{'question': <질문>, 'choices': [<선택지1>, <선택지2>, <선택지3>, <선택지4>], 'answer': <정답>, 'difficulty': <난이도>}}: {detail}"
                    },
                ]
            ))
            # API 응답에서 퀴즈 생성 결과를 추출.
            response = completion.choices[0].message.content if completion.choices else "응답 없음"
            print(f"비디오 {doc.id}에 대한 응답: {response}")

            # response 문자열에서 불필요한 부분 제거
            response_cleaned = response.replace("```json\n", "").replace("\n```", "")

            # 퀴즈를 JSON으로 변환.
            quiz_json = json.loads(response_cleaned)

            # 'Quizzes' 컬렉션에 퀴즈를 저장.
            quizzes_ref = db.collection('quizzes')

            # 퀴즈에 대한 각 문항을 개별적으로 처리.
            for quiz_item in quiz_json:
                # 퀴즈에 비디오 ID와 생성일자 추가.
                quiz_item["video_id"] = doc.id
                quiz_item["created_at"] = firestore.SERVER_TIMESTAMP

                # 정답을 선택지 리스트에서 찾아 인덱스로 저장.
                answer_index = quiz_item["choices"].index(quiz_item["answer"])
                quiz_item["answer"] = answer_index

                # 각각의 퀴즈 항목을 'Quizzes' 컬렉션에 추가.
                quizzes_ref.add(quiz_item)
            
            # 퀴즈 생성 여부를 업데이트.
            doc.reference.update({"quiz_generated": True})
            
            print("-----퀴즈 저장 완료-----")
        except Exception as e:
            print(f"비디오 {doc.id} 처리 중 오류 발생: {e}")

# 메인 비동기 함수.
async def main():
    videos_ref = db.collection(u'videos')  # 'videos' 컬렉션에 대한 참조를 가져옴.
    docs = videos_ref.where(u'quiz_generated', '==', False).stream()  # 아직 퀴즈가 생성되지 않은 문서만 스트리밍.

    # 각 문서에 대해 fetch_and_process_document 함수를 비동기적으로 실행하는 태스크를 생성.
    tasks = [fetch_and_process_document(doc) for doc in docs]
    await asyncio.gather(*tasks)  # 모든 태스크가 완료될 때까지 기다림.

if __name__ == "__main__":
    asyncio.run(main())  # 메인 함수를 비동기적으로 실행.
