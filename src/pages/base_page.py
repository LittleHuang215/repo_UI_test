'''
Docstring for pages.base_page
基础页面类 - 封装所有页面的公共操作
采用POM模式，所有页面类都继承此类
'''


from playwright.sync_api import Page,expect
from utils.logger import Logger

class BasePage:
    '''
    Docstring for BasePage
    基础页面类
    提供页面操作的通用方法，避免重复代码
    '''
    def __init__(self,page:Page):
        '''
        Docstring for __init__
        初始化页面对象
        :param self: Description
        :param page: Playwright的Page对象
        :type page: Page
        '''
        self.page = page
        self.logger = Logger().get_logger()
    
    def navigate_to(self,url):
        '''
        Docstring for navigate_to
        导航到指定url
        :param self: Description
        :param url: 目标网址
        '''
        self.logger.info(f"导航到网页：{url}")
        self.page.goto(url)

    def click(self,selector):
        '''
        Docstring for click
        点击元素
        :param self: Description
        :param selector: 元素选择器
        '''
        self.logger.info(f"点击元素：{selector}")
        self.page.click(selector)
    
    def fill(self,selector,text):
        '''
        Docstring for fill
        填充到输入框
        :param self: Description
        :param selector: 元素选择器
        :param text: 要填充的文本
        '''
        self.logger.info(f"在{selector}中输入：{text}")
        self.page.fill(selector,text)

    def get_text(self,selector):
        '''
        Docstring for get_text
        获取元素文本
        :param self: Description
        :param selector: 元素选择器
        return：元素的文本内容
        '''
        text =  self.page.locator(selector).inner_text()
        self.logger.info(f"获取元素{selector}的文本：{text}")
        return text
    
    def is_visible(self,selector):
        '''
        Docstring for is_visible
        检查元素是否可见
        :param self: Description
        :param selector: 元素选择器
        return：元素是否可见
        '''
        visible = self.page.locator(selector).is_visible()
        self.logger.info(f"元素{selector}可见性：{visible}")
        return visible
    
    def wait_for_url(self,url_pattern,timeout = 3000):
        '''
        Docstring for wait_for_url
        等待URL包含指定内容
        :param self: Description
        :param url_pattern: url匹配模式
        :param timeout: 超时时间
        '''
        self.logger.info(f"等待URL包含：{url_pattern}")
        self.page.wait_for_url(f"**{url_pattern}**",timeout=timeout)
    
    def get_current_url(self):
        '''
        Docstring for get_current_url
        获取当前的url
        :param self: Description
        return：当前url
        '''
        url = self.page.url
        self.logger.info(f"当前页面的URL：{url}")
        return url
    
    def take_screenshot(self,name):
        '''
        Docstring for take_screenshot
        截图保存
        :param self: Description
        :param name: 保存的文件名
        '''
        path = f"reports/screenshots/{name}.png"
        self.page.screenshot(path=path)
        self.logger.info(f"截图已保存：{path}")