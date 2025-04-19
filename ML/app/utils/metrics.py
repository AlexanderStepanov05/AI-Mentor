import time
from prometheus_client import Counter, Histogram, Gauge, Info
from fastapi import FastAPI, Request, Response

# Определяем метрики
REQUEST_COUNT = Counter(
    "api_request_count", 
    "Count of API requests received",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", 
    "Latency of API requests in seconds",
    ["method", "endpoint"]
)

ACTIVE_REQUESTS = Gauge(
    "api_active_requests", 
    "Number of active API requests"
)

ERROR_COUNT = Counter(
    "api_error_count", 
    "Count of API errors",
    ["method", "endpoint", "error_type"]
)

MODEL_RESPONSE_TIME = Histogram(
    "model_response_time_seconds", 
    "Response time from ML model in seconds"
)

CACHE_HIT_COUNT = Counter(
    "cache_hit_count", 
    "Count of cache hits"
)

CACHE_MISS_COUNT = Counter(
    "cache_miss_count", 
    "Count of cache misses"
)

API_INFO = Info(
    "api_info", 
    "Information about the API"
)

def setup_metrics(app: FastAPI, app_name: str, app_version: str):
    """Настройка метрик Prometheus для FastAPI приложения."""
    
    # Установка информации о приложении
    API_INFO.info({"name": app_name, "version": app_version})
    
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        # Увеличиваем количество активных запросов
        ACTIVE_REQUESTS.inc()
        
        # Фиксируем время начала запроса
        start_time = time.time()
        
        # Ждем ответа
        try:
            response = await call_next(request)
            
            # Фиксируем время окончания запроса и вычисляем задержку
            latency = time.time() - start_time
            
            # Обновляем метрики
            REQUEST_COUNT.labels(
                method=request.method, 
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method, 
                endpoint=request.url.path
            ).observe(latency)
            
            return response
        except Exception as e:
            # Увеличиваем количество ошибок
            ERROR_COUNT.labels(
                method=request.method, 
                endpoint=request.url.path,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            # Уменьшаем количество активных запросов
            ACTIVE_REQUESTS.dec()
    
    @app.on_event("startup")
    async def startup():
        # Действия при запуске
        pass
    
    @app.on_event("shutdown")
    async def shutdown():
        # Действия при остановке
        pass 