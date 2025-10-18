from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.api.v1.api import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создаём таблицы при запуске приложения
    try:
        from app.db.database import engine
        from app.models import user, module, card, interval_repetition, module_access
        
        user.Base.metadata.create_all(bind=engine)
        module.Base.metadata.create_all(bind=engine)
        card.Base.metadata.create_all(bind=engine)
        interval_repetition.Base.metadata.create_all(bind=engine)
        module_access.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Could not create database tables: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")

app = FastAPI(
    title="T-Prep API",
    description="Backend API for T-Prep - exam preparation application",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.allowed_origins == "*" else settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "T-Prep API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/test_web.html")
async def test_page():
    """Serve the test page"""
    from fastapi.responses import FileResponse
    return FileResponse("static/test_web.html")
