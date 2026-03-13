# -*- coding: utf-8 -*-
"""历史速递详情页 DOM 探索脚本"""
from playwright.sync_api import sync_playwright
import yaml

with open('config/config.yaml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

base_url = config['base_url']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    ctx = browser.new_context()
    page = ctx.new_page()

    # 登录
    page.goto(f"{base_url}/login")
    page.wait_for_load_state('networkidle')
    page.fill('#user_name_input', 'test001')
    page.fill('#password_input', '12345678')
    page.click('button[type=submit]')
    page.wait_for_timeout(3000)

    # 进入历史速递列表页
    page.goto(f"{base_url}/history")
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(2000)

    print("=" * 60)
    print("历史速递列表页 URL:", page.url)
    print("=" * 60)

    # 探索列表页卡片
    print("\n[1] 列表页 - 日期卡片")
    result = page.evaluate("""
    () => {
        const results = [];
        const els = document.querySelectorAll('[class*="card"],[class*="Card"]');
        els.forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.length > 5 && text.length < 200) {
                results.push({tag: el.tagName, class: el.className.substring(0,80), preview: text.substring(0,60)});
            }
        });
        return results.slice(0, 10);
    }
    """)
    for r in result:
        print(f"  <{r['tag']}> class='{r['class']}' preview='{r['preview']}'")

    # 点击第一个卡片进入详情
    cards = page.locator('[class*="card"]')
    print(f"\n卡片数量: {cards.count()}")
    if cards.count() > 0:
        cards.first.click()
        page.wait_for_timeout(2500)

    print("\n历史速递详情页 URL:", page.url)

    # 探索详情页文献条目
    print("\n[2] 详情页 - 文献条目")
    result2 = page.evaluate("""
    () => {
        const results = [];
        const els = document.querySelectorAll('[class*="item"],[class*="Item"],[class*="split"],[class*="Split"],[class*="wrap"],[class*="Wrap"]');
        els.forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.length > 80) {
                results.push({tag: el.tagName, class: el.className.substring(0,100), textLen: text.length, preview: text.substring(0,80)});
            }
        });
        return results.slice(0, 15);
    }
    """)
    for r in result2:
        print(f"  <{r['tag']}> class='{r['class']}' len={r['textLen']} preview='{r['preview'][:60]}'")

    # 探索标题元素
    print("\n[3] 详情页 - 标题元素")
    result3 = page.evaluate("""
    () => {
        const results = [];
        const els = document.querySelectorAll('[class*="title"],[class*="Title"]');
        els.forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.length > 10 && text.length < 300) {
                results.push({tag: el.tagName, class: el.className.substring(0,80), preview: text.substring(0,80)});
            }
        });
        return results.slice(0, 10);
    }
    """)
    for r in result3:
        print(f"  <{r['tag']}> class='{r['class']}' preview='{r['preview']}'")

    # 截图
    page.screenshot(path="reports/explore_history.png")
    print("\n[截图] 已保存 reports/explore_history.png")

    browser.close()
