"""Admin authentication: one organiser account from settings, held in a signed session."""

import hmac
import logging

from fastapi import Request

from app.core.config import get_settings

log = logging.getLogger("synsara.security")
DEFAULT_PASSWORD = "synsara-admin"


def check_admin_credentials(username: str, password: str) -> bool:
    settings = get_settings()
    user_ok = hmac.compare_digest(username.encode(), settings.admin_username.encode())
    pass_ok = hmac.compare_digest(password.encode(), settings.admin_password.encode())
    return user_ok and pass_ok


def is_admin(request: Request) -> bool:
    return request.session.get("admin") is True


def warn_if_default_credentials() -> None:
    settings = get_settings()
    if settings.admin_password == DEFAULT_PASSWORD:
        log.warning("ADMIN_PASSWORD is the development default. Set it before deploying.")
    if settings.secret_key.startswith("dev-only"):
        log.warning("SECRET_KEY is the development default. Set it before deploying.")
