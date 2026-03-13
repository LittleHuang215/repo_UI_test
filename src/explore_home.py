# -*- coding: utf-8 -*-
"""首页 DOM 探索脚本"""
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
    page.goto(base_url)
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(2000)

    print("=" * 60)
    print("当前 URL:", page.url)
    print("=" * 60)

    # 1. 探索课题组名称
    print("\n[1] 课题组名称区域 - 查找所有含 class 的文本元素")
    result = page.evaluate("""
    () => {
        const results = [];
        // 找所有可能是标题的元素
        const els = document.querySelectorAll('h1,h2,h3,h4,[class*="group"],[class*="Group"],[class*="title"],[class*="name"],[class*="header"],[class*="info"]');
        els.forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.length < 60 && text.length > 1) {
                results.push({tag: el.tagName, class: el.className, text: text.substring(0,50)});
            }
        });
        return results.slice(0, 20);
    }
    """)
    for r in result:
        print(f"  <{r['tag']}> class='{r['class']}' text='{r['text']}'")

    # 2. 探索文献速递列表
    print("\n[2] 文献速递列表 - 查找条目容器")
    result2 = page.evaluate("""
    () => {
        const results = [];
        // 找到所有含 class 的 li 或 article 或 div，且文本超过 30 字
        const els = document.querySelectorAll('[class*="item"],[class*="Item"],[class*="card"],[class*="Card"],[class*="week"],[class*="Week"],[class*="split"],[class*="Split"]');
        els.forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.length > 50) {
                results.push({tag: el.tagName, class: el.className.substring(0,80), textLen: text.length, preview: text.substring(0,60)});
            }
        });
        return results.slice(0, 15);
    }
    """)
    for r in result2:
        print(f"  <{r['tag']}> class='{r['class']}' len={r['textLen']} preview='{r['preview']}'")

    # 3. 探索搜索框
    print("\n[3] 搜索框")
    result3 = page.evaluate("""
    () => {
        const results = [];
        const els = document.querySelectorAll('input,textarea');
        els.forEach(el => {
            results.push({tag: el.tagName, type: el.type, placeholder: el.placeholder, class: el.className.substring(0,60), id: el.id});
        });
        return results;
    }
    """)
    for r in result3:
        print(f"  <{r['tag']} type={r['type']} id={r['id']} placeholder='{r['placeholder']}'> class='{r['class']}'")

    # 4. 查找收藏按钮
    print("\n[4] 收藏按钮")
    result4 = page.evaluate("""
    () => {
        const results = [];
        const els = document.querySelectorAll('[class*="collect"],[class*="Collect"],[class*="star"],[class*="Star"],[class*="favor"],[class*="Favor"],[class*="bookmark"]');
        els.forEach(el => {
            results.push({tag: el.tagName, class: el.className.substring(0,80)});
        });
        return results.slice(0, 10);
    }
    """)
    for r in result4:
        print(f"  <{r['tag']}> class='{r['class']}'")

    # 5. 关键词区域
    print("\n[5] 关键词标签")
    result5 = page.evaluate("""
    () => {
        const results = [];
        const els = document.querySelectorAll('[class*="keyword"],[class*="Keyword"],[class*="tag"],[class*="Tag"],[class*="pill"],[class*="Pill"],[class*="kw"]');
        els.forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.length < 50) {
                results.push({tag: el.tagName, class: el.className.substring(0,80), text: text.substring(0,30)});
            }
        });
        return results.slice(0, 15);
    }
    """)
    for r in result5:
        print(f"  <{r['tag']}> class='{r['class']}' text='{r['text']}'")

    # 6. "共X篇"按钮
    print("\n[6] 共X篇按钮")
    result6 = page.evaluate("""
    () => {
        const els = document.querySelectorAll('*');
        const results = [];
        els.forEach(el => {
            const text = el.innerText?.trim();
            if (text && text.includes('共') && text.includes('篇') && text.length < 30) {
                results.push({tag: el.tagName, class: el.className.substring(0,80), text: text});
            }
        });
        return results.slice(0, 10);
    }
    """)
    for r in result6:
        print(f"  <{r['tag']}> class='{r['class']}' text='{r['text']}'")

    # 7. 页面截图
    page.screenshot(path="reports/explore_home.png")
    print("\n[截图] 已保存 reports/explore_home.png")

    browser.close()
