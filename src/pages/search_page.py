# -*- coding: utf-8 -*-
"""
AI 检索页面对象 - POM 模式实现
封装 /search 页面的所有元素定位与操作
对应测试模块 TC-03
"""
from pages.base_page import BasePage
from playwright.sync_api import Page


class SearchPage(BasePage):
    """AI 检索页类"""

    # ── 初始状态 ───────────────────────────────────────────────
    INITIAL_PROMPT = ':has-text("开始您的文献检索")'

    # ── 搜索输入区域 ────────────────────────────────────────────
    SEARCH_INPUT  = 'textarea, input[type="text"], input[placeholder]'
    SEARCH_BUTTON = 'button:has-text("搜索"), button[type="submit"], button:has-text("检索")'

    # ── 检索结果列表 ────────────────────────────────────────────
    # TODO: 通过 DOM 探索确认 CSS Module 类名
    RESULT_ITEMS     = '[class*="resultItem"], [class*="searchItem"], [class*="literatureItem"]'
    RESULT_TITLE     = '[class*="title"], h2, h3, a'
    RESULT_TITLE_ZH  = '[class*="titleZh"], [class*="titleCn"]'
    RESULT_META      = '[class*="meta"], [class*="info"]'
    RESULT_AI        = '[class*="ai"], [class*="analysis"], [class*="summary"]'
    RESULT_COLLECT   = '[class*="collect"], [class*="bookmark"], [aria-label*="收藏"]'

    # ── 筛选面板 ──────────────────────────────────────────────
    FILTER_PANEL      = '[class*="filter"], [class*="sidebar"]'
    FILTER_YEAR       = ':has-text("发表年份")'
    FILTER_IF         = ':has-text("影响因子")'
    FILTER_QUALITY    = ':has-text("期刊质量")'
    FILTER_AUTHOR     = ':has-text("作者")'
    FILTER_ORG        = ':has-text("机构")'

    # ── 排序按钮 ──────────────────────────────────────────────
    SORT_BUTTON = 'button:has-text("排序"), [class*="sort"]'

    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url
        self.search_url = f"{base_url}/search"

    def goto_search_page(self):
        """直接导航至 AI 检索页"""
        self.logger.info("打开 AI 检索页面")
        self.navigate_to(self.search_url)
        self.page.wait_for_load_state('networkidle')

    def click_search_nav(self):
        """通过导航栏点击 AI 检索进入"""
        self.page.get_by_role("link", name="AI检索").click()
        self.page.wait_for_load_state('networkidle')
        self.logger.info("通过导航栏进入 AI 检索")

    # ── 初始状态校验 ──────────────────────────────────────────

    def is_initial_prompt_visible(self) -> bool:
        """是否显示"开始您的文献检索"初始提示"""
        try:
            return self.page.locator(self.INITIAL_PROMPT).first.is_visible()
        except Exception:
            return False

    def is_search_input_empty(self) -> bool:
        """搜索框是否为空"""
        try:
            val = self.page.locator(self.SEARCH_INPUT).first.input_value()
            return val == ''
        except Exception:
            return True

    # ── 搜索操作 ──────────────────────────────────────────────

    def search(self, keyword: str):
        """输入关键词并触发检索"""
        self.logger.info(f"AI 检索关键词: {keyword}")
        inp = self.page.locator(self.SEARCH_INPUT).first
        inp.fill(keyword)
        try:
            self.page.locator(self.SEARCH_BUTTON).first.click()
        except Exception:
            self.page.keyboard.press('Enter')
        self.page.wait_for_load_state('networkidle')

    # ── 结果列表 ──────────────────────────────────────────────

    def get_result_count(self) -> int:
        """获取检索结果数量"""
        count = self.page.locator(self.RESULT_ITEMS).count()
        self.logger.info(f"检索结果共 {count} 条")
        return count

    def get_result_locator(self):
        """返回结果列表定位器"""
        return self.page.locator(self.RESULT_ITEMS)

    def get_result_title(self, index: int) -> str:
        """获取第 index 条结果标题"""
        try:
            item = self.page.locator(self.RESULT_ITEMS).nth(index)
            return item.locator(self.RESULT_TITLE).first.inner_text().strip()
        except Exception:
            return ''

    def get_result_title_zh(self, index: int) -> str:
        """获取第 index 条结果中文标题翻译"""
        try:
            item = self.page.locator(self.RESULT_ITEMS).nth(index)
            return item.locator(self.RESULT_TITLE_ZH).first.inner_text().strip()
        except Exception:
            return ''

    def get_result_meta(self, index: int) -> str:
        """获取第 index 条结果元数据文本"""
        try:
            item = self.page.locator(self.RESULT_ITEMS).nth(index)
            return item.locator(self.RESULT_META).first.inner_text().strip()
        except Exception:
            return ''

    def get_result_ai(self, index: int) -> str:
        """获取第 index 条结果 AI 解读"""
        try:
            item = self.page.locator(self.RESULT_ITEMS).nth(index)
            return item.locator(self.RESULT_AI).first.inner_text().strip()
        except Exception:
            return ''

    def click_result_title(self, index: int):
        """点击第 index 条结果标题"""
        item = self.page.locator(self.RESULT_ITEMS).nth(index)
        item.locator(self.RESULT_TITLE).first.click()
        self.logger.info(f"点击检索结果[{index}]标题")

    def get_collect_state(self, index: int) -> str:
        """获取第 index 条收藏按钮 class（用于状态判断）"""
        try:
            item = self.page.locator(self.RESULT_ITEMS).nth(index)
            return item.locator(self.RESULT_COLLECT).first.get_attribute('class') or ''
        except Exception:
            return ''

    def click_collect(self, index: int):
        """点击第 index 条收藏按钮"""
        item = self.page.locator(self.RESULT_ITEMS).nth(index)
        item.locator(self.RESULT_COLLECT).first.click()
        self.logger.info(f"点击检索结果[{index}]收藏按钮")

    # ── 筛选操作 ──────────────────────────────────────────────

    def click_filter_item(self, filter_name: str):
        """按筛选项名称点击"""
        self.page.locator(f':has-text("{filter_name}")').last.click()
        self.logger.info(f"点击筛选项: {filter_name}")
        self.page.wait_for_load_state('networkidle')

    # ── 排序操作 ──────────────────────────────────────────────

    def click_sort(self):
        """点击排序按钮"""
        self.page.locator(self.SORT_BUTTON).first.click()
        self.logger.info("点击排序按钮")
        self.page.wait_for_load_state('networkidle')
