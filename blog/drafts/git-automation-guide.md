# Git이 무서운 당신을 위한 Python 자동화 도구 만들기

**카테고리**: Python / 자동화  
**작성일**: 2026-04-23  
**태그**: Python, Git, 자동화, 초보자

---

## 들어가며

Git을 쓰다 보면 매번 반복하는 작업이 있습니다.

```bash
git add .
git commit -m "수정했음"
git push
```

파일 하나 고칠 때마다 이 세 줄을 입력하는 게 귀찮지 않으신가요?  
저도 그랬습니다. 그래서 Python으로 이 과정을 한 줄로 줄이는 도구를 만들었습니다.

이 글에서는 `git_helper.py`를 만들면서 배운 내용을 공유합니다.  
Git을 처음 쓰시는 분도 이해할 수 있도록 최대한 친절하게 설명할게요.

---

## 완성된 모습 먼저 보기

만들고 나면 이렇게 쓸 수 있습니다.

```bash
# 기존 방식 (3줄)
git add .
git commit -m "블로그 글 작성 완료"
git push

# 자동화 이후 (1줄)
python git_helper.py save "블로그 글 작성 완료"
```

메시지를 생략하면 현재 시각을 자동으로 커밋 메시지로 사용합니다.

```bash
python git_helper.py save
# → Auto commit: 2026-04-23 14:32:10
```

---

## 핵심 개념: subprocess로 터미널 명령어 실행하기

Python에서 Git 명령어를 실행하려면 `subprocess` 모듈을 사용합니다.  
쉽게 말하면 "Python이 대신 터미널에 명령어를 입력해 준다"는 개념입니다.

```python
import subprocess

result = subprocess.run(
    "git status",       # 실행할 명령어
    shell=True,         # 터미널(쉘)을 통해 실행
    capture_output=True, # 출력 결과를 변수로 받기
    text=True           # 결과를 문자열로 변환
)

print(result.stdout)   # 정상 출력
print(result.stderr)   # 에러 출력
print(result.returncode) # 0이면 성공, 그 외는 실패
```

`returncode`가 0이면 명령어가 성공한 것이고, 1 이상이면 오류가 발생한 것입니다.  
이 값으로 성공/실패를 판단합니다.

---

## 전체 코드

```python
"""
Git 작업을 간편하게 해주는 헬퍼 스크립트

사용법:
    python git_helper.py save [메시지]  - 저장 및 푸시
    python git_helper.py sync           - 최신 버전 가져오기
    python git_helper.py status         - 상태 확인
"""
import subprocess
import sys
from datetime import datetime


def run_command(command):
    """명령어 실행 후 결과 반환"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def quick_save(message=None):
    """빠른 저장: add → commit → push 한 번에"""
    if not message:
        message = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    print("📝 변경사항 추가 중...")
    run_command("git add .")

    print(f"💾 커밋 중: {message}")
    code, out, err = run_command(f'git commit -m "{message}"')

    if code != 0 and "nothing to commit" in out + err:
        print("ℹ️  변경사항이 없습니다.")
        return

    print("☁️  GitHub에 업로드 중...")
    code, out, err = run_command("git push")

    if code == 0:
        print("✅ 완료! GitHub에 동기화되었습니다.")
    else:
        print(f"❌ 에러 발생: {err}")


def sync():
    """원격 저장소에서 최신 변경사항 가져오기"""
    print("🔄 최신 버전 가져오는 중...")
    code, out, err = run_command("git pull")

    if code == 0:
        print("✅ 동기화 완료!")
        if "Already up to date" in out:
            print("ℹ️  이미 최신 버전입니다.")
    else:
        print(f"❌ 에러 발생: {err}")


def status():
    """현재 Git 상태 출력"""
    print("📊 Git 상태 확인 중...")
    code, out, err = run_command("git status")
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
사용법:
    python git_helper.py save [메시지]  - 저장 및 푸시
    python git_helper.py sync           - 최신 버전 가져오기
    python git_helper.py status         - 상태 확인

예시:
    python git_helper.py save "블로그 글 작성 완료"
    python git_helper.py sync
        """)
        sys.exit(1)

    command = sys.argv[1]

    if command == "save":
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        quick_save(message)
    elif command == "sync":
        sync()
    elif command == "status":
        status()
    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        sys.exit(1)
```

---

## 기능별 설명

### 1. `quick_save()` — add + commit + push 한 번에

가장 자주 쓰는 기능입니다. 세 단계를 하나로 묶었습니다.

```python
def quick_save(message=None):
    if not message:
        # 메시지 없으면 현재 시각을 자동으로 사용
        message = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    run_command("git add .")          # 1단계: 모든 변경사항 스테이징
    run_command(f'git commit -m "{message}"')  # 2단계: 커밋
    run_command("git push")           # 3단계: 원격에 푸시
```

**실행 예시:**
```bash
$ python git_helper.py save "기능 추가: 자동 저장"
📝 변경사항 추가 중...
💾 커밋 중: 기능 추가: 자동 저장
☁️  GitHub에 업로드 중...
✅ 완료! GitHub에 동기화되었습니다.
```

변경사항이 없을 때도 안전하게 처리합니다.

```bash
$ python git_helper.py save
ℹ️  변경사항이 없습니다.
```

### 2. `sync()` — 최신 버전 가져오기

다른 컴퓨터에서 작업했거나 GitHub에서 직접 수정한 경우, 최신 내용을 가져올 때 사용합니다.

```bash
$ python git_helper.py sync
🔄 최신 버전 가져오는 중...
✅ 동기화 완료!
ℹ️  이미 최신 버전입니다.
```

### 3. `status()` — 현재 상태 확인

어떤 파일이 변경됐는지 확인합니다. `git status`를 그대로 출력합니다.

```bash
$ python git_helper.py status
📊 Git 상태 확인 중...
On branch main
Changes not staged for commit:
    modified:   blog/drafts/git-automation-guide.md
```

---

## 코드 구조 설명: `sys.argv`란?

터미널에서 Python 스크립트를 실행할 때 인자를 넘길 수 있습니다.

```bash
python git_helper.py save "블로그 작성"
```

이때 `sys.argv`의 값은 이렇습니다.

```python
sys.argv[0]  # "git_helper.py"  (스크립트 이름)
sys.argv[1]  # "save"           (첫 번째 인자: 명령어)
sys.argv[2]  # "블로그 작성"    (두 번째 인자: 메시지)
```

커밋 메시지가 여러 단어일 때도 대응합니다.

```python
# "블로그 글 작성 완료" 처럼 띄어쓰기 있는 메시지 처리
message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
```

---

## 실제 사용 시나리오

**블로그 글 초안 저장:**
```bash
python git_helper.py save "docs: git 자동화 글 초안 작성"
```

**코드 수정 후 자동 저장 (메시지 생략):**
```bash
python git_helper.py save
# → Auto commit: 2026-04-23 15:00:00
```

**다른 PC에서 작업 시작 전:**
```bash
python git_helper.py sync
```

**뭔가 수정했는데 어떤 파일인지 모를 때:**
```bash
python git_helper.py status
```

---

## 주의사항

**`git add .`은 모든 파일을 포함합니다.**  
`.env` 같은 민감한 파일이 있다면 반드시 `.gitignore`에 등록하세요.

```bash
# .gitignore 예시
.env
data/
logs/
__pycache__/
```

**커밋 메시지 컨벤션을 지키면 나중에 편합니다.**  
`feat:`, `fix:`, `docs:` 같은 접두사를 사용하면 히스토리를 보기 쉬워집니다.

```bash
python git_helper.py save "feat: 웹 스크래핑 기능 추가"
python git_helper.py save "fix: 인코딩 오류 수정"
python git_helper.py save "docs: README 업데이트"
```

---

## 마무리

이 스크립트 덕분에 Git이 한결 편해졌습니다.  
터미널에서 세 줄 입력하던 것을 이제는 한 줄로 끝냅니다.

Python의 `subprocess`를 배우면 Git 말고도 다양한 터미널 명령어를 자동화할 수 있습니다.  
다음에는 이 도구를 확장해서 커밋 히스토리 자동 요약이나 브랜치 관리 자동화도 만들어볼 예정입니다.

코드 전체는 GitHub에서 확인하실 수 있습니다.  
👉 [https://github.com/JASON2EMBED/my-automation-blog](https://github.com/JASON2EMBED/my-automation-blog)

---

*궁금한 점은 댓글로 남겨주세요!*
