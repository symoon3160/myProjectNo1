# Growlog — 사내 자기개발 학습 대시보드

학습 목표와 수행 내역을 기록하고 개인·팀·전사 관점에서 계획 대비 진척도를 확인하는 Streamlit MVP입니다.

## 로컬 실행

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속합니다.

## 제공 기능

- 개인 학습 KPI, 주별 계획 대비 수행, 목표별 진척도
- 목표 등록 및 학습 수행 기록
- 팀 참여율과 지원 필요 구성원 확인
- HRD·경영진용 조직별 현황과 필터
- 목표·수행·리포트 CSV 다운로드
- 역할별 데모 화면과 샘플 데이터

## 데이터 저장 방식

현재 버전은 빠른 화면 검증을 위한 MVP로, 데이터가 Streamlit 세션에 저장됩니다. 서버 재시작 후에도 데이터를 유지해야 하는 운영 버전에서는 SQLite, PostgreSQL 또는 사내 데이터베이스 연결이 필요합니다.

## Streamlit Community Cloud 배포

1. 이 폴더를 GitHub 저장소에 올립니다.
2. Streamlit Community Cloud에서 저장소를 연결합니다.
3. Main file path를 `app.py`로 지정합니다.
4. Deploy를 실행합니다.

