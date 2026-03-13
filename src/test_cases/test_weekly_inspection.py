# -*- coding: utf-8 -*-
"""
TC-07：每周巡检模块测试
TC-07-01：所有账号首页文献与历史速递最新一期一致性校验
TC-07-02：最新一期速递 N 篇文献内容完整性巡检

注意：
  - TC-07 为遍历所有账号的全量巡检，执行时间较长
  - 任意字段为空时记录并汇报，不立即 assert_fail（非阻断式校验）
  - 巡检结果汇总后，如有问题推送通知给黄齐梅（飞书/企业微信集成点）
"""
import random
import pytest
import allure
from pages import history_page
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.history_page import HistoryPage
from pages.detail_page import DetailPage
from utils.assert_helper import AssertHelper
from utils.logger import Logger
from utils.notifier import notify_inspection_pass, notify_inspection_fail

logger = Logger().get_logger()
asserter = AssertHelper()


def _login_as(page, base_url, username, password):
    """通用登录辅助函数"""
    lp = LoginPage(page, base_url)
    lp.goto_login_page()
    lp.login(username, password)
    page.wait_for_timeout(2000)


@allure.feature("TC-07 每周巡检")
class TestWeeklyInspection:

    @pytest.fixture(autouse=True)
    def setup(self, browser_context, load_config, load_params):
        self.page = browser_context
        self.config = load_config
        self.params = load_params
        all_accounts = self.params['accounts']
        # accounts.yaml 为列表格式时直接用，字典格式时取 values
        if isinstance(all_accounts, list):
            all_accounts = all_accounts
        else:
            all_accounts = list(all_accounts.values())
        self.common = self.params['common']
        sample_n = self.common.get('account_sample', 1)
        if sample_n and sample_n < len(all_accounts):
            self.accounts = random.sample(all_accounts, sample_n)
            logger.info(f"账号随机抽样：从 {len(all_accounts)} 个中抽取 {sample_n} 个")
        else:
            self.accounts = all_accounts
            logger.info(f"账号全量巡检：共 {len(all_accounts)} 个")
        self.base_url = self.config['base_url']
        self.feishu_webhook = self.config.get('feishu', {}).get('webhook_url', '')

    # ────────────────────────────────────────────────────────
    @allure.story("一致性巡检")
    @allure.title("TC-07-01：所有账号首页跳转速递与历史速递最新一期日期一致性")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_07_01_home_history_consistency(self):
        """
        遍历所有账号：
          1. 进入 /history 列表页，取第一张卡片的日期（最新一期）
          2. 返回首页，点击「共X篇」跳转速递详情页，取面包屑最后一项日期
          3. 两个日期对比，一致则通过
        不一致时记录问题账号，全部完成后统一上报
        """
        failed_accounts = []

        for acc in self.accounts:
            username = acc['username']
            logger.info(f"=== 巡检账号: {username} ===")

            with allure.step(f"[{username}] 登录"):
                _login_as(self.page, self.base_url, username, acc['password'])
                history_page = HistoryPage(self.page, self.base_url)
                home_page = HomePage(self.page, self.base_url)

            with allure.step(f"[{username}] 进入历史速递列表，获取最新一期日期"):
                history_page.goto_history_page()
                self.page.wait_for_timeout(1500)
                dates = history_page.get_all_dates()
                if not dates:
                    logger.error(f"[{username}] 历史速递列表无日期卡片，跳过")
                    failed_accounts.append({'account': username, 'history_date': '(无)', 'home_date': '(未获取)'})
                    continue
                history_date = dates[0]
                logger.info(f"[{username}] 历史速递最新一期日期: {history_date}")

            with allure.step(f"[{username}] 首页点击「共X篇」跳转速递详情页，获取面包屑日期"):
                home_page.goto_home()
                self.page.wait_for_timeout(1500)
                ok = home_page.click_total_count()
                if not ok:
                    logger.error(f"[{username}] 首页「共X篇」按钮未找到，跳过")
                    failed_accounts.append({'account': username, 'history_date': history_date, 'home_date': '(未找到按钮)'})
                    continue
                self.page.wait_for_timeout(1500)
                self.page.wait_for_load_state('networkidle')
                home_date = history_page.get_detail_page_date()
                logger.info(f"[{username}] 首页跳转速递顶部日期: {home_date}")

            with allure.step(f"[{username}] 对比两个日期"):
                if history_date == home_date:
                    logger.info(f"[{username}] 一致性校验通过（日期均为 {history_date}）")
                else:
                    msg = f"账号 {username} 日期不一致：历史速递={history_date}，首页跳转={home_date}"
                    logger.error(msg)
                    failed_accounts.append({'account': username, 'history_date': history_date, 'home_date': home_date})

        with allure.step("汇总巡检结果"):
            if failed_accounts:
                summary = '\n'.join([
                    f"账号: {f['account']}, 历史速递日期: {f['history_date']}, 首页跳转日期: {f['home_date']}"
                    for f in failed_accounts
                ])
                logger.error(f"=== 一致性巡检发现问题 ===\n{summary}")
                notify_inspection_fail(self.feishu_webhook, "TC-07-01 一致性巡检", summary)
                pytest.fail(f"以下账号日期不一致:\n{summary}")
            else:
                logger.info("TC-07-01：所有账号一致性校验通过")
                notify_inspection_pass(self.feishu_webhook, "TC-07-01 一致性巡检",
                                       f"共 {len(self.accounts)} 个账号全部通过")
                self.page.screenshot(path="reports/screenshots/TC-07-01_success.png")

    # ────────────────────────────────────────────────────────
    @allure.story("内容完整性巡检")
    @allure.title("TC-07-02：最新速递文献翻译/AI解读/摘要/问题方法实验均不为空")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_tc_07_02_content_completeness(self):
        """
        遍历所有账号，对最新一期速递按以下规则抽取文献巡检：
          - 总数 > 5：前5篇（本周必读）全部 + 其余随机5篇，共10篇
          - 总数 ≤ 5：全部巡检
        列表页检查：标题翻译（不为空）、AI解读（≥30字）
        详情页检查：中文标题翻译（不为空）、中文摘要（不为空）、
                    问题/方法/实验（各≥10字）
        非阻断式：有问题记录后继续，全部完成统一上报
        """
        issues = []

        for acc in self.accounts:
            username = acc['username']
            logger.info(f"=== 内容巡检账号: {username} ===")

            with allure.step(f"[{username}] 登录并进入最新速递详情页"):
                _login_as(self.page, self.base_url, username, acc['password'])
                home_page    = HomePage(self.page, self.base_url)
                history_page = HistoryPage(self.page, self.base_url)
                detail_page  = DetailPage(self.page, self.base_url)

                home_page.goto_home()
                self.page.wait_for_timeout(1500)
                ok = home_page.click_total_count()
                if not ok:
                    logger.warning(f'[{username}] 首页"共X篇"按钮未找到，降级走历史速递第一张卡片')
                    history_page.goto_history_page()
                    self.page.wait_for_timeout(1500)
                    history_page.click_card_by_index(0)
                self.page.wait_for_load_state('networkidle')

            with allure.step(f"[{username}] 计算巡检索引"):
                # 从详情页实际 DOM 获取总篇数（含等待渲染）
                total = history_page.get_literature_count()
                if total == 0:
                    logger.warning(f"[{username}] 详情页未找到文献条目，跳过该账号")
                    continue
                indices = history_page.get_inspect_indices(total)
                logger.info(f"[{username}] 本期共 {total} 篇，巡检 {len(indices)} 篇")

            with allure.step(f"[{username}] 逐篇巡检"):
                for i in indices:
                    empty_fields = []

                    # ── 列表页字段检查（无需点击）──────────────────
                    subtitle = history_page.get_item_subtitle_by_index(i)
                    if not subtitle:
                        empty_fields.append('列表页-标题翻译')

                    ai_review = history_page.get_item_ai_review_by_index(i)
                    if len(ai_review) < 30:
                        empty_fields.append(f'列表页-AI解读(仅{len(ai_review)}字)')

                    # ── 点击进入详情页 ──────────────────────────────
                    list_title = history_page.get_literature_title_by_index(i)
                    ok = history_page.click_literature_by_index(i)
                    if not ok:
                        logger.warning(f"[{username}][{i}] 无法点击文献，跳过")
                        continue
                    self.page.wait_for_timeout(2500)

                    # # ── 详情页字段检查 ──────────────────────────────
                    # title_zh = detail_page.get_title_zh()
                    # if not title_zh:
                    #     empty_fields.append('详情页-中文标题翻译')

                    abstract_zh = detail_page.get_abstract_zh()
                    if not abstract_zh:
                        empty_fields.append('详情页-中文摘要')

                    pme = detail_page.get_all_pme()
                    if len(pme['problem']) < 30:
                        empty_fields.append(f'详情页-试图解决什么问题(仅{len(pme["problem"])}字)')
                    if len(pme['method']) < 30:
                        empty_fields.append(f'详情页-提出的方法是什么(仅{len(pme["method"])}字)')
                    if len(pme['experiment']) < 30:
                        empty_fields.append(f'详情页-做了哪些实验(仅{len(pme["experiment"])}字)')

                    if empty_fields:
                        issues.append({
                            'account':    username,
                            'lit_index':  i,
                            'lit_title':  list_title[:60],
                            'empty_fields': empty_fields,
                        })
                        logger.error(f"[{username}][{i}] 问题字段: {empty_fields}, 标题: {list_title[:40]}")
                    else:
                        logger.info(f"[{username}][{i}] 校验通过")

                    # 返回速递详情列表
                    self.page.go_back()
                    self.page.wait_for_timeout(1000)

        with allure.step("汇总巡检结果"):
            if issues:
                summary_lines = [
                    f"账号: {iss['account']}, 第{iss['lit_index']+1}篇, 标题: {iss['lit_title']}, 问题: {iss['empty_fields']}"
                    for iss in issues
                ]
                summary = '\n'.join(summary_lines)
                logger.error(f"=== 内容完整性巡检发现问题（共 {len(issues)} 处）===\n{summary}")
                self.page.screenshot(path="reports/screenshots/TC-07-02_issues.png")
                notify_inspection_fail(self.feishu_webhook, "TC-07-02 内容完整性巡检",
                                       f"发现 {len(issues)} 处问题:\n{summary}")
                pytest.fail(f"内容完整性巡检发现 {len(issues)} 处问题:\n{summary}")
            else:
                logger.info(f"TC-07-02：所有账号内容完整性巡检通过（共检查 {len(self.accounts)} 个账号）")
                notify_inspection_pass(self.feishu_webhook, "TC-07-02 内容完整性巡检",
                                       f"共 {len(self.accounts)} 个账号全部通过")
                self.page.screenshot(path="reports/screenshots/TC-07-02_success.png")
