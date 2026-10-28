const SETTINGS_KEY='collateral.precheck.mail.v1';
const validEmail=s=>typeof s==='string'&&s.length<=254&&/^[^\s@<>?,;:"\\]+@[^\s@<>?,;:"\\]+\.[^\s@<>?,;:"\\]+$/.test(s);
export function readMailSettings(){try{const s=JSON.parse(localStorage.getItem(SETTINGS_KEY)||'{}');return {recipient:validEmail(s.recipient)?s.recipient:'',method:s.method==='web'?'web':'desktop'};}catch{return {recipient:'',method:'desktop'};}}
export function saveMailSettings(s){const recipient=s.recipient.trim();if(!validEmail(recipient))throw Error('Invalid recipient');localStorage.setItem(SETTINGS_KEY,JSON.stringify({recipient,method:s.method==='web'?'web':'desktop'}));}
export function createReviewMail(v,r,cfg){
 if(r.result!=='legal'||!validEmail(cfg.recipient))throw Error('Review result and recipient required');
 const queries={토지:[['land','토지이용계획']],건물:[['land','토지이용계획'],['building','건축물대장']],집합건물:[['kb','KB시세'],['price','공동주택가격']]};
 const rights=[['senior','선순위 채권'],['seizure','압류'],['provisional','가압류'],['lease','전세권'],['other','기타 특이 권리']];
 const subject=`[담보평가 사전체크] 준법지원팀 검토 요청 · ${v.type} · ${r.id}`;
 const body=['준법지원팀 담당자님,','담보평가 의뢰 전 사전체크 결과에 대한 검토를 요청드립니다.','',`작성일시: ${new Date().toLocaleString('ko-KR',{timeZone:'Asia/Seoul'})} (한국시간)`,`물건유형: ${v.type}`,'판정: 준법지원팀 검토 필요',`적용 Rule: ${r.id} / ${r.name}`,`판단 사유: ${r.condition}`,`Rule 출처: ${r.source}`,'',...((queries[v.type]||[]).map(([k,n])=>`${n}: ${v[k]==='Y'?'확인 완료':'미확인'}`)),...rights.map(([k,n])=>`${n}: ${v[k]==='Y'?'있음':'없음'}`),'','주소·채권금액·개인정보·첨부파일은 포함하지 않았습니다.','본 결과는 사전체크 데모 기준이며 법적 판단 및 최종 담보가액 산정을 대체하지 않습니다.'].join('\r\n');
 const url=cfg.method==='web'?'https://outlook.office.com/mail/deeplink/compose?'+new URLSearchParams({to:cfg.recipient,subject,body}).toString():`mailto:${encodeURIComponent(cfg.recipient)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
 return {url,subject,body};
}
