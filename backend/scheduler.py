"""
调度器：定时执行全量仓库检查 + 通知。
"""

import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from backend.config import load_config, load_repos
from backend.checker import github as github_checker
from backend.checker import gitee as gitee_checker
from backend.checker.state import check_and_update, get_repo_state
from backend.notifier import feishu as feishu_notifier
from backend.notifier import mail as mail_notifier

logger = logging.getLogger(__name__)

JOB_ID = "poll_repos"

scheduler = BackgroundScheduler()


def _build_message(repo_info: dict, commit: dict) -> tuple[str, str]:
    platform = repo_info["platform"]
    owner = repo_info["owner"]
    repo = repo_info["repo"]
    branch = repo_info.get("branch", "main")
    title = f"[仓库更新] {owner}/{repo} ({branch})"
    text = (
        f"平台: {platform}\n"
        f"仓库: {owner}/{repo}\n"
        f"分支: {branch}\n"
        f"提交: {commit['sha'][:8]}\n"
        f"作者: {commit['author']}\n"
        f"信息: {commit['message']}\n"
        f"时间: {commit['time']}\n"
        f"链接: {commit['url']}"
    )
    return title, text


async def _notify(title: str, text: str, cfg: dict):
    if cfg.get("feishu_enabled") and cfg.get("feishu_webhook_url"):
        await feishu_notifier.send(
            cfg["feishu_webhook_url"], title, text, cfg.get("feishu_secret", "")
        )
    if cfg.get("email_enabled") and cfg.get("smtp_host") and cfg.get("to_addrs"):
        mail_notifier.send(
            smtp_host=cfg["smtp_host"],
            smtp_port=cfg.get("smtp_port", 465),
            smtp_user=cfg.get("smtp_user", ""),
            smtp_password=cfg.get("smtp_password", ""),
            smtp_use_tls=cfg.get("smtp_use_tls", True),
            from_addr=cfg.get("from_addr", cfg.get("smtp_user", "")),
            to_addrs=cfg["to_addrs"],
            subject=title,
            body=text,
        )


async def run_check_all() -> list[dict]:
    """
    执行一次全量检查，返回有更新的仓库列表。
    """
    cfg = load_config()
    repos = load_repos()
    updated_repos = []

    for repo_info in repos:
        platform = repo_info.get("platform", "github")
        owner = repo_info.get("owner", "")
        repo = repo_info.get("repo", "")
        branch = repo_info.get("branch", "main")

        if not owner or not repo:
            continue

        token = cfg.get("github_token", "") if platform == "github" else cfg.get("gitee_token", "")
        fetcher = github_checker if platform == "github" else gitee_checker
        commit = await fetcher.fetch_latest_commit(owner, repo, branch, token)

        if commit is None:
            logger.warning("无法获取 %s/%s@%s 的最新提交", owner, repo, branch)
            continue

        has_update = check_and_update(platform, owner, repo, branch, commit)
        if has_update:
            title, text = _build_message(repo_info, commit)
            await _notify(title, text, cfg)
            updated_repos.append({
                "platform": platform,
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "commit": commit,
            })
            logger.info("发现更新: %s/%s@%s -> %s", owner, repo, branch, commit["sha"][:8])

    return updated_repos


def _sync_check():
    """同步包装器，供 APScheduler 调用"""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(run_check_all())
    finally:
        loop.close()


def start_scheduler():
    cfg = load_config()
    interval = max(cfg.get("poll_interval_seconds", 600), 60)

    if scheduler.running:
        return

    scheduler.add_job(
        _sync_check,
        "interval",
        seconds=interval,
        id=JOB_ID,
        replace_existing=True,
    )
    scheduler.start()
    logger.info("调度器已启动，轮询间隔 %d 秒", interval)


def reschedule():
    cfg = load_config()
    interval = max(cfg.get("poll_interval_seconds", 600), 60)
    enabled = cfg.get("scheduler_enabled", True)

    if not scheduler.running:
        if enabled:
            start_scheduler()
        return

    if not enabled:
        try:
            scheduler.remove_job(JOB_ID)
        except Exception:
            pass
        logger.info("调度器已暂停")
        return

    scheduler.reschedule_job(JOB_ID, trigger="interval", seconds=interval)
    logger.info("调度器已重新调度，新间隔 %d 秒", interval)


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
