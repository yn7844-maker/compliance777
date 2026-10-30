const local=globalThis.location&&['127.0.0.1','localhost'].includes(globalThis.location.hostname);
const base=local?'http://127.0.0.1:8000':'/api/bge';
export let connected=false;
export let connectionDetail='checking';
async function request(path,options={}){const response=await fetch(base+path,{...options,cache:'no-store',signal:AbortSignal.timeout(path==='/health'?10000:22000)});if(!response.ok){const data=await response.json().catch(()=>({}));const error=new Error('HTTP '+response.status);error.detail=data.detail;throw error;}return response.json();}
export async function health(){try{const r=await request('/health');connected=r.ok===true&&r.engine==='BGE-M3';connectionDetail=connected?'ready':(r.detail||'model_unavailable');}catch(err){connected=false;connectionDetail=err.detail||'backend_unavailable';}return connected;}
export function keyword(query,docs){const words=query.toLowerCase().split(/\s+/).filter(Boolean);return docs.map(d=>({...d,score:words.reduce((s,w)=>s+([d.title,d.content,d.target_type,d.rule_id].join(' ').toLowerCase().includes(w)?1:0),0)/Math.max(words.length,1)})).filter(d=>!words.length||d.score>0).sort((a,b)=>b.score-a.score);}
export async function search(query,docs){query=String(query??'').trim();if(!query)return {mode:'Local Keyword Search',items:keyword('',docs)};
if(connected){try{const r=await request('/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,top_k:50})});const a=r.results;if(r.engine!=='BGE-M3'||!Array.isArray(a)||a.some(d=>typeof d.id!=='string'||typeof d.title!=='string'||typeof d.content!=='string'||!Number.isFinite(d.score)))throw Error('Invalid response');return {mode:'BGE-M3 Semantic Search',items:a.map(d=>({...docs.find(x=>x.id===d.id),...d}))};}catch{connected=false;connectionDetail='backend_unavailable';globalThis.dispatchEvent?.(new Event('bge-fallback'));}}
return {mode:'Local Keyword Search',items:keyword(query,docs)};}
