"""Application factory."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.content import get_content
from app.core.config import get_settings
from app.core.security import warn_if_default_credentials
from app.web import admin, public
from app.web.common import render

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "font-src 'self'; script-src 'self'; form-action 'self'; "
        "frame-ancestors 'none'; base-uri 'self'"
    ),
}


def create_app() -> FastAPI:
    settings = get_settings()
    get_content()  # fail fast on an invalid content file
    warn_if_default_credentials()

    app = FastAPI(title="SYNSARA", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="synsara_session",
        same_site="lax",
        https_only=settings.cookie_secure,
        max_age=8 * 60 * 60,
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            response.headers.setdefault(k, v)
        return response

    app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
    app.include_router(public.router)
    app.include_router(admin.router)

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(admin.NotAdmin)
    async def to_login(request: Request, _exc: admin.NotAdmin):
        return RedirectResponse(f"/admin/login?next={request.url.path}", status_code=303)

    @app.exception_handler(StarletteHTTPException)
    async def html_errors(request: Request, exc: StarletteHTTPException):
        return render(
            request,
            "error.html",
            status_code=exc.status_code,
            status=exc.status_code,
            detail=exc.detail,
        )

    return app


app = create_app()
