"""FastAPI Main Application Entry Point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.core.config import settings
from backend.app.core.model_loader import model_loader
from backend.app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to load model into RAM upon startup."""
    logger.info("Initializing CropForecastLK backend microservice...")
    model_loader.load()
    yield
    logger.info("Shutting down CropForecastLK backend microservice...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production REST Microservice for Sri Lankan Highland Crop Production "
        "and Harvest Yield Forecasting using tuned XGBoost ML Pipeline."
    ),
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits seamless development frontend requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to interactive Swagger API documentation."""
    return RedirectResponse(url="/docs")
