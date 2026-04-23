# Python 자동화 + 티스토리 기술 블로그 프로젝트

## 프로젝트 개요
Python 자동화 프로젝트를 개발하면서 개발 과정을 티스토리 블로그에 기록하는 프로젝트

## 블로그 정보
- 블로그: https://embedstory.tistory.com/
- 주제: 개발, 자동화, Python, 기술 튜토리얼
- 목표: 개발 과정을 실시간으로 기록하여 기술 블로그 작성

## 프로젝트 구조
```
my-automation-blog/
├── src/                    # 개발 소스 코드
│   ├── scrapers/          # 웹 스크래핑 관련
│   ├── automation/        # 자동화 스크립트
│   └── utils/             # 공통 유틸리티
├── blog/
│   ├── drafts/            # 작성 중인 블로그 글 (마크다운)
│   ├── posts/             # 완성된 블로그 글 (마크다운)
│   ├── html/              # 티스토리용 HTML 변환 파일
│   └── templates/         # 블로그 글 템플릿
├── scripts/               # 자동화 스크립트
│   ├── md_to_html.py     # 마크다운 → HTML 변환
│   └── git_helper.py     # Git 자동화 도구
├── data/                  # 데이터 파일 (gitignore)
├── logs/                  # 로그 파일 (gitignore)
├── .gitignore
├── requirements.txt
├── claude.md
└── README.md
```

## 기술 스택
- Python 3.10+
- pandas (데이터 처리)
- requests (API 호출)
- beautifulsoup4 (웹 스크래핑)
- selenium (브라우저 자동화)
- markdown (마크다운 처리)

## 블로그 작성 규칙
### 파일명 규칙
- 형식: `YYYY-MM-DD-title.md`
- 예시: `2026-04-23-python-web-scraping.md`

### 카테고리
- Python
- 자동화
- 웹개발
- 프로젝트
- 튜토리얼

### 작성 워크플로우
1. 개발하면서 `blog/drafts/`에 마크다운으로 기록
2. 완성되면 `blog/posts/`로 이동
3. `md_to_html.py`로 티스토리용 HTML 변환
4. `blog/html/`에 저장된 HTML을 티스토리에 복사-붙여넣기

## 코딩 규칙
- 함수명: snake_case
- 클래스명: PascalCase
- 상수: UPPER_CASE
- 주석: 한글로 명확하게
- docstring: Google 스타일
- 타입 힌팅 사용

## Git 사용 규칙
### 커밋 메시지
- feat: 새 기능 추가
- fix: 버그 수정
- docs: 문서 수정
- style: 코드 포맷팅
- refactor: 코드 리팩토링
- test: 테스트 추가
- chore: 기타 작업

### 예시
```
git commit -m "feat: 웹 스크래핑 기본 기능 추가"
git commit -m "docs: 블로그 글 작성 - Python 크롤링 튜토리얼"
git commit -m "fix: 인코딩 에러 수정"
```

## 개발 + 블로그 작성 패턴
1. 새 기능 개발 시작
2. `blog/drafts/`에 초안 작성
3. 개발 진행하면서 단계별로 업데이트
4. 완성 후 `blog/posts/`로 이동
5. HTML 변환 후 티스토리 발행
6. Git commit & push

## 환경 설정
### 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 가상환경 사용 (권장)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 주의사항
- `.env` 파일에 민감한 정보 저장 (API 키, 비밀번호 등)
- `.env` 파일은 절대 Git에 커밋하지 않음
- 대용량 데이터는 `data/` 폴더에 (gitignore 처리됨)
- 한글 파일명 사용 시 인코딩 주의

## 참고 자료
- 티스토리 블로그: https://embedstory.tistory.com/
- GitHub 저장소: https://github.com/JASON2EMBED/my-automation-blog
