"""
登录认证：固定管理员密码 + JWT，未登录禁止访问后台 API。
"""

import os
import time
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import load_config, save_config

# 仅支持从请求头 Bearer token 获取，便于前后端分离
security = HTTPBearer(auto_error=False)

# 默认初始密码（仅当未配置 config 与环境变量时生效，首次登录后请尽快修改）
DEFAULT_ADMIN_PASSWORD = "admin"

# 进程内生成的默认密码哈希（未配置时使用，重启后仍为 admin）
_default_password_hash: str | None = None
# 环境变量密码哈希缓存（避免每次请求都重新 hash）
_env_password_hash: bytes | None = None

# JWT 配置：密钥与过期时间（24 小时）
JWT_SECRET = os.environ.get("JWT_SECRET", "repo-watcher-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 24 * 3600


def _get_default_password_hash() -> str:
    """未配置时使用的默认密码（admin）哈希，进程内单例。"""
    global _default_password_hash
    if _default_password_hash is None:
        _default_password_hash = bcrypt.hashpw(
            DEFAULT_ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
    return _default_password_hash


def _get_admin_password_hash() -> str | None:
    """获取管理员密码的 bcrypt 哈希：优先 config，其次环境变量 ADMIN_PASSWORD，最后默认 admin。"""
    global _env_password_hash
    cfg = load_config()
    stored = (cfg.get("admin_password") or "").strip()
    if stored:
        return stored
    plain = os.environ.get("ADMIN_PASSWORD", "").strip()
    if plain:
        if _env_password_hash is None:
            _env_password_hash = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
        return _env_password_hash.decode("utf-8")
    return _get_default_password_hash()


def verify_password(username: str, password: str) -> bool:
    """校验用户名与密码。当前仅支持单用户 admin。"""
    if username != "admin":
        return False
    h = _get_admin_password_hash()
    try:
        return bcrypt.checkpw(password.encode("utf-8"), h.encode("utf-8"))
    except Exception:
        return False


def create_access_token() -> str:
    """签发 JWT，payload 含 sub=admin 与过期时间。"""
    payload = {
        "sub": "admin",
        "exp": int(time.time()) + JWT_EXPIRE_SECONDS,
        "iat": int(time.time()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict:
    """依赖项：解析 Authorization: Bearer <token>，校验 JWT，未登录或无效则 401。"""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        if sub != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效凭证")
        return {"username": sub}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效凭证",
        )


def change_password(old_password: str, new_password: str) -> None:
    """修改管理员密码：校验旧密码后写入新密码的 bcrypt 哈希到 config。"""
    if not verify_password("admin", old_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码错误")
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码至少 6 位")
    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    save_config({"admin_password": new_hash})
