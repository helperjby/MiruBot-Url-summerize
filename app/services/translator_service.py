# app/services/translator_service.py

from app.services.gemini_service import GeminiLLM
import re

# Gemini LLM 인스턴스 생성
gemini = GeminiLLM()

def translate_to_language(text: str, target_language: str) -> str:
    """텍스트를 지정된 언어로 번역"""
    language_name = "한국어" if target_language == "ko" else "영어"
    
    prompt = f"""다음 문장을 {language_name}로 자연스럽게 번역해줘:
{text}

번역만 출력하고 다른 설명은 하지 마세요."""
    return gemini._call(prompt)

def is_korean_text(text: str) -> bool:
    """텍스트가 한국어인지 확인하는 함수"""
    # 한글 유니코드 범위: AC00-D7A3 (가-힣)
    korean_char_pattern = re.compile(r'[가-힣]')
    korean_chars = korean_char_pattern.findall(text)
    
    # 한글 문자가 전체 텍스트의 30% 이상이면 한국어로 간주
    if len(korean_chars) > 0 and len(korean_chars) / len(text) >= 0.3:
        return True
    return False

def process_translation(text: str) -> str:
    """번역 처리 함수 (이전 버전 호환용)"""
    # '$번역' 키워드 제거하고 텍스트 추출
    clean_text = text.replace('$번역', '').strip()
    
    if not clean_text:
        return "번역할 텍스트가 없습니다. '$번역 [텍스트]' 형식으로 입력해주세요."
    
    try:
        # 한국어 여부 확인
        if is_korean_text(clean_text):
            result = translate_to_language(clean_text, "en")
            return f"🌐 번역 결과 (한국어 → 영어):\n{result}"
        else:
            result = translate_to_language(clean_text, "ko")
            return f"🌐 번역 결과 (외국어 → 한국어):\n{result}"
    except Exception as e:
        print(f"번역 처리 중 오류 발생: {str(e)}")
        return f"번역 처리 중 오류가 발생했습니다: {str(e)}"

def translate_text(text: str, target_language: str) -> str:
    """메신저봇R용 번역 함수"""
    try:
        result = translate_to_language(text, target_language)
        return result
    except Exception as e:
        print(f"번역 처리 중 오류 발생: {str(e)}")
        return f"번역 처리 중 오류가 발생했습니다: {str(e)}"
