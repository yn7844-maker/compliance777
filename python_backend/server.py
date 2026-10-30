"""BGE-M3 document retrieval. Loads local model files; never downloads on startup."""
import asyncio
import os
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from python_backend.corpus import load_documents

ROOT = Path(__file__).resolve().parents[1]
model = None
vectors = None
docs = []
error = 'model_unavailable'
encode_lock = threading.Lock()


def load():
    global model, vectors, docs, error
    model, vectors, docs = None, None, []
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    try:
        docs = load_documents(os.environ.get('BGE_DOCS_PATH', ROOT / 'data/docs.json'))
    except (ValueError, OSError):
        error = 'documents_unavailable'
        return
    path = os.environ.get('BGE_MODEL_PATH', '')
    if not path or not Path(path).is_dir():
        error = 'model_unavailable'
        return
    try:
        from sentence_transformers import SentenceTransformer
        candidate = SentenceTransformer(path, local_files_only=True, device=os.environ.get('BGE_DEVICE', 'cpu'))
        embeddings = candidate.encode([d['title'] + '\n' + d['content'] for d in docs], normalize_embeddings=True, batch_size=8)
        vectors, model, error = embeddings, candidate, ''
    except Exception:
        model, vectors, error = None, None, 'model_load_failed'


@asynccontextmanager
async def lifespan(app):
    if os.environ.get('BGE_REQUIRE_AUTH', '').lower() == 'true' and not os.environ.get('BGE_API_KEY'):
        raise RuntimeError('BGE_REQUIRE_AUTH=true requires BGE_API_KEY')
    await asyncio.to_thread(load)
    yield


def authorize(authorization: str | None = Header(default=None)):
    token = os.environ.get('BGE_API_KEY', '')
    if token and not secrets.compare_digest((authorization or '').encode(), ('Bearer ' + token).encode()):
        raise HTTPException(401, 'Unauthorized')


app = FastAPI(lifespan=lifespan, dependencies=[Depends(authorize)])
origins = [o.strip() for o in os.environ.get('BGE_ALLOWED_ORIGINS', 'http://127.0.0.1:8080,http://localhost:8080').split(',') if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET', 'POST'], allow_headers=['Content-Type', 'Authorization'])


@app.get('/health')
def health():
    return {'ok': model is not None, 'engine': 'BGE-M3' if model is not None else None, 'detail': error or 'ready', 'documents': len(docs)}


class Query(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50, strict=True)

    @field_validator('query')
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError('검색어를 입력하세요.')
        return value.strip()


@app.post('/search')
def search(q: Query):
    if model is None:
        raise HTTPException(503, 'BGE-M3 미연결')
    # Serialize model inference to avoid overlapping CPU/GPU memory spikes.
    with encode_lock:
        scores = vectors @ model.encode(q.query, normalize_embeddings=True)
    indexes = scores.argsort()[::-1][:q.top_k]
    return {'engine': 'BGE-M3', 'results': [{**docs[int(i)], 'score': float(scores[i])} for i in indexes]}
