'''
登录页面对象 - POM模式实现
将页面元素和操作封装在一起，提高代码可维护性
'''
from pages.base_page import BasePage
from playwright.sync_api import Page

class LoginPage(BasePage):
    """
    Docstring for LoginPage
    登录页面类
    封装登录页面的所有元素定位和操作
    """

    # 页面元素定位器 - 集中管理，便于维护
    USERNAME_INPUT = '#user_name_input' # 用户名输入框
    PASSWORD_INPUT = '#password_input' # 密码输入框
    LOGIN_BUTTON = '._submitBtn_191sl_225' # 登录按钮
    ERROR_MESSAGE = '._messageContent_co722_98' # 错误提示信息
    SUCCESS_MESSAGE = '._messageContent_co722_98'#提示登录成功信息
    SUCCESS_TITLE = '.font-bold.tracking-tight' # 标题栏的文字是智库


    def __init__(self, page:Page, base_url):
        '''
        Docstring for __init__
        初始化登录页面
        :param self: Description
        :param page: Playwright的Page对象
        :param base_url: 基础URL
        '''
        super().__init__(page)
        self.base_url = base_url
        self.login_url = f"{base_url}/login"

    def goto_login_page(self):
        '''
        Docstring for goto_login_page
        进入登录页面
        :param self: Description
        '''
        self.logger.info("打开登录页面")
        self.navigate_to(self.login_url)
    
    def input_username(self,username):
        '''
        Docstring for input_username
        输入用户名
        :param self: Description
        :param username: 用户名
        '''
        
        self.fill(self.USERNAME_INPUT,username)

    def input_password(self,password):
        '''
        Docstring for input_userpassword
        输入密码
        :param self: Description
        :param password: 密码
        '''
        self.fill(self.PASSWORD_INPUT,password)

    def click_login_button(self):
        '''
        Docstring for click_login_button
        点击登录按钮
        :param self: Description
        '''
        self.click(self.LOGIN_BUTTON)

    def login(self,username,password):
        '''
        Docstring for login
        执行登录操作
        :param self: Description
        :param username: 用户名
        :param password: 密码
        '''
        self.logger.info(f"执行登录操作-用户名：{username}")
        self.input_username(username)
        self.input_password(password)
        self.click_login_button()

    def get_error_message(self):
        '''
        Docstring for get_error_message
        获取错误提示信息
        :param self: Description
        return：错误提示文本
        '''
        return self.get_text(self.ERROR_MESSAGE)
    
    
    def get_text_homePage(self):
        '''
        Docstring for get_success_message
        获取成功提示信息
        :param self: Description
        return：成功信息文本
        '''
        return self.get_text(self.SUCCESS_MESSAGE)
    
    def is_login_sucessful(self):
        '''
        Docstring for is_login_sucessful
        判断是否登录成功
        是否展示首页
        return：是否登录成功
        :param self: Description
        '''
        message = "智库"
        actual_text = self.get_text(self.SUCCESS_TITLE)
        return message in actual_text