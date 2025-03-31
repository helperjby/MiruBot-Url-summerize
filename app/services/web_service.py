from langchain_community.document_loaders import WebBaseLoader
from langchain.document_loaders import PyPDFLoader
from app.services.gemini_service import GeminiLLM
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def get_domain_type(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if "dcinside" in domain:
        return "dc"
    if "fmkorea" in domain:
        return "fm"
    if "youtube" in domain or "youtu.be" in domain:
        return "youtube"
    if any(x in domain for x in ["coupang","11st","smartstore","gmarket","auction","amazon"]):
        return "product"
    if url.lower().endswith(".pdf"):
        return "pdf"

    # -- 네이버 세분화
    if "naver" in domain:
        # 뉴스
        if any(x in url for x in ["news.naver.com", "n.news.naver.com", "m.news.naver.com"]):
            return "naver_news"
        # 카페
        if "cafe.naver.com" in domain or "m.cafe.naver.com" in domain:
            return "naver_cafe"
        # 기타
        return "naver_other"

    # 기본
    return "generic"


def fetch_arxiv_abstract(url: str) -> str:
    paper_id = url.rstrip(".pdf").split("/")[-1]
    api_url = f"http://export.arxiv.org/api/query?id_list={paper_id}"
    resp = requests.get(api_url, timeout=10)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    summary_el = root.find(".//{http://www.w3.org/2005/Atom}summary")
    if summary_el is None:
        raise ValueError("arXiv abstract를 찾을 수 없습니다.")
    abstract = summary_el.text.strip()
    if not abstract:
        raise ValueError("arXiv abstract가 비어있습니다.")
    return abstract


def fetch_youtube_transcript(url: str) -> str:
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip("/")
    else:
        video_id = parse_qs(parsed.query).get("v", [None])[0]
    if not video_id:
        raise ValueError("잘못된 YouTube URL 입니다.")
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ko", "en"])
    return "\n".join(seg["text"] for seg in transcript)


def generate_dc_prompt(url: str, content: str) -> str:
    return f"""
아래 DCInside 게시글 내용을 읽고, 아래의 <template>으로 직접 요약을 작성하세요: 
- markdown 문법을 사용하지 마세요.
- 지시문을 답변에 포함하지 마세요.
- 요약 내용 외에 답변은 하지 마세요.

<template>
👉 글 제목 또는 핵심 요약 문장
📌 글의 주제 또는 분위기 요약 (1줄)  
✅ 주요 주장, 댓글 반응 요약 (2~3줄 이내)  

🚀 재미요소, 반전, 감정적 표현 등 포함 (있다면)

게시글 내용:
{content}
"""

def generate_fmkorea_prompt(url: str, content: str) -> str:
    return f"""
아래 FMKorea 게시글을 읽고, 아래의 <template>으로 직접 요약을 작성하세요:
- markdown 문법을 사용하지 마세요.
- 지시문을 답변에 포함하지 마세요.
- 요약 내용 외에 답변은 하지 마세요.

<template>
👉 글 제목 또는 핵심 요약 문장  
📌 글의 주제나 분위기 요약 (1줄)  
✅ 주요 주장, 반응, 이슈 요약 (2~3줄 이내)  
🚀 유머, 반전, 커뮤니티 반응 등 포함 (있다면)  

게시글 내용:
{content}
"""

def generate_youtube_prompt(url: str, content: str) -> str:
    return f"""
아래 유튜브 영상 설명 및 내용을 참고하여 아래의 <template>으로 직접 요약을 작성하세요:
- markdown 문법을 사용하지 마세요.
- 지시문을 답변에 포함하지 마세요.
- 요약 내용 외에 답변은 하지 마세요.

<template>
👉 영상 제목 또는 핵심 주제 
📌 영상의 핵심 내용 요약 (1줄)  
✅ 강조된 내용, 설명, 정보 정리 (2~3줄 이내)  
🚀 유익한 팁, 흥미 요소, 추천 포인트 등 (있다면)  

영상 관련 내용:
{content}
"""

def generate_naver_prompt(url: str, content: str) -> str:
    return f"""
아래 뉴스 또는 네이버 카페 콘텐츠를 읽고, 아래의 <template>으로 직접 요약을 작성하세요:
- markdown 문법을 사용하지 마세요.
- 지시문을 답변에 포함하지 마세요.
- 요약 내용 외에 답변은 하지 마세요.

<template>
👉 기사 제목 또는 핵심 문장 요약
📌 핵심 사실 또는 사건 개요 (1줄)  
✅ 배경, 맥락 설명 요약 (2~3줄 이내)  
🚀 영향, 전망, 이슈 포인트 등 (있다면)  

본문 내용:
{content}
"""

def generate_product_prompt(url: str, content: str) -> str:
    return f"""
다음 상품 설명을 읽고, 소비자에게 도움이 될 수 있는 요약을 아래의 <template>으로 작성하세요:
- markdown 문법을 사용하지 마세요.
- 지시문을 답변에 포함하지 마세요.
- 요약 내용 외에 답변은 하지 마세요.

<template>
👉 상품명 또는 특징 요약 문장 
📌 상품의 용도, 주요 장점 요약 (1줄)  
✅ 가격, 브랜드, 사양 등 핵심 정보 요약 (2~3줄 이내)  
🚀 추천 대상, 장점, 유의사항 등 (있다면)  

상품 설명 내용:
{content}
"""

def generate_generic_prompt(url: str, content: str) -> str:
    return f"""
다음 웹페이지 내용을 읽고, 핵심 내용을 아래의 <template>으로 요약을 작성하세요:
- markdown 문법을 사용하지 마세요.
- 지시문을 답변에 포함하지 마세요.
- 요약 내용 외에 답변은 하지 마세요.

<template>
👉 페이지 제목 또는 핵심 문장
📌 전체 내용의 개요 요약 (1줄)  
✅ 핵심 정보, 기능, 설명 요약 (2~3줄 이내)  
🚀 추가 특징, 흥미로운 포인트 등 (있다면)  

웹페이지 내용:
{content}
"""


def get_prompt_func(domain: str):
    domain_map = {
        "dc": generate_dc_prompt,
        "fm": generate_fmkorea_prompt,
        "youtube": generate_youtube_prompt,
        "product": generate_product_prompt,
        "naver_cafe": generate_naver_prompt,
        "naver_news": generate_naver_prompt,
        "naver_other": generate_naver_prompt,
        "generic": generate_generic_prompt,
    }
    return domain_map.get(domain, generate_generic_prompt)


def process_url_content(url: str):
    try:
        domain = get_domain_type(url)

        # 네이버 카페 -> 무응답
        if domain == "naver_cafe":
            return None, None

        if domain == "youtube":
            content = fetch_youtube_transcript(url)

        elif domain == "pdf":
            if "arxiv.org/pdf" in url:
                content = fetch_arxiv_abstract(url)
            else:
                return None, None

        else:
            # 기본 웹 로더
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
            except Exception:
                # 연결 실패 / HTTP오류 → 무응답
                return None, None

            if not docs:
                # 페이지 내용 없음 → 무응답
                return None, None

            content = "\n\n".join(doc.page_content for doc in docs)
            # 본문이 너무 짧으면 무응답
            if len(content.strip()) < 200:
                return None, None

        # --- 요약 ---
        llm = GeminiLLM()
        prompt_func = get_prompt_func(domain)
        if not prompt_func:
            return None, None

        prompt = prompt_func(url, content)
        summary = llm._call(prompt)
        if not summary or not summary.strip():
            return None, None

        headline = f"{url} 에 대한 사이트 요약입니다:"
        return headline, summary

    except Exception:
        # 예기치 않은 에러 → 무응답
        return None, None
