# BGE-M3 문서 검색 연결

BGE-M3는 문서를 벡터로 바꿔 관련 문서를 찾는 모델입니다. 답변 생성 API를 사용하지 않습니다. 기본 문서는 `data/docs.json`의 예시 자료이며, 실제 사내 규정이 아닙니다. 사전체크 Rule 판정은 바뀌지 않습니다.

## 1. 로컬 PC에서 먼저 실행

프로젝트 폴더에서 Python 3.10 이상으로 실행합니다. 가상환경 사용을 권장합니다.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r python_backend/requirements.txt
python -m python_backend.download_model --output models/bge-m3
```

다운로드는 최초 한 번만 필요하며 인터넷과 수 GB 이상의 저장공간이 필요합니다. 모델 실행에는 충분한 메모리가 필요하고 CPU에서는 검색/시작이 느릴 수 있습니다. 기본은 CPU이고 GPU가 준비되어 있으면 `BGE_DEVICE=cuda`를 설정합니다. 이후 서버 시작 시 모델을 인터넷에서 내려받지 않습니다.

Windows에서는 **`setup_bge.bat` → `start_bge_offline.bat` → `start_dashboard.bat` 순서로 실행**하면 됩니다. 설치 파일은 `.venv` 가상환경을 만들고 의존성 및 모델을 내려받습니다. 위 수동 설치를 완료했다면 `start_bge_offline.bat`부터 실행합니다. 기본 모델 위치는 프로젝트의 `models/bge-m3`입니다. 다른 위치라면 먼저 `BGE_MODEL_PATH`를 설정하세요.

macOS/Linux:

```bash
export BGE_MODEL_PATH="$PWD/models/bge-m3"
python -m uvicorn python_backend.server:app --host 127.0.0.1 --port 8000
```

별도 터미널에서 `python server.py`를 실행하고 `http://127.0.0.1:8080`의 **설정 → 연결 다시 확인**을 누릅니다. `BGE-M3 연결됨`이 표시되면 사례검색에서 질문/검색어를 입력합니다. 검색어 없이 열면 기본 문서 목록이 표시되고, 검색어를 입력하면 의미 검색을 수행합니다.

`GET http://127.0.0.1:8000/health`가 `ok: true`, `engine: BGE-M3`를 반환해야 실제 모델이 로드된 상태입니다. 파일이 없거나 모델 로딩에 실패하면 연결됨으로 표시하지 않습니다.

## 2. 내 문서 넣기

UTF-8 TXT/Markdown 파일을 `documents/` 폴더에 넣습니다. PDF/HWP/DOCX는 이 도구가 직접 해석하지 않으므로 먼저 검토한 텍스트로 변환하세요. 원본 파일명은 검색 결과의 출처에 표시됩니다. 파일명에 규정 버전이나 시행일을 넣으면 구분하기 좋습니다.

```bash
python -m python_backend.prepare_documents --input documents --output data/docs.json --overwrite
```

Windows에서는 `documents/` 폴더에 문서를 넣은 뒤 `import_documents.bat`로 같은 작업을 수행할 수 있습니다.

이 명령은 **기본 예시 문서를 교체**합니다. 원본을 보존하려면 `--output work/company-docs.json`처럼 새 파일로 생성하고 `BGE_DOCS_PATH`를 해당 파일의 절대 경로로 설정하세요. 검색 서버를 재시작하면 임베딩을 다시 만듭니다. 서버 전용 문서 파일을 사용하면 모델 미연결 시 브라우저의 키워드 검색은 기존 `data/docs.json`만 검색합니다.

기존 JSON도 입력 폴더에 넣어 합칠 수 있습니다. 필수 필드는 `id`, `title`, `content`, `source`입니다. 필터를 사용하려면 `kind` (`case`/`knowledge`), `target_type` (`토지`/`건물`/`집합건물`), `result` (`pass`/`supplement`/`legal`), `rule_id`도 넣으세요. TXT/MD로 만든 문서는 기본적으로 `knowledge`이며 다른 필터값은 자동 추론하지 않습니다. 중복 ID와 잘못된 필수 필드는 오류로 처리됩니다.

현재 사이트에는 직원 인증/문서 권한이 없습니다. `data/docs.json`은 방문자가 내려받을 수 있으며, 연결한 검색 결과도 사이트 방문자에게 제공됩니다. 접근 제한이 필요한 사내 문서는 직원 인증과 문서 권한을 갖춘 뒤 연결하세요. 원본 `documents/`, 모델 파일, 환경변수는 Git에 포함하지 않습니다.

## 3. 현재 Vercel 사이트에서 연결

Vercel 함수에서 BGE-M3 모델 자체를 실행하지 않습니다. 충분한 메모리가 있는 별도 PC/서버/컨테이너에 모델을 올리고 HTTPS 주소로 제공해야 합니다. 로컬 PC의 127.0.0.1 주소는 Vercel에서 접근할 수 없습니다.

흐름: 브라우저 `/api/bge/search` → Vercel 서버 함수 → 별도 BGE 서버 `/search`.

1. BGE 서버에 `BGE_MODEL_PATH`, 필요 시 `BGE_DOCS_PATH`를 지정합니다.
2. 긴 임의 문자열을 만들어 서버의 `BGE_API_KEY`에 지정하고 `BGE_REQUIRE_AUTH=true`를 지정합니다.
3. 서버를 시작합니다. 외부 제공 시 `--host 0.0.0.0`으로 실행하고, HTTPS 종료 프록시/호스팅을 구성합니다. Uvicorn 단독 실행은 HTTPS를 제공하지 않습니다. 외부 경로는 키 인증을 요구해야 합니다.
4. Vercel 프로젝트 **Settings → Environment Variables**에 아래 두 항목을 Production 환경으로 등록합니다.
   - `BGE_SERVER_URL`: 실제 HTTPS BGE 서버 주소. 예: `https://bge.example.com`
   - `BGE_API_KEY`: BGE 서버와 같은 키
5. Vercel을 재배포합니다. 설정 화면에서 **연결 다시 확인**을 누릅니다.

키는 브라우저 설정이나 소스에 쓰지 않습니다. `.env.example`은 항목 안내이며 자동으로 로드되는 설정 파일이 아닙니다. Vercel 변수는 대시보드/CLI로, Python 서버 변수는 실행 환경에서 설정합니다. Vercel 서버 함수는 키를 브라우저에 전달하지 않습니다. 외부 서버 주소/키가 없으면 설정 필요 상태를 표시하고 키워드 검색을 사용합니다.

로컬 직접 연결은 키 없이 루프백으로 실행하는 개발용 경로입니다. 키를 설정한 외부 서버에는 Vercel 프록시로 접근하세요. 브라우저가 키를 저장하도록 구현하지 않았습니다.

## 4. 확인 및 운영

- `model_unavailable`: 모델 경로 미설정 또는 폴더 없음
- `documents_unavailable`: 문서 JSON 또는 필수 필드 확인 필요
- `model_load_failed`: 의존성, 메모리, 모델 파일 확인 필요
- `not_configured`: Vercel 서버 주소/키 설정 필요
- `backend_unavailable`: 서버 중지, HTTPS/인증, 타임아웃 등 연결 실패

현재 연결 상태는 시작 시 또는 설정의 재확인 버튼으로 갱신합니다. 검색 실패 시 즉시 키워드 검색으로 전환합니다. 문서가 적으면 시작할 때 메모리 색인으로 충분하며, 대량 문서에서는 영속 벡터 색인과 문서별 접근 권한을 추가하는 편이 좋습니다.

별도 생성형 AI API 요금은 없지만, 모델 서버의 장비·호스팅 비용과 Vercel 플랜 사용량은 별개입니다.

검증:

```bash
npm test
npm run build
python -m pip install numpy
python -m unittest discover -s tests -p bge_backend_test.py
```

테스트는 문서 변환, 인증, 요청 검증, 프록시, 장애 시 대체 검색, 모의 벡터 순위를 확인합니다. 실제 BGE-M3 검색 품질은 모델을 설치한 서버에서 별도로 확인해야 합니다.
