# -*- coding: utf-8 -*-
"""
TC-02：首页模块测试
TC-02-01：课题组信息与账号配置一致
TC-02-02：首页搜索框跳转
TC-02-03：本周文献速递内容完整性
TC-02-04：收藏按钮状态切换
TC-02-05：点击速递标题进入详情（5.1–5.4）
TC-02-10：共X篇跳转最新历史速递
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.detail_page import DetailPage
from pages.history_page import HistoryPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger

logger = Logger().get_logger()
asserter = AssertHelper()


@allure.feature("TC-02 首页")
class TestHome:

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_params):
        self.page = browser_context
        self.config = load_config
        self.params = load_params
        self.acc = self.params['accounts']['test001']
        self.group = self.params['group']
        self.common = self.params['common']
        base_url = self.config['base_url']

        self.home_page = HomePage(self.page, base_url)
        self.detail_page = DetailPage(self.page, base_url)
        self.history_page = HistoryPage(self.page, base_url)

        # 登录 → 进入首页
        login_page = LoginPage(self.page, base_url)
        login_page.goto_login_page()
        login_page.login(self.acc['username'], self.acc['password'])
        self.page.wait_for_timeout(2000)
        self.home_page.goto_home()

    # ────────────────────────────────────────────────────────
    @allure.story("课题组信息")
    @allure.title("TC-02-01：首页课题组名称与关键词与账号配置一致")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_02_01_group_info_match(self):
        with allure.step("读取首页课题组名称"):
            name = self.home_page.get_group_name()
            asserter.assert_not_empty(name, "首页课题组名称不应为空")
            logger.info(f"课题组名称: {name}")

        with allure.step("与账号配置期望值比对"):
            expected = self.acc.get('display_name', '')
            if expected:
                asserter.assert_contains(name, expected.split('大学')[0],
                                         f"课题组名称应包含 '{expected}'")

        with allure.step("验证首页关键词列表非空"):
            keywords = self.home_page.get_displayed_keywords()
            asserter.assert_true(len(keywords) >= 1, "首页应展示至少 1 个关键词")
            logger.info(f"首页关键词数量: {len(keywords)}")

        self.home_page.take_screenshot("TC-02-01_success")

    # ────────────────────────────────────────────────────────
    @allure.story("搜索框")
    @allure.title("TC-02-02：首页搜索框输入关键词后跳转搜索页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_02_02_search_box_jump(self):
        keyword = self.group.get('search_box_keyword', 'Water treatment')

        with allure.step("验证搜索框存在且可交互"):
            asserter.assert_true(
                self.home_page.is_search_box_visible(),
                "首页搜索框应可见"
            )

        with allure.step(f"输入关键词: {keyword}"):
            self.home_page.search(keyword)
            self.page.wait_for_timeout(2000)

        with allure.step("验证 URL 已变化（跳转至搜索页）"):
            url = self.home_page.get_current_url()
            asserter.assert_true(
                url != self.config['base_url'] and '/login' not in url,
                f"应跳转搜索页，实际 URL: {url}"
            )
            logger.info(f"跳转后 URL: {url}")

        self.home_page.take_screenshot("TC-02-02_success")

    # ────────────────────────────────────────────────────────
    @allure.story("文献速递列表")
    @allure.title("TC-02-03：本周速递文献标题/元数据/AI解读均不为空")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_02_03_literature_list_complete(self):
        expected_count = self.common.get('literature_count', 5)

        with allure.step("定位文献速递区域"):
            self.home_page.goto_home()
            self.page.wait_for_timeout(1500)
            items = self.home_page.get_literature_item_locator()
            asserter.assert_true(items is not None, "应能定位文献速递列表")

        with allure.step(f"验证条目数 = {expected_count}"):
            count = self.home_page.get_literature_count()
            asserter.assert_equal(count, expected_count,
                                   f"速递条目数应为 {expected_count}")
            logger.info(f"速递条目数: {count}")

        with allure.step("逐篇验证标题/元数据/AI解读"):
            items = self.home_page.get_literature_item_locator()
            for i in range(count):
                title = self.home_page.get_item_title(items, i)
                asserter.assert_not_empty(title, f"第 {i+1} 篇标题不应为空")

                meta = self.home_page.get_item_metadata(items, i)
                asserter.assert_not_empty(meta.get('raw', ''), f"第 {i+1} 篇元数据不应为空")

                ai = self.home_page.get_item_ai_analysis(items, i)
                asserter.assert_not_empty(ai, f"第 {i+1} 篇 AI 解读不应为空")

                logger.info(f"  [{i+1}] 标题={title[:40]}, AI长度={len(ai)}")

        self.home_page.take_screenshot("TC-02-03_success")

    # ────────────────────────────────────────────────────────
    @allure.story("收藏")
    @allure.title("TC-02-04：点击收藏按钮系统不报错且图标状态切换")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_02_04_collect_toggle(self):
        with allure.step("定位第 1 篇收藏按钮并记录初始状态"):
            self.home_page.goto_home()
            self.page.wait_for_timeout(1500)
            items = self.home_page.get_literature_item_locator()
            asserter.assert_true(items is not None, "应能定位文献列表")
            state_before = self.home_page.get_collect_state(items, 0)
            logger.info(f"收藏初始状态: {state_before[:60]}")

        with allure.step("点击收藏按钮"):
            ok = self.home_page.click_collect(items, 0)
            asserter.assert_true(ok, "点击收藏按钮应成功")
            self.page.wait_for_timeout(1000)

        with allure.step("验证图标状态已切换"):
            state_after = self.home_page.get_collect_state(items, 0)
            asserter.assert_true(
                state_before != state_after,
                "收藏按钮状态应改变"
            )
            logger.info(f"收藏切换后状态: {state_after[:60]}")

        with allure.step("再次点击还原（取消收藏）"):
            self.home_page.click_collect(items, 0)
            self.page.wait_for_timeout(800)

        self.home_page.take_screenshot("TC-02-04_success")

    # ────────────────────────────────────────────────────────
    @allure.story("文献详情")
    @allure.title("TC-02-05：点击速递标题进详情并验证核心字段 [篇 {lit_index}]")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("lit_index", [0, 1, 2, 3, 4])
    def test_tc_02_05_click_title_to_detail(self, lit_index):
        """
        5.1 中文标题翻译存在
        5.2 元数据与列表一致
        5.3 摘要中英文均不为空
        5.4 问题/方法/实验均不为空
        """
        with allure.step(f"记录第 {lit_index+1} 篇标题和元数据"):
            self.home_page.goto_home()
            self.page.wait_for_timeout(1500)
            items = self.home_page.get_literature_item_locator()
            list_title = self.home_page.get_item_title(items, lit_index)
            list_meta  = self.home_page.get_item_metadata(items, lit_index)
            asserter.assert_not_empty(list_title, "列表标题不应为空")
            logger.info(f"列表标题[{lit_index}]: {list_title[:60]}")

        with allure.step("点击标题进入详情页"):
            ok = self.home_page.click_item_title(items, lit_index)
            asserter.assert_true(ok, "点击标题应成功")
            self.page.wait_for_timeout(2500)

        with allure.step("[5.1] 验证中文标题翻译存在"):
            title_zh = self.detail_page.get_title_zh()
            asserter.assert_not_empty(title_zh, "详情页中文标题不应为空")
            logger.info(f"中文标题: {title_zh[:60]}")

        with allure.step("[5.2] 验证详情页元数据非空"):
            detail_meta = self.detail_page.get_metadata_raw()
            asserter.assert_not_empty(detail_meta, "详情页元数据不应为空")

        with allure.step("[5.3] 验证中英文摘要均不为空"):
            abstract_zh = self.detail_page.get_abstract_zh()
            abstract_en = self.detail_page.get_abstract_en()
            asserter.assert_not_empty(abstract_zh, "中文摘要不应为空")
            asserter.assert_not_empty(abstract_en, "英文摘要不应为空")
            logger.info(f"摘要 ZH 长度={len(abstract_zh)}, EN 长度={len(abstract_en)}")

        with allure.step("[5.4] 验证问题/方法/实验均不为空"):
            pme = self.detail_page.get_all_pme()
            # 账号与课题组信息（系统未处理数据时，失败消息中携带定位信息）
            acc_info = (
                f"账号={self.acc['username']} | "
                f"课题组={self.acc.get('display_name', self.acc.get('group', ''))}"
            )
            asserter.assert_not_empty(
                pme['problem'],
                f"[{acc_info}] 「文献试图解决什么问题？」答案为空，系统可能未完成数据处理"
            )
            asserter.assert_not_empty(
                pme['method'],
                f"[{acc_info}] 「文献提出的方法是什么？」答案为空，系统可能未完成数据处理"
            )
            asserter.assert_not_empty(
                pme['experiment'],
                f"[{acc_info}] 「文献做了哪些实验？」答案为空，系统可能未完成数据处理"
            )

        with allure.step("返回首页"):
            self.page.go_back()
            self.page.wait_for_timeout(1000)

        self.detail_page.take_screenshot(f"TC-02-05_{lit_index}_success")
        logger.info(f"TC-02-05[{lit_index}] 通过")

    # ────────────────────────────────────────────────────────
    @allure.story("历史速递跳转")
    @allure.title("TC-02-10：点击共X篇跳转与历史速递最新一期一致")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_02_10_total_link_to_latest_history(self):
        with allure.step("访问历史速递页，记录最新一期名称"):
            self.history_page.goto_history_page()
            latest_name = self.history_page.get_latest_history_name()
            asserter.assert_not_empty(latest_name, "历史速递最新期名称不应为空")
            logger.info(f"最新历史速递名称: {latest_name}")

        with allure.step("返回首页，点击共X篇按钮"):
            self.home_page.goto_home()
            self.page.wait_for_timeout(1500)
            ok = self.home_page.click_total_count()
            asserter.assert_true(ok, "点击共X篇按钮应成功")
            self.page.wait_for_timeout(2000)

        with allure.step("验证跳转到速递详情页"):
            asserter.assert_true(
                self.history_page.is_detail_page_loaded(),
                f"应跳转 /history/detail，实际 URL: {self.page.url}"
            )

        with allure.step("验证当前速递名称与最新一期一致"):
            current_name = self.history_page.get_current_history_name()
            logger.info(f"跳转后速递名称: {current_name}")
            asserter.assert_not_empty(current_name, "当前速递名称不应为空")
            # 名称可能包含日期子串，做包含判断
            asserter.assert_true(
                latest_name in current_name or current_name in latest_name,
                f"速递名称应一致，历史最新='{latest_name}'，当前='{current_name}'"
            )

        self.home_page.take_screenshot("TC-02-10_success")
        logger.info("TC-02-10 通过")
