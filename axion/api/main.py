from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from axion.config import settings
from axion.database.connection import init_db
from axion.api.routes import documents, graph, baseline, reasoning, transfer, hypothesis, validation, memory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database schema and tables are initialized
    await init_db()
    yield
    # Shutdown logic if any

def create_app() -> FastAPI:
    app = FastAPI(
        title="AXION Intelligence Platform API",
        description="Universal Knowledge and Cross-Domain Intelligence Platform API (Phase 1 Baseline)",
        version="0.1.0",
        lifespan=lifespan
    )

    # Enable CORS for future frontend integration
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
