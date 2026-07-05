from fastapi import APIRouter
import asyncio
import time

router = APIRouter(prefix="/health")

@router.get("")
async def health_check():
    return {"status": "ok"}

@router.get("/slow")
async def health_check_slow():
    await asyncio.sleep(2)
    return {"status": "ok", "delay": "2s"}