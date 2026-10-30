import {test,after} from 'node:test';import assert from 'node:assert/strict';
import {health,search,keyword} from '../js/search.js';
const originalFetch=globalThis.fetch;after(()=>globalThis.fetch=originalFetch);
const docs=[{id:'A',title:'압류 가이드',content:'압류 확인',source:'예시'}];
test('keyword fallback and empty queries work without model',async()=>{globalThis.fetch=async()=>{throw Error('offline');};assert.equal(await health(),false);assert.equal((await search('압류',docs)).items.length,1);assert.equal(keyword('없는단어',docs).length,0);assert.equal((await search('',docs)).items.length,1);});
test('hosted browser calls same-origin proxy and accepts new server corpus IDs',async()=>{globalThis.fetch=async(url,opts)=>{assert(url.startsWith('/api/bge/'));if(url.endsWith('/health'))return {ok:true,json:async()=>({ok:true,engine:'BGE-M3'})};assert.equal(JSON.parse(opts.body).query,'권리');return {ok:true,json:async()=>({engine:'BGE-M3',results:[{id:'NEW',title:'권리 안내',content:'새 문서',source:'규정',score:.9}]})};};assert.equal(await health(),true);const r=await search('권리',docs);assert.equal(r.items[0].id,'NEW');assert.match(r.mode,/BGE/);});
test('a failed model search falls back to local results',async()=>{globalThis.fetch=async()=>{throw Error('timeout');};const r=await search('압류',docs);assert.match(r.mode,/Local/);assert.equal(r.items[0].id,'A');});
test('health with a different engine is not a BGE connection',async()=>{globalThis.fetch=async()=>({ok:true,json:async()=>({ok:true,engine:'other'})});assert.equal(await health(),false);});
