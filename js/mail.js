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

export function createRequestMail(item,cfg){
 if(!validEmail(cfg.recipient))throw Error('수신 이메일을 설정하세요.');
 const subject=`[담보평가 의뢰] ${item.target_type} · ${item.id}`;
 const body=['준법지원팀 담당자님,','검토 요청 의뢰가 등록되었습니다.','',`접수번호: ${item.id}`,`의뢰구분: ${item.purpose}`,`물건유형: ${item.target_type}`,`사전체크 결과: ${item.result==='legal'?'준법지원팀 검토 필요':'진행 가능'}`,`적용 기준: ${item.rule_id} / ${item.rule_name}`,`판정 사유: ${item.reason}`,`처리 상태: ${item.status}`,'','의뢰 상세는 앱의 준법지원팀 메뉴에서 확인합니다.','현재 데모는 동일 브라우저에만 저장됩니다. 다른 직원에게 목록이 공유되지 않습니다.','주소·개인정보·채권금액·첨부파일은 포함하지 않았습니다.'].join('\r\n');
 return {subject,body,url:cfg.method==='web'?'https://outlook.office.com/mail/deeplink/compose?'+new URLSearchParams({to:cfg.recipient,subject,body}).toString():`mailto:${encodeURIComponent(cfg.recipient)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`};
}

export function createSupplementMail(item,cfg){if(!validEmail(cfg.recipient))throw Error('담당자 업무 이메일이 필요합니다.');const subject=`[담보평가 사전체크] 보완 요청${item.id?' · '+item.id:''}`;const body=['담당 FC님,','사전체크/검토 결과 아래 항목의 보완을 요청드립니다.','',...(item.id?[`접수번호: ${item.id}`]:[]),`물건유형: ${item.target_type}`,`적용 기준: ${item.rule_id}`,`보완 항목: ${item.supplementReason||item.reason}`,'','해당 정보를 확인한 뒤 앱에서 수정·재판정해주세요. 이관된 건은 의뢰내역에서 보완 후 재제출할 수 있습니다.','주소·개인정보·채권금액·첨부파일은 포함하지 않았습니다.','현재 데모는 같은 브라우저에만 기록이 저장됩니다.'].join('\r\n');return {subject,body,url:cfg.method==='web'?'https://outlook.office.com/mail/deeplink/compose?'+new URLSearchParams({to:cfg.recipient,subject,body}).toString():`mailto:${encodeURIComponent(cfg.recipient)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`};}
