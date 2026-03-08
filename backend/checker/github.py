"""
GitHub 仓库最新 commit 获取。
"""

import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com/repos/{owner}/{repo}/commits"


async def fetch_latest_commit(
    owner: str, repo: str, branch: str, token: str = ""
) -> dict | None:
    """
    返回 {"sha", "message", "author", "url", "time"} 或 None（失败时）。
    """
    url = GITHUB_API.format(owner=owner, repo=repo)
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    params = {"sha": branch, "per_page": 1}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            if not data:
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
        logger.error("GitHub fetch failed for %s/%s@%s: %s", owner, repo, branch, e)
        return None
