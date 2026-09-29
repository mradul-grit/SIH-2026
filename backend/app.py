"""
SIH-26227: Semantic Retrieval & Multi-Temporal Change Analysis of Satellite Imagery
Backend API Application Entrypoint
Organization: Ministry of Defence (MoD) / Indian Army (DGIS)
"""

from project_code.api.app import app

__all__ = ["app"]

if __name__ == "__main__":
    import os
    import uvicorn
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run("backend.app:app", host=host, port=port, reload=False)
