# URL 요약 API

카카오톡 메신저봇R과 연동되는 URL 요약 API 서비스입니다.

## 기능

- URL 추출 및 처리
- 다양한 웹사이트 유형 감지 및 맞춤형 요약 생성
- Google Gemini AI를 활용한 콘텐츠 요약
- 번역 기능 지원

## 지원 사이트

- DCInside
- FMKorea
- YouTube (트랜스크립트 기반)
- 네이버 (뉴스, 카페 등)
- 쇼핑몰 (쿠팡, 11번가, 스마트스토어 등)
- PDF 파일 (arXiv 논문 등)
- 일반 웹사이트

## 기술 스택

- FastAPI
- Docker
- LangChain
- Google Gemini API
- BeautifulSoup4

## 설치 및 실행

### 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가합니다:

```
GEMINI_API_KEY=your_api_key_here
```

### Docker를 이용한 실행

```bash
docker-compose up -d
```

### API 엔드포인트

- `GET /`: API 상태 확인
- `GET /test`: 서버 상태 테스트
- `POST /process-url`: URL 처리 및 요약

## 카카오톡 메신저봇 연동

`메신저봇.txt` 파일에 포함된 JavaScript 코드를 카카오톡 메신저봇R에 적용하여 사용할 수 있습니다.
