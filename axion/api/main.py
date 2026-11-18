from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from axion.config import settings
from axion.database.connection import init_db
from axion.api.routes import (
    documents,
    graph,
    baseline,
    reasoning,
    transfer,
    hypothesis,
    validation,
    memory,
    investigation,
    acquisition,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database schema and tables are initialized
    await init_db()
    yield
    # Shutdown logic if any

def create_app() -> FastAPI:
    app = FastAPI(
        title="AXION Intelligence Platform API",
        description="Universal Knowledge and Cross-Domain Intelligence Platform API",
        version="0.1.0",
        lifespan=lifespan
    )

    # Enable CORS for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers under /api/v1
    app.include_router(documents.router, prefix="/api/v1")
    app.include_router(graph.router, prefix="/api/v1")
    app.include_router(baseline.router, prefix="/api/v1")
    app.include_router(reasoning.router, prefix="/api/v1")
    app.include_router(transfer.router, prefix="/api/v1")
    app.include_router(hypothesis.router, prefix="/api/v1")
    app.include_router(validation.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(investigation.router, prefix="/api/v1")
    app.include_router(acquisition.router, prefix="/api/v1")

    # Static assets mounting & Minimal Homepage
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        @app.get("/", include_in_schema=False)
        async def serve_homepage():
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return {"message": "AXION Intelligence Platform API"}

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "environment": settings.axion_env,
            "version": "0.1.0"
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "axion.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.axion_env == "development")
    )
