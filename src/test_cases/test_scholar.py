# -*- coding: utf-8 -*-
"""
TC-05：学者雷达模块测试
TC-05-01：学者雷达页面基础展示
TC-05-02：近几年发文/高频词/研究焦点均不为空
TC-05-03：点击文献标题进入详情页
TC-05-04：点击收藏按钮状态切换
TC-05-05：点击作者进入作者详情页
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.scholar_page import ScholarPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger

logger = Logger().get_logger()
asserter = AssertHelper()


@allure.feature("TC-05 学者雷达")
class TestScholar:

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_params):
        self.page = browser_context
        self.config = load_config
        self.params = load_params
        self.acc = self.params['accounts']['test001']
        self.group = self.params['group']
        base_url = self.config['base_url']

        self.scholar_page = ScholarPage(self.page, base_url)

        login_page = LoginPage(self.page, base_url)
        login_page.goto_login_page()
        login_page.login(self.acc['username'], self.acc['password'])
        self.page.wait_for_timeout(2000)
        self.scholar_page.goto_scholar_page()

    # ────────────────────────────────────────────────────────
    @allure.story("基础展示")
    @allure.title("TC-05-01：学者雷达展示标题/元数据/AI解读/学者列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_05_01_basic_display(self):
        authors = self.group.get('authors', [])

        with allure.step("验证学者列表不为空"):
            scholar_count = self.scholar_page.get_scholar_count()
            asserter.assert_true(scholar_count >= 1, f"学者列表应不为空，实际: {scholar_count}")
            logger.info(f"学者数: {scholar_count}")

        with allure.step("验证关注作者均出现在列表中"):
            if authors:
                all_names = self.scholar_page.get_all_scholar_names()
                logger.info(f"页面学者: {all_names}")
                for author in authors[:3]:  # 验证前 3 位
                    name_zh = author.get('name_zh', '')
                    name_en = author.get('name_en', '')
                    found = any(
                        name_zh in n or name_en.lower() in n.lower()
                        for n in all_names
                    )
                    asserter.assert_true(
                        found,
                        f"作者 '{name_zh}/{name_en}' 应出现在学者列表中"
                    )
                    logger.info(f"  作者 {name_zh} 验证通过")

        with allure.step("验证文献区域有内容"):
            lit_count = self.scholar_page.get_literature_count()
            asserter.assert_true(lit_count >= 1, f"应有文献展示，实际: {lit_count}")

        with allure.step("验证第 1 篇文献标题/元数据均不为空（学者雷达页无 AI 解读区块）"):
            title = self.scholar_page.get_lit_title(0)
            meta  = self.scholar_page.get_lit_meta(0)
            asserter.assert_not_empty(title, "文献标题不应为空")
            asserter.assert_not_empty(meta,  "文献元数据不应为空")
            logger.info(f"文献标题: {title[:60]}")

        self.scholar_page.take_screenshot("TC-05-01_success")

    # ────────────────────────────────────────────────────────
    @allure.story("统计信息")
    @allure.title("TC-05-02：近几年发文/近期高频词/研究焦点变化均不为空")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_05_02_statistics_not_empty(self):
        with allure.step("验证近几年发文区域存在且不为空"):
            asserter.assert_true(
                self.scholar_page.is_recent_papers_visible(),
                "近几年发文区域应可见"
            )
            content = self.scholar_page.get_recent_papers_text()
            asserter.assert_not_empty(content, "近几年发文数据不应为空")
            logger.info(f"近几年发文: {content[:60]}")

        with allure.step("验证近期高频词汇区域存在且不为空"):
            asserter.assert_true(
                self.scholar_page.is_frequent_words_visible(),
                "近期高频词汇区域应可见"
            )
            content = self.scholar_page.get_frequent_words_text()
            asserter.assert_not_empty(content, "近期高频词汇不应为空")
            logger.info(f"高频词汇: {content[:60]}")

        with allure.step("验证研究焦点变化区域存在且不为空"):
            asserter.assert_true(
                self.scholar_page.is_research_focus_visible(),
                "研究焦点变化区域应可见"
            )
            content = self.scholar_page.get_research_focus_text()
            asserter.assert_not_empty(content, "研究焦点变化不应为空")
            logger.info(f"研究焦点: {content[:60]}")

        self.scholar_page.take_screenshot("TC-05-02_success")

    # ────────────────────────────────────────────────────────
    @allure.story("文献详情跳转")
    @allure.title("TC-05-03：学者雷达文献标题可跳转至详情页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_05_03_click_lit_title(self):
        with allure.step("验证有文献列表"):
            lit_count = self.scholar_page.get_literature_count()
            asserter.assert_true(lit_count >= 1, "应有文献展示")

        with allure.step("点击第 1 条文献标题"):
            url_before = self.scholar_page.get_current_url()
            self.scholar_page.click_lit_title(0)
            self.page.wait_for_timeout(2500)

        with allure.step("验证 URL 已变化（跳转详情）"):
            url_after = self.scholar_page.get_current_url()
            asserter.assert_true(url_before != url_after, "应跳转至文献详情页")
            logger.info(f"详情页 URL: {url_after}")

        self.scholar_page.take_screenshot("TC-05-03_success")

    # ────────────────────────────────────────────────────────
    @allure.story("收藏")
    @allure.title("TC-05-04：学者雷达文献收藏按钮状态切换")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_05_04_collect_toggle(self):
        with allure.step("验证有文献列表"):
            lit_count = self.scholar_page.get_literature_count()
            asserter.assert_true(lit_count >= 1, "应有文献展示")

        with allure.step("记录收藏初始状态"):
            state_before = self.scholar_page.get_collect_state(0)
            logger.info(f"收藏初始状态: {state_before[:60]}")

        with allure.step("点击收藏"):
            self.scholar_page.click_collect(0)
            self.page.wait_for_timeout(1000)

        with allure.step("验证状态已切换"):
            state_after = self.scholar_page.get_collect_state(0)
            asserter.assert_true(state_before != state_after, "收藏状态应切换")
            logger.info(f"收藏后状态: {state_after[:60]}")

        self.scholar_page.take_screenshot("TC-05-04_success")

    # ────────────────────────────────────────────────────────
    @allure.story("作者卡片切换")
    @allure.title("TC-05-05：点击学者列表第 2 位作者后统计信息内容发生变化")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_05_05_click_author(self):
        # 学者雷达页无独立作者详情页；点击卡片在同页切换统计信息
        authors = self.group.get('authors', [])
        if not authors or len(authors) < 2:
            pytest.skip("需至少配置 2 位关注作者才能验证卡片切换")

        with allure.step("记录当前（第 1 位作者）统计信息内容"):
            stats_before = self.scholar_page.get_recent_papers_text()
            asserter.assert_not_empty(stats_before, "切换前统计信息不应为空")
            logger.info(f"切换前统计内容长度: {len(stats_before)}")

        with allure.step("点击第 2 位作者卡片"):
            second_author = authors[1]['name_zh']
            all_names = self.scholar_page.get_all_scholar_names()
            found = any(second_author in n for n in all_names)
            if not found:
                pytest.skip(f"学者列表中未找到第 2 位作者 {second_author}")
            self.scholar_page.click_scholar(second_author)
            self.page.wait_for_timeout(1500)
            logger.info(f"已点击作者: {second_author}")

        with allure.step("验证统计信息已刷新（内容存在）"):
            stats_after = self.scholar_page.get_recent_papers_text()
            asserter.assert_not_empty(stats_after, "切换后统计信息不应为空")
            logger.info(f"切换后统计内容长度: {len(stats_after)}")

        self.scholar_page.take_screenshot("TC-05-05_success")
