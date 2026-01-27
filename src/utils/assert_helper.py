
'''
Docstring for utils.assert_helper
断言助手类 - 封装常用断言逻辑
实现断言与测试代码分离，提供更友好的断言失败信息
'''
from utils.logger import Logger

class AssertHelper:
    '''
    断言助手类
    提供各种断言方法，并自动记录日志
    '''

    def __init__(self):
        self.logger = Logger().get_logger()

    def assert_equal(self, actual, expected, message=""):
        '''
        Docstring for assert_equal
        断言相等
        :param self: Description
        :param actual: 实际值
        :param excepted: 期望值
        :param message: 自定义断言失败信息
        '''
        try:
            assert actual == expected, f"断言失败：期望{expected}'，实际{actual}.{message}'"
            self.logger.info(f"✓ 断言通过: {actual} == {expected}")
        except AssertionError as e:
            self.logger.error(f'x {str(e)}')
            raise

    def assert_not_equal(self, actual, expected, message=""):
        '''
        Docstring for assert_not_equal
        断言不相等
        :param self: Description
        :param actual: 实际值
        :param expected: 期望值
        :param message: 自定义断言失败信息
        '''
        try: 
            assert actual != expected,  f"断言失败: 不应该等于 '{expected}', 但实际为 '{actual}'. {message}"
            self.logger.info(f"✓ 断言通过: {actual} != {expected}")
        except AssertionError as e:
            self.logger.error(f"x {str(e)}")
            raise

    def assert_true(self, condition, message = ""):
        '''
        Docstring for assert_true
        断言为真
        :param self: Description
        :param condition: 条件表达式
        :param message: 自定义断言失败信息
        '''
        try:
            assert condition is True,  f"断言失败: 期望为 True, 实际为 {condition}. {message}"
            self.logger.info(f"✓ 断言通过: 条件为 True")
        except AssertionError as e:
            self.logger.error(f"x {str(e)}")
            raise
    
    def assert_false(self, condition, message=""):
        '''
        Docstring for assert_false
        断言为假
        :param self: Description
        :param condition: 条件表达式
        :param message: 自定义断言失败消息
        '''
        try:
            assert condition is False, f"断言失败：期望为False，实际为{condition}.{message}"
            self.logger.info(f"✓ 断言通过: 条件为 False")
        except AssertionError as e:
            self.logger.error(f"x {str(e)}")
       
    def assert_contains(self, text, substring, message=""):
        """
        断言包含子字符串
        Args:
            text: 完整文本
            substring: 子字符串
            message: 自定义断言失败信息
        """
        try:
            assert substring in text, f"断言失败: '{text}' 不包含 '{substring}'. {message}"
            self.logger.info(f"✓ 断言通过: '{text}' 包含 '{substring}'")
        except AssertionError as e:
            self.logger.error(f"✗ {str(e)}")
            raise
    
    def assert_not_empty(self, value, message=""):
        """
        断言非空
        Args:
            value: 要检查的值
            message: 自定义断言失败信息
        """
        try:
            assert value, f"断言失败: 值为空. {message}"
            self.logger.info(f"✓ 断言通过: 值不为空")
        except AssertionError as e:
            self.logger.error(f"✗ {str(e)}")
            raise
