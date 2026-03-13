# -*- coding: utf-8 -*-
"""
首页页面对象 - POM 模式实现
封装首页的课题组信息、文献速递列表、搜索框、收藏按钮等操作
"""
from pages.base_page import BasePage
from playwright.sync_api import Page


class HomePage(BasePage):
    """首页页面类"""

    # ── 课题组信息区域 ─────────────────────────────────────────
    # TODO: 通过实际 DOM 探索确认选择器
    GROUP_NAME = '.uppercase.tracking-wide'   # 首页顶部课题组名称

    # ── 首页搜索框 ─────────────────────────────────────────────
    SEARCH_INPUT = 'input[placeholder]'        # 首页搜索输入框（通用）
    SEARCH_BUTTON = '._searchButton_49jgu_22'   # 搜索按钮

    # ── 文献速递区域 ────────────────────────────────────────────
    LITERATURE_SECTION   = '[class*="cardWrap"]'                        # 整个文献卡片容器
    LITERATURE_ITEMS     = '[class*="cardWrap"] > [class*="_item_"]'    # 每篇文献条目（限定在 cardWrap 内）
    ITEM_TITLE           = '[class*="_title_"]'                         # 英文标题
    ITEM_META_ROW        = '[class*="metaRow"]'                         # 元数据行（期刊/作者）
    AI_ANALYSIS          = '[class*="highlightBox"]'                    # AI 解读内容框
    LITERATURE_TRANSLATE = '[class*="subtitle"]'                        # 中文副标题（翻译）
    COLLECT_BTN          = 'span[style*="cursor: pointer"]'     # 收藏按钮（含 bookmark SVG 的可点击 span）

    # ── "共X篇"跳转按钮 ──────────────────────────────────────
    TOTAL_COUNT_BTN = ':is([class*="_more_"], .cursor-pointer):has-text("共")'

    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url

    def goto_home(self):
        """导航至首页"""
        self.logger.info("打开首页")
        self.navigate_to(self.base_url)
        self.page.wait_for_load_state('networkidle')

    # ── 课题组信息 ────────────────────────────────────────────

    def get_group_name(self) -> str:
        """获取首页展示的课题组名称"""
        try:
            text = self.page.locator(self.GROUP_NAME).first.inner_text().strip()
            self.logger.info(f"课题组名称: {text}")
            return text
        except Exception as e:
            self.logger.warning(f"获取课题组名称失败: {e}")
            return ''

    def get_displayed_keywords(self) -> list:
        """获取首页展示的关键词列表"""
        items = self.page.locator(self.LITERATURE_TRANSLATE)
        if items.count() > 0:
            keywords = [items.nth(i).inner_text().strip() for i in range(items.count())]
            self.logger.info(f"首页关键词({len(keywords)}个): {keywords[:5]}...")
            return keywords
        self.logger.warning("未找到关键词标签")
        return []

    # ── 搜索框操作 ────────────────────────────────────────────

    def is_search_box_visible(self) -> bool:
        """搜索框是否可见"""
        try:
            return self.page.locator(self.SEARCH_INPUT).first.is_visible()
        except Exception:
            return False

    def search(self, keyword: str):
        """在首页搜索框输入关键词并触发搜索"""
        self.logger.info(f"首页搜索关键词: {keyword}")
        self.page.locator(self.SEARCH_INPUT).first.fill(keyword)
        # 尝试多种触发方式
        try:
            self.page.locator(self.SEARCH_BUTTON).first.click()
        except Exception:
            self.page.keyboard.press('Enter')


    # ── 文献速递列表 ──────────────────────────────────────────

    def get_literature_count(self) -> int:
        """获取本周文献速递列表条目数"""
        count = self.page.locator(self.LITERATURE_ITEMS).count()
        if count > 0:
            self.logger.info(f"文献速递条目数: {count}")
            return count
        self.logger.warning("未找到文献速递条目")
        return 0

    def get_literature_item_locator(self):
        """返回文献列表的定位器"""
        loc = self.page.locator(self.LITERATURE_ITEMS)
        if loc.count() > 0:
            return loc
        return None

    def get_item_title(self, item_locator, index: int) -> str:
        """获取指定文献的标题"""
        try:
            item = item_locator.nth(index)
            return item.locator(self.ITEM_TITLE).first.inner_text().strip()
        except Exception as e:
            self.logger.warning(f"获取文献[{index}]标题失败: {e}")
            return ''

    def get_item_metadata(self, item_locator, index: int) -> dict:
        """获取指定文献的元数据（作者、期刊、日期）"""
        meta = {'author': '', 'journal': '', 'date': ''}
        try:
            item = item_locator.nth(index)
            meta_text = item.locator(self.ITEM_META_ROW).first.inner_text().strip()
            meta['raw'] = meta_text
            self.logger.info(f"文献[{index}]元数据: {meta_text[:80]}")
        except Exception as e:
            self.logger.warning(f"获取文献[{index}]元数据失败: {e}")
        return meta

    def get_item_ai_analysis(self, item_locator, index: int) -> str:
        """获取指定文献的 AI 解读内容"""
        try:
            item = item_locator.nth(index)
            ai_text = item.locator(self.AI_ANALYSIS).first.inner_text().strip()
            self.logger.info(f"文献[{index}]AI解读长度: {len(ai_text)}")
            return ai_text
        except Exception as e:
            self.logger.warning(f"获取文献[{index}]AI解读失败: {e}")
            return ''

    def click_item_title(self, item_locator, index: int) -> bool:
        """点击指定文献标题，跳转详情页"""
        try:
            item = item_locator.nth(index)
            item.locator(self.ITEM_TITLE).first.click()
            self.logger.info(f"点击文献[{index}]标题")
            return True
        except Exception as e:
            self.logger.error(f"点击文献[{index}]标题失败: {e}")
            return False

    def get_collect_button(self, item_locator, index: int):
        """获取指定文献的收藏按钮定位器（标题行末尾 SVG）"""
        item = item_locator.nth(index)
        btn = item.locator(self.COLLECT_BTN)
        if btn.count() > 0:
            return btn.first
        return None

    def click_collect(self, item_locator, index: int) -> bool:
        """点击收藏按钮"""
        btn = self.get_collect_button(item_locator, index)
        if btn:
            btn.click()
            self.logger.info(f"点击文献[{index}]收藏按钮")
            return True
        self.logger.warning(f"未找到文献[{index}]收藏按钮")
        return False

    def get_collect_state(self, item_locator, index: int) -> str:
        """获取收藏按钮当前状态（取 SVG fill 属性，收藏前后颜色不同）"""
        btn = self.get_collect_button(item_locator, index)
        if btn:
            return btn.evaluate('el => { const svg = el.querySelector("svg"); return svg ? svg.getAttribute("fill") : el.innerHTML; }') or ''
        return ''

    # ── "共X篇"跳转 ──────────────────────────────────────────

    def get_total_count(self) -> int:
        """从"共X篇"按钮文字中提取本期速递总篇数，找不到时返回 0"""
        import re
        try:
            text = self.page.locator(self.TOTAL_COUNT_BTN).first.inner_text().strip()
            match = re.search(r'\d+', text)
            if match:
                count = int(match.group())
                self.logger.info(f"本期速递总篇数（来自按钮文字 '{text}'）: {count}")
                return count
            self.logger.warning(f"共X篇按钮文字无法解析数字: '{text}'")
        except Exception as e:
            self.logger.warning(f"获取本期速递总篇数失败: {e}")
        return 0

    def click_total_count(self) -> bool:
        """点击"共X篇"按钮跳转历史速递"""
        try:
            self.page.locator(self.TOTAL_COUNT_BTN).first.click()
            self.logger.info("点击共X篇按钮")
            return True
        except Exception as e:
            self.logger.error(f"点击共X篇按钮失败: {e}")
            return False
