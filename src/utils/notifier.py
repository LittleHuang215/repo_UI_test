# -*- coding: utf-8 -*-
"""
飞书通知工具 - 通过群机器人 Webhook 发送巡检结果
"""
import json
import urllib.request
from datetime import datetime
from utils.logger import Logger

logger = Logger().get_logger()


def _send_feishu(webhook_url: str, content: str) -> bool:
    """向飞书 Webhook 发送文本消息，返回是否成功"""
    if not webhook_url:
        logger.warning("飞书 Webhook URL 未配置，跳过通知")
        return False
    payload = json.dumps({
        "msg_type": "text",
        "content": {"text": content}
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                logger.info("飞书通知发送成功")
                return True
            else:
                logger.error(f"飞书通知返回异常: {result}")
                return False
    except Exception as e:
        logger.error(f"飞书通知发送失败: {e}")
        return False


def notify_inspection_pass(webhook_url: str, case_id: str, detail: str = ""):
    """巡检全部通过时发送成功通知"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"✅ 巡检通过 [{case_id}]",
        f"时间：{now}",
    ]
    if detail:
        lines.append(detail)
    _send_feishu(webhook_url, "\n".join(lines))


def notify_inspection_fail(webhook_url: str, case_id: str, summary: str):
    """巡检发现问题时发送告警通知"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = "\n".join([
        f"❌ 巡检异常 [{case_id}]",
        f"时间：{now}",
        "---",
        summary,
    ])
    _send_feishu(webhook_url, content)
