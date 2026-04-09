"""
飞书 Webhook 通知。
"""

import hashlib
import hmac
import base64
import time
import logging

from backend.http_relay import send_request

logger = logging.getLogger(__name__)


def _gen_sign(secret: str, timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


async def send(
    webhook_url: str,
    title: str,
    text: str,
    secret: str = "",
    relay_url: str = "",
):
    timestamp = str(int(time.time()))
    body: dict = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [{"tag": "text", "text": text}]
                    ],
                }
            }
        },
    }
    if secret:
        body["timestamp"] = timestamp
        body["sign"] = _gen_sign(secret, timestamp)

    try:
        resp = await send_request(
            "POST",
            webhook_url,
            json_body=body,
            timeout=15,
            relay_url=relay_url,
        )
        resp.raise_for_status()
        result = resp.json()
        if not isinstance(result, dict):
            logger.error("飞书返回格式异常: %s", result)
            return

        if result.get("code", 0) != 0:
            logger.error("飞书发送失败: %s", result)
        else:
            logger.info("飞书通知已发送: %s", title)
    except Exception as e:
        logger.error("飞书请求异常: %s", e)
