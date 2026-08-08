"""Aggregates every v1 sub-router into a single mountable APIRouter."""

from fastapi import APIRouter

from app.api.v1 import audio, fusion, history, text, video

api_v1_router = APIRouter()
api_v1_router.include_router(text.router)
api_v1_router.include_router(audio.router)
api_v1_router.include_router(video.router)
api_v1_router.include_router(fusion.router)
api_v1_router.include_router(history.router)
