import logging
import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from prometheus_client import make_asgi_app

from app.api.routes import router as api_router
from app.config.settings import settings
from app.utils.metrics import setup_metrics

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Персональный ментор на базе Mistral AI",
    description="API для работы с персональным ментором на базе Mistral AI",
    version="0.1.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка метрик Prometheus
setup_metrics(app, "personal-mentor-api", "0.1.0")

# Добавление эндпоинта для метрик Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Регистрация маршрутов
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения."""
    logger.info("Starting up the application")

@app.on_event("shutdown")
async def shutdown_event():
    """Действия при завершении работы приложения."""
    logger.info("Shutting down the application")

@app.get("/")
async def root():
    """Корневой маршрут для проверки работоспособности."""
    return {"status": "ok", "message": "API персонального ментора работает"}

@app.get("/health")
async def health_check():
    """Маршрут для проверки состояния приложения."""
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )

if __name__ == "__main__":
    # Запуск сервера с помощью uvicorn, если скрипт запущен напрямую
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        workers=4,
    ) 