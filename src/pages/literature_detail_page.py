'''
文献详情页面对象 - POM模式实现
封装文献详情页面的所有元素定位和操作
'''
from pages.base_page import BasePage
from playwright.sync_api import Page


class LiteratureDetailPage(BasePage):
    """
    Docstring for LiteratureDetailPage
    文献详情页面类
    封装文献详情页面的所有元素定位和操作
    """

    # 页面元素定位器 - 集中管理，便于维护
    # 标题元素
    TITLE_EN = 'h1, h2'  # 英文标题
    TITLE_CN = '.title-cn, .chinese-title'  # 中文标题
    
    # 基本信息元素
    AUTHORS = 'text=/et al|S. Rai/'  # 作者信息
    JOURNAL = 'text=/ENVIRONMENTAL SCIENCE|期刊/'  # 期刊名称
    PUBLISH_DATE = 'text=/2026-01|2025-/'  # 发表日期
    
    # 计量信息
    IMPACT_FACTOR = 'text=/IF:|Q1/'  # 影响因子
    CITATION_COUNT = 'text=/被引|引:/'  # 被引次数
    
    # AI解读
    AI_INTERPRETATION_TITLE = 'text=AI解读'  # AI解读标题
    AI_INTERPRETATION_CONTENT = '.ai-interpretation'  # AI解读内容
    
    # 内容区域
    FULL_TEXT_SECTION = '.full-text-content, .article-content'  # 全文内容
    CHART_SECTION = '.charts-section, .figures'  # 图表
    DATA_SECTION = '.data-section, .supplementary'  # 数据
    
    # 关键词标签
    KEYWORD_TAGS = 'text=/命中关键词/'  # 命中关键词
    
    # 页面加载指示器
    LOADING_INDICATOR = '.loading, .spinner'  # 加载指示器

    def __init__(self, page: Page):
        '''
        Docstring for __init__
        初始化文献详情页面
        :param self: Description
        :param page: Playwright的Page对象
        '''
        super().__init__(page)

    def wait_for_page_load(self, timeout=10000):
        '''
        Docstring for wait_for_page_load
        等待页面加载完成
        :param self: Description
        :param timeout: 超时时间（毫秒）
        return: 是否加载完成
        '''
        self.logger.info("等待文献详情页加载")
        try:
            # 等待英文标题或AI解读标题出现
            self.page.wait_for_selector(
                f"{self.TITLE_EN}, {self.AI_INTERPRETATION_TITLE}",
                timeout=timeout
            )
            self.logger.info("文献详情页加载完成")
            return True
        except Exception as e:
            self.logger.error(f"页面加载超时: {str(e)}")
            return False

    def is_detail_page_loaded(self):
        '''
        Docstring for is_detail_page_loaded
        检查详情页面是否已加载
        :param self: Description
        return: 是否已加载
        '''
        self.logger.info("检查详情页面是否已加载")
        
        # 检查英文标题或AI解读标题是否存在
        title_exists = self.page.locator(self.TITLE_EN).count() > 0
        ai_title_exists = self.page.locator(self.AI_INTERPRETATION_TITLE).count() > 0
        
        is_loaded = title_exists or ai_title_exists
        self.logger.info(f"详情页面加载状态: {is_loaded}")
        return is_loaded

    def get_title_en(self):
        '''
        Docstring for get_title_en
        获取英文标题
        :param self: Description
        return: 英文标题文本
        '''
        try:
            title = self.page.locator(self.TITLE_EN).first.inner_text()
            self.logger.info(f"英文标题: {title[:50]}...")
            return title
        except:
            self.logger.warning("未找到英文标题")
            return ""

    def get_title_cn(self):
        '''
        Docstring for get_title_cn
        获取中文标题
        :param self: Description
        return: 中文标题文本
        '''
        try:
            title = self.page.locator(self.TITLE_CN).first.inner_text()
            self.logger.info(f"中文标题: {title[:50]}...")
            return title
        except:
            self.logger.warning("未找到中文标题")
            return ""

    def get_authors(self):
        '''
        Docstring for get_authors
        获取作者信息
        :param self: Description
        return: 作者文本
        '''
        try:
            authors = self.page.locator(self.AUTHORS).first.inner_text()
            self.logger.info(f"作者: {authors}")
            return authors
        except:
            self.logger.warning("未找到作者信息")
            return ""

    def get_journal(self):
        '''
        Docstring for get_journal
        获取期刊名称
        :param self: Description
        return: 期刊名称
        '''
        try:
            journal = self.page.locator(self.JOURNAL).first.inner_text()
            self.logger.info(f"期刊: {journal}")
            return journal
        except:
            self.logger.warning("未找到期刊信息")
            return ""

    def get_publish_date(self):
        '''
        Docstring for get_publish_date
        获取发表日期
        :param self: Description
        return: 发表日期
        '''
        try:
            date = self.page.locator(self.PUBLISH_DATE).first.inner_text()
            self.logger.info(f"发表日期: {date}")
            return date
        except:
            self.logger.warning("未找到发表日期")
            return ""

    def get_impact_factor(self):
        '''
        Docstring for get_impact_factor
        获取影响因子
        :param self: Description
        return: 影响因子文本
        '''
        try:
            if_text = self.page.locator(self.IMPACT_FACTOR).first.inner_text()
            self.logger.info(f"影响因子: {if_text}")
            return if_text
        except:
            self.logger.warning("未找到影响因子")
            return ""

    def get_citation_count(self):
        '''
        Docstring for get_citation_count
        获取被引次数
        :param self: Description
        return: 被引次数文本
        '''
        try:
            citation = self.page.locator(self.CITATION_COUNT).first.inner_text()
            self.logger.info(f"被引次数: {citation}")
            return citation
        except:
            self.logger.warning("未找到被引次数")
            return ""

    def get_ai_interpretation(self):
        '''
        Docstring for get_ai_interpretation
        获取AI解读内容
        :param self: Description
        return: AI解读文本
        '''
        try:
            ai_content = self.page.locator(self.AI_INTERPRETATION_CONTENT).first.inner_text()
            self.logger.info(f"AI解读内容长度: {len(ai_content)} 字符")
            return ai_content
        except:
            self.logger.warning("未找到AI解读内容")
            return ""

    def has_ai_interpretation(self):
        '''
        Docstring for has_ai_interpretation
        检查是否存在AI解读
        :param self: Description
        return: 是否存在AI解读
        '''
        has_ai = self.page.locator(self.AI_INTERPRETATION_TITLE).count() > 0
        self.logger.info(f"AI解读存在: {has_ai}")
        return has_ai

    def has_full_text(self):
        '''
        Docstring for has_full_text
        检查是否存在全文内容
        :param self: Description
        return: 是否存在全文
        '''
        has_text = self.page.locator(self.FULL_TEXT_SECTION).count() > 0
        self.logger.info(f"全文内容存在: {has_text}")
        return has_text

    def has_charts(self):
        '''
        Docstring for has_charts
        检查是否存在图表
        :param self: Description
        return: 是否存在图表
        '''
        has_chart = self.page.locator(self.CHART_SECTION).count() > 0
        self.logger.info(f"图表存在: {has_chart}")
        return has_chart

    def has_data(self):
        '''
        Docstring for has_data
        检查是否存在数据部分
        :param self: Description
        return: 是否存在数据
        '''
        has_data_section = self.page.locator(self.DATA_SECTION).count() > 0
        self.logger.info(f"数据部分存在: {has_data_section}")
        return has_data_section

    def verify_basic_info_complete(self):
        '''
        Docstring for verify_basic_info_complete
        验证基本信息是否完整
        :param self: Description
        return: 验证结果字典
        '''
        self.logger.info("开始验证基本信息完整性")
        
        result = {
            'has_title': bool(self.get_title_en() or self.get_title_cn()),
            'has_authors': bool(self.get_authors()),
            'has_journal': bool(self.get_journal()),
            'has_date': bool(self.get_publish_date()),
            'has_impact_factor': bool(self.get_impact_factor()),
            'has_citation_count': bool(self.get_citation_count()),
            'has_ai_interpretation': self.has_ai_interpretation()
        }
        
        result['all_basic_present'] = all([
            result['has_title'],
            result['has_authors'],
            result['has_journal'],
            result['has_date']
        ])
        
        self.logger.info(f"基本信息验证结果: {result}")
        return result

    def get_full_literature_info(self):
        '''
        Docstring for get_full_literature_info
        获取完整的文献信息
        :param self: Description
        return: 包含所有文献信息的字典
        '''
        self.logger.info("获取完整文献信息")
        
        info = {
            'title_cn': self.get_title_cn(),
            'title_en': self.get_title_en(),
            'authors': self.get_authors(),
            'journal': self.get_journal(),
            'publish_date': self.get_publish_date(),
            'impact_factor': self.get_impact_factor(),
            'citation_count': self.get_citation_count(),
            'ai_interpretation': self.get_ai_interpretation(),
            'has_full_text': self.has_full_text(),
            'has_charts': self.has_charts(),
            'has_data': self.has_data()
        }
        
        return info