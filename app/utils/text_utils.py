import re

def extract_urls(text: str) -> list:
    """텍스트에서 URL을 추출하는 함수"""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
    urls = re.findall(url_pattern, text)
    return urls