"""Review UI QA. No external email is opened or sent."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',8125),partial(SimpleHTTPRequestHandler,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1100});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8125')
  page.locator('[data-page="준법지원팀"]').click();page.locator('#decision-status').select_option('거부');page.locator('#review-decision button').click();assert page.evaluate("localStorage.getItem('collateral.precheck.requests.v1')") is None
  page.screenshot(path=str(root/'work/review-samples.png'),full_page=True)
  for width in [1440,1024]:
   page.set_viewport_size({'width':width,'height':1100});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.locator('#new').click();page.locator('[data-type="집합건물"]').click();page.locator('#next').click();page.locator('#address').fill('PRIVATE_ADDRESS');page.locator('[data-key="kb"][data-value="Y"]').click();page.locator('#next').click();page.locator('[data-key="seizure"][data-value="Y"]').click();page.locator('#next').click();page.locator('#result-action').click();page.get_by_role('heading',name='FC 의뢰서 작성').wait_for();page.locator('#request-confirm').check();page.locator('#request-submit').click()
  rows=page.evaluate("JSON.parse(localStorage.getItem('collateral.precheck.requests.v1'))");assert len(rows)==1 and rows[0]['status']=='처리 전';assert 'PRIVATE_ADDRESS' not in str(rows)
  page.locator('[data-page="준법지원팀"]').click();page.get_by_role('heading',name='준법지원팀 의뢰 관리').wait_for()
  for status in ['확인 중','승인','거부']:
   page.locator('#decision-status').select_option(status);page.locator('#review-decision button').click();assert page.evaluate("JSON.parse(localStorage.getItem('collateral.precheck.requests.v1'))[0].status")==status
  assert page.locator('.review-history li').count()==4
  page.screenshot(path=str(root/'work/review-detail.png'),full_page=True)
  page.locator('[data-page="의뢰내역"]').click();assert page.locator('#review-decision').count()==0;assert '거부' in page.locator('.review-detail').inner_text();page.reload();page.locator('[data-page="의뢰내역"]').click();assert '거부' in page.locator('.review-detail').inner_text()
  page.locator('[data-page="설정"]').click();page.locator('#mail-recipient').fill('team@example.invalid');page.locator('#mail-method').select_option('web');page.locator('#mail-settings button').click();page.locator('[data-page="의뢰내역"]').click();page.evaluate('window.open=url=>{window.testMailUrl=url;return null;}');page.locator('#request-mail').click();url=page.evaluate('window.testMailUrl');assert 'outlook.office.com' in url and rows[0]['id'] in url and 'PRIVATE_ADDRESS' not in url
  page.locator('[data-page="준법지원팀"]').click();page.locator('[data-status="처리 전"]').click();assert '해당하는 의뢰가 없습니다.' in page.locator('.review-list').inner_text();page.locator('#review-all').click();assert page.locator('[data-request]').count()==1
  assert not errors,errors;b.close();print('PASS: sample isolation, FC request, private-field exclusion, 4 states/history, FC status read-only, reload persistence, status filters, 1440/1024px, Outlook draft URL, zero JS errors. No email sent.')
finally:server.shutdown()
