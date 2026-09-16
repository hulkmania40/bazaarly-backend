from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.errors import BazaarlyError
from app.db.session import init_db
from app.api.v1.router import router as api_v1_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BazaarlyError)
async def bazaarly_error_handler(request, exc: BazaarlyError):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=400, content={"detail": exc.detail, "code": exc.code})


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(api_v1_router, prefix="/api/v1")
