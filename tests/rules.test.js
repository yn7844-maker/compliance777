import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {evaluate,makeLog,saveLog,readLogs,LOG_KEY} from '../js/rules.js';import {keyword} from '../js/search.js';
const rules=JSON.parse(fs.readFileSync(new URL('../data/rules.json',import.meta.url))),docs=JSON.parse(fs.readFileSync(new URL('../data/docs.json',import.meta.url)));
const base={type:'토지',land:'Y',building:'Y',kb:'Y',price:'Y',seizure:'N',provisional:'N',lease:'N',other:'N'};
for(const [name,v,id] of [['집합건물 압류',{type:'집합건물',seizure:'Y'},'R001'],['집합건물 공개정보 부족',{type:'집합건물',kb:'N',price:'N'},'R004'],['건축물대장 미확인',{type:'건물',building:'N'},'R006'],['일반 토지',{},'R099']])test(name,()=>assert.equal(evaluate({...base,...v},rules).id,id));
test('법무 검토 우선 및 추가 권리',()=>{assert.equal(evaluate({...base,land:'N',provisional:'Y'},rules).id,'R002');for(const k of ['lease','other'])assert.equal(evaluate({...base,[k]:'Y'},rules).id,'R003');});
test('집합건물 한 조회만 확인 및 선순위 금액 무관',()=>{for(const amount of ['0','999999999999'])assert.equal(evaluate({...base,type:'집합건물',kb:'N',price:'Y',senior:'Y',amount},rules).id,'R099');});
test('주소 및 개인정보 없는 영속 로그',()=>{const store=new Map();globalThis.localStorage={getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)};saveLog({...base,address:'서울시 ○○구 ○○동 *-',amount:123},rules.at(-1));assert.equal(readLogs().length,1);assert.deepEqual(Object.keys(JSON.parse(store.get(LOG_KEY))[0]),['timestamp','target_type','result','rule_id','rule_name','reason']);assert.ok(!store.get(LOG_KEY).includes('○○'));assert.equal(makeLog(base,rules[0]).target_type,'토지');});
test('로컬 키워드 검색',()=>assert.ok(keyword('가압류',docs)[0].content.includes('가압류')));
