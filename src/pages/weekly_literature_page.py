'''
本周文献速递页面对象 - POM模式实现
封装本周文献速递页面的所有元素定位和操作
'''
from pages.base_page import BasePage
from playwright.sync_api import Page


class WeeklyLiteraturePage(BasePage):
    """
    Docstring for WeeklyLiteraturePage
    本周文献速递页面类
    封装本周文献速递页面的所有元素定位和操作
    """

    # 页面元素定位器 - 集中管理，便于维护
    WEEKLY_SECTION_TITLE = 'text=本周文献速递'  # 本周文献速递标题
    LITERATURE_LIST_CONTAINER = '.literature-list'  # 文献列表容器
    LITERATURE_ITEMS = '.literature-item'  # 文献条目
    
    # 文献信息元素
    LITERATURE_TITLE = 'h4, strong'  # 文献标题（英文）
    LITERATURE_TITLE_CN = '.title-cn'  # 文献标题（中文）
    LITERATURE_AUTHOR = 'text=/et al|作者/'  # 作者信息
    LITERATURE_JOURNAL = 'text=/ENVIRONMENTAL|SCIENCE|期刊/'  # 期刊名称
    LITERATURE_DATE = 'text=/2026-|2025-/'  # 发表日期
    IMPACT_FACTOR = 'text=/IF:|Q1/'  # 影响因子
    
    # 总数提示
    TOTAL_COUNT_TEXT = 'text=/共.*篇/'  # 共XX篇
    
    # 关键词标签
    KEYWORD_TAG = 'text=/命中关键词/'  # 命中关键词标签

    def __init__(self, page: Page, base_url):
        '''
        Docstring for __init__
        初始化本周文献速递页面
        :param self: Description
        :param page: Playwright的Page对象
        :param base_url: 基础URL
        '''
        super().__init__(page)
        self.base_url = base_url

    def goto_home_page(self):
        '''
        Docstring for goto_home_page
        进入系统首页
        :param self: Description
        '''
        self.logger.info("打开系统首页")
        self.navigate_to(self.base_url)

    def is_weekly_section_visible(self):
        '''
        Docstring for is_weekly_section_visible
        检查本周文献速递区域是否可见
        :param self: Description
        return: 是否可见
        '''
        self.logger.info("检查本周文献速递区域是否显示")
        return self.is_visible(self.WEEKLY_SECTION_TITLE)

    def get_literature_count(self):
        '''
        Docstring for get_literature_count
        获取文献列表中的文献数量
        :param self: Description
        return: 文献数量
        '''
        self.logger.info("获取文献列表数量")
        items = self.page.locator(self.LITERATURE_ITEMS)
        count = items.count()
        self.logger.info(f"文献列表中共有 {count} 篇文献")
        return count

    def get_total_count_from_text(self):
        '''
        Docstring for get_total_count_from_text
        从页面文本中获取文献总数（如：共 111 篇）
        :param self: Description
        return: 文献总数
        '''
        try:
            import re
            text_element = self.page.locator(self.TOTAL_COUNT_TEXT).first
            text = text_element.inner_text()
            match = re.search(r'共\s*(\d+)\s*篇', text)
            if match:
                total = int(match.group(1))
                self.logger.info(f"页面显示文献总数: 共 {total} 篇")
                return total
        except Exception as e:
            self.logger.warning(f"无法获取文献总数: {str(e)}")
        return None

    def get_literature_info_by_index(self, index=0):
        '''
        Docstring for get_literature_info_by_index
        获取指定索引的文献信息
        :param self: Description
        :param index: 文献索引（从0开始）
        return: 文献信息字典
        '''
        self.logger.info(f"获取第 {index + 1} 篇文献信息")
        
        items = self.page.locator(self.LITERATURE_ITEMS)
        if index >= items.count():
            self.logger.error(f"索引 {index} 超出范围")
            return None
        
        item = items.nth(index)
        
        info = {
            'title': '',
            'title_cn': '',
            'author': '',
            'journal': '',
            'date': '',
            'impact_factor': ''
        }
        
        try:
            # 获取英文标题
            title_locator = item.locator(self.LITERATURE_TITLE).first
            if title_locator.count() > 0:
                info['title'] = title_locator.inner_text()
        except:
            pass
        
        try:
            # 获取中文标题
            title_cn_locator = item.locator(self.LITERATURE_TITLE_CN).first
            if title_cn_locator.count() > 0:
                info['title_cn'] = title_cn_locator.inner_text()
        except:
            pass
        
        try:
            # 获取作者信息
            author_locator = item.locator(self.LITERATURE_AUTHOR).first
            if author_locator.count() > 0:
                info['author'] = author_locator.inner_text()
        except:
            pass
        
        try:
            # 获取期刊信息
            journal_locator = item.locator(self.LITERATURE_JOURNAL).first
            if journal_locator.count() > 0:
                info['journal'] = journal_locator.inner_text()
        except:
            pass
        
        try:
            # 获取日期
            date_locator = item.locator(self.LITERATURE_DATE).first
            if date_locator.count() > 0:
                info['date'] = date_locator.inner_text()
        except:
            pass
        
        try:
            # 获取影响因子
            if_locator = item.locator(self.IMPACT_FACTOR).first
            if if_locator.count() > 0:
                info['impact_factor'] = if_locator.inner_text()
        except:
            pass
        
        self.logger.info(f"文献信息: 标题={info['title'][:50]}...")
        return info

    def click_literature_by_index(self, index=0):
        '''
        Docstring for click_literature_by_index
        点击指定索引的文献标题
        :param self: Description
        :param index: 文献索引（从0开始）
        '''
        self.logger.info(f"点击第 {index + 1} 篇文献")
        
        items = self.page.locator(self.LITERATURE_ITEMS)
        if index >= items.count():
            self.logger.error(f"索引 {index} 超出范围")
            return False
        
        item = items.nth(index)
        title = item.locator(self.LITERATURE_TITLE).first
        
        # 点击标题
        title.click()
        self.logger.info("文献标题已点击")
        return True

    def verify_literature_has_basic_info(self, index=0):
        '''
        Docstring for verify_literature_has_basic_info
        验证指定文献是否包含基本信息
        :param self: Description
        :param index: 文献索引
        return: 验证结果字典
        '''
        info = self.get_literature_info_by_index(index)
        
        if not info:
            return {
                'has_title': False,
                'has_author': False,
                'has_journal': False,
                'has_date': False,
                'all_present': False
            }
        
        result = {
            'has_title': bool(info['title'] or info['title_cn']),
            'has_author': bool(info['author']),
            'has_journal': bool(info['journal']),
            'has_date': bool(info['date']),
        }
        result['all_present'] = all(result.values())
        
        self.logger.info(f"文献信息完整性验证: {result}")
        return result

    def get_all_literature_titles(self):
        '''
        Docstring for get_all_literature_titles
        获取所有文献标题列表
        :param self: Description
        return: 标题列表
        '''
        self.logger.info("获取所有文献标题")
        titles = []
        items = self.page.locator(self.LITERATURE_ITEMS)
        
        for i in range(items.count()):
            item = items.nth(i)
            title_locator = item.locator(self.LITERATURE_TITLE).first
            if title_locator.count() > 0:
                titles.append(title_locator.inner_text())
        
        self.logger.info(f"共获取 {len(titles)} 个标题")
        return titles