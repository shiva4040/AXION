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

    # Static assets mounting & PWA Serving
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        icons_dir = static_dir / "icons"
        if icons_dir.exists():
            app.mount("/icons", StaticFiles(directory=str(icons_dir)), name="icons")

        @app.get("/sw.js", include_in_schema=False)
        async def serve_sw():
            sw_file = static_dir / "sw.js"
            if sw_file.exists():
                return FileResponse(
                    str(sw_file),
                    media_type="application/javascript",
                    headers={"Service-Worker-Allowed": "/"}
                )
            return Response(status_code=404)

        @app.get("/manifest.webmanifest", include_in_schema=False)
        @app.get("/manifest.json", include_in_schema=False)
        async def serve_manifest():
            m_file = static_dir / "manifest.webmanifest"
            if not m_file.exists():
                m_file = static_dir / "manifest.json"
            if m_file.exists():
                return FileResponse(str(m_file), media_type="application/manifest+json")
            return Response(status_code=404)

        @app.get("/favicon.svg", include_in_schema=False)
        async def serve_favicon():
            fav = static_dir / "favicon.svg"
            if fav.exists():
                return FileResponse(str(fav), media_type="image/svg+xml")
            return Response(status_code=404)

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
