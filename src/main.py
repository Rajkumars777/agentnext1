import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure path (add root to sys.path so 'src' can be imported)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set event loop policy for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Import Routers (Corrected paths)
from src.api.routers import agent as agent_router
from src.api.routers import events as events_router
from src.api.routers import settings as settings_router
from src.api.routers import openclaw as openclaw_router

from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Startup: Connecting to services...")
    
    # Auto-start OpenClaw gateway
    try:
        from src.core.openclaw_process import start_gateway
        gw_result = start_gateway()
        logger.info(f"OpenClaw Gateway: {gw_result.get('message', 'unknown')}")
    except Exception as e:
        logger.warning(f"OpenClaw gateway auto-start skipped: {e}")
    
    logger.info("✅ Services ready")
    yield
    # Shutdown logic
    logger.info("Shutdown: Closing connections...")

app = FastAPI(lifespan=lifespan, title="AI Agent Backend")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router.router)
app.include_router(events_router.router)
app.include_router(settings_router.router)
app.include_router(openclaw_router.router)

@app.get("/")
async def read_root():
    return {"status": "online", "service": "AI Agent Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def main():
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        loop="asyncio"
    )

if __name__ == "__main__":
    main()
