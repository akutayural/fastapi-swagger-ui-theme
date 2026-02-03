from __future__ import annotations

import warnings
from importlib import resources
from typing import Any
from collections.abc import Mapping

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.routing import Mount


def setup_swagger_ui_theme(
    app: FastAPI,
    docs_path: str = "/docs",
    title: str | None = None,
    static_mount_path: str = "/swagger-ui-theme-static",
    swagger_js_url: str = "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
    swagger_css_url: str = "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    swagger_favicon_url: str | None = None,
    oauth2_redirect_url: str | None = None,
    init_oauth: Mapping[str, Any] | None = None,
    swagger_ui_parameters: Mapping[str, Any] | None = None,
) -> None:
    """
    Fully sets up Swagger UI with dark/light theme support.

    Mounts static assets and registers the themed Swagger UI endpoint.
    """

    # 1. Mount static files (idempotent)
    if not _has_mount(app, static_mount_path):
        _mount_swagger_ui_theme_static(app, static_mount_path)

    # 2. Register docs endpoint
    if any(getattr(route, "path", None) == docs_path for route in app.router.routes):
        warnings.warn(
            f"A route already exists at '{docs_path}'. "
            "FastAPI may already have registered its default Swagger UI. "
            "Consider initializing FastAPI with docs_url=None and redoc_url=None, "
            "or pass a different docs_path to setup_swagger_ui_theme().",
            UserWarning,
            stacklevel=2,
        )

    @app.get(docs_path, include_in_schema=False)
    def swagger_docs(request: Request) -> HTMLResponse:
        root_path = (request.scope.get("root_path") or "").rstrip("/")
        openapi_url = root_path + (app.openapi_url or "/openapi.json")

        return _swagger_ui_theme_docs(
            openapi_url=openapi_url,
            title=title or f"{app.title} Docs",
            static_mount_path=static_mount_path,
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
            swagger_favicon_url=swagger_favicon_url,
            oauth2_redirect_url=oauth2_redirect_url,
            init_oauth=init_oauth,
            swagger_ui_parameters=swagger_ui_parameters,
        )


def _swagger_ui_theme_docs(
    *,
    openapi_url: str,
    title: str,
    static_mount_path: str = "/swagger-ui-theme-static",
    swagger_js_url: str = "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
    swagger_css_url: str = "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    swagger_favicon_url: str | None = None,
    oauth2_redirect_url: str | None = None,
    init_oauth: Mapping[str, Any] | None = None,
    swagger_ui_parameters: Mapping[str, Any] | None = None,
) -> HTMLResponse:
    """Swagger UI with dark/light toggle and packaged static assets."""

    default_params: dict[str, Any] = {
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
        "persistAuthorization": True,
        "displayRequestDuration": True,
    }

    merged_params: dict[str, Any] = default_params.copy()
    if swagger_ui_parameters:
        merged_params.update(dict(swagger_ui_parameters))

    base = get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_js_url=swagger_js_url,
        swagger_css_url=swagger_css_url,
        swagger_favicon_url=swagger_favicon_url
        or "https://fastapi.tiangolo.com/img/favicon.png",
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=init_oauth,
        swagger_ui_parameters=merged_params,
    )

    html = base.body.decode("utf-8")

    html = html.replace(
        "</head>",
        f"""
<link rel="stylesheet" href="{static_mount_path}/swagger_ui_custom.css" />
<link rel="stylesheet" href="{static_mount_path}/swagger_ui_toggle.css" />
<link id="swagger-dark-css" rel="stylesheet" href="{static_mount_path}/swagger_ui_dark.css" disabled />
</head>
""",
        1,
    )

    html = html.replace(
        "</body>",
        f"""
<script src="{static_mount_path}/swagger_theme_toggle.js"></script>
</body>
""",
        1,
    )

    return HTMLResponse(content=html, status_code=base.status_code)


def _has_mount(app: FastAPI, mount_path: str) -> bool:
    for route in app.router.routes:
        if isinstance(route, Mount) and getattr(route, "path", None) == mount_path:
            return True
    return False


def _mount_swagger_ui_theme_static(app: FastAPI, mount_path: str) -> str:
    """Mount this package's static assets into the FastAPI app."""
    static_dir = resources.files("fastapi_swagger_ui_theme").joinpath("static")

    app.mount(
        mount_path,
        StaticFiles(directory=str(static_dir)),
        name="fastapi-swagger-ui-theme-static",
    )

    return mount_path
