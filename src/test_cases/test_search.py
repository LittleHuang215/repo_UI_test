# -*- coding: utf-8 -*-
"""
TC-03：AI 检索模块测试
TC-03-01：进入 AI 检索页初始状态
TC-03-02：DOI 关键字检索
TC-03-03：课题组相关关键词检索（参数化）
TC-03-04：课题组无关关键词检索
TC-03-05：筛选条件逐项验证（参数化）
TC-03-06：排序按钮切换列表顺序
TC-03-07：点击检索结果标题进入详情
TC-03-08：检索结果收藏文献
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger

logger = Logger().get_logger()
asserter = AssertHelper()


@allure.feature("TC-03 AI 检索")
class TestSearch:

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_params):
        self.page = browser_context
        self.config = load_config
        self.params = load_params
        self.acc = self.params['accounts']['test001']
        self.group = self.params['group']
        self.common = self.params['common']
        base_url = self.config['base_url']

        self.search_page = SearchPage(self.page, base_url)

        login_page = LoginPage(self.page, base_url)
        login_page.goto_login_page()
        login_page.login(self.acc['username'], self.acc['password'])
        self.page.wait_for_timeout(2000)

    # ────────────────────────────────────────────────────────
    @allure.story("初始状态")
    @allure.title("TC-03-01：进入 AI 检索页初始提示正确")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_03_01_initial_state(self):
        with allure.step("点击导航进入 AI 检索页"):
            self.search_page.goto_search_page()

        with allure.step("验证初始提示文字可见"):
            asserter.assert_true(
                self.search_page.is_initial_prompt_visible(),
                "应显示'开始您的文献检索'"
            )
            logger.info("初始提示验证通过")

        with allure.step("验证搜索框存在且为空"):
            asserter.assert_true(
                self.search_page.is_search_input_empty(),
                "搜索框初始应为空"
            )

        with allure.step("验证结果区域为空"):
            count = self.search_page.get_result_count()
            asserter.assert_true(count == 0, f"初始应无检索结果，实际: {count}")

        self.search_page.take_screenshot("TC-03-01_success")

    # ────────────────────────────────────────────────────────
    @allure.story("检索")
    @allure.title("TC-03-02：DOI 检索返回结果各字段不为空")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_03_02_doi_search(self):
        """使用课题组动态 DOI 检索（运行时从系统取值）"""
        # 若未配置固定 DOI，使用关键词代替
        doi = self.group.get('doi', '')
        if not doi:
            pytest.skip("huazhong.doi 未配置，跳过 DOI 检索用例（待运行时动态获取）")

        with allure.step("进入 AI 检索页并输入 DOI"):
            self.search_page.goto_search_page()
            self.search_page.search(doi)
            self.page.wait_for_timeout(3000)

        with allure.step("验证第 1 条标题不为空"):
            title = self.search_page.get_result_title(0)
            asserter.assert_not_empty(title, "DOI 检索第 1 条标题不应为空")

        with allure.step("验证元数据不为空"):
            meta = self.search_page.get_result_meta(0)
            asserter.assert_not_empty(meta, "元数据不应为空")

        with allure.step("验证 AI 解读不为空"):
            ai = self.search_page.get_result_ai(0)
            asserter.assert_not_empty(ai, "AI 解读不应为空")

        self.search_page.take_screenshot("TC-03-02_success")

    # ────────────────────────────────────────────────────────
    @allure.story("检索")
    @allure.title("TC-03-03：课题组相关关键词检索有结果且字段完整 [{keyword}]")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("keyword", [
        "Single-atom catalysts",
        "Emerging contaminants",
        "Fenton-like catalytic oxidation",
    ])
    def test_tc_03_03_related_keyword_search(self, keyword):
        check_n = self.common.get('search_result_check', 3)

        with allure.step(f"输入课题组相关关键词: {keyword}"):
            self.search_page.goto_search_page()
            self.search_page.search(keyword)
            self.page.wait_for_timeout(3000)

        with allure.step("验证结果数 ≥ 1"):
            count = self.search_page.get_result_count()
            asserter.assert_true(count >= 1, f"相关词检索应有结果，实际: {count}")
            logger.info(f"关键词[{keyword}]检索结果数: {count}")

        with allure.step(f"验证前 {check_n} 条各字段完整"):
            check = min(check_n, count)
            for i in range(check):
                title    = self.search_page.get_result_title(i)
                title_zh = self.search_page.get_result_title_zh(i)
                meta     = self.search_page.get_result_meta(i)
                ai       = self.search_page.get_result_ai(i)
                asserter.assert_not_empty(title,    f"[{i}] 标题不应为空")
                asserter.assert_not_empty(title_zh, f"[{i}] 标题翻译不应为空")
                asserter.assert_not_empty(meta,     f"[{i}] 元数据不应为空")
                asserter.assert_not_empty(ai,       f"[{i}] AI解读不应为空")
                logger.info(f"  [{i}] 标题={title[:40]}")

        self.search_page.take_screenshot(f"TC-03-03_{keyword[:20]}_success")

    # ────────────────────────────────────────────────────────
    @allure.story("检索")
    @allure.title("TC-03-04：无关关键词检索显示空结果 [{keyword}]")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("keyword", ["古代诗词", "中国古典建筑"])
    def test_tc_03_04_unrelated_keyword_search(self, keyword):
        with allure.step(f"输入无关关键词: {keyword}"):
            self.search_page.goto_search_page()
            self.search_page.search(keyword)
            self.page.wait_for_timeout(3000)

        with allure.step("验证无报错（页面正常渲染）"):
            url = self.search_page.get_current_url()
            asserter.assert_true('/login' not in url, "应不跳转到登录页")

        with allure.step("验证结果为空或结果数为 0"):
            count = self.search_page.get_result_count()
            asserter.assert_true(count == 0, f"无关词应无结果，实际: {count}")
            logger.info(f"无关词[{keyword}]结果数: {count}")

        self.search_page.take_screenshot(f"TC-03-04_{keyword}_success")

    # ────────────────────────────────────────────────────────
    @allure.story("筛选")
    @allure.title("TC-03-05：筛选条件 [{filter_name}] 可正确过滤结果")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("filter_name", ["发表年份", "影响因子", "期刊质量", "作者", "机构"])
    def test_tc_03_05_filter_items(self, filter_name):
        with allure.step("先检索获得初始结果"):
            self.search_page.goto_search_page()
            self.search_page.search("Emerging contaminants")
            self.page.wait_for_timeout(3000)
            total_before = self.search_page.get_result_count()
            asserter.assert_true(total_before >= 1, "筛选前应有结果")
            logger.info(f"筛选前结果数: {total_before}")

        with allure.step(f"选择筛选条件: {filter_name}"):
            self.search_page.click_filter_item(filter_name)
            self.page.wait_for_timeout(2000)

        with allure.step("验证筛选后结果数 ≤ 筛选前且 ≥ 0"):
            total_after = self.search_page.get_result_count()
            asserter.assert_true(
                0 <= total_after <= total_before,
                f"筛选后结果数({total_after})应 ≤ 筛选前({total_before})"
            )
            logger.info(f"筛选[{filter_name}]后结果数: {total_after}")

        self.search_page.take_screenshot(f"TC-03-05_{filter_name}_success")

    # ────────────────────────────────────────────────────────
    @allure.story("排序")
    @allure.title("TC-03-06：点击排序按钮后结果列表顺序改变")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_03_06_sort_toggle(self):
        with allure.step("先检索获得有结果的列表"):
            self.search_page.goto_search_page()
            self.search_page.search("Advanced oxidation processes")
            self.page.wait_for_timeout(3000)
            count = self.search_page.get_result_count()
            if count < 2:
                pytest.skip("结果数 < 2，无法验证排序变化")

        with allure.step("记录排序前第 1 条标题"):
            first_title_before = self.search_page.get_result_title(0)
            logger.info(f"排序前第 1 条: {first_title_before[:60]}")

        with allure.step("点击排序按钮"):
            self.search_page.click_sort()
            self.page.wait_for_timeout(2000)

        with allure.step("验证第 1 条标题已变化"):
            first_title_after = self.search_page.get_result_title(0)
            logger.info(f"排序后第 1 条: {first_title_after[:60]}")
            asserter.assert_true(
                first_title_before != first_title_after,
                "排序切换后第 1 条标题应改变"
            )

        self.search_page.take_screenshot("TC-03-06_success")

    # ────────────────────────────────────────────────────────
    @allure.story("详情跳转")
    @allure.title("TC-03-07：点击检索结果标题跳转详情页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_03_07_click_result_title(self):
        with allure.step("检索关键词获取结果"):
            self.search_page.goto_search_page()
            self.search_page.search("Single-atom catalysts")
            self.page.wait_for_timeout(3000)
            count = self.search_page.get_result_count()
            asserter.assert_true(count >= 1, "应有检索结果")

        with allure.step("点击第 1 条标题"):
            url_before = self.search_page.get_current_url()
            self.search_page.click_result_title(0)
            self.page.wait_for_timeout(2500)

        with allure.step("验证跳转至详情页"):
            url_after = self.search_page.get_current_url()
            asserter.assert_true(url_before != url_after, "URL 应已变化")
            logger.info(f"详情页 URL: {url_after}")

        self.search_page.take_screenshot("TC-03-07_success")

    # ────────────────────────────────────────────────────────
    @allure.story("收藏")
    @allure.title("TC-03-08：点击检索结果收藏按钮图标状态切换")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc_03_08_collect_result(self):
        with allure.step("检索关键词获取结果"):
            self.search_page.goto_search_page()
            self.search_page.search("Emerging contaminants")
            self.page.wait_for_timeout(3000)
            count = self.search_page.get_result_count()
            asserter.assert_true(count >= 1, "应有检索结果")

        with allure.step("记录第 1 条收藏初始状态"):
            state_before = self.search_page.get_collect_state(0)
            logger.info(f"收藏初始状态: {state_before[:60]}")

        with allure.step("点击收藏按钮"):
            self.search_page.click_collect(0)
            self.page.wait_for_timeout(1000)

        with allure.step("验证收藏状态已切换"):
            state_after = self.search_page.get_collect_state(0)
            asserter.assert_true(
                state_before != state_after,
                "收藏状态应切换"
            )
            logger.info(f"收藏后状态: {state_after[:60]}")

        self.search_page.take_screenshot("TC-03-08_success")
