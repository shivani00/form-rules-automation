from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes.rules import router as rules_router
from routes.osari import router as osari_router
from routes.ai import router as ai_router
from routes.automation import router as automation_router
from logger import get_logger
from config import config
from langchain.globals import set_debug, set_verbose

set_debug(True)
set_verbose(True)

logger = get_logger("main")

# 🔥 NEW LIFESPAN HANDLER
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("🚀 Backend started successfully")
    yield
    # SHUTDOWN
    logger.info("🛑 Backend shutting down")


app = FastAPI(
    title=config.APP_NAME,
    lifespan=lifespan 
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rules_router)
app.include_router(osari_router)
app.include_router(ai_router)
app.include_router(automation_router)