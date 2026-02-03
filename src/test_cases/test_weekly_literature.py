'''
TC-02: 本周文献速递浏览与查看 - 测试用例
测试本周文献速递功能，包括文献列表展示和详情页面查看
'''
import pytest
from pages.login_page import LoginPage
from pages.weekly_literature_page import WeeklyLiteraturePage
from pages.literature_detail_page import LiteratureDetailPage
from utils.assert_helper import AssertHelper


class TestWeeklyLiterature:
    """
    Docstring for TestWeeklyLiterature
    本周文献速递测试类
    包含TC-02-01和TC-02-02两个测试用例
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config):
        '''
        Docstring for setup
        测试前置条件：登录系统并进入首页
        :param self: Description
        :param browser_context: Playwright page对象
        :param load_config: 配置信息
        '''
        self.page = browser_context
        self.config = load_config
        self.assert_helper = AssertHelper()
        
        # 执行登录操作
        login_page = LoginPage(self.page, self.config['base_url'])
        login_page.goto_login_page()
        
        # 从测试数据中读取用户信息（你可以根据实际情况调整）
        login_page.login("huangqimei", "123456")  # 需要替换为实际密码
        
        # 等待登录成功
        self.page.wait_for_timeout(2000)

    def test_tc_02_01_view_weekly_literature_list(self):
        '''
        Docstring for test_tc_02_01_view_weekly_literature_list
        TC-02-01: 查看本周文献速递列表
        
        测试步骤:
        1. 进入系统首页
        2. 在"本周文献速递"区域查看文献列表
        
        预期结果:
        1. 页面正常显示多篇推荐文献
        2. 每篇文献展示标题、作者、期刊、日期等信息
        :param self: Description
        '''
        print("\n" + "=" * 50)
        print("开始执行测试用例: TC-02-01 查看本周文献速递列表")
        print("=" * 50)
        
        # 初始化页面对象
        weekly_page = WeeklyLiteraturePage(self.page, self.config['base_url'])
        
        # 步骤1: 进入系统首页
        print("\n【步骤1】进入系统首页")
        weekly_page.goto_home_page()
        self.page.wait_for_timeout(2000)
        
        # 步骤2: 验证本周文献速递区域是否显示
        print("\n【步骤2】验证本周文献速递区域是否显示")
        self.assert_helper.assert_true(
            weekly_page.is_weekly_section_visible(),
            "本周文献速递区域未显示"
        )
        
        # 步骤3: 获取文献列表数量
        print("\n【步骤3】获取文献列表数量")
        literature_count = weekly_page.get_literature_count()
        print(f"文献列表中共有 {literature_count} 篇文献")
        
        # 验证文献数量大于0
        self.assert_helper.assert_true(
            literature_count > 0,
            "本周文献速递列表为空，未显示任何文献"
        )
        
        # 步骤4: 验证前3篇文献的基本信息完整性
        print("\n【步骤4】验证文献基本信息完整性")
        check_count = min(3, literature_count)  # 检查前3篇或所有文献
        
        for i in range(check_count):
            print(f"\n检查第 {i+1} 篇文献的信息...")
            
            # 获取文献信息
            literature_info = weekly_page.get_literature_info_by_index(i)
            self.assert_helper.assert_not_empty(
                literature_info,
                f"无法获取第 {i+1} 篇文献信息"
            )
            
            # 记录文献信息
            print(f"  标题: {literature_info['title'][:50] if literature_info['title'] else literature_info['title_cn'][:50]}...")
            print(f"  作者: {literature_info['author']}")
            print(f"  期刊: {literature_info['journal']}")
            print(f"  日期: {literature_info['date']}")
            
            # 验证信息完整性
            verification = weekly_page.verify_literature_has_basic_info(i)
            
            self.assert_helper.assert_true(
                verification['has_title'],
                f"第 {i+1} 篇文献缺少标题信息"
            )
            self.assert_helper.assert_true(
                verification['has_author'],
                f"第 {i+1} 篇文献缺少作者信息"
            )
            self.assert_helper.assert_true(
                verification['has_journal'],
                f"第 {i+1} 篇文献缺少期刊信息"
            )
            self.assert_helper.assert_true(
                verification['has_date'],
                f"第 {i+1} 篇文献缺少日期信息"
            )
            
            print(f"✓ 第 {i+1} 篇文献信息完整")
        
        # 获取并验证总数提示
        total_count = weekly_page.get_total_count_from_text()
        if total_count:
            print(f"\n页面显示文献总数: 共 {total_count} 篇")
            self.assert_helper.assert_true(
                total_count > 0,
                "显示的文献总数应大于0"
            )
        
        print("\n" + "=" * 50)
        print("TC-02-01 测试通过：本周文献速递列表显示正常")
        print("=" * 50)
        
        # 截图保存
        self.page.screenshot(path="reports/screenshots/TC-02-01_success.png")

    def test_tc_02_02_click_literature_and_view_detail(self):
        '''
        Docstring for test_tc_02_02_click_literature_and_view_detail
        TC-02-02: 点击文献标题查看详情
        
        测试步骤:
        1. 在"本周文献速递"列表中点击任意一篇文献标题
        
        预期结果:
        1. 跳转至该文献的详情页面
        2. 页面正常加载文献内容与AI解读
        :param self: Description
        '''
        print("\n" + "=" * 50)
        print("开始执行测试用例: TC-02-02 点击文献标题查看详情")
        print("=" * 50)
        
        # 初始化页面对象
        weekly_page = WeeklyLiteraturePage(self.page, self.config['base_url'])
        detail_page = LiteratureDetailPage(self.page)
        
        # 步骤1: 确认在首页
        print("\n【步骤1】确认在系统首页")
        weekly_page.goto_home_page()
        self.page.wait_for_timeout(2000)
        
        # 确认本周文献速递区域存在
        self.assert_helper.assert_true(
            weekly_page.is_weekly_section_visible(),
            "本周文献速递区域未显示"
        )
        
        # 步骤2: 获取第一篇文献信息（用于后续验证）
        print("\n【步骤2】获取第一篇文献信息")
        literature_info = weekly_page.get_literature_info_by_index(0)
        self.assert_helper.assert_not_empty(
            literature_info,
            "无法获取文献信息"
        )
        
        literature_title = literature_info['title'] or literature_info['title_cn']
        print(f"准备点击文献: {literature_title[:50]}...")
        
        # 步骤3: 点击第一篇文献标题
        print("\n【步骤3】点击文献标题")
        click_success = weekly_page.click_literature_by_index(0)
        self.assert_helper.assert_true(
            click_success,
            "点击文献标题失败"
        )
        print("✓ 成功点击文献标题")
        
        # 等待页面跳转
        self.page.wait_for_timeout(2000)
        
        # 步骤4: 验证是否跳转到详情页面
        print("\n【步骤4】验证页面跳转")
        self.assert_helper.assert_true(
            detail_page.wait_for_page_load(timeout=10000),
            "详情页面加载超时"
        )
        
        self.assert_helper.assert_true(
            detail_page.is_detail_page_loaded(),
            "未成功跳转到文献详情页面"
        )
        print("✓ 成功跳转至文献详情页面")
        
        # 步骤5: 验证详情页面基本信息
        print("\n【步骤5】验证详情页面基本信息")
        
        # 获取详情页面的完整信息
        detail_info = detail_page.get_full_literature_info()
        
        print("\n文献详情信息:")
        print(f"  中文标题: {detail_info['title_cn'][:50] if detail_info['title_cn'] else '无'}...")
        print(f"  英文标题: {detail_info['title_en'][:50] if detail_info['title_en'] else '无'}...")
        print(f"  作者: {detail_info['authors']}")
        print(f"  期刊: {detail_info['journal']}")
        print(f"  发表日期: {detail_info['publish_date']}")
        print(f"  影响因子: {detail_info['impact_factor']}")
        print(f"  被引次数: {detail_info['citation_count']}")
        
        # 验证基本信息完整性
        verification = detail_page.verify_basic_info_complete()
        
        self.assert_helper.assert_true(
            verification['has_title'],
            "详情页面缺少文献标题"
        )
        print("✓ 文献标题显示正常")
        
        self.assert_helper.assert_true(
            verification['has_authors'],
            "详情页面缺少作者信息"
        )
        print("✓ 作者信息显示正常")
        
        self.assert_helper.assert_true(
            verification['has_journal'],
            "详情页面缺少期刊信息"
        )
        print("✓ 期刊信息显示正常")
        
        self.assert_helper.assert_true(
            verification['has_date'],
            "详情页面缺少发表日期"
        )
        print("✓ 发表日期显示正常")
        
        # 步骤6: 验证AI解读内容
        print("\n【步骤6】验证AI解读内容")
        
        has_ai_interpretation = detail_page.has_ai_interpretation()
        if has_ai_interpretation:
            ai_content = detail_info['ai_interpretation']
            print(f"AI解读内容长度: {len(ai_content)} 字符")
            print(f"AI解读预览: {ai_content[:100]}...")
            self.assert_helper.assert_true(
                len(ai_content) > 0,
                "AI解读内容为空"
            )
            print("✓ AI解读内容正常加载")
        else:
            print("⚠ 该文献暂无AI解读内容")
        
        # 步骤7: 检查其他内容元素
        print("\n【步骤7】检查其他内容元素")
        
        if detail_info['has_full_text']:
            print("✓ 包含全文内容")
        
        if detail_info['has_charts']:
            print("✓ 包含图表内容")
        
        if detail_info['has_data']:
            print("✓ 包含数据内容")
        
        print("\n" + "=" * 50)
        print("TC-02-02 测试通过：文献详情页面加载正常")
        print("=" * 50)
        
        # 截图保存
        self.page.screenshot(path="reports/screenshots/TC-02-02_success.png")

    @pytest.mark.parametrize("literature_index", [0, 1, 2])
    def test_tc_02_03_view_multiple_literature_details(self, literature_index):
        '''
        Docstring for test_tc_02_03_view_multiple_literature_details
        TC-02-03: 查看多篇文献详情（参数化测试）
        
        测试步骤:
        1. 在本周文献速递列表中依次点击不同文献
        2. 验证每篇文献详情页面加载正常
        
        :param self: Description
        :param literature_index: 文献索引（0, 1, 2）
        '''
        print("\n" + "=" * 50)
        print(f"开始执行测试用例: TC-02-03 查看第 {literature_index + 1} 篇文献详情")
        print("=" * 50)
        
        weekly_page = WeeklyLiteraturePage(self.page, self.config['base_url'])
        detail_page = LiteratureDetailPage(self.page)
        
        # 确认在首页
        weekly_page.goto_home_page()
        self.page.wait_for_timeout(2000)
        
        # 获取文献总数
        total_count = weekly_page.get_literature_count()
        
        # 如果索引超出范围，跳过测试
        if literature_index >= total_count:
            pytest.skip(f"文献索引 {literature_index} 超出范围（总数: {total_count}）")
        
        # 获取文献信息
        literature_info = weekly_page.get_literature_info_by_index(literature_index)
        title = literature_info['title'] or literature_info['title_cn']
        print(f"目标文献: {title[:50]}...")
        
        # 点击文献
        click_success = weekly_page.click_literature_by_index(literature_index)
        self.assert_helper.assert_true(
            click_success,
            f"点击第 {literature_index + 1} 篇文献失败"
        )
        
        self.page.wait_for_timeout(2000)
        
        # 验证详情页加载
        self.assert_helper.assert_true(
            detail_page.is_detail_page_loaded(),
            f"第 {literature_index + 1} 篇文献详情页未正常加载"
        )
        
        # 验证基本信息
        verification = detail_page.verify_basic_info_complete()
        self.assert_helper.assert_true(
            verification['all_basic_present'],
            f"第 {literature_index + 1} 篇文献详情信息不完整"
        )
        
        print(f"✓ 第 {literature_index + 1} 篇文献详情页加载正常")
        
        # 截图
        self.page.screenshot(
            path=f"reports/screenshots/TC-02-03_{literature_index}_success.png"
        )
        
        # 返回列表页面（为下一次测试做准备）
        self.page.go_back()
        self.page.wait_for_timeout(1000)
        
        print("=" * 50)
        print(f"TC-02-03 测试通过：第 {literature_index + 1} 篇文献验证完成")
        print("=" * 50)