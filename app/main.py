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
from app.wallet.router import wallet_type_router as wallet_type_router
from app.ai.router import router as ai_router
from app.ai.exception_handlers import register_ai_exception_handlers
from app.ai.summary.router import router as summary_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()

setup_logging()
app = FastAPI(lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transaction_router)
app.include_router(analytics_router)
app.include_router(report_router)
app.include_router(wallet_type_router)
app.include_router(ai_router)
app.include_router(summary_router)

register_ai_exception_handlers(app)