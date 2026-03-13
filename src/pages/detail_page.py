# -*- coding: utf-8 -*-
"""
文献详情页面对象 - POM 模式实现
URL：/article
供 TC-02-05/06/07/08/09、TC-04-03、TC-05-03 等多个模块复用
选择器均已通过实际 DOM 探索确认
"""
from pages.base_page import BasePage
from playwright.sync_api import Page


class DetailPage(BasePage):
    """文献详情页类 (/article)"""

    # ── 标题区域 ──────────────────────────────────────────────
    TITLE_EN = '[class*="_en_"]'      # 英文原标题
    TITLE_ZH = '[class*="_zh_"]'      # 中文翻译标题

    # ── 元数据区域 ────────────────────────────────────────────
    META_CONTAINER = '[class*="_contentContainer_"]'  # 整体元数据区
    JOURNAL_NAME   = '[class*="_journalName_"]'        # 期刊名称
    KEYWORDS       = '[class*="_keyWordContainer_"]'   # 关键词区域

    # ── Tab 导航 ─────────────────────────────────────────────
    TAB_ABSTRACT = 'text=文献摘要'          # 文献摘要 tab
    TAB_PME      = 'text=问题·方法·实验'   # 问题·方法·实验 tab

    # ── 文献摘要 tab 内容 ─────────────────────────────────────
    ABSTRACT_ZH = '[class*="_backgroundZh_"]'   # 中文摘要
    ABSTRACT_EN = '[class*="_backgroundEn_"]'   # 英文摘要

    # ── 问题·方法·实验 tab 内容 ──────────────────────────────
    # 有内容时每个 section 内存在 .markdown-content，无内容时只有标题和分隔线
    PME_SECTIONS = '.markdown-content'
    # 系统渲染的题目标签（用于从 section 全文中剥除，判断答案是否为空）
    PME_LABEL_PROBLEM    = '文献试图解决什么问题？'
    PME_LABEL_METHOD     = '文献提出的方法是什么？'
    PME_LABEL_EXPERIMENT = '文献做了哪些实验？'

    # ── 操作按钮（_overViewButton_1au7n_68 为每个按钮的容器）────
    BTN_PDF     = '._overViewButton_1au7n_68:has-text("PDF")'
    BTN_SOURCE  = '._overViewButton_1au7n_68:has-text("来源")'
    BTN_DOI     = '._overViewButton_1au7n_68:has-text("DOI")'
    BTN_COLLECT = '._overViewButton_1au7n_68:has-text("收藏")'
    BTN_CITE    = '._overViewButton_1au7n_68:has-text("引用")'

    # ── 引用弹窗 ─────────────────────────────────────────────
    CITE_MODAL        = '.arco-modal, [class*="citeModal"]'
    CITE_CONTENT      = '[class*="citeContent"], [class*="citationText"]'
    CITE_DOWNLOAD_BTN = 'button:has-text("下载")'
    CITE_COPY_BTN     = 'button:has-text("复制")'
    CITE_FORMAT_RIS   = 'button:has-text("RIS")'
    CITE_TOAST        = ':has-text("引用已复制")'

    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url

    def is_detail_page(self) -> bool:
        """是否在文献详情页（URL 包含 /article）"""
        return '/article' in self.page.url

    # ── 标题 ─────────────────────────────────────────────────

    def get_title_zh(self) -> str:
        """获取中文标题翻译"""
        try:
            loc = self.page.locator(self.TITLE_ZH).first
            text = loc.inner_text().strip()
            self.logger.info(f"中文标题: {text[:60]}")
            return text
        except Exception as e:
            self.logger.warning(f"获取中文标题失败: {e}")
            return ''

    def get_title_en(self) -> str:
        """获取英文原标题"""
        try:
            return self.page.locator(self.TITLE_EN).first.inner_text().strip()
        except Exception:
            return ''

    # ── 元数据 ───────────────────────────────────────────────

    def get_metadata_raw(self) -> str:
        """获取元数据区域的原始文本"""
        try:
            text = self.page.locator(self.META_CONTAINER).first.inner_text().strip()
            self.logger.info(f"元数据: {text[:80]}")
            return text
        except Exception as e:
            self.logger.warning(f"获取元数据失败: {e}")
            return ''

    def get_journal(self) -> str:
        """获取期刊名称"""
        try:
            return self.page.locator(self.JOURNAL_NAME).first.inner_text().strip()
        except Exception:
            return ''

    # ── Tab 切换 ─────────────────────────────────────────────

    def _switch_to_abstract_tab(self):
        """切换到文献摘要 tab"""
        try:
            self.page.locator(self.TAB_ABSTRACT).first.click()
            self.page.wait_for_timeout(800)
        except Exception:
            pass  # 默认已在文献摘要 tab

    def _switch_to_pme_tab(self):
        """切换到问题·方法·实验 tab"""
        self.page.locator(self.TAB_PME).first.click()
        self.page.wait_for_timeout(1000)
        self.logger.info("切换到问题·方法·实验 tab")

    # ── 摘要 ─────────────────────────────────────────────────

    def get_abstract_zh(self) -> str:
        """获取中文摘要（文献摘要 tab）"""
        try:
            # 文献摘要 tab 为默认激活，直接读取
            text = self.page.locator(self.ABSTRACT_ZH).first.inner_text().strip()
            self.logger.info(f"中文摘要长度: {len(text)}")
            return text
        except Exception:
            # 若不可见，先切换 tab
            self._switch_to_abstract_tab()
            try:
                return self.page.locator(self.ABSTRACT_ZH).first.inner_text().strip()
            except Exception as e:
                self.logger.warning(f"获取中文摘要失败: {e}")
                return ''

    def get_abstract_en(self) -> str:
        """获取英文摘要（文献摘要 tab）"""
        try:
            text = self.page.locator(self.ABSTRACT_EN).first.inner_text().strip()
            self.logger.info(f"英文摘要长度: {len(text)}")
            return text
        except Exception:
            self._switch_to_abstract_tab()
            try:
                return self.page.locator(self.ABSTRACT_EN).first.inner_text().strip()
            except Exception as e:
                self.logger.warning(f"获取英文摘要失败: {e}")
                return ''

    # ── 问题·方法·实验 ──────────────────────────────────────

    def _get_pme_sections(self) -> list:
        """切换到问题·方法·实验 tab，等待内容渲染后返回三个 section 的内容"""
        self._switch_to_pme_tab()
        sections = self.page.locator(self.PME_SECTIONS)
        # 等待至少一个 section 出现（最多 5 秒），避免内容还未渲染就读取
        try:
            sections.first.wait_for(state='attached', timeout=5000)
        except Exception:
            self.logger.warning("PME section 等待超时，可能内容未加载")
        texts = []
        for i in range(sections.count()):
            try:
                texts.append(sections.nth(i).inner_text().strip())
            except Exception:
                texts.append('')
        self.logger.info(f"问题·方法·实验共 {len(texts)} 个 section")
        return texts

    def get_problem(self) -> str:
        """获取"试图解决什么问题"内容（第 1 个 section）"""
        sections = self._get_pme_sections()
        text = sections[0] if sections else ''
        self.logger.info(f"问题 section 长度: {len(text)}")
        return text

    def get_method(self) -> str:
        """获取"提出的方法是什么"内容（第 2 个 section）"""
        sections = self._get_pme_sections()
        text = sections[1] if len(sections) > 1 else ''
        self.logger.info(f"方法 section 长度: {len(text)}")
        return text

    def get_experiment(self) -> str:
        """获取"做了哪些实验"内容（第 3 个 section）"""
        sections = self._get_pme_sections()
        text = sections[2] if len(sections) > 2 else ''
        self.logger.info(f"实验 section 长度: {len(text)}")
        return text

    def _extract_pme_answer(self, section_text: str, label: str) -> str:
        """从 section 全文中剥除题目标签，返回纯回答内容。
        若系统仅输出了题目而无回答（数据未处理），则返回空字符串。"""
        text = section_text.strip()
        if text.startswith(label):
            text = text[len(label):].strip()
        return text

    def get_all_pme(self) -> dict:
        """一次性获取问题/方法/实验三项（剥除题目标签后的纯回答内容）。
        系统未处理数据时，对应字段返回空字符串。"""
        sections = self._get_pme_sections()
        raw_problem    = sections[0] if len(sections) > 0 else ''
        raw_method     = sections[1] if len(sections) > 1 else ''
        raw_experiment = sections[2] if len(sections) > 2 else ''
        return {
            'problem':    self._extract_pme_answer(raw_problem,    self.PME_LABEL_PROBLEM),
            'method':     self._extract_pme_answer(raw_method,     self.PME_LABEL_METHOD),
            'experiment': self._extract_pme_answer(raw_experiment, self.PME_LABEL_EXPERIMENT),
        }

    # ── 操作按钮 ─────────────────────────────────────────────

    def is_pdf_visible(self) -> bool:
        return self.page.locator(self.BTN_PDF).count() > 0

    def is_source_visible(self) -> bool:
        return self.page.locator(self.BTN_SOURCE).count() > 0

    def is_doi_visible(self) -> bool:
        return self.page.locator(self.BTN_DOI).count() > 0

    def click_pdf(self):
        self.page.locator(self.BTN_PDF).first.click()
        self.logger.info("点击 PDF 按钮")

    def click_source(self):
        self.page.locator(self.BTN_SOURCE).first.click()
        self.logger.info("点击来源按钮")

    def click_doi(self):
        self.page.locator(self.BTN_DOI).first.click()
        self.logger.info("点击 DOI 按钮")

    def click_collect(self):
        self.page.locator(self.BTN_COLLECT).first.click()
        self.logger.info("点击收藏按钮")

    def get_collect_state(self) -> str:
        try:
            return self.page.locator(self.BTN_COLLECT).first.get_attribute('class') or ''
        except Exception:
            return ''

    # ── 引用功能 ─────────────────────────────────────────────

    def click_cite(self):
        self.page.locator(self.BTN_CITE).first.click()
        self.logger.info("点击引用按钮")

    def is_cite_modal_visible(self) -> bool:
        try:
            return self.page.locator(self.CITE_MODAL).first.is_visible()
        except Exception:
            return False

    def get_cite_content(self) -> str:
        try:
            return self.page.locator(self.CITE_CONTENT).first.inner_text().strip()
        except Exception:
            return ''

    def click_cite_download(self):
        self.page.locator(self.CITE_DOWNLOAD_BTN).first.click()

    def click_cite_copy(self):
        self.page.locator(self.CITE_COPY_BTN).first.click()

    def is_copy_toast_visible(self) -> bool:
        try:
            return self.page.locator(self.CITE_TOAST).first.is_visible()
        except Exception:
            return False

    def select_ris_format(self):
        self.page.locator(self.CITE_FORMAT_RIS).first.click()
