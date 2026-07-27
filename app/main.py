from fastapi import FastAPI
from app.routers import health
from app.auth.router import router as auth_router
from app.wallet.router import router as wallet_router
from app.transaction.router import router as transaction_router


app = FastAPI()

app.include_router(health.router)
app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transaction_router)



