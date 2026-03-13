# -*- coding: utf-8 -*-
"""
我的收藏页面对象 - POM 模式实现
封装收藏列表的元素定位与操作
对应测试模块 TC-06
"""
from pages.base_page import BasePage
from playwright.sync_api import Page


class CollectionPage(BasePage):
    """我的收藏页类"""

    # ── 收藏列表（选择器已通过 DOM 探索确认）──────────────────────
    COLLECTION_ITEMS  = '[class*="_item_1ret0"]'          # 每条收藏文献（与首页共用）
    ITEM_TITLE        = '[class*="_title_1ret0"]'          # 文献标题
    ITEM_CANCEL_BTN   = 'span[style*="cursor: pointer"]'  # 取消收藏按钮（bookmark SVG 容器）

    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url
        self.collection_url = f"{base_url}/collections"   # 正确路由（原为 /collect）

    def goto_collection_page(self):
        """直接导航至我的收藏页"""
        self.logger.info("打开我的收藏页面")
        self.navigate_to(self.collection_url)
        self.page.wait_for_load_state('networkidle')

    def click_collection_nav(self):
        """通过导航栏进入我的收藏"""
        self.page.get_by_role("link", name="我的收藏").click()
        self.page.wait_for_load_state('networkidle')

    def get_collection_count(self) -> int:
        """获取收藏列表条目数"""
        count = self.page.locator(self.COLLECTION_ITEMS).count()
        self.logger.info(f"收藏列表共 {count} 条")
        return count

    def get_item_title(self, index: int) -> str:
        """获取第 index 条收藏文献标题"""
        try:
            item = self.page.locator(self.COLLECTION_ITEMS).nth(index)
            return item.locator(self.ITEM_TITLE).first.inner_text().strip()
        except Exception as e:
            self.logger.warning(f"获取收藏[{index}]标题失败: {e}")
            return ''

    def find_title_in_list(self, title: str) -> bool:
        """在收藏列表中查找指定标题"""
        items = self.page.locator(self.COLLECTION_ITEMS)
        for i in range(items.count()):
            try:
                t = items.nth(i).locator(self.ITEM_TITLE).first.inner_text().strip()
                if title in t or t in title:
                    self.logger.info(f"在收藏列表[{i}]找到标题: {t[:60]}")
                    return True
            except Exception:
                continue
        self.logger.warning(f"未在收藏列表中找到标题: {title[:60]}")
        return False

    def cancel_collect(self, index: int) -> bool:
        """取消第 index 条收藏"""
        try:
            item = self.page.locator(self.COLLECTION_ITEMS).nth(index)
            btn = item.locator(self.ITEM_CANCEL_BTN).first
            btn.click()
            self.logger.info(f"取消收藏[{index}]")
            self.page.wait_for_load_state('networkidle')
            return True
        except Exception as e:
            self.logger.error(f"取消收藏[{index}]失败: {e}")
            return False
