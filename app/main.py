from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import auth_routes, org_routes
from app.core.config import settings
from app.db.mongo import close_client, create_indexes, get_client

if settings.is_development:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_client()
    await create_indexes()
    yield
    await close_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title="BugSentry Auth Service",
        version="1.0.0",
        description="Authentication & organization management for BugSentry AI DevOps platform.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_routes.router)
    app.include_router(org_routes.router)

    @app.get("/health", tags=["Health"])
    def health():
        return JSONResponse({"status": "healthy", "service": "BugSentry Auth", "version": "1.0.0"})

    @app.get("/", include_in_schema=False)
    def root():
        return {"service": "BugSentry Auth Service", "docs": "/docs"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=settings.is_development)
