# Langflow 설치 가이드 (Python 3.13)

## 1. Homebrew로 Python 설치
```bash
# Python 3.13 설치
brew install python@3.13

# Python 3.14도 함께 유지 (기본 brew python)
brew install python@3.14
```

## 2. .zshrc에 Python 3.13 alias 설정
```bash
# .zshrc 파일 편집
nano ~/.zshrc

# 아래 내용 추가 (파일 끝에)
alias python3="/home/linuxbrew/.linuxbrew/opt/python@3.13/bin/python3.13"
alias python="/home/linuxbrew/.linuxbrew/opt/python@3.13/bin/python3.13"

# 저장 후 적용
source ~/.zshrc

# 확인
python3 --version  # Python 3.13.11 출력되어야 함
python --version   # Python 3.13.11 출력되어야 함
```

## 3. Python 가상환경 생성
```bash
# 작업 디렉토리로 이동
cd /app/python

# Python 3.13으로 가상환경 생성
python3 -m venv langflow

# 가상환경 활성화
source langflow/bin/activate

# Python 버전 확인 (가상환경 내)
python --version  # Python 3.13.11 확인
```

## 4. Langflow 설치
```bash
# 가상환경이 활성화된 상태에서
uv pip install langflow -U
```

### 참고: uv 설치 (필요시)
```bash
# uv가 없는 경우
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 5. Langflow 실행
```bash
# 가상환경 활성화 상태에서
uv run langflow run

# 또는
langflow run
```

기본적으로 `http://localhost:7860`에서 접속 가능합니다.

---

## 문제 해결

### Python 3.14 호환성 문제
- Langflow는 Python 3.10-3.13을 권장
- Python 3.14에서는 `hnswlib` 빌드 에러 발생
- 해결: Python 3.13 사용

### alias가 적용 안 될 때
```bash
# .zshrc 다시 로드
source ~/.zshrc

# alias 확인
alias | grep python
```

### 가상환경 비활성화
```bash
deactivate
```

### 가상환경 재활성화
```bash
cd /app/python
source langflow/bin/activate
```

---

## 시스템 정보
- OS: Ubuntu 24.04.3 LTS
- Shell: zsh 5.9
- Python 3.13: Homebrew 설치 (alias로 기본 설정)
- Python 3.14: Homebrew 기본 버전 (시스템)
- 작업 디렉토리: `/app/python/langflow`
