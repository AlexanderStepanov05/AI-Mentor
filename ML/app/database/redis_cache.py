import json
import logging
from typing import Any, Dict, Optional
import redis.asyncio as redis

from app.config.settings import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Сервис для работы с Redis кэшем."""
    
    def __init__(self):
        """Инициализация соединения с Redis."""
        try:
            redis_url = f"redis://{settings.redis_password + '@' if settings.redis_password else ''}"\
                      f"{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
            self.redis = redis.from_url(redis_url)
            logger.info(f"Connected to Redis: {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Получение данных из кэша.
        
        Args:
            key: Ключ для поиска
            
        Returns:
            Dict: Данные из кэша или None, если данные не найдены
        """
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting data from Redis: {e}")
            return None
    
    async def set(self, key: str, value: Dict[str, Any], expire: int = 3600) -> bool:
        """
        Сохранение данных в кэш.
        
        Args:
            key: Ключ для сохранения
            value: Данные для сохранения
            expire: Время жизни данных в секундах (по умолчанию 1 час)
            
        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            serialized_value = json.dumps(value)
            await self.redis.set(key, serialized_value, ex=expire)
            logger.debug(f"Cached data with key {key} for {expire} seconds")
            return True
        except Exception as e:
            logger.error(f"Error setting data in Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Удаление данных из кэша.
        
        Args:
            key: Ключ для удаления
            
        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            await self.redis.delete(key)
            logger.debug(f"Deleted cache for key {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting data from Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Проверка наличия данных в кэше.
        
        Args:
            key: Ключ для проверки
            
        Returns:
            bool: True, если данные найдены
        """
        try:
            return await self.redis.exists(key)
        except Exception as e:
            logger.error(f"Error checking existence in Redis: {e}")
            return False
            
    async def get_hash_field(self, hash_key: str, field: str) -> Optional[Dict[str, Any]]:
        """
        Получение поля из хэш-структуры.
        
        Args:
            hash_key: Ключ хэш-структуры
            field: Поле для получения
            
        Returns:
            Dict: Данные из поля хэш-структуры или None
        """
        try:
            data = await self.redis.hget(hash_key, field)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting hash field from Redis: {e}")
            return None
            
    async def set_hash_field(self, hash_key: str, field: str, value: Dict[str, Any]) -> bool:
        """
        Установка поля в хэш-структуре.
        
        Args:
            hash_key: Ключ хэш-структуры
            field: Поле для установки
            value: Данные для сохранения
            
        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            serialized_value = json.dumps(value)
            await self.redis.hset(hash_key, field, serialized_value)
            logger.debug(f"Cached data in hash {hash_key} field {field}")
            return True
        except Exception as e:
            logger.error(f"Error setting hash field in Redis: {e}")
            return False 