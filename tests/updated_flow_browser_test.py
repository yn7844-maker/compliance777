from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];server=ThreadingHTTPServer(('127.0.0.1',8128),partial(SimpleHTTPRequestHandler,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);context=browser.new_context(viewport={'width':1440,'height':1050},permissions=['clipboard-read','clipboard-write']);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8128');page.evaluate("localStorage.setItem('collateral.precheck.mail.v1', JSON.stringify({recipient:'team@example.invalid',method:'web'}))")
  def rights(values={}):
   for key in ['senior','seizure','provisional','lease','other']:page.locator(f'[data-key="{key}"][data-value="{values.get(key,"N")}"]').click()
   page.locator('#rightsConfirmed').check()
  def start(ty='토지',public={'land':'Y'},staff=True):
   page.locator('#new').click();page.locator(f'[data-type="{ty}"]').click();page.locator('#next').click();page.locator('#address').fill('서울시 ○○구 ○○동 *-')
   if staff:
    page.locator('#staff').fill('TEST_FC');page.locator('#department').fill('TEST_DEPT');page.locator('#email').fill('fc@example.invalid')
   for key,value in public.items():page.locator(f'[data-key="{key}"][data-value="{value}"]').click()
   page.locator('#next').click()
  page.locator('#new').click();page.locator('[data-type="토지"]').click();page.locator('#next').click();page.locator('#next').click();assert page.locator('#address').count()==1 and '주소를 입력' in page.locator('#input-errors').inner_text();assert not page.evaluate("localStorage.getItem('collateral.precheck.logs.v1')")
  page.locator('#address').fill('서울시 ○○구 ○○동 *-');page.locator('[data-key="land"][data-value="Y"]').click();page.locator('#next').click();page.locator('#next').click();assert '선순위 채권' in page.locator('#input-errors').inner_text();assert page.locator('.rights-guide').count()==1;rights();page.locator('#next').click();assert page.locator('dd code').inner_text()=='R099'
  start();rights({'senior':'Y'});page.locator('#amount').fill('1234567');page.locator('#next').click();assert page.locator('dd code').inner_text()=='R099';plain=page.locator('#document-plain').input_value();assert all(x in plain for x in ['서울시 ○○구 ○○동 *-','TEST_FC','TEST_DEPT','fc@example.invalid','1,234,567원']);page.locator('#copy-all').click();assert page.evaluate('navigator.clipboard.readText()')==plain;page.get_by_role('button',name='주소 복사',exact=True).click();assert page.evaluate('navigator.clipboard.readText()')=='주소: 서울시 ○○구 ○○동 *-';page.locator('#result-action').click();assert page.locator('#request-form').count()==0;assert page.evaluate("localStorage.getItem('collateral.precheck.requests.v1')") is None
  page.screenshot(path=str(root/'work/updated-pass.png'),full_page=True)
  start('집합건물',{},True);rights();page.locator('#next').click();assert page.locator('dd code').inner_text()=='R004';page.evaluate('window.open=url=>{window.testMail=url;return null;}');page.locator('#supplement-mail').click();assert 'fc%40example.invalid' in page.evaluate('window.testMail');assert '보완' in page.locator('#document-plain').input_value()
  start('건물',{'land':'Y'},False);rights();page.locator('#next').click();assert page.locator('dd code').inner_text()=='R006';assert '담당자: 미입력' in page.locator('#document-plain').input_value()
  start('집합건물',{'kb':'Y','price':'Y'});rights({'seizure':'Y'});page.locator('#next').click();assert page.locator('dd code').inner_text()=='R001';page.locator('#result-action').click();page.locator('#request-confirm').check();page.locator('#request-submit').click();rows=page.evaluate("JSON.parse(localStorage.getItem('collateral.precheck.requests.v1'))");assert len(rows)==1;request_id=rows[0]['id'];assert not any(x in str(rows) for x in ['TEST_FC','TEST_DEPT','fc@example.invalid','○○'])
  page.locator('[data-page="준법지원팀"]').click();page.locator('#decision-status').select_option('보완 요청');page.locator('#review-decision button').click();page.locator('#supplement-recipient').fill('fc@example.invalid');page.locator('#send-supplement').click();assert 'fc%40example.invalid' in page.evaluate('window.testMail');page.locator('[data-page="의뢰내역"]').click();page.locator('#resubmit-request').click();assert page.locator('#address').input_value()=='';page.locator('#address').fill('서울시 ○○구 ○○동 *-');page.locator('#next').click();rights({'seizure':'Y'});page.locator('#next').click();page.locator('#result-action').click();page.locator('#request-confirm').check();page.locator('#request-submit').click();rows=page.evaluate("JSON.parse(localStorage.getItem('collateral.precheck.requests.v1'))");assert len(rows)==1 and rows[0]['id']==request_id and rows[0]['status']=='처리 전'
  for width in [1440,1024]:
   page.set_viewport_size({'width':width,'height':1050});page.locator('[data-page="준법지원팀"]').click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors;browser.close();print('PASS: blank address gate, rights unknown/confirmation gates, four required Rules, document all/field clipboard, no pass transfer, missing field labels, supplement email draft, exception-only request, same-ID resubmission, private data exclusion, 1440/1024px and no JS errors. No actual mail sent.')
finally:server.shutdown()
