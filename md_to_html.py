"""
마크다운을 티스토리용 HTML로 변환하는 스크립트

사용법:
    python md_to_html.py <마크다운파일.md>

예시:
    python md_to_html.py blog/posts/my-first-post.md
"""
import markdown
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def convert_md_to_html(md_file, output_dir="blog/html"):
    """마크다운을 HTML로 변환"""
    
    # 파일 읽기
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 메타데이터 제거 (--- 로 감싸진 부분)
    if md_content.startswith('---'):
        parts = md_content.split('---', 2)
        if len(parts) >= 3:
            md_content = parts[2].strip()
    
    # 마크다운 → HTML 변환 (코드 하이라이팅 포함)
    html = markdown.markdown(
        md_content,
        extensions=['fenced_code', 'codehilite', 'tables', 'toc']
    )
    
    # 티스토리용 HTML 템플릿
    html_template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
/* 전체 컨테이너 */
.blog-post {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.8;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
}}

/* 제목 스타일 */
.blog-post h1 {{
    font-size: 2em;
    font-weight: bold;
    margin-top: 0;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 3px solid #333;
}}

.blog-post h2 {{
    font-size: 1.5em;
    font-weight: bold;
    margin-top: 40px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #ddd;
    color: #222;
}}

.blog-post h3 {{
    font-size: 1.25em;
    font-weight: bold;
    margin-top: 24px;
    margin-bottom: 12px;
    color: #444;
}}

/* 코드 블록 스타일 */
.blog-post pre {{
    background-color: #f6f8fa;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    margin: 16px 0;
    font-size: 14px;
}}

.blog-post code {{
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
}}

/* 인라인 코드 */
.blog-post p code,
.blog-post li code {{
    background-color: #f6f8fa;
    padding: 2px 6px;
    border-radius: 3px;
    border: 1px solid #e1e4e8;
    font-size: 0.9em;
}}

/* 단락 스타일 */
.blog-post p {{
    margin: 16px 0;
}}

/* 리스트 스타일 */
.blog-post ul, .blog-post ol {{
    margin: 16px 0;
    padding-left: 28px;
}}

.blog-post li {{
    margin: 8px 0;
}}

/* 링크 스타일 */
.blog-post a {{
    color: #0366d6;
    text-decoration: none;
}}

.blog-post a:hover {{
    text-decoration: underline;
}}

/* 인용구 스타일 */
.blog-post blockquote {{
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    margin: 16px 0;
    color: #6a737d;
}}

/* 테이블 스타일 */
.blog-post table {{
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
}}

.blog-post table th,
.blog-post table td {{
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
    text-align: left;
}}

.blog-post table th {{
    background-color: #f6f8fa;
    font-weight: bold;
}}

/* 구분선 */
.blog-post hr {{
    border: none;
    border-top: 2px solid #e1e4e8;
    margin: 32px 0;
}}

/* 이미지 */
.blog-post img {{
    max-width: 100%;
    height: auto;
    margin: 16px 0;
    border-radius: 4px;
}}
</style>
</head>
<body>
<div class="blog-post">
{html}
</div>
</body>
</html>
"""
    
    # 출력 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 출력 파일명
    output_file = Path(output_dir) / (Path(md_file).stem + ".html")
    
    # HTML 파일 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"[완료] 변환 완료: {output_file}")
    print(f"\n[사용 방법]")
    print(f"1. {output_file} 파일을 브라우저로 열기")
    print(f"2. 전체 선택 (Ctrl+A)")
    print(f"3. 복사 (Ctrl+C)")
    print(f"4. 티스토리 에디터에서 붙여넣기 (Ctrl+V)")
    print(f"\n또는 메모장으로 열어서 HTML 코드를 복사해도 됩니다!")
    
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python md_to_html.py <마크다운파일.md>")
        print("\n예시:")
        print("  python md_to_html.py blog/posts/my-first-post.md")
        sys.exit(1)
    
    md_file = sys.argv[1]
    
    if not os.path.exists(md_file):
        print(f"❌ 파일을 찾을 수 없습니다: {md_file}")
        sys.exit(1)
    
    convert_md_to_html(md_file)
