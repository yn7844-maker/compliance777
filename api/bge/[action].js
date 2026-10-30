// The browser calls only this same-origin endpoint. Upstream credentials stay here.
export default async function handler(req,res){
 res.setHeader('Cache-Control','no-store');
 const action=req.query?.action||new URL(req.url,'http://localhost').pathname.split('/').pop();
 const send=(status,body)=>res.status(status).json(body);
 if(!['health','search'].includes(action))return send(404,{error:'not_found'});
 const method=action==='health'?'GET':'POST';
 if(req.method!==method){res.setHeader('Allow',method);return send(405,{error:'method_not_allowed'});}
 let payload;
 if(action==='search'){
  try{payload=typeof req.body==='string'?JSON.parse(req.body):req.body;}catch{return send(400,{error:'invalid_query'});}
  if(!payload||typeof payload.query!=='string'||!payload.query.trim()||payload.query.length>1000||!Number.isInteger(payload.top_k??5)||(payload.top_k??5)<1||(payload.top_k??5)>50)return send(400,{error:'invalid_query'});
  payload={query:payload.query.trim(),top_k:payload.top_k??5};
 }
 let base;
 try{base=new URL(process.env.BGE_SERVER_URL);if(base.protocol!=='https:'||base.username||base.password||base.search||base.hash)throw Error();}catch{return send(503,{ok:false,detail:'not_configured'});}
 const token=process.env.BGE_API_KEY;
 if(!token)return send(503,{ok:false,detail:'not_configured'});
 const url=new URL(base.toString().replace(/\/$/,'')+'/'+action);
 try{
  const upstream=await fetch(url,{method,headers:{Authorization:'Bearer '+token,...(payload?{'Content-Type':'application/json'}:{})},...(payload?{body:JSON.stringify(payload)}:{}),signal:AbortSignal.timeout(action==='health'?8000:20000),redirect:'error'});
  if(!upstream.ok)return send(503,{ok:false,detail:'backend_unavailable'});
  const data=await upstream.json();
  if(action==='health')return send(200,{ok:data.ok===true&&data.engine==='BGE-M3',engine:data.ok===true&&data.engine==='BGE-M3'?'BGE-M3':null,detail:data.ok===true&&data.engine==='BGE-M3'?'ready':'model_unavailable',documents:Number.isInteger(data.documents)?data.documents:0});
  if(data.engine!=='BGE-M3'||!Array.isArray(data.results)||data.results.length>payload.top_k||data.results.some(d=>typeof d.id!=='string'||typeof d.title!=='string'||typeof d.content!=='string'||!Number.isFinite(d.score)))return send(502,{error:'invalid_backend_response'});
  return send(200,{engine:'BGE-M3',results:data.results.map(d=>Object.fromEntries(['id','title','content','kind','source','target_type','result','rule_id','score'].filter(k=>k in d).map(k=>[k,d[k]])))});
 }catch{return send(503,{ok:false,detail:'backend_unavailable'});}
}
