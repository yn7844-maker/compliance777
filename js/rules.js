export const labels={pass:'진행 가능',supplement:'보완 필요',legal:'법무팀 검토 필요'};
export function evaluate(v,rules){let id=v.seizure==='Y'?'R001':v.provisional==='Y'?'R002':v.lease==='Y'||v.other==='Y'?'R003':v.type==='집합건물'&&v.kb!=='Y'&&v.price!=='Y'?'R004':v.type==='토지'&&v.land!=='Y'?'R005':v.type==='건물'&&(v.land!=='Y'||v.building!=='Y')?'R006':'R099';return rules.find(r=>r.id===id);}
export function makeLog(v,r){return {timestamp:new Date().toISOString(),target_type:v.type,result:r.result,rule_id:r.id,rule_name:r.name,reason:r.id==='R003'?[v.lease==='Y'?'전세권 있음':'',v.other==='Y'?'기타 특이 권리 있음':''].filter(Boolean).join(' / '):r.condition};}
export const LOG_KEY='collateral.precheck.logs.v1';
export function readLogs(){try{const a=JSON.parse(localStorage.getItem(LOG_KEY)||'[]');return Array.isArray(a)?a.filter(x=>x&&labels[x.result]&&typeof x.timestamp==='string').map(x=>({timestamp:x.timestamp,target_type:x.target_type,result:x.result,rule_id:x.rule_id,rule_name:x.rule_name,reason:x.reason})):[];}catch{return [];}}
export function saveLog(v,r){const a=readLogs();a.push(makeLog(v,r));localStorage.setItem(LOG_KEY,JSON.stringify(a));}
