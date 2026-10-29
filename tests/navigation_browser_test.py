from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',8126),partial(SimpleHTTPRequestHandler,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8126')
  expected=['홈','사전체크','의뢰내역','사례검색','준법지원팀','설정'];assert page.locator('#sidebar [data-page]').all_text_contents()==expected
  page.locator('[data-page="사례검색"]').click();page.locator('[data-section="판정 기준"]').click();assert page.locator('h1').inner_text()=='사례검색';assert page.locator('#sidebar .active').inner_text()=='사례검색';assert page.locator('tbody tr').count()==7
  page.locator('[data-section="사례검색"]').click();page.locator('#query').fill('가압류');page.locator('#search-form button').click();page.wait_for_function("document.querySelector('#result-count').textContent.includes('1건')");assert page.locator('[data-section]').count()==2
  page.locator('[data-page="준법지원팀"]').click();page.locator('[data-section="운영 대시보드"]').click();assert page.locator('.kpi').count()==5;assert page.locator('h1').inner_text()=='준법지원팀';assert page.locator('#sidebar .active').inner_text()=='준법지원팀';page.locator('#sample').uncheck();assert page.locator('[data-section="운영 대시보드"]').get_attribute('aria-pressed')=='true'
  for width in [1440,1024]:
   page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.locator('[data-section="준법지원팀"]').click();page.locator('#review-sample').uncheck();assert page.locator('[data-section]').count()==2
  page.locator('#new').click();page.locator('[data-type="토지"]').click();page.locator('#next').click();page.locator('[data-key="land"][data-value="Y"]').click();page.locator('#next').click();page.locator('#next').click();page.locator('#dashboard').click();assert page.locator('#sidebar .active').inner_text()=='준법지원팀';assert page.locator('[data-section="운영 대시보드"]').get_attribute('aria-pressed')=='true'
  page.locator('[data-page="설정"]').click();assert page.locator('#section-nav').inner_text()=='';assert not errors,errors;b.close();print('PASS: six menus/order, nested search/rules and team/dashboard, active parent, tab preservation after redraw, result CTA, 1440/1024px, no JS errors.')
finally:server.shutdown()
