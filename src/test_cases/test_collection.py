# -*- coding: utf-8 -*-
"""
TC-06：我的收藏模块测试
TC-06-01：收藏列表展示已收藏文献
TC-06-02：取消收藏后列表更新
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.collection_page import CollectionPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger

logger = Logger().get_logger()
asserter = AssertHelper()


@allure.feature("TC-06 我的收藏")
class TestCollection:

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_params):
        self.page = browser_context
        self.config = load_config
        self.params = load_params
        self.acc = self.params['accounts']['test001']
        base_url = self.config['base_url']

        self.collection_page = CollectionPage(self.page, base_url)
        self.home_page = HomePage(self.page, base_url)

        login_page = LoginPage(self.page, base_url)
        login_page.goto_login_page()
        login_page.login(self.acc['username'], self.acc['password'])
        self.page.wait_for_timeout(2000)
        self.collection_page.goto_collection_page()

        # ── 前置：收藏列表为空时，先去首页收藏若干篇 ────────────
        self._pre_collected = False
        if self.collection_page.get_collection_count() == 0:
            logger.info("收藏列表为空，前往首页收藏文献")
            self.home_page.goto_home()
            items = self.home_page.get_literature_item_locator()
            if items:
                count = min(3, self.home_page.get_literature_count())
                for i in range(count):
                    self.home_page.click_collect(items, i)
                    self.page.wait_for_timeout(500)
                self._pre_collected = True
                logger.info(f"已收藏首页前 {count} 篇文献")
            self.collection_page.goto_collection_page()

        yield

        # ── 后置：取消前置收藏的文献，恢复空状态 ────────────────
        if self._pre_collected:
            logger.info("后置清理：取消前置收藏的所有文献")
            self.collection_page.goto_collection_page()
            while self.collection_page.get_collection_count() > 0:
                ok = self.collection_page.cancel_collect(0)
                if not ok:
                    break
                self.page.wait_for_timeout(500)
            logger.info("后置清理完成")

    # ────────────────────────────────────────────────────────
    @allure.story("展示")
    @allure.title("TC-06-01：我的收藏页正常展示已收藏文献")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_06_01_collection_list_display(self):
        with allure.step("验证页面正常加载（URL 正确）"):
            url = self.collection_page.get_current_url()
            asserter.assert_true('/login' not in url, f"应进入收藏页，实际: {url}")
            logger.info(f"收藏页 URL: {url}")

        with allure.step("验证收藏列表不为空（至少 1 条）"):
            count = self.collection_page.get_collection_count()
            asserter.assert_true(count >= 1, f"收藏列表应不为空，实际: {count}")
            logger.info(f"收藏数量: {count}")

        with allure.step("验证第 1 条文献标题不为空"):
            title = self.collection_page.get_item_title(0)
            asserter.assert_not_empty(title, "收藏第 1 条标题不应为空")
            logger.info(f"第 1 条收藏: {title[:60]}")

        self.collection_page.take_screenshot("TC-06-01_success")

    # ────────────────────────────────────────────────────────
    @allure.story("取消收藏")
    @allure.title("TC-06-02：取消收藏后文献从列表中消失且总数减一")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_06_02_cancel_collect(self):
        with allure.step("记录当前收藏总数和第 1 条标题"):
            total_before = self.collection_page.get_collection_count()
            if total_before == 0:
                pytest.skip("收藏列表为空，无法执行取消收藏用例")
            first_title = self.collection_page.get_item_title(0)
            asserter.assert_not_empty(first_title, "第 1 条标题应不为空")
            logger.info(f"取消前总数: {total_before}，标题: {first_title[:60]}")

        with allure.step("点击取消收藏"):
            ok = self.collection_page.cancel_collect(0)
            asserter.assert_true(ok, "取消收藏操作应成功")
            self.page.wait_for_timeout(1500)

        with allure.step(f"验证总数变为 {total_before} - 1"):
            total_after = self.collection_page.get_collection_count()
            asserter.assert_equal(total_after, total_before - 1,
                                   f"取消收藏后数量应为 {total_before - 1}")
            logger.info(f"取消后总数: {total_after}")

        with allure.step("验证被取消的文献不再出现在列表中"):
            found = self.collection_page.find_title_in_list(first_title)
            asserter.assert_false(found, f"'{first_title[:40]}' 应已从收藏列表消失")

        self.collection_page.take_screenshot("TC-06-02_success")
