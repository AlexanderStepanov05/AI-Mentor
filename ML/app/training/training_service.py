import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiofiles
from app.database.mongodb import MongoDBService

logger = logging.getLogger(__name__)

class TrainingService:
    """Сервис для подготовки данных и дообучения модели."""
    
    def __init__(self, mongodb_service: MongoDBService):
        """
        Инициализация сервиса.
        
        Args:
            mongodb_service: Экземпляр сервиса MongoDB
        """
        self.mongodb_service = mongodb_service
        self.training_data_dir = os.environ.get("TRAINING_DATA_DIR", "app/training/data")
        os.makedirs(self.training_data_dir, exist_ok=True)
        
    async def prepare_training_data(self, limit: int = 1000, min_quality_score: Optional[int] = 3) -> str:
        """
        Подготавливает данные для обучения модели из MongoDB.
        
        Args:
            limit: Максимальное количество диалогов
            min_quality_score: Минимальная оценка качества (если указана)
            
        Returns:
            str: Путь к файлу с подготовленными данными
        """
        # Получаем данные из MongoDB
        training_data = await self.mongodb_service.get_training_data(limit, min_quality_score)
        
        if not training_data:
            logger.warning("No training data found")
            return None
            
        # Форматируем данные для дообучения
        formatted_data = []
        for entry in training_data:
            messages = entry.get("messages", [])
            if len(messages) < 2:
                continue  # Пропускаем диалоги с недостаточным количеством сообщений
                
            # Преобразуем в формат для дообучения
            formatted_dialog = {"messages": messages}
            formatted_data.append(formatted_dialog)
            
        if not formatted_data:
            logger.warning("No valid training dialogs found")
            return None
            
        # Создаем имя файла на основе текущей даты и времени
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"training_data_{timestamp}.jsonl"
        filepath = os.path.join(self.training_data_dir, filename)
        
        # Записываем в JSONL файл
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            for dialog in formatted_data:
                await f.write(json.dumps(dialog, ensure_ascii=False) + '\n')
                
        logger.info(f"Prepared {len(formatted_data)} dialogs for training, saved to {filepath}")
        return filepath
        
    async def save_conversation_for_training(self, conversation_id: str, quality_score: Optional[int] = None) -> bool:
        """
        Сохраняет беседу для последующего использования в обучении.
        
        Args:
            conversation_id: ID беседы
            quality_score: Оценка качества диалога (опционально)
            
        Returns:
            bool: True, если операция выполнена успешно
        """
        metadata = {
            "source": "user_dialog",
            "saved_by": "automatic_system",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.mongodb_service.save_for_training(
            conversation_id=conversation_id,
            quality_score=quality_score,
            metadata=metadata
        ) 