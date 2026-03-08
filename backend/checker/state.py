"""
状态管理：比较 commit SHA，判断仓库是否有更新。
"""

from datetime import datetime, timezone
from backend.config import load_state, save_state, get_state_key


def check_and_update(
    platform: str, owner: str, repo: str, branch: str, latest_commit: dict
) -> bool:
    """
    比较最新 commit 与 state 中的记录。
    有更新则写入新 state 并返回 True，否则返回 False。
    """
    state = load_state()
    key = get_state_key(platform, owner, repo, branch)
    new_sha = latest_commit["sha"]

    old = state.get(key, {})
    if old.get("last_sha") == new_sha:
        state[key] = {
            **old,
            "last_check_time": datetime.now(timezone.utc).isoformat(),
        }
        save_state(state)
        return False

    state[key] = {
        "last_sha": new_sha,
        "last_time": latest_commit.get("time", ""),
        "last_message": latest_commit.get("message", ""),
        "last_author": latest_commit.get("author", ""),
        "last_url": latest_commit.get("url", ""),
        "last_check_time": datetime.now(timezone.utc).isoformat(),
        "updated": True,
    }
    save_state(state)
    return True


def get_repo_state(platform: str, owner: str, repo: str, branch: str) -> dict:
    state = load_state()
    key = get_state_key(platform, owner, repo, branch)
    return state.get(key, {})
