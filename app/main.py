import os
from fastapi import FastAPI, HTTPException
from typing import Union

from app.models import MessageRequest, SummaryResponse, TranslationResponse, TranslateRequest, TranslateResponse
from app.services.web_service import process_url_content
from app.services.translator_service import process_translation, translate_text
from app.utils.text_utils import extract_urls, is_translation_request

app = FastAPI(title="URL 요약 및 번역 API", description="카카오톡 메신저봇R과 연동되는 URL 요약 및 번역 API")

@app.get("/")
def hello():
    return {"message": "URL 요약 및 번역 API가 실행 중입니다!"}

@app.get("/test")
def test():
    return {"status": "ok", "message": "FastAPI 서버가 정상 작동 중입니다."}

@app.post("/process-message", response_model=Union[SummaryResponse, TranslationResponse])
def process_message(request: MessageRequest):
    try:
        # 번역 요청인지 확인
        if is_translation_request(request.text):
            # 번역 처리
            translation_result = process_translation(request.text)
            return {"translation": translation_result}
        
        # URL 요약 처리
        urls = extract_urls(request.text)
        if not urls:
            return {"headline": "URL 없음", "gemini_summary": "입력된 텍스트에서 유효한 URL을 찾을 수 없습니다."}
        
        url = urls[0]
        # SSRF 및 내부 주소 방지를 위해 로컬 주소 검증 추가
        if "localhost" in url or "127.0.0.1" in url:
            return {"headline": "오류", "gemini_summary": "내부 IP 또는 로컬 주소는 사용할 수 없습니다."}
        
        # URL 처리 서비스 호출
        headline, summary = process_url_content(url)
        return {"headline": headline, "gemini_summary": summary}
    
    except Exception as e:
        # 전체 프로세스에 대한 예외 처리
        print(f"전체 처리 오류: {str(e)}")
        return {"headline": "처리 오류", "gemini_summary": f"처리 중 오류 발생: {str(e)}"}

@app.post("/process-url", response_model=SummaryResponse)
def process_url(request: MessageRequest):
    """기존 URL 처리 엔드포인트 (하위 호환성 유지)"""
    try:
        urls = extract_urls(request.text)
        if not urls:
            return {"headline": "URL 없음", "gemini_summary": "입력된 텍스트에서 유효한 URL을 찾을 수 없습니다."}
        
        url = urls[0]
        # SSRF 및 내부 주소 방지를 위해 로컬 주소 검증 추가
        if "localhost" in url or "127.0.0.1" in url:
            return {"headline": "오류", "gemini_summary": "내부 IP 또는 로컬 주소는 사용할 수 없습니다."}
        
        # URL 처리 서비스 호출
        headline, summary = process_url_content(url)
        return {"headline": headline, "gemini_summary": summary}
    
    except Exception as e:
        # 전체 프로세스에 대한 예외 처리
        print(f"전체 처리 오류: {str(e)}")
        return {"headline": "처리 오류", "gemini_summary": f"처리 중 오류 발생: {str(e)}"}

@app.post("/translate", response_model=TranslateResponse)
def translate(request: TranslateRequest):
    """메신저봇R용 번역 엔드포인트"""
    try:
        # 번역 처리
        translated_text = translate_text(request.text, request.target_language)
        return {"translated_text": translated_text}
    
    except Exception as e:
        # 예외 처리
        print(f"번역 처리 오류: {str(e)}")
        return {"translated_text": f"번역 처리 중 오류 발생: {str(e)}"}
