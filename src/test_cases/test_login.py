'''
Docstring for test_cases.test_login
登录功能测试用例
使用数据驱动方式，测试数据与代码分离
'''

import pytest
import allure
from conftest import load_test_data
from pages.login_page import LoginPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger

#初始化工具
logger = Logger().get_logger()
asserter = AssertHelper()

@allure.feature("登录功能")
class TestLogin:
    '''
    Docstring for TestLogin
    登录功能测试类
    '''

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_test_data):
        '''
        Docstring for setup
        测试前置条件
        autouse=True ： 自动执行，无需在测试方法中声明
        :param self: Description
        :param browser_context: Description
        :param load_config: Description
        :param load_test_data: Description
        '''
        self.page = browser_context
        self.config = load_config
        self.test_data = load_test_data("login_data.yaml")
        self.login_page = LoginPage(self.page,self.config['base_url'])

        #每个测试前都打开登录页面
        self.login_page.goto_login_page()

    @allure.story("正向场景")
    @allure.title("测试用例1：使用正确的用户名和密码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_sucess(self):
        '''
        Docstring for test_login_sucess
        测试场景：成功登录
        预期结果：跳转到首页，显示登录成功信息
        :param self: Description
        '''

        #从测试数据中获取用例数据
        test_case = self.test_data['test_login_sucess']
        logger.info(f"执行测试：{test_case['description']}")

        # 执行登录操作
        with allure.step("输入用户名和密码"):
            self.login_page.login(
                test_case['username'],
                test_case['password']
            )
        
        # 断言验证
        with allure.step("断言验证"):
            # 验证URL跳转后页面包含系统名称
            excepted_text = test_case['expected_result']['message']
            asserter.assert_contains(
                self.login_page.get_text_homePage(),
                excepted_text,
                "登录后跳转页面应该提示登录成功"
            )
            # 验证登录状态
            asserter.assert_true(
                self.login_page.is_login_sucessful(),
                "登录应该成功"
            )

    @allure.story("反向场景")
    @allure.title("测试用例2：使用的用户名和密码登录")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_invalid_password(self):
        '''
        Docstring for test_login_invalid_password
        测试场景：使用错误的用户名登录
        预期结果：提示"用户名或密码错误"
        :param self: Description
        '''
        
        #从用例中获取用例数据
        test_case = self.test_data['test_login_invalid_username']
        logger.info(f"执行测试：{test_case['description']}")

        #执行登录操作
        with allure.step("输入用户名和密码"):
            self.login_page.login(
                test_case['username'],
                test_case['password']
            )

        #断言验证
        with allure.step("断言验证"):
            #验证弹出提示词
            expected_text = test_case['expected_result']['message']
            asserter.assert_contains(
                self.login_page.get_error_message(),
                expected_text,
                "账号错误，提示\"该手机号未注册，请注册后登录\""
            )