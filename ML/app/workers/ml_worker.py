import logging
import asyncio
import json
from typing import Dict, Any

from app.ml_engine.mistral_client import MistralAIService
from app.database.mongodb import MongoDBService
from app.database.redis_cache import RedisService
from app.services.message_queue import RabbitMQService
from app.training.training_service import TrainingService
from app.config.settings import settings

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Инициализация сервисов
mistral_service = MistralAIService()
mongodb_service = MongoDBService()
redis_service = RedisService()
rabbitmq_service = RabbitMQService()
training_service = TrainingService(mongodb_service)

async def process_message(message: Dict[str, Any]) -> None:
    """
    Обработка сообщения из очереди.
    
    Args:
        message: Сообщение для обработки
    """
    try:
        logger.info(f"Processing message: {message.get('type')}")
        
        message_type = message.get("type")
        
        if message_type == "new_conversation":
            await handle_new_conversation(message)
        elif message_type == "new_message":
            await handle_new_message(message)
        else:
            logger.warning(f"Unknown message type: {message_type}")
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)

async def handle_new_conversation(message: Dict[str, Any]) -> None:
    """
    Обработка создания новой беседы.
    
    Args:
        message: Данные для создания беседы
    """
    try:
        query = message.get("query")
        user_id = message.get("user_id")
        
        # Проверяем кэш
        cache_key = f"query:{query.lower()[:50]}"
        cached_response = await redis_service.get(cache_key)
        
        if cached_response:
            # Используем кэшированный ответ
            response_text = cached_response["response"]
        else:
            # Получаем ответ от Mistral AI
            conversation_data = await mistral_service.create_conversation(query)
            response_text = conversation_data["messages"][1]["content"]
            
            # Кэшируем ответ
            await redis_service.set(
                cache_key, 
                {"response": response_text},
                expire=3600  # Кэш на 1 час
            )
        
        # Создаем беседу в MongoDB
        conversation_data = {
            "user_id": user_id,
            "title": message.get("title") or query[:30],
            "messages": [
                {"role": "user", "content": query},
                {"role": "assistant", "content": response_text}
            ]
        }
        
        conversation_id = await mongodb_service.create_conversation(conversation_data)
        logger.info(f"Created conversation with ID: {conversation_id}")
        
        # Сохраняем диалог для дообучения модели
        # Для нового диалога пока не сохраняем - нужно минимум 2 обмена сообщениями
        
    except Exception as e:
        logger.error(f"Error handling new conversation: {e}", exc_info=True)

async def handle_new_message(message: Dict[str, Any]) -> None:
    """
    Обработка нового сообщения в существующей беседе.
    
    Args:
        message: Данные о новом сообщении
    """
    try:
        conversation_id = message.get("conversation_id")
        query = message.get("query")
        
        # Получаем беседу из MongoDB
        conversation = await mongodb_service.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation not found: {conversation_id}")
            return
        
        # Проверяем кэш
        cache_key = f"query:{query.lower()[:50]}"
        cached_response = await redis_service.get(cache_key)
        
        if cached_response:
            # Используем кэшированный ответ
            response_text = cached_response["response"]
        else:
            # Получаем историю сообщений
            history = conversation.get("messages", [])
            
            # Получаем ответ от Mistral AI
            response_text = await mistral_service.continue_conversation(
                conversation_id, query, history
            )
            
            # Кэшируем ответ
            await redis_service.set(
                cache_key, 
                {"response": response_text},
                expire=3600  # Кэш на 1 час
            )
        
        # Добавляем сообщение пользователя в историю
        await mongodb_service.update_conversation(
            conversation_id, 
            {"role": "user", "content": query}
        )
        
        # Добавляем ответ ассистента в историю
        await mongodb_service.update_conversation(
            conversation_id, 
            {"role": "assistant", "content": response_text}
        )
        
        logger.info(f"Added new message to conversation: {conversation_id}")
        
        # Сохраняем диалог для дообучения, если в нем уже достаточно сообщений
        # Получаем обновленную беседу
        updated_conversation = await mongodb_service.get_conversation(conversation_id)
        if len(updated_conversation.get("messages", [])) >= 4:  # Минимум 2 обмена сообщениями
            # Автоматически оцениваем качество диалога (пример простой логики)
            # В реальной системе здесь могла бы быть более сложная оценка
            quality_score = 4  # По умолчанию считаем диалог хорошим
            
            # Сохраняем для дообучения
            await training_service.save_conversation_for_training(
                conversation_id, 
                quality_score=quality_score
            )
            logger.info(f"Saved conversation {conversation_id} for training")
        
    except Exception as e:
        logger.error(f"Error handling new message: {e}", exc_info=True)

async def run_worker():
    """Запуск воркера для обработки сообщений из очереди."""
    try:
        logger.info("Starting ML worker")
        
        # Подключаемся к RabbitMQ
        await rabbitmq_service.connect()
        
        # Запускаем обработку сообщений
        await rabbitmq_service.start_worker(process_message)
    except Exception as e:
        logger.error(f"Error running worker: {e}", exc_info=True)
    finally:
        # Закрываем соединения
        await rabbitmq_service.close()

if __name__ == "__main__":
    # Запуск воркера
    asyncio.run(run_worker()) 