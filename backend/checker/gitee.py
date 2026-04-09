"""
Gitee 仓库最新 commit 获取。
"""

import logging

from backend.http_relay import send_request

logger = logging.getLogger(__name__)

GITEE_API = "https://gitee.com/api/v5/repos/{owner}/{repo}/commits"


async def fetch_latest_commit(
    owner: str,
    repo: str,
    branch: str,
    token: str = "",
    relay_url: str = "",
) -> dict | None:
    """
    返回 {"sha", "message", "author", "url", "time"} 或 None（失败时）。
    """
    url = GITEE_API.format(owner=owner, repo=repo)
    params = {"sha": branch, "per_page": 1}
    if token:
        params["access_token"] = token

    try:
        resp = await send_request(
            "GET",
            url,
            params=params,
            timeout=30,
            relay_url=relay_url,
        )
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list) or not data:
            logger.error(
                "Gitee fetch returned unexpected payload for %s/%s@%s: %s",
                owner,
                repo,
                branch,
                data,
            )
            return None

        item = data[0]
        return {
            "sha": item["sha"],
            "message": item["commit"]["message"].split("\n")[0],
            "author": item["commit"]["author"]["name"],
            "url": item["html_url"],
            "time": item["commit"]["author"]["date"],
        }
    except Exception as e:
        logger.error("Gitee fetch failed for %s/%s@%s: %s", owner, repo, branch, e)
        return None
