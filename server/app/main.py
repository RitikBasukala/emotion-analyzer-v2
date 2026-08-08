"""FastAPI application entry point.

Run with: `uvicorn app.main:app --reload` from the `backend/` directory.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.session import dispose_engine, init_models
from app.ml.registry import get_model_registry

configure_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup.begin", extra={"environment": settings.environment})

    await init_models()

    registry = get_model_registry(settings)
    if settings.preload_models:
        logger.info("startup.preloading_models")
        registry.preload()

    logger.info("startup.complete")
    yield

    logger.info("shutdown.begin")
    await dispose_engine()
    logger.info("shutdown.complete")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered multi-modal emotion recognition across text, audio, and video, "
    "combined through a multi-tier (early/mid/late) fusion mechanism.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Ensure every unhandled error is logged with context and returns a clean JSON body."""
    logger.exception("unhandled_exception", extra={"path": request.url.path})
    return JSONResponse(
        status_code=500, content={"error": "internal_server_error", "detail": str(exc)}
    )


app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["meta"])
async def root():
    return {
        "message": settings.app_name,
        "version": "2.0.0",
        "docs": "/docs",
        "api_prefix": settings.api_v1_prefix,
    }


@app.get("/health", tags=["meta"])
async def health_check():
    return {"status": "healthy", "environment": settings.environment}
