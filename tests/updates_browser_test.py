"""Simulate version changes without deploying or changing user data."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];old=json.loads((root/'dist/version.json').read_text())['version'];new='f'*64
server=ThreadingHTTPServer(('127.0.0.1',8129),partial(SimpleHTTPRequestHandler,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();state={'version':old,'bad':False};errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  def version(route):
   route.fulfill(status=200,content_type='application/json',body=json.dumps({'version':state['version']}) if not state['bad'] else 'not-json')
  page.route('**/version.json?*',version);page.goto('http://127.0.0.1:8129');page.locator('#new').click();page.locator('[data-type="토지"]').click();page.locator('#next').click();page.locator('#address').fill('서울시 ○○구 ○○동 *-')
  page.wait_for_timeout(200);assert '🔴' not in page.title();state['bad']=True
  with page.expect_response('**/version.json?*'):page.evaluate('window.dispatchEvent(new Event("focus"))')
  page.wait_for_timeout(200);assert page.locator('#update-notice').count()==0
  state['bad']=False;state['version']='broken'
  with page.expect_response('**/version.json?*'):page.evaluate('window.dispatchEvent(new Event("focus"))')
  page.wait_for_timeout(200);assert page.locator('#update-notice').count()==0
  state['version']=new
  with page.expect_response('**/version.json?*'):page.evaluate('window.dispatchEvent(new Event("focus"))')
  page.locator('#update-notice').wait_for();assert page.title()=='담보평가 사전체크 🔴';assert page.locator('#address').input_value()=='서울시 ○○구 ○○동 *-';assert 'circle' in page.locator('link[rel="icon"]').get_attribute('href');page.evaluate('window.dispatchEvent(new Event("focus"))');assert page.locator('#update-notice').count()==1
  page.route('http://127.0.0.1:8129/',lambda route:route.fulfill(status=200,content_type='text/html',body=(root/'dist/index.html').read_text().replace(old,new)))
  page.locator('#update-notice button').click();page.wait_for_load_state();page.locator('#new').wait_for();page.wait_for_timeout(200);assert page.title()=='담보평가 사전체크';assert page.locator('#update-notice').count()==0;assert not errors,errors;b.close()
  print('PASS: unchanged/malformed versions ignored; newer version marks tab title/favicon once; draft preserved; explicit reload clears marker after loading latest version; no JS errors.')
finally:server.shutdown()
