# -*- coding: utf-8 -*-
"""
历史速递页面对象 - POM 模式实现
封装 /history 列表页与 /history/detail 详情页的所有元素定位和操作
对应测试模块 TC-04
"""
from pages.base_page import BasePage
from playwright.sync_api import Page


class HistoryPage(BasePage):
    """历史速递页面类"""

    # ── 列表页元素 ────────────────────────────────────────────
    DATE_CARDS    = '._card_9ksjr_12'          # 每一个日期卡片
    DATE_LABEL    = '._date_9ksjr_45'          # 卡片上的日期文字
    CARD_TITLE    = '._title_9ksjr_32'         # 卡片标题（"本周速递"）
    CARD_CONTENT  = '._cardContent_9ksjr_27'   # 卡片内容区域（包含关键词预览）

    # ── 详情页元素 ────────────────────────────────────────────
    BREADCRUMB_ITEMS  = '.arco-breadcrumb-item'        # 面包屑导航
    LITERATURE_ITEMS  = '[class*="itemSplit"]'          # 文献条目
    KEYWORD_PILLS     = '[class*="pill"]'               # 关键词标签
    ITEM_SUBTITLE     = '[class*="_subtitleLarge_"]'    # 列表页标题翻译（中文副标题）
    ITEM_AI_BOX       = '[class*="_highlightBox_"]'     # 列表页 AI 解读容器

    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url
        self.history_url = f"{base_url}/history"

    def goto_history_page(self):
        """导航至历史速递列表页"""
        self.logger.info("打开历史速递页面")
        self.navigate_to(self.history_url)
        self.page.wait_for_load_state('networkidle')

    # ── 列表页操作 ────────────────────────────────────────────

    def get_date_card_count(self) -> int:
        """获取日期卡片总数"""
        count = self.page.locator(self.DATE_CARDS).count()
        self.logger.info(f"历史速递共 {count} 个日期卡片")
        return count

    def get_all_dates(self) -> list:
        """获取所有日期卡片的日期文字列表"""
        labels = self.page.locator(self.DATE_LABEL)
        dates = [labels.nth(i).inner_text().strip() for i in range(labels.count())]
        self.logger.info(f"日期列表: {dates}")
        return dates

    def get_card_info_by_index(self, index: int = 0) -> dict:
        """获取指定索引卡片的 date / title / content_preview"""
        cards = self.page.locator(self.DATE_CARDS)
        if index >= cards.count():
            self.logger.error(f"卡片索引 {index} 超出范围")
            return {}
        card = cards.nth(index)
        info = {'date': '', 'title': '', 'content_preview': ''}
        try:
            info['date'] = card.locator(self.DATE_LABEL).inner_text().strip()
        except Exception:
            pass
        try:
            info['title'] = card.locator(self.CARD_TITLE).inner_text().strip()
        except Exception:
            pass
        try:
            info['content_preview'] = card.locator(self.CARD_CONTENT).inner_text().strip()[:100]
        except Exception:
            pass
        self.logger.info(f"卡片[{index}]: {info}")
        return info

    def get_all_card_keywords(self) -> list:
        """
        获取列表页所有卡片的关键词列表（用于 TC-04-01 相关性验证）
        返回：[卡片0的关键词列表, 卡片1的关键词列表, ...]
        """
        cards = self.page.locator(self.DATE_CARDS)
        all_keywords = []
        for i in range(cards.count()):
            card = cards.nth(index=i)
            try:
                content = card.locator(self.CARD_CONTENT).inner_text().strip()
                # 关键词通常以空格、逗号、换行分隔
                words = [w.strip() for w in content.replace(',', '\n').split('\n') if w.strip()]
                all_keywords.append(words)
            except Exception:
                all_keywords.append([])
        self.logger.info(f"列表页关键词（共 {len(all_keywords)} 卡片）")
        return all_keywords

    def click_card_by_index(self, index: int = 0) -> bool:
        """点击指定索引卡片，跳转详情页"""
        cards = self.page.locator(self.DATE_CARDS)
        if index >= cards.count():
            self.logger.error(f"卡片索引 {index} 超出范围，共 {cards.count()} 个")
            return False
        cards.nth(index).click()
        self.logger.info(f"点击第 {index + 1} 个日期卡片")
        return True

    # ── 详情页操作 ────────────────────────────────────────────

    def is_detail_page_loaded(self) -> bool:
        """是否成功进入速递详情页"""
        return '/history/detail' in self.page.url

    def get_breadcrumb_texts(self) -> list:
        """获取面包屑导航文字列表"""
        items = self.page.locator(self.BREADCRUMB_ITEMS)
        texts = [items.nth(i).inner_text().strip() for i in range(items.count())]
        self.logger.info(f"面包屑: {texts}")
        return texts

    def get_literature_count(self) -> int:
        """获取详情页文献条目数，等待列表渲染后再计数"""
        self.logger.info(f"当前页面 URL: {self.page.url}")
        try:
            self.page.wait_for_selector(self.LITERATURE_ITEMS, timeout=8000)
        except Exception:
            self.logger.warning(f"等待文献列表超时，选择器: {self.LITERATURE_ITEMS}")
        count = self.page.locator(self.LITERATURE_ITEMS).count()
        self.logger.info(f"详情页文献数: {count}")
        return count

    def get_literature_info_by_index(self, index: int = 0) -> dict:
        """获取详情页指定文献的信息（标题文本、关键词列表）"""
        items = self.page.locator(self.LITERATURE_ITEMS)
        if index >= items.count():
            return {}
        item = items.nth(index)
        info = {'keywords': [], 'text_preview': ''}
        try:
            pills = item.locator(self.KEYWORD_PILLS)
            info['keywords'] = [pills.nth(i).inner_text().strip() for i in range(pills.count())]
        except Exception:
            pass
        try:
            info['text_preview'] = item.inner_text().strip()[:150]
        except Exception:
            pass
        self.logger.info(f"文献[{index}]: keywords={info['keywords'][:3]}")
        return info

    def get_literature_title_by_index(self, index: int = 0) -> str:
        """获取详情页指定文献的英文标题（模糊匹配，兼容 CSS Module 哈希）"""
        items = self.page.locator(self.LITERATURE_ITEMS)
        if index >= items.count():
            return ''
        try:
            item = items.nth(index)
            loc = item.locator('[class*="_title_"]').first
            if loc.count() > 0:
                return loc.inner_text().strip()
        except Exception:
            pass
        return ''

    def get_inspect_indices(self, total: int) -> list:
        """根据总篇数返回需巡检的文献索引列表。
        规则：前5篇（本周必读）全部 + 其余随机5篇；总数≤5时全部巡检。
        """
        import random
        if total <= 5:
            indices = list(range(total))
        else:
            must_read = list(range(5))
            other = list(range(5, total))
            random_other = sorted(random.sample(other, min(5, len(other))))
            indices = must_read + random_other
        self.logger.info(f"巡检索引列表（共{len(indices)}篇）: {indices}")
        return indices

    def _scroll_item_into_view(self, index: int) -> bool:
        """将指定索引的文献条目滚动到可视区域（触发懒加载渲染）"""
        try:
            self.page.locator(self.LITERATURE_ITEMS).nth(index).scroll_into_view_if_needed(timeout=3000)
            self.page.wait_for_timeout(300)  # 等待懒加载内容渲染
            return True
        except Exception as e:
            self.logger.warning(f"滚动到文献[{index}]失败: {e}")
            return False

    def get_item_subtitle_by_index(self, index: int) -> str:
        """获取列表页指定文献的标题翻译（中文副标题）"""
        items = self.page.locator(self.LITERATURE_ITEMS)
        if index >= items.count():
            return ''
        try:
            self._scroll_item_into_view(index)
            text = items.nth(index).locator(self.ITEM_SUBTITLE).first.inner_text().strip()
            self.logger.info(f"文献[{index}]标题翻译: {text[:40]}")
            return text
        except Exception:
            return ''

    def get_item_ai_review_by_index(self, index: int) -> str:
        """获取列表页指定文献的 AI 解读内容（去掉"[AI解读]："前缀）"""
        items = self.page.locator(self.LITERATURE_ITEMS)
        if index >= items.count():
            return ''
        try:
            # 列表页读取前已由 get_item_subtitle_by_index 滚动过，此处直接读取
            full_text = items.nth(index).locator(self.ITEM_AI_BOX).first.inner_text().strip()
            prefix = '[AI解读]：'
            if full_text.startswith(prefix):
                full_text = full_text[len(prefix):].strip()
            self.logger.info(f"文献[{index}]AI解读长度: {len(full_text)}")
            return full_text
        except Exception:
            return ''

    def click_literature_by_index(self, index: int = 0) -> bool:
        """点击详情页指定文献标题"""
        # 若条目尚未渲染（go_back 后可能需要重新等待），则先等待
        items = self.page.locator(self.LITERATURE_ITEMS)
        if items.count() == 0:
            try:
                self.page.wait_for_selector(self.LITERATURE_ITEMS, timeout=8000)
            except Exception:
                self.logger.warning(f"等待文献列表渲染超时，选择器: {self.LITERATURE_ITEMS}")
        items = self.page.locator(self.LITERATURE_ITEMS)
        if index >= items.count():
            self.logger.error(f"文献索引 {index} 超出范围，共 {items.count()} 篇")
            return False
        try:
            item = items.nth(index)
            title_loc = item.locator('[class*="_title_"]').first
            if title_loc.count() > 0 and title_loc.is_visible():
                title_loc.click()
                self.logger.info(f"点击速递文献[{index}]标题")
                return True
        except Exception as e:
            self.logger.error(f"点击速递文献[{index}]失败: {e}")
        return False

    def get_latest_history_name(self) -> str:
        """获取历史速递列表中最新一期的名称（日期）"""
        dates = self.get_all_dates()
        name = dates[0] if dates else ''
        self.logger.info(f"最新一期速递名称: {name}")
        return name

    def get_current_history_name(self) -> str:
        """获取当前详情页的速递名称（从面包屑或页面标题提取）"""
        try:
            breadcrumbs = self.get_breadcrumb_texts()
            # 面包屑最后一项通常是当前页名称
            return breadcrumbs[-1] if breadcrumbs else ''
        except Exception:
            return ''

    def get_detail_page_date(self) -> str:
        """从详情页顶部标题「文献速递 · YYYY-MM-DD」中提取日期"""
        try:
            self.logger.info(f"当前页面 URL: {self.page.url}")
            self.page.wait_for_selector('div.font-medium:has-text("文献速递")', timeout=8000)
            text = self.page.locator('div.font-medium:has-text("文献速递")').first.inner_text().strip()
            # 格式：文献速递 · 2026-02-08
            if ' · ' in text:
                date = text.split(' · ', 1)[1].strip()
                self.logger.info(f"详情页顶部日期: {date}")
                return date
        except Exception as e:
            self.logger.warning(f"获取详情页顶部日期失败: {e}")
        return ''
