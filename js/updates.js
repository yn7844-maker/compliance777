export function startUpdateNotifier({intervalMs=60000}={}){
 const loadedVersion=document.querySelector('meta[name="app-version"]')?.content;
 if(!loadedVersion||loadedVersion==='__APP_VERSION__')return ()=>{};
 const baseTitle=document.title;let stopped=false,checking=false,notified=false;
 function notify(){if(stopped||notified)return;notified=true;document.title=baseTitle+' 🔴';
 const icon=document.querySelector('link[rel="icon"]');if(icon)icon.href='data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#2563eb"/><path d="m9 16 5 5 10-11" stroke="white" fill="none" stroke-width="3"/><circle cx="25" cy="7" r="6" fill="#dc2626" stroke="white" stroke-width="2"/></svg>');
 const panel=document.createElement('aside');panel.id='update-notice';panel.setAttribute('role','status');panel.setAttribute('aria-live','polite');panel.innerHTML='<div><strong><span aria-hidden="true">🔴</span> 새 버전이 있습니다</strong><p>저장하지 않은 입력은 새로고침하면 사라집니다. 필요한 정보를 복사한 뒤 새로고침하세요.</p></div><button type="button" class="primary">새로고침</button>';panel.querySelector('button').onclick=()=>location.reload();document.body.append(panel);
 }
 async function check(){if(stopped||checking||notified||!navigator.onLine)return;checking=true;try{const response=await fetch('/version.json?check='+Date.now(),{cache:'no-store',credentials:'same-origin',signal:AbortSignal.timeout(3000)});if(!response.ok)return;const data=await response.json();if(typeof data.version==='string'&&/^[a-f0-9]{64}$/.test(data.version)&&data.version!==loadedVersion)notify();}catch{/* 다음 주기에 재시도. 네트워크 실패를 업데이트로 표시하지 않습니다. */}finally{checking=false;}}
 const onVisible=()=>{if(document.visibilityState==='visible')check();};
 const timer=setInterval(check,intervalMs);window.addEventListener('focus',check);window.addEventListener('online',check);document.addEventListener('visibilitychange',onVisible);check();
 return ()=>{stopped=true;clearInterval(timer);window.removeEventListener('focus',check);window.removeEventListener('online',check);document.removeEventListener('visibilitychange',onVisible);};
}
