from contextlib import asynccontextmanager
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware

from fastapi import FastAPI

from app.analytics.router import router as analytics_router
from app.auth.router import router as auth_router
from app.core.scheduler import scheduler, setup_scheduler
from app.routers import health
from app.transaction.router import router as transaction_router
from app.wallet.router import router as wallet_router
from app.features.reports.router import router as report_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()

setup_logging()
app = FastAPI(lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(health.router)
app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transaction_router)
app.include_router(analytics_router)
app.include_router(report_router)