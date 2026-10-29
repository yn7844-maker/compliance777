export const targetTypes=['토지','건물','집합건물'];
export const rightsFields=[['senior','선순위 채권'],['seizure','압류'],['provisional','가압류'],['lease','전세권'],['other','기타 특이 권리']];
export const publicFields={토지:[['land','토지이용계획']],건물:[['land','토지이용계획'],['building','건축물대장']],집합건물:[['kb','KB시세'],['price','공동주택가격']]};
export function validateInput(v,{step=3}={}){
 const errors=[];const add=(field,message,at)=>{if(at<=step)errors.push({field,message,step:at});};
 if(!targetTypes.includes(v.type))add('type','물건유형을 선택해주세요.',1);
 if(typeof v.address!=='string'||!v.address.trim()||v.address.length>160)add('address','주소를 입력해주세요. 마스킹된 주소도 사용할 수 있습니다.',2);
 for(const [k,n] of publicFields[v.type]||[])if(!['Y','N'].includes(v[k]))add(k,n+' 확인 여부를 선택해주세요.',2);
 for(const [k,n] of rightsFields)if(!['Y','N'].includes(v[k]))add(k,n+'를 확인한 뒤 있음 또는 없음을 선택해주세요.',3);
 if(v.rightsConfirmed!==true)add('rightsConfirmed','권리관계 확인 완료에 체크해주세요.',3);
 if(v.senior==='Y'&&String(v.amount??'').trim()&&!/^\d{1,15}$/.test(String(v.amount)))add('amount','선순위 채권금액은 0 이상의 정수로 입력해주세요. 확인하지 못한 금액은 비워두세요.',3);
 if(v.email&&(!/^[^\s@<>?,;:"\\]+@[^\s@<>?,;:"\\]+\.[^\s@<>?,;:"\\]+$/.test(v.email)||v.email.length>254))add('email','담당자 업무 이메일 형식을 확인해주세요.',2);
 return errors;
}
export class InputValidationError extends Error{constructor(errors){super(errors.map(e=>e.message).join('\n'));this.name='InputValidationError';this.errors=errors;}}
export function assertValidInput(v){const errors=validateInput(v);if(errors.length)throw new InputValidationError(errors);}
export function missingPublicInfo(v){return (publicFields[v.type]||[]).filter(([k])=>v[k]!=='Y').map(([,n])=>n);}
