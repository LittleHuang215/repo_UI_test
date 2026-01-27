
# conftest.py
"""
Pytest配置文件 - 定义全局fixtures和钩子函数
实现测试环境的初始化、清理和报告生成
"""
import pytest
import yaml
import os
from playwright.sync_api import sync_playwright
from datetime import datetime
from utils.logger import Logger

# 全局配置
CONFIG = None
LOGGER = Logger().get_logger()

def pytest_configure(config):
    """Pytest启动时的配置"""
    # 创建必要的目录
    os.makedirs("reports/screenshots", exist_ok=True)
    os.makedirs("reports/logs", exist_ok=True)
    os.makedirs("reports/html", exist_ok=True)
    
    LOGGER.info("=" * 50)
    LOGGER.info("测试开始执行")
    LOGGER.info("=" * 50)

def pytest_unconfigure(config):
    """Pytest结束时的清理"""
    LOGGER.info("=" * 50)
    LOGGER.info("测试执行完毕")
    LOGGER.info("=" * 50)

@pytest.fixture(scope="session")
def load_config():
    """
    加载配置文件
    scope="session": 整个测试会话只加载一次
    """
    global CONFIG
    if CONFIG is None:
        config_path = "config/config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            CONFIG = yaml.safe_load(f)
        LOGGER.info(f"配置文件已加载: {config_path}")
    return CONFIG

@pytest.fixture(scope="function")
def browser_context(load_config):
    """
    创建浏览器上下文
    scope="function": 每个测试函数都会创建新的浏览器实例
    """
    config = load_config
    
    LOGGER.info("启动浏览器")
    with sync_playwright() as p:
        # 根据配置选择浏览器类型
        browser_type = config['browser']['type']
        if browser_type == 'chromium':
            browser = p.chromium.launch(
                headless=config['headless'],
                slow_mo=config['browser']['slow_mo']
            )
        elif browser_type == 'firefox':
            browser = p.firefox.launch(
                headless=config['headless'],
                slow_mo=config['browser']['slow_mo']
            )
        else:
            browser = p.webkit.launch(
                headless=config['headless'],
                slow_mo=config['browser']['slow_mo']
            )
        
        # 创建上下文
        context = browser.new_context(
            viewport={
                'width': config['browser']['viewport']['width'],
                'height': config['browser']['viewport']['height']
            }
        )
        
        # 创建页面
        page = context.new_page()
        
        yield page
        
        # 测试结束后清理
        LOGGER.info("关闭浏览器")
        context.close()
        browser.close()

@pytest.fixture
def load_test_data():
    """
    加载测试数据的工具函数
    Returns:
        加载测试数据的函数
    """

    def _load_data(file_name: str):
        """
        从YAML文件加载测试数据
        Args:
            file_name: 测试数据文件名
        Returns:
            测试数据字典
        """
        data_path = f"test_data/{file_name}"
        with open(data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        LOGGER.info(f"测试数据已加载: {data_path}")
        return data

    return _load_data

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    获取测试结果，用于失败时截图
    """
    outcome = yield
    report = outcome.get_result()
    
    # 只在测试执行阶段（call）处理
    if report.when == 'call':
        # 测试失败时截图
        if report.failed:
            # 获取browser_context fixture
            if 'browser_context' in item.fixturenames:
                page = item.funcargs['browser_context']
                screenshot_name = f"{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_failed"
                screenshot_path = f"reports/screenshots/{screenshot_name}.png"
                page.screenshot(path=screenshot_path)
                LOGGER.error(f"测试失败截图已保存: {screenshot_path}")