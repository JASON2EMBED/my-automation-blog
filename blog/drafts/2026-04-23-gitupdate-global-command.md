# Git 커밋을 한 단어로 끝내는 전역 명령어 만들기 — gitupdate

**카테고리**: Python / 자동화  
**작성일**: 2026-04-23  
**태그**: Python, Git, 자동화, Windows, 생산성

---

## 이전 글에서 이어서

지난 글에서 `git_helper.py`를 만들어서 `add → commit → push` 세 단계를 한 번에 처리했습니다.

```bash
python git_helper.py save "블로그 글 작성 완료"
```

이번에는 한 단계 더 나아갑니다.

1. **커밋 메시지도 자동 생성** — 변경된 파일을 분석해서 알아서 씁니다
2. **어느 경로에서든 사용** — 프로젝트 폴더 안에 있을 필요가 없습니다

최종 목표는 이것입니다.

```bash
# 어떤 Git 저장소에서든, 그냥 이것만 입력
gitupdate
```

---

## 완성된 모습

```
====================================================
 gitupdate  —  my-automation-blog
====================================================

[감지] 변경된 파일 3개:
  [수정] git_helper.py
  [새 파일] blog/drafts/2026-04-23-gitupdate.md
  [수정] requirements.txt

[메시지] feat: Python 스크립트 git_helper.py / 블로그 초안 2026-04-23-gitupdate.md / 패키지 설정 requirements.txt (3개 파일 변경)

[추가]   git add .
[커밋]   git commit ...
[업로드] git push ...

====================================================
 완료! GitHub에 동기화되었습니다.
====================================================
```

변경된 파일을 스스로 파악하고, 파일 종류에 따라 `feat:` / `docs:` / `chore:` 접두사까지 붙인 커밋 메시지를 자동으로 만듭니다.

---

## 전체 구조

```
C:\Users\User\bin\        ← Windows PATH에 등록된 폴더
  ├── gitupdate.py        ← 핵심 로직
  └── gitupdate.bat       ← gitupdate 명령어 진입점
```

`gitupdate.bat`은 단 두 줄짜리 실행 파일입니다.

```batch
@echo off
python "%~dp0gitupdate.py" %*
```

`%~dp0`는 `.bat` 파일 자신이 있는 경로를 의미합니다. 어디서 실행하든 `gitupdate.py`를 정확히 찾아갑니다.

---

## 핵심 1 — 현재 디렉토리가 Git 저장소인지 확인

가장 먼저 할 일은 "지금 여기가 Git 저장소인가?" 확인입니다.

```python
def main():
    code, out, _ = run("git rev-parse --show-toplevel")
    if code != 0:
        print(f"[오류] 현재 경로는 Git 저장소가 아닙니다: {os.getcwd()}")
        print("       git init 으로 저장소를 먼저 초기화하세요.")
        sys.exit(1)

    repo_root = out.strip()
    print(f" gitupdate  —  {Path(repo_root).name}")
```

`git rev-parse --show-toplevel`은 현재 위치에서 가장 가까운 Git 저장소 루트 경로를 반환합니다. 저장소가 아니면 오류 코드를 반환하므로, 이걸로 저장소 여부를 판단합니다.

**실행 예시 (저장소가 아닌 경우):**
```bash
$ cd C:\Users\User\Documents
$ gitupdate
[오류] 현재 경로는 Git 저장소가 아닙니다: C:\Users\User\Documents
       git init 으로 저장소를 먼저 초기화하세요.
```

---

## 핵심 2 — 변경 파일 목록 파싱

`git status --porcelain`은 변경 파일 목록을 깔끔한 형식으로 출력합니다.

```bash
$ git status --porcelain
M  git_helper.py
?? blog/drafts/new-post.md
 D old_file.txt
```

각 줄은 `상태코드 + 파일경로` 형식입니다. Python으로 파싱합니다.

```python
def _parse_changed_files():
    _, out, _ = run("git status --porcelain")
    files = []
    status_map = {"M": "수정", "A": "추가", "D": "삭제", "R": "이름변경", "?": "새 파일"}

    for line in out.splitlines():
        tokens = line.strip().split()   # ['M', 'git_helper.py']
        if not tokens:
            continue
        xy = tokens[0]                  # 상태 코드 ('M', '??', 'MM' 등)
        code = xy.replace(" ", "")[-1]  # 마지막 문자로 상태 판단
        path = tokens[-1]               # 파일 경로 (rename도 마지막 토큰이 최종 경로)
        prefix, label = _classify(path)
        files.append({
            "path": path,
            "name": Path(path).name,
            "action": status_map.get(code, "변경"),
            "prefix": prefix,
            "label": label,
        })
    return files
```

`tokens[-1]`을 쓰는 이유는 파일명 변경(`rename`) 처리 때문입니다. 이름 변경은 `R old.py -> new.py` 형식으로 출력되는데, 마지막 토큰이 항상 최종 파일명이라 `-1` 인덱스로 통일하면 됩니다.

---

## 핵심 3 — 파일 종류로 커밋 메시지 자동 생성

파일 경로를 보고 어떤 종류의 변경인지 분류합니다.

```python
_PREFIX_RULES = [
    ("blog/drafts/",  "docs",  "블로그 초안"),
    ("blog/posts/",   "docs",  "블로그 글"),
    ("blog/html/",    "docs",  "HTML 변환"),
    (".py",           "feat",  "Python 스크립트"),
    (".js",           "feat",  "JS 스크립트"),
    (".md",           "docs",  "문서"),
    (".bat",          "chore", "실행 스크립트"),
    ("requirements",  "chore", "패키지 설정"),
    (".gitignore",    "chore", "Git 설정"),
]

def _classify(path):
    p = path.replace("\\", "/")
    for pattern, prefix, label in _PREFIX_RULES:
        if p.startswith(pattern) or p.endswith(pattern):
            return prefix, label
    return "chore", "기타 파일"
```

분류 결과를 모아서 커밋 메시지를 조립합니다.

```python
def _auto_message(files):
    prefixes = [f["prefix"] for f in files]

    # 가장 많이 나온 prefix 선택, 동수면 feat > docs > chore 순
    priority = ["feat", "fix", "docs", "chore"]
    prefix = max(set(prefixes), key=lambda p: (
        prefixes.count(p), -priority.index(p) if p in priority else -99
    ))

    # 파일 종류별로 그룹화
    groups: dict[str, list[str]] = {}
    for f in files:
        groups.setdefault(f["label"], []).append(f["name"])

    # 요약 문장 조립
    parts = []
    for label, names in groups.items():
        if len(names) <= 2:
            parts.append(f"{label} {', '.join(names)}")
        else:
            parts.append(f"{label} {len(names)}개")

    return f"{prefix}: {' / '.join(parts)} ({len(files)}개 파일 변경)"
```

**자동 생성 예시:**

| 변경 내용 | 자동 생성 메시지 |
|-----------|-----------------|
| `.py` 파일 1개 수정 | `feat: Python 스크립트 git_helper.py (1개 파일 변경)` |
| 블로그 초안 + `.py` | `feat: Python 스크립트 git_helper.py / 블로그 초안 new-post.md (2개 파일 변경)` |
| `.md` 파일 3개 추가 | `docs: 문서 3개 (3개 파일 변경)` |
| `requirements.txt` | `chore: 패키지 설정 requirements.txt (1개 파일 변경)` |

---

## Windows PATH 등록하기

스크립트를 어디서든 실행하려면 PATH에 폴더를 추가해야 합니다.

**PowerShell에서 한 번만 실행:**

```powershell
$binPath = "C:\Users\사용자이름\bin"
$current = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$current;$binPath", "User")
```

`"User"` 파라미터는 현재 사용자에게만 PATH를 적용합니다. 관리자 권한이 필요 없습니다.

PATH 등록 후 **터미널을 새로 열면** 바로 사용 가능합니다.

---

## 실제 사용 시나리오

**시나리오 1 — 블로그 글 작성 후 저장**

```bash
cd C:\Users\User\my-automation-blog
# 블로그 글 작성 완료 후
gitupdate

# 출력:
# [감지] 변경된 파일 1개:
#   [새 파일] blog/drafts/2026-04-23-gitupdate.md
# [메시지] docs: 블로그 초안 2026-04-23-gitupdate.md (1개 파일 변경)
# 완료!
```

**시나리오 2 — Python 코드 수정 후 저장**

```bash
cd C:\Users\User\another-project
gitupdate

# 출력:
# [감지] 변경된 파일 2개:
#   [수정] src/main.py
#   [수정] src/utils.py
# [메시지] feat: Python 스크립트 main.py, utils.py (2개 파일 변경)
# 완료!
```

**시나리오 3 — 변경사항이 없을 때**

```bash
gitupdate

# 출력:
# [완료] 변경사항 없음. 이미 최신 상태입니다.
```

**시나리오 4 — Git 저장소가 아닌 폴더에서**

```bash
cd C:\Users\User\Downloads
gitupdate

# 출력:
# [오류] 현재 경로는 Git 저장소가 아닙니다: C:\Users\User\Downloads
#        git init 으로 저장소를 먼저 초기화하세요.
```

---

## 마무리

`gitupdate` 하나로 이제 이 모든 걸 자동으로 처리합니다.

- 변경된 파일 감지
- 파일 종류 분석 (`.py` → `feat:`, `.md` → `docs:`, 설정 파일 → `chore:`)
- 커밋 메시지 자동 생성
- `git add .` → `git commit` → `git push` 순서 실행
- Git 저장소가 아닌 경우 안전하게 오류 처리

스크립트 전체 코드는 GitHub에서 확인하세요.  
👉 [https://github.com/JASON2EMBED/my-automation-blog](https://github.com/JASON2EMBED/my-automation-blog)

---

*다음 글에서는 커밋 히스토리를 자동으로 요약해주는 기능을 추가해볼 예정입니다.*
