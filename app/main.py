from fastapi import FastAPI
from app.routers import health
from app.auth.router import router as auth_router
from app.wallet.router import router as wallet_router
from app.transaction.router import router as transaction_router
from contextlib import asynccontextmanager

from app.core.scheduler import scheduler, setup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transaction_router)



