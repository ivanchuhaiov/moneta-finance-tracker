from fastapi import FastAPI
from app.routers import health
from app.auth.router import router

app = FastAPI()

app.include_router(health.router)
app.include_router(router)


