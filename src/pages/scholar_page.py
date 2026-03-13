# -*- coding: utf-8 -*-
"""
学者雷达页面对象 - POM 模式实现
封装学者雷达页面的所有元素定位与操作
对应测试模块 TC-05
"""
from pages.base_page import BasePage
from playwright.sync_api import Page


class ScholarPage(BasePage):
    """学者雷达页类"""

    # ── 学者列表区域 ────────────────────────────────────────────
    SCHOLAR_LIST     = '[class*="_trackerScrollWrap_4y21g"]'   # 学者卡片滚动容器
    SCHOLAR_ITEM     = '[class*="_trackerCard_4y21g"]'         # 每张学者卡片
    SCHOLAR_NAME     = '[class*="_trackerName_4y21g"]'         # 学者姓名标签

    # ── 文献列表区域（与首页共用同一套 CSS Module）────────────────
    LITERATURE_ITEMS = '[class*="_item_1ret0"]'                # 每篇文献条目
    LIT_TITLE        = '[class*="_title_1ret0"]'               # 文献标题
    LIT_META         = '[class*="_metaRow_1ret0"]'             # 元数据行
    LIT_AI           = '[class*="_highlightBox_1ret0"]'        # AI 解读内容框
    LIT_COLLECT      = 'span[style*="cursor: pointer"]'        # 收藏按钮（bookmark SVG 容器）

    # ── 统计信息区域（需先点击学者卡片才可见）──────────────────────
    STATS_CONTAINER  = '[class*="_insightContent_4y21g"]'      # 统计整体容器
    FREQUENT_WORDS   = '[class*="_higKeywords_4y21g"]'         # 近期高频词汇内容
    RESEARCH_FOCUS   = '[class*="_insightBlock_4y21g"]'        # 研究焦点变化块

    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url
        self.scholar_url = f"{base_url}/radar"

    def goto_scholar_page(self):
        """直接导航至学者雷达页，并点击第一张学者卡片使统计信息可见"""
        self.logger.info("打开学者雷达页面")
        self.navigate_to(self.scholar_url)
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(1000)
        # 点击第一张学者卡片，触发统计信息加载（TC-05-02 依赖此操作）
        try:
            first_card = self.page.locator(self.SCHOLAR_ITEM).first
            first_card.click()
            self.page.wait_for_timeout(1200)
            self.logger.info("已点击第一张学者卡片，统计信息已加载")
        except Exception as e:
            self.logger.warning(f"点击学者卡片失败: {e}")

    def click_scholar_nav(self):
        """通过导航栏进入学者雷达"""
        self.page.get_by_role("link", name="学者雷达").click()
        self.page.wait_for_load_state('networkidle')

    # ── 学者列表 ──────────────────────────────────────────────

    def get_scholar_count(self) -> int:
        """获取学者列表人数"""
        count = self.page.locator(self.SCHOLAR_ITEM).count()
        self.logger.info(f"学者列表共 {count} 位")
        return count

    def get_all_scholar_names(self) -> list:
        """获取所有学者姓名列表"""
        names = []
        items = self.page.locator(self.SCHOLAR_ITEM)
        for i in range(items.count()):
            try:
                name = items.nth(i).locator(self.SCHOLAR_NAME).first.inner_text().strip()
                if name:
                    names.append(name)
            except Exception:
                pass
        self.logger.info(f"学者名单: {names}")
        return names

    def click_scholar(self, name: str):
        """点击指定姓名的学者卡片"""
        self.page.locator(f'{self.SCHOLAR_ITEM}:has-text("{name}")').first.click()
        self.logger.info(f"点击学者: {name}")

    # ── 文献列表 ──────────────────────────────────────────────

    def get_literature_count(self) -> int:
        """获取文献列表条目数"""
        count = self.page.locator(self.LITERATURE_ITEMS).count()
        self.logger.info(f"学者雷达文献数: {count}")
        return count

    def get_lit_title(self, index: int) -> str:
        """获取指定文献标题"""
        try:
            item = self.page.locator(self.LITERATURE_ITEMS).nth(index)
            return item.locator(self.LIT_TITLE).first.inner_text().strip()
        except Exception:
            return ''

    def get_lit_meta(self, index: int) -> str:
        """获取指定文献元数据"""
        try:
            item = self.page.locator(self.LITERATURE_ITEMS).nth(index)
            return item.locator(self.LIT_META).first.inner_text().strip()
        except Exception:
            return ''

    def get_lit_ai(self, index: int) -> str:
        """获取指定文献 AI 解读"""
        try:
            item = self.page.locator(self.LITERATURE_ITEMS).nth(index)
            return item.locator(self.LIT_AI).first.inner_text().strip()
        except Exception:
            return ''

    def click_lit_title(self, index: int):
        """点击指定文献标题"""
        item = self.page.locator(self.LITERATURE_ITEMS).nth(index)
        item.locator(self.LIT_TITLE).first.click()
        self.logger.info(f"点击学者雷达文献[{index}]标题")

    def get_collect_state(self, index: int) -> str:
        """获取收藏按钮状态（通过 SVG fill 属性区分已收藏/未收藏）"""
        try:
            item = self.page.locator(self.LITERATURE_ITEMS).nth(index)
            btn = item.locator(self.LIT_COLLECT).first
            return btn.evaluate(
                'el => { const svg = el.querySelector("svg"); return svg ? svg.getAttribute("fill") : el.innerHTML; }'
            ) or ''
        except Exception:
            return ''

    def click_collect(self, index: int):
        """点击收藏按钮"""
        item = self.page.locator(self.LITERATURE_ITEMS).nth(index)
        item.locator(self.LIT_COLLECT).first.click()
        self.logger.info(f"点击学者雷达文献[{index}]收藏按钮")

    # ── 统计信息 ──────────────────────────────────────────────

    def is_recent_papers_visible(self) -> bool:
        """统计信息容器（含近几年发文）是否可见"""
        try:
            return self.page.locator(self.STATS_CONTAINER).first.is_visible()
        except Exception:
            return False

    def get_recent_papers_text(self) -> str:
        """获取统计信息容器（含近几年发文）内容"""
        try:
            return self.page.locator(self.STATS_CONTAINER).first.inner_text().strip()
        except Exception:
            return ''

    def is_frequent_words_visible(self) -> bool:
        """近期高频词汇区域是否可见"""
        try:
            return self.page.locator(self.FREQUENT_WORDS).first.is_visible()
        except Exception:
            return False

    def get_frequent_words_text(self) -> str:
        """获取近期高频词汇内容"""
        try:
            return self.page.locator(self.FREQUENT_WORDS).first.inner_text().strip()
        except Exception:
            return ''

    def is_research_focus_visible(self) -> bool:
        """研究焦点变化区域是否可见"""
        try:
            return self.page.locator(self.RESEARCH_FOCUS).first.is_visible()
        except Exception:
            return False

    def get_research_focus_text(self) -> str:
        """获取研究焦点变化内容"""
        try:
            return self.page.locator(self.RESEARCH_FOCUS).first.inner_text().strip()
        except Exception:
            return ''
