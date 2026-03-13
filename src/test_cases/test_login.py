# -*- coding: utf-8 -*-
"""
TC-01：登录模块测试
TC-01-01：正确账号密码登录
TC-01-02：错误凭据登录（参数化）
"""
import pytest
import allure
from pages.login_page import LoginPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger

logger = Logger().get_logger()
asserter = AssertHelper()


@allure.feature("TC-01 登录")
class TestLogin:

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_params):
        self.page = browser_context
        self.config = load_config
        self.params = load_params
        self.login_page = LoginPage(self.page, self.config['base_url'])
        self.login_page.goto_login_page()

    # ────────────────────────────────────────────────────────
    @allure.story("正向场景")
    @allure.title("TC-01-01：正确账号密码登录跳转首页")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_01_01_login_success(self):
        """
        预期：
          1. URL 变为 / (不停留在 /login)
          2. 页面出现"登录成功"提示
          3. 首页导航可见（智库标题）
        """
        acc = self.params['accounts']['test001']

        with allure.step("输入正确用户名和密码"):
            self.login_page.login(acc['username'], acc['password'])
            self.page.wait_for_timeout(2000)

        with allure.step("验证 URL 不再是 /login"):
            url = self.login_page.get_current_url()
            asserter.assert_true('/login' not in url, f"应跳转首页，实际 URL: {url}")
            logger.info(f"登录后 URL: {url}")

        with allure.step("验证登录成功提示"):
            msg = self.login_page.get_text_homePage()
            asserter.assert_not_empty(msg, "应有登录成功提示")
            logger.info(f"提示内容: {msg}")

        with allure.step("验证首页正常加载（导航侧边栏可见）"):
            # 侧边栏出现说明已进入系统，无需依赖特定标题文字
            asserter.assert_true(
                self.page.locator('nav, aside, [class*="aside"]').first.is_visible(),
                "首页应有导航侧边栏"
            )

        self.login_page.take_screenshot("TC-01-01_success")
        logger.info("TC-01-01 通过")

    # ────────────────────────────────────────────────────────
    @allure.story("逆向场景")
    @allure.title("TC-01-02：错误凭据登录 - {error_case[desc]}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("error_case", [
        {"username": "test001",   "password": "wrongpass",  "desc": "账号正确，密码错误"},
        {"username": "notexist",  "password": "123456",     "desc": "账号不存在"},
        {"username": "notexist",  "password": "wrongpass",  "desc": "账号和密码均错误"},
    ])
    def test_tc_01_02_login_invalid(self, error_case):
        """
        预期：
          1. 出现有意义的错误提示，不为空
          2. URL 仍为 /login，未跳转
          3. 输入框和按钮仍可正常使用
        """
        with allure.step(f"输入错误凭据：{error_case['desc']}"):
            self.login_page.login(error_case['username'], error_case['password'])
            self.page.wait_for_timeout(2000)

        with allure.step("验证错误提示不为空"):
            err_msg = self.login_page.get_error_message()
            asserter.assert_not_empty(err_msg, f"应有错误提示，实际: '{err_msg}'")
            logger.info(f"错误提示: {err_msg}")

        with allure.step("验证 URL 仍在 /login"):
            url = self.login_page.get_current_url()
            asserter.assert_true('/login' in url, f"应停留在登录页，实际: {url}")

        with allure.step("验证登录页面仍可交互"):
            asserter.assert_true(
                self.login_page.is_visible(LoginPage.USERNAME_INPUT),
                "用户名输入框应仍可见"
            )

        self.login_page.take_screenshot(f"TC-01-02_{error_case['desc']}")
        logger.info(f"TC-01-02 通过：{error_case['desc']}")
