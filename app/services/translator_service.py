# app/services/translator_service.py

from app.services.gemini_service import GeminiLLM

# Gemini LLM 인스턴스 생성
gemini = GeminiLLM()

def translate_to_korean(text: str) -> str:
    prompt = f"다음 문장을 한국어로 자연스럽게 번역해줘:\n{text}"
    return gemini(prompt)
