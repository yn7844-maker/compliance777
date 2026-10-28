"""Optional genuine offline BGE-M3 server. Never downloads a model."""
import json, os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=['http://127.0.0.1:8080','http://localhost:8080'],allow_methods=['GET','POST'],allow_headers=['Content-Type'])
model=None; vectors=None; error='BGE_MODEL_PATH에 로컬 BGE-M3 모델 폴더를 지정하세요.'
docs=json.loads((Path(__file__).resolve().parents[1]/'data/docs.json').read_text(encoding='utf-8'))
@app.on_event('startup')
def load():
    global model,vectors,error
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    path=os.environ.get('BGE_MODEL_PATH','')
    if not path or not Path(path).is_dir(): return
    try:
        from sentence_transformers import SentenceTransformer
        model=SentenceTransformer(path,local_files_only=True)
        vectors=model.encode([d['title']+' '+d['content'] for d in docs],normalize_embeddings=True)
        error=''
    except Exception as e: model=None;error=type(e).__name__+': 로컬 모델 로딩 실패'
@app.get('/health')
def health(): return {'ok':model is not None,'engine':'BGE-M3' if model else None,'detail':error}
class Query(BaseModel):
    query:str=Field(min_length=1,max_length=1000)
    top_k:int=Field(default=5,ge=1,le=50)
@app.post('/search')
def search(q:Query):
    if model is None: raise HTTPException(503,'BGE-M3 미연결')
    scores=vectors@model.encode(q.query,normalize_embeddings=True)
    indexes=scores.argsort()[::-1][:q.top_k]
    return {'engine':'BGE-M3','results':[{**docs[int(i)],'score':float(scores[i])} for i in indexes]}
