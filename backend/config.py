"""
配置与存储管理：读写 config.json / repos.json，敏感字段脱敏。
"""

import json
import os
import threading
import uuid
from pathlib import Path
from copy import deepcopy

DATA_DIR = Path(__file__).parent / "data"

CONFIG_FILE = DATA_DIR / "config.json"
REPOS_FILE = DATA_DIR / "repos.json"
STATE_FILE = DATA_DIR / "state.json"

_lock = threading.Lock()

MASKED_RESPONSE_FIELDS = {
    "smtp_password",
    "feishu_secret",
    "github_token",
    "gitee_token",
    "admin_password",
}

# Relay URLs should stay visible in the settings page, but we still accept the
# legacy mask value on save so an already-open page will not overwrite them.
MASK_PRESERVE_FIELDS = MASKED_RESPONSE_FIELDS | {
    "github_relay_url",
    "gitee_relay_url",
    "feishu_relay_url",
}
MASK = "******"

DEFAULT_CONFIG = {
    "poll_interval_seconds": 600,
    "scheduler_enabled": True,
    "github_token": "",
    "gitee_token": "",
    "github_relay_url": "",
    "gitee_relay_url": "",
    "feishu_enabled": False,
    "feishu_webhook_url": "",
    "feishu_secret": "",
    "feishu_relay_url": "",
    "email_enabled": False,
    "smtp_host": "",
    "smtp_port": 465,
    "smtp_user": "",
    "smtp_password": "",
    "smtp_use_tls": True,
    "from_addr": "",
    "to_addrs": [],
    "admin_password": "",
}


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default):
    if not path.exists():
        return deepcopy(default)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data):
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Config ──────────────────────────────────────────────

def load_config() -> dict:
    with _lock:
        cfg = _read_json(CONFIG_FILE, DEFAULT_CONFIG)
        merged = {**DEFAULT_CONFIG, **cfg}
        return merged


def save_config(new_cfg: dict):
    with _lock:
        old = _read_json(CONFIG_FILE, DEFAULT_CONFIG)
        merged = {**DEFAULT_CONFIG, **old}
        for key, val in new_cfg.items():
            if key in MASK_PRESERVE_FIELDS and val == MASK:
                continue
            merged[key] = val
        _write_json(CONFIG_FILE, merged)
        return merged


def mask_config(cfg: dict) -> dict:
    """返回脱敏后的配置（用于 API 响应）"""
    out = deepcopy(cfg)
    for field in MASKED_RESPONSE_FIELDS:
        if out.get(field):
            out[field] = MASK
    return out


# ── Repos ───────────────────────────────────────────────

def load_repos() -> list[dict]:
    with _lock:
        return _read_json(REPOS_FILE, [])


def save_repos(repos: list[dict]):
    with _lock:
        _write_json(REPOS_FILE, repos)


def add_repo(repo: dict) -> dict:
    repos = load_repos()
    repo["id"] = str(uuid.uuid4())[:8]
    if not repo.get("branch"):
        repo["branch"] = "master"
    repos.append(repo)
    save_repos(repos)
    return repo


def update_repo(repo_id: str, data: dict) -> dict | None:
    repos = load_repos()
    for r in repos:
        if r["id"] == repo_id:
            r.update({k: v for k, v in data.items() if k != "id"})
            save_repos(repos)
            return r
    return None


def delete_repo(repo_id: str) -> bool:
    repos = load_repos()
    new_repos = [r for r in repos if r["id"] != repo_id]
    if len(new_repos) == len(repos):
        return False
    save_repos(new_repos)
    return True


# ── State ───────────────────────────────────────────────

def load_state() -> dict:
    with _lock:
        return _read_json(STATE_FILE, {})


def save_state(state: dict):
    with _lock:
        _write_json(STATE_FILE, state)


def get_state_key(platform: str, owner: str, repo: str, branch: str) -> str:
    return f"{platform}:{owner}/{repo}:{branch}"
