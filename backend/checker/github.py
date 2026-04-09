"""
GitHub 仓库最新 commit 获取。
"""

import logging

from backend.http_relay import send_request

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com/repos/{owner}/{repo}/commits"


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
    url = GITHUB_API.format(owner=owner, repo=repo)
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    params = {"sha": branch, "per_page": 1}

    try:
        resp = await send_request(
            "GET",
            url,
            headers=headers,
            params=params,
            timeout=30,
            relay_url=relay_url,
        )
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list) or not data:
            logger.error(
                "GitHub fetch returned unexpected payload for %s/%s@%s: %s",
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
        logger.error("GitHub fetch failed for %s/%s@%s: %s", owner, repo, branch, e)
        return None
