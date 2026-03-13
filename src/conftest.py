# -*- coding: utf-8 -*-
"""
Pytest 配置文件 - 全局 fixtures 与钩子
"""
import os
import shutil
import yaml
import pytest
from playwright.sync_api import sync_playwright
from datetime import datetime
from utils.logger import Logger

LOGGER = Logger().get_logger()

# 用于在钩子与 fixture 之间传递用例执行结果
_phase_report_key = pytest.StashKey()


# ──────────────────────────────────────────────────────────
# Pytest 生命周期钩子
# ──────────────────────────────────────────────────────────

def pytest_configure(config):
    for d in ["reports/screenshots", "reports/logs", "reports/html", "reports/videos", "reports/traces"]:
        os.makedirs(d, exist_ok=True)
    LOGGER.info("=" * 50)
    LOGGER.info("测试开始执行")
    LOGGER.info("=" * 50)


def pytest_unconfigure(config):
    LOGGER.info("=" * 50)
    LOGGER.info("测试执行完毕")
    LOGGER.info("=" * 50)


# ──────────────────────────────────────────────────────────
# 基础 fixtures
# ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def load_config():
    """加载 config/config.yaml，整个会话只加载一次"""
    config_path = "config/config.yaml"
    with open(config_path, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    LOGGER.info(f"配置文件已加载: {config_path}")
    return cfg


@pytest.fixture(scope="session")
def load_params():
    """
    加载 params/ 目录下所有参数文件，返回统一参数字典。
    结构：
      params['accounts']          # dict  {id: account_dict}
      params['common']            # dict  通用配置
      params['groups']            # dict  {group_id: group_dict}
      params['group']             # dict  test001 对应课题组的快捷引用
    """
    params = {}

    # 账号列表
    with open("params/accounts.yaml", encoding='utf-8') as f:
        raw = yaml.safe_load(f)
    params['accounts'] = {acc['id']: acc for acc in raw['accounts']}

    # 通用配置
    with open("params/common.yaml", encoding='utf-8') as f:
        params['common'] = yaml.safe_load(f)['common']

    # 课题组数据（按 group id 映射）
    params['groups'] = {}
    for acc in params['accounts'].values():
        group_id = acc.get('group')
        group_file = f"params/group_{group_id}.yaml"
        if group_id and os.path.exists(group_file):
            with open(group_file, encoding='utf-8') as f:
                params['groups'][group_id] = yaml.safe_load(f)['group']

    # 默认课题组（test001）快捷引用
    default_group = params['accounts'].get('test001', {}).get('group')
    params['group'] = params['groups'].get(default_group, {})

    LOGGER.info(f"参数文件已加载，共 {len(params['accounts'])} 个账号，{len(params['groups'])} 个课题组")
    return params


@pytest.fixture(scope="function")
def browser_context(load_config, request):
    """每个测试函数创建独立的浏览器页面；全程录制视频，失败时保留，通过时删除"""
    config = load_config
    case_name = request.node.name
    # execution_count 由 pytest-rerunfailures 注入，从 1 开始：
    #   1 = 首次执行，2 = 第 1 次重试，3 = 第 2 次重试 …
    retry_count = getattr(request.node, 'execution_count', 1)
    is_retry = retry_count > 1

    retry_index = retry_count - 1  # 对外展示从 1 计数（第 1 次重试）
    LOGGER.info("启动浏览器" + (f"（第 {retry_index} 次重试）" if is_retry else ""))

    with sync_playwright() as p:
        browser_type = config['browser']['type']
        launch_kwargs = {
            'headless': config['headless'],
            'slow_mo': config['browser']['slow_mo'],
        }
        if browser_type == 'chromium':
            browser = p.chromium.launch(**launch_kwargs)
        elif browser_type == 'firefox':
            browser = p.firefox.launch(**launch_kwargs)
        else:
            browser = p.webkit.launch(**launch_kwargs)

        viewport_w = config['browser']['viewport']['width']
        viewport_h = config['browser']['viewport']['height']
        # 始终开启视频录制，根据结果决定保留或删除
        context_kwargs = {
            'viewport': {'width': viewport_w, 'height': viewport_h},
            'record_video_dir': 'reports/videos',
            'record_video_size': {'width': viewport_w, 'height': viewport_h},
        }

        context = browser.new_context(**context_kwargs)
        # 开启 Trace 录制：截图 + DOM 快照 + 源码映射
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        # 每次页面加载完成后，用 evaluate 注入悬浮用例标签
        def _inject_label():
            try:
                page.evaluate("""(caseName) => {
                    const existing = document.getElementById('__pytest_case_label__');
                    if (existing) existing.remove();
                    const label = document.createElement('div');
                    label.id = '__pytest_case_label__';
                    label.innerText = '用例：' + caseName;
                    Object.assign(label.style, {
                        position: 'fixed',
                        bottom: '12px',
                        right: '12px',
                        zIndex: '999999',
                        background: 'rgba(0, 0, 0, 0.65)',
                        color: '#fff',
                        padding: '6px 14px',
                        borderRadius: '6px',
                        fontSize: '13px',
                        fontFamily: 'monospace',
                        pointerEvents: 'none',
                        letterSpacing: '0.5px',
                    });
                    document.body.appendChild(label);
                }""", case_name)
            except Exception:
                pass  # 部分特殊页面（如 about:blank）注入失败时静默跳过

        page.on("load", lambda: _inject_label())
        LOGGER.info(f"已注册用例标签注入监听：{case_name}")

        yield page

        # ── 收集视频临时路径（context.close() 后文件才完整写入）──
        video_tmp = None
        try:
            video_tmp = page.video.path()
        except Exception:
            pass

        # ── 根据用例结果决定 Trace / 视频去向 ──
        report = request.node.stash.get(_phase_report_key, None)
        failed = report is not None and report.failed
        safe_name = case_name.replace('[', '_').replace(']', '').replace('/', '_')
        suffix = f"_retry{retry_index}" if is_retry else ""

        # 停止 Trace 录制并保存（需在 context.close() 之前）
        trace_dest = f"reports/traces/{safe_name}{suffix}_{'failed' if failed else 'pass'}.zip"
        try:
            context.tracing.stop(path=trace_dest)
            if failed:
                LOGGER.error(f"失败 Trace 已保存: {trace_dest}")
            else:
                # 通过时删除 Trace，节省磁盘
                os.remove(trace_dest)
                LOGGER.info("测试通过，Trace 已清除")
        except Exception as e:
            LOGGER.warning(f"Trace 保存失败: {e}")

        LOGGER.info("关闭浏览器")
        context.close()
        browser.close()

        # ── 根据用例结果决定视频去向 ──
        if video_tmp and os.path.exists(video_tmp):
            if failed:
                dest = f"reports/videos/{safe_name}{suffix}_failed.webm"
                shutil.move(video_tmp, dest)
                LOGGER.error(f"失败录制视频已保存: {dest}")
            else:
                os.remove(video_tmp)
                LOGGER.info("测试通过，视频已清除")


@pytest.fixture
def load_test_data():
    """兼容旧版：从 test_data/ 目录加载 YAML 文件"""
    def _load(file_name: str):
        data_path = f"test_data/{file_name}"
        with open(data_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        LOGGER.info(f"测试数据已加载: {data_path}")
        return data
    return _load


# ──────────────────────────────────────────────────────────
# 失败自动截图钩子
# ──────────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    # 将 call 阶段结果存入 stash，供 browser_context fixture teardown 读取
    if report.when == 'call':
        item.stash[_phase_report_key] = report
    if report.when == 'call' and report.failed:
        if 'browser_context' in item.fixturenames:
            page = item.funcargs.get('browser_context')
            if page:
                name = f"{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_failed"
                path = f"reports/screenshots/{name}.png"
                page.screenshot(path=path)
                LOGGER.error(f"失败截图: {path}")
