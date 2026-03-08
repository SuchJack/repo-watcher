"""
FastAPI 主入口：REST API 路由 + 静态文件托管 + 生命周期管理。
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config import (
    load_config, save_config, mask_config,
    load_repos, add_repo, update_repo, delete_repo,
    load_state,
)
from backend.checker.state import get_repo_state
from backend.scheduler import start_scheduler, reschedule, shutdown_scheduler, run_check_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_config()
    if cfg.get("scheduler_enabled", True):
        start_scheduler()
    logger.info("应用启动完成")
    yield
    shutdown_scheduler()
    logger.info("应用已关闭")


app = FastAPI(title="仓库变更监控工具", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Repos API ────────────────────────────────────────────

@app.get("/api/repos")
async def get_repos():
    repos = load_repos()
    result = []
    for r in repos:
        state = get_repo_state(
            r.get("platform", "github"),
            r.get("owner", ""),
            r.get("repo", ""),
            r.get("branch", "master"),
        )
        result.append({**r, "state": state})
    return result


@app.post("/api/repos")
async def create_repo(body: dict):
    if not body.get("owner") or not body.get("repo"):
        raise HTTPException(400, "owner 和 repo 不能为空")
    if body.get("platform") not in ("github", "gitee"):
        body["platform"] = "github"
    repo = add_repo(body)
    return repo


@app.put("/api/repos/{repo_id}")
async def modify_repo(repo_id: str, body: dict):
    updated = update_repo(repo_id, body)
    if updated is None:
        raise HTTPException(404, "仓库不存在")
    return updated


@app.delete("/api/repos/{repo_id}")
async def remove_repo(repo_id: str):
    ok = delete_repo(repo_id)
    if not ok:
        raise HTTPException(404, "仓库不存在")
    return {"ok": True}


# ── Config API ───────────────────────────────────────────

@app.get("/api/config")
async def get_config():
    cfg = load_config()
    return mask_config(cfg)


@app.put("/api/config")
async def put_config(body: dict):
    interval = body.get("poll_interval_seconds")
    if interval is not None:
        if not isinstance(interval, (int, float)) or interval < 60:
            raise HTTPException(400, "轮询间隔最小 60 秒")
        if interval > 86400:
            raise HTTPException(400, "轮询间隔最大 86400 秒")

    saved = save_config(body)
    reschedule()
    return mask_config(saved)


# ── Check API ────────────────────────────────────────────

@app.post("/api/check")
async def trigger_check():
    updated = await run_check_all()
    return {
        "checked": len(load_repos()),
        "updated": len(updated),
        "details": updated,
    }


# ── State API ────────────────────────────────────────────

@app.get("/api/state")
async def get_state():
    return load_state()


# ── 静态文件（生产环境托管前端构建产物）───────────────────

DIST_DIR = Path(__file__).parent.parent / "frontend" / "dist"
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")
