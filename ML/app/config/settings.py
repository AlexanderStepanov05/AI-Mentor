import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Загрузка переменных окружения из .env файла
load_dotenv()

class Settings(BaseSettings):
    # API настройки
    api_port: int = Field(default=int(os.getenv("API_PORT", 8000)))
    api_host: str = Field(default=os.getenv("API_HOST", "0.0.0.0"))
    
    # Настройки Mistral AI
    mistral_api_key: str = Field(default=os.getenv("MISTRAL_API_KEY"))
    mistral_model: str = Field(default=os.getenv("MISTRAL_MODEL", "mistral-large-latest"))
    
    # MongoDB настройки
    mongo_uri: str = Field(default=os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    mongo_db: str = Field(default=os.getenv("MONGO_DB", "mentor_db"))
    mongo_collection: str = Field(default=os.getenv("MONGO_COLLECTION", "conversations"))
    
    # Redis настройки
    redis_host: str = Field(default=os.getenv("REDIS_HOST", "localhost"))
    redis_port: int = Field(default=int(os.getenv("REDIS_PORT", 6379)))
    redis_password: str = Field(default=os.getenv("REDIS_PASSWORD", ""))
    redis_db: int = Field(default=int(os.getenv("REDIS_DB", 0)))
    
    # RabbitMQ настройки
    rabbitmq_host: str = Field(default=os.getenv("RABBITMQ_HOST", "localhost"))
    rabbitmq_port: int = Field(default=int(os.getenv("RABBITMQ_PORT", 5672)))
    rabbitmq_user: str = Field(default=os.getenv("RABBITMQ_USER", "guest"))
    rabbitmq_password: str = Field(default=os.getenv("RABBITMQ_PASSWORD", "guest"))
    rabbitmq_vhost: str = Field(default=os.getenv("RABBITMQ_VHOST", "/"))
    rabbitmq_queue: str = Field(default=os.getenv("RABBITMQ_QUEUE", "ml_queue"))
    
    # JWT настройки
    jwt_secret: str = Field(default=os.getenv("JWT_SECRET", "your_jwt_secret_key_here"))
    jwt_algorithm: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))
    access_token_expire_minutes: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    )
    
    # Настройки логирования
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Создание экземпляра настроек для использования в приложении
settings = Settings() 