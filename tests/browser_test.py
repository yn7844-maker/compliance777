from playwright.sync_api import sync_playwright
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1100})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8080');page.get_by_text('업무 현황 한눈에 보기').wait_for()
    page.screenshot(path=str(root/'work/home.png'),full_page=True)
    assert page.locator('.kpi strong').first.inner_text()=='48건'
    cases=[('집합건물',{'kb':'Y','price':'Y'},{'seizure':'Y'},'R001','법무팀 사전 검토 필요'),('집합건물',{}, {},'R004','정보 보완 필요'),('건물',{'land':'Y'}, {},'R006','정보 보완 필요'),('토지',{'land':'Y'}, {},'R099','담보평가 진행 가능')]
    for ty,public,rights,rid,title in cases:
        page.locator('#new').click();page.locator(f'[data-type="{ty}"]').click();page.locator('#next').click()
        page.locator('#address').fill('서울시 ○○구 ○○동 *-')
        for k,v in public.items():page.locator(f'[data-key="{k}"][data-value="{v}"]').click()
        assert page.locator('#address').input_value()=='서울시 ○○구 ○○동 *-'
        page.locator('#next').click()
        for k,v in rights.items():page.locator(f'[data-key="{k}"][data-value="{v}"]').click()
        page.locator('#next').click();page.get_by_role('heading',name=title,exact=True).wait_for()
        assert page.locator('dd code').inner_text()==rid
        page.locator('#related .doc').first.wait_for()
        print('Browser Rule PASS',rid)
        if rid=='R099':
            page.locator('#result-action').click();assert '결재 연결 기능 미구현' in page.locator('#toast').inner_text()
            page.screenshot(path=str(root/'work/result.png'),full_page=True)
    logs=page.evaluate("JSON.parse(localStorage.getItem('collateral.precheck.logs.v1'))")
    assert len(logs)==4 and all(set(l)=={'timestamp','target_type','result','rule_id','rule_name','reason'} for l in logs)
    assert '○○' not in json.dumps(logs,ensure_ascii=False)
    page.locator('#dashboard').click();assert page.locator('.kpi strong').first.inner_text()=='4건'
    assert '75.0%' in page.locator('.notice').inner_text()
    page.screenshot(path=str(root/'work/dashboard.png'),full_page=True)
    page.reload();page.locator('[data-page="운영 대시보드"]').click();assert page.locator('.kpi strong').first.inner_text()=='4건'
    page.locator('[data-page="사례검색"]').click();page.locator('#query').fill('가압류');page.locator('#search-form button').click();page.wait_for_function("document.querySelector('#result-count').textContent.includes('1건')")
    assert page.locator('#search-mode').inner_text()=='Local Keyword Search'
    assert '가압류' in page.locator('#search-results').inner_text()
    page.locator('[data-page="Rule 정보"]').click();assert page.locator('tbody tr').count()==7
    page.locator('[data-page="홈"]').click();page.set_viewport_size({'width':1024,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    page.screenshot(path=str(root/'work/home-1024.png'),full_page=True)
    assert not errors,errors
    print('Browser PASS: 4 Rules, masked address preserved, 4 private logs, dashboard persistence, keyword fallback, Rule menu, 1024px, no JS errors')
    browser.close()
