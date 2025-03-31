import os
import requests
from langchain.llms.base import LLM
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class GeminiLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "gemini"

    def _call(self, prompt: str, stop=None) -> str:
        # 환경 변수에서 API 키 로드
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

        # ** gemini-2.0-flash 및 v1beta 엔드포인트 사용**
        model_name = "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}" # **v1beta 엔드포인트 유지**

        # 요청 본문 구조는 이전과 동일하게 유지
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.5,
                "topK": 40,
                "topP": 0.9,
                "maxOutputTokens": 800,
                "stopSequences": []
            }
        }

        # 디버깅을 위한 출력 (API 키 노출 방지)
        print(f"API 요청 URL: https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent")

        # API 요청
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            # 응답 상태 코드 확인 및 오류 처리 강화
            print(f"응답 상태 코드: {response.status_code}")
            response.raise_for_status()  # HTTP 오류 발생 시 예외를 발생시킴

            # 응답 파싱
            response_json = response.json()

            # 응답에서 텍스트 추출 (기존 로직 유지)
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                if "content" in response_json["candidates"][0]:
                    if "parts" in response_json["candidates"][0]["content"]:
                        if len(response_json["candidates"][0]["content"]["parts"]) > 0:
                            if "text" in response_json["candidates"][0]["content"]["parts"][0]:
                                return response_json["candidates"][0]["content"]["parts"][0]["text"]

            # 응답 구조가 예상과 다른 경우
            print("응답 구조가 예상과 다릅니다.")
            return f"응답 파싱 오류: {response_json}"

        except requests.exceptions.HTTPError as e:
            # HTTP 에러 (404 포함) 처리
            print(f"HTTP 오류 발생: {e}")
            print(f"오류 응답 내용: {e.response.text}")  # 오류 응답 내용 출력 (자세한 오류 정보 확인)
            return f"API HTTP 오류: {e.response.status_code} - {e.response.text}"

        except Exception as e:
            # 기타 예외 처리
            print(f"API 요청 중 오류 발생: {str(e)}")
            return f"API 요청 오류: {str(e)}"

    def _identifying_params(self):
        return {"model": "gemini-2.0-flash"}

# 사용 예시 (테스트)
if __name__ == "__main__":
    gemini_llm = GeminiLLM()
    prompt_text = "간단한 자기소개를 해줘."
    response_text = gemini_llm(prompt_text)
    print(f"질문: {prompt_text}")
    print(f"답변: {response_text}")
