# 담보평가 사전체크

FC가 법무팀에 담보평가 의뢰하기 전에 공개정보와 최소 권리관계로 일반 의뢰 대상을 확인하는 데모입니다.

## Vercel 배포

Vercel에서 `yn7844-maker/compliance777` 저장소를 Import합니다.

- Git Branch: `main`
- Root Directory: `./` (기본값 유지)
- Project Name: `compliance777` (또는 원하는 이름)
- Framework: Other
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `node --version` (설치 의존성 없음)
- Node.js: 22 이상
- 서버 환경변수: 없음

설정은 `vercel.json`에 포함되어 있습니다. Python/FastAPI는 Vercel 정적 웹 배포에 필요하지 않습니다.
웹 배포에서는 브라우저의 로컬 8000 포트에 연결하지 않고 Local Keyword Search를 사용합니다.
Vercel 프로젝트 접근 보호는 Vercel 계정/요금제에 맞게 설정해야 하며, GitHub 저장소의 공개/비공개와 웹사이트 접근 보호는 별개입니다.

## 로컬 실행

Windows: `start_dashboard.bat` 더블클릭. Python 3.10 이상 필요.
또는 `python server.py` → `http://127.0.0.1:8080`.
상세 안내: `README_WINDOWS.txt`.

## 검증

```sh
npm test
npm run build
```

Rule, 단계형 사전체크, 로컬 로그, 홈/운영 대시보드, 사례검색, Rule 정보, 설정을 포함합니다.
집합건물은 전체 1~9단계 중 3단계 조회 행동만 KB시세/공동주택가격으로 대체합니다.

## 데이터 및 판정 범위

- `data/rules.json`: Rule 표시 정보 및 출처
- `js/rules.js`: Rule 조건 및 우선순위
- `data/docs.json`: 실제 사례가 아닌 DEMO 예시 문서
- BGE는 관련 문서 검색용이며 최종 판정에 사용하지 않습니다.
- 모든 현재 Rule은 원문 Excel 미제공으로 **데모 가정**입니다.
- 주소, 채권금액, 개인정보는 로그에 저장하지 않습니다.
- 로그는 해당 웹사이트 주소의 브라우저 localStorage에만 저장되며 공용 DB가 아닙니다.
- 법적 판단 및 최종 담보가액 산정을 대체하지 않습니다.
