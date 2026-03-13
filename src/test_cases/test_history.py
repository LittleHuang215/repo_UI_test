# -*- coding: utf-8 -*-
"""
TC-04：历史速递模块测试
TC-04-01：历史速递列表关键词与课题组相关
TC-04-02：点击速递卡片跳转详情页
TC-04-03：历史速递文献详情核心字段验证（4.1–4.5，参数化）
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.history_page import HistoryPage
from pages.detail_page import DetailPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger

logger = Logger().get_logger()
asserter = AssertHelper()


@allure.feature("TC-04 历史速递")
class TestHistory:

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_params):
        self.page = browser_context
        self.config = load_config
        self.params = load_params
        self.acc = self.params['accounts']['test001']
        self.group = self.params['group']
        self.common = self.params['common']
        base_url = self.config['base_url']

        self.history_page = HistoryPage(self.page, base_url)
        self.detail_page  = DetailPage(self.page, base_url)

        login_page = LoginPage(self.page, base_url)
        login_page.goto_login_page()
        login_page.login(self.acc['username'], self.acc['password'])
        self.page.wait_for_timeout(2000)

    # ────────────────────────────────────────────────────────
    @allure.story("列表页")
    @allure.title("TC-04-01：历史速递卡片展示的关键词与课题组关键词相近")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_04_01_keywords_match_group(self):
        group_keywords = self.group.get('keywords', {})
        en_keywords = [kw.lower() for kw in group_keywords.get('en', [])]

        with allure.step("进入历史速递页面"):
            self.history_page.goto_history_page()
            self.page.wait_for_timeout(1500)

        with allure.step("获取列表页所有卡片关键词"):
            all_card_keywords = self.history_page.get_all_card_keywords()
            asserter.assert_true(len(all_card_keywords) >= 1, "应有至少 1 个卡片")

        with allure.step("验证关键词不为空且与课题组相关"):
            has_relevant = False
            for i, card_kws in enumerate(all_card_keywords):
                if not card_kws:
                    continue
                for kw in card_kws:
                    if any(gkw in kw.lower() or kw.lower() in gkw for gkw in en_keywords):
                        has_relevant = True
                        logger.info(f"卡片[{i}] 找到相关关键词: {kw}")
                        break
                if has_relevant:
                    break
            asserter.assert_true(has_relevant, "历史速递关键词应与课题组关键词相关")

        self.history_page.take_screenshot("TC-04-01_success")

    # ────────────────────────────────────────────────────────
    @allure.story("列表页")
    @allure.title("TC-04-02：点击历史速递日期卡片跳转至速递详情页")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_04_02_click_card_enter_detail(self):
        with allure.step("进入历史速递页面"):
            self.history_page.goto_history_page()
            self.page.wait_for_timeout(1500)

        with allure.step("验证卡片数 ≥ 1"):
            card_count = self.history_page.get_date_card_count()
            asserter.assert_true(card_count >= 1, f"应至少有 1 个日期卡片，实际: {card_count}")
            logger.info(f"日期卡片数: {card_count}")

        with allure.step("点击第 1 个卡片"):
            ok = self.history_page.click_card_by_index(0)
            asserter.assert_true(ok, "点击卡片应成功")
            self.page.wait_for_timeout(2000)

        with allure.step("验证跳转至 /history/detail"):
            asserter.assert_true(
                self.history_page.is_detail_page_loaded(),
                f"应跳转 /history/detail，实际: {self.page.url}"
            )

        with allure.step("验证面包屑包含'历史速递'"):
            breadcrumbs = self.history_page.get_breadcrumb_texts()
            asserter.assert_true(
                any('历史速递' in b for b in breadcrumbs),
                f"面包屑应含'历史速递'，实际: {breadcrumbs}"
            )

        with allure.step("验证文献条目数 ≥ 1"):
            lit_count = self.history_page.get_literature_count()
            asserter.assert_true(lit_count >= 1, f"详情页应至少有 1 篇文献，实际: {lit_count}")
            logger.info(f"文献数: {lit_count}")

        self.history_page.take_screenshot("TC-04-02_success")
        logger.info("TC-04-02 通过")

    # ────────────────────────────────────────────────────────
    @allure.story("详情页")
    @allure.title("TC-04-03：历史速递文献详情核心字段验证 [篇 {lit_index}]")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("lit_index", [0, 1, 2])
    def test_tc_04_03_detail_core_fields(self, lit_index):
        """
        4.1 中文标题翻译存在
        4.2 元数据非空
        4.3 中英文摘要均不为空
        4.4 问题/方法/实验均不为空
        4.5 PDF/来源按钮存在
        """
        with allure.step("进入历史速递，点击第 1 个卡片"):
            self.history_page.goto_history_page()
            self.page.wait_for_timeout(1500)
            lit_count_on_list = self.history_page.get_date_card_count()
            if lit_count_on_list == 0:
                pytest.skip("无历史速递卡片")
            self.history_page.click_card_by_index(0)
            self.page.wait_for_timeout(2000)

        with allure.step(f"验证文献数 > {lit_index}"):
            detail_count = self.history_page.get_literature_count()
            if detail_count <= lit_index:
                pytest.skip(f"速递文献数({detail_count}) ≤ {lit_index}，跳过")

        with allure.step(f"记录第 {lit_index+1} 篇标题并点击进入详情"):
            list_title = self.history_page.get_literature_title_by_index(lit_index)
            asserter.assert_not_empty(list_title, f"列表第 {lit_index+1} 篇标题不应为空")
            logger.info(f"列表标题[{lit_index}]: {list_title[:60]}")

            ok = self.history_page.click_literature_by_index(lit_index)
            asserter.assert_true(ok, "点击文献标题应成功")
            self.page.wait_for_timeout(2500)

        with allure.step("[4.1] 验证中文标题翻译存在"):
            title_zh = self.detail_page.get_title_zh()
            asserter.assert_not_empty(title_zh, "详情页中文标题不应为空")
            logger.info(f"中文标题: {title_zh[:60]}")

        with allure.step("[4.2] 验证详情页元数据非空"):
            meta = self.detail_page.get_metadata_raw()
            asserter.assert_not_empty(meta, "详情页元数据不应为空")

        with allure.step("[4.3] 验证中英文摘要均不为空"):
            abstract_zh = self.detail_page.get_abstract_zh()
            abstract_en = self.detail_page.get_abstract_en()
            asserter.assert_not_empty(abstract_zh, "中文摘要不应为空")
            asserter.assert_not_empty(abstract_en, "英文摘要不应为空")

        with allure.step("[4.4] 验证问题/方法/实验均不为空"):
            pme = self.detail_page.get_all_pme()
            asserter.assert_not_empty(pme['problem'],    "试图解决什么问题 不应为空")
            asserter.assert_not_empty(pme['method'],     "提出的方法是什么 不应为空")
            asserter.assert_not_empty(pme['experiment'], "做了哪些实验 不应为空")

        with allure.step("[4.5] 验证 PDF/来源按钮存在"):
            asserter.assert_true(self.detail_page.is_pdf_visible(),    "PDF 按钮应存在")
            asserter.assert_true(self.detail_page.is_source_visible(), "来源按钮应存在")

        with allure.step("返回速递详情页"):
            self.page.go_back()
            self.page.wait_for_timeout(1000)

        self.detail_page.take_screenshot(f"TC-04-03_{lit_index}_success")
        logger.info(f"TC-04-03[{lit_index}] 通过")

    # ────────────────────────────────────────────────────────
    # 保留已验证通过的基础用例（兼容旧版 TC-03-XX 逻辑）
    # ────────────────────────────────────────────────────────

    @allure.story("列表页")
    @allure.title("TC-04-BASE-01：历史速递列表页正常加载（≥1 卡片，日期非空）")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tc_04_base_01_list_loads(self):
        with allure.step("进入历史速递页面"):
            self.history_page.goto_history_page()
            self.page.wait_for_timeout(1500)

        with allure.step("验证 URL 含 /history"):
            url = self.history_page.get_current_url()
            asserter.assert_contains(url, '/history', "URL 应包含 /history")

        with allure.step("验证卡片数 ≥ 1"):
            count = self.history_page.get_date_card_count()
            asserter.assert_true(count >= 1, f"应至少有 1 个卡片，实际: {count}")

        with allure.step("验证每个卡片日期非空"):
            dates = self.history_page.get_all_dates()
            for i, d in enumerate(dates):
                asserter.assert_not_empty(d, f"卡片[{i}]日期不应为空")
                logger.info(f"  卡片{i+1} 日期: {d}")

        self.history_page.take_screenshot("TC-04-BASE-01_success")
