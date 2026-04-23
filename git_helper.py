"""
Git 작업을 간편하게 해주는 헬퍼 스크립트

사용법:
    python git_helper.py update            - 변경사항 자동 분석 후 커밋 & 푸시
    python git_helper.py save [메시지]     - 메시지 지정해서 저장 & 푸시
    python git_helper.py sync              - 최신 버전 가져오기
    python git_helper.py status            - 상태 확인
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def run_command(command):
    """명령어 실행 후 (returncode, stdout, stderr) 반환"""
    result = subprocess.run(
        command, shell=True, capture_output=True,
        text=True, encoding='utf-8', errors='replace'
    )
    return result.returncode, result.stdout, result.stderr


# ── 파일 분류 규칙 ────────────────────────────────────────────────────────────

_PREFIX_RULES = [
    # (경로 접두사 또는 확장자,  prefix,   변경 종류 설명)
    ("blog/drafts/",   "docs",   "블로그 초안"),
    ("blog/posts/",    "docs",   "블로그 글"),
    ("blog/html/",     "docs",   "HTML 변환"),
    ("blog/",          "docs",   "블로그 파일"),
    (".py",            "feat",   "Python 스크립트"),
    ("requirements",   "chore",  "패키지 설정"),
    (".gitignore",     "chore",  "Git 설정"),
    (".md",            "docs",   "문서"),
]

def _classify_file(path: str) -> tuple[str, str]:
    """파일 경로 → (prefix, 종류 설명) 반환"""
    p = path.replace("\\", "/")
    for pattern, prefix, label in _PREFIX_RULES:
        if p.startswith(pattern) or p.endswith(pattern):
            return prefix, label
    return "chore", "기타 파일"


def _parse_status() -> list[dict]:
    """git status --porcelain 파싱 → 변경 파일 목록 반환"""
    _, out, _ = run_command("git status --porcelain")
    files = []
    status_map = {
        "M": "수정", "A": "추가", "D": "삭제",
        "R": "이름변경", "?": "새 파일",
    }
    for line in out.strip().splitlines():
        if not line.strip():
            continue
        xy = line[:2].strip()          # 상태 코드 (XY 중 비어있지 않은 쪽)
        code = xy[-1] if xy else "?"   # 워킹트리 상태 우선
        path = line[3:].strip()
        if " -> " in path:             # rename 처리
            path = path.split(" -> ")[-1]
        action = status_map.get(code, "변경")
        prefix, label = _classify_file(path)
        files.append({
            "path": path,
            "name": Path(path).name,
            "action": action,
            "prefix": prefix,
            "label": label,
        })
    return files


def _build_commit_message(files: list[dict]) -> str:
    """변경 파일 목록 → 커밋 메시지 자동 생성"""
    prefixes = [f["prefix"] for f in files]
    # 가장 많이 등장한 prefix 사용, 동수면 우선순위: feat > docs > chore
    priority = ["feat", "fix", "docs", "chore"]
    prefix = max(set(prefixes), key=lambda p: (prefixes.count(p), -priority.index(p) if p in priority else -99))

    # 파일 종류 그룹핑
    label_groups: dict[str, list[str]] = {}
    for f in files:
        label_groups.setdefault(f["label"], []).append(f["name"])

    # 요약 문장 구성
    parts = []
    for label, names in label_groups.items():
        if len(names) <= 2:
            parts.append(f"{label} {', '.join(names)}")
        else:
            parts.append(f"{label} {len(names)}개")

    summary = " / ".join(parts)

    # 총 파일 수
    total = len(files)
    return f"{prefix}: {summary} ({total}개 파일 변경)"


# ── 핵심 명령어 함수들 ─────────────────────────────────────────────────────────

def gitupdate():
    """변경사항 자동 분석 후 커밋 메시지 생성 → add → commit → push"""
    print("=" * 50)
    print(" gitupdate 시작")
    print("=" * 50)

    # 1. 변경 파일 확인
    files = _parse_status()

    if not files:
        print("[완료] 변경사항이 없습니다. 이미 최신 상태입니다.")
        return

    # 2. 변경 내역 출력
    print(f"\n[감지] 변경된 파일 {len(files)}개:")
    for f in files:
        print(f"  {f['action']:6s}  {f['path']}")

    # 3. 커밋 메시지 자동 생성
    message = _build_commit_message(files)
    print(f"\n[메시지] {message}")

    # 4. add → commit → push
    print("\n[추가] git add ...")
    run_command("git add .")

    print("[커밋] 커밋 중...")
    code, out, err = run_command(f'git commit -m "{message}"')
    if code != 0:
        if "nothing to commit" in out + err:
            print("[완료] 변경사항이 없습니다.")
        else:
            print(f"[오류] 커밋 실패:\n{err or out}")
        return

    print("[업로드] GitHub에 푸시 중...")
    code, out, err = run_command("git push")

    print()
    if code == 0:
        print("=" * 50)
        print(" 완료! GitHub에 동기화되었습니다.")
        print(f" 커밋: {message}")
        print("=" * 50)
    else:
        print(f"[오류] 푸시 실패:\n{err or out}")
        print("  힌트: git push --set-upstream origin main 을 먼저 실행해 보세요.")


def quick_save(message=None):
    """메시지 지정 저장: add → commit → push"""
    if not message:
        message = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    print("[추가] 변경사항 추가 중...")
    run_command("git add .")

    print(f"[커밋] {message}")
    code, out, err = run_command(f'git commit -m "{message}"')

    if code != 0 and "nothing to commit" in out + err:
        print("[정보] 변경사항이 없습니다.")
        return

    print("[업로드] GitHub에 업로드 중...")
    code, out, err = run_command("git push")

    if code == 0:
        print("[완료] GitHub에 동기화되었습니다.")
    else:
        print(f"[오류] {err}")


def sync():
    """원격 저장소에서 최신 변경사항 가져오기"""
    print("[동기화] 최신 버전 가져오는 중...")
    code, out, err = run_command("git pull")

    if code == 0:
        print("[완료] 동기화 완료!")
        if "Already up to date" in out:
            print("[정보] 이미 최신 버전입니다.")
    else:
        print(f"[오류] {err}")


def status():
    """현재 Git 상태 출력"""
    print("[상태] Git 상태 확인 중...")
    _, out, _ = run_command("git status")
    print(out)


# ── 진입점 ────────────────────────────────────────────────────────────────────

HELP = """
사용법:
    python git_helper.py update            - 자동 분석 후 커밋 & 푸시  ★
    python git_helper.py save [메시지]     - 메시지 지정해서 저장 & 푸시
    python git_helper.py sync              - 최신 버전 가져오기
    python git_helper.py status            - 상태 확인

예시:
    python git_helper.py update
    python git_helper.py save "feat: 웹 스크래핑 기능 추가"
    python git_helper.py sync
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "update":
        gitupdate()
    elif cmd == "save":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        quick_save(msg)
    elif cmd == "sync":
        sync()
    elif cmd == "status":
        status()
    else:
        print(f"[오류] 알 수 없는 명령어: {cmd}")
        print(HELP)
        sys.exit(1)
