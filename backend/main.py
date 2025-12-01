import uvicorn
from fastapi import FastAPI
from backend.core.config import settings
from backend.db import session as db_session
from backend import models
from backend.routers import ai_router, auth_router, user_router, history_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    # DB tables
    models.Base.metadata.create_all(bind=db_session.engine)

    # Routers
    app.include_router(ai_router.router, prefix=settings.api_prefix)
    app.include_router(auth_router.router, prefix=settings.api_prefix)
    app.include_router(user_router.router, prefix=settings.api_prefix)
    app.include_router(history_router.router, prefix=settings.api_prefix)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
