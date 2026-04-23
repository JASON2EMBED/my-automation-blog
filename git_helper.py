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
    """명령어 실행"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def quick_save(message=None):
    """빠른 저장: add, commit, push"""
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
    """최신 버전 가져오기"""
    print("🔄 최신 버전 가져오는 중...")
    code, out, err = run_command("git pull")
    
    if code == 0:
        print("✅ 동기화 완료!")
        if "Already up to date" in out:
            print("ℹ️  이미 최신 버전입니다.")
    else:
        print(f"❌ 에러 발생: {err}")


def status():
    """상태 확인"""
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
