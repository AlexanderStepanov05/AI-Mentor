import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import motor.motor_asyncio
from bson import ObjectId
from pymongo.errors import PyMongoError

from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBService:
    """Сервис для работы с MongoDB."""
    
    def __init__(self):
        """Инициализация соединения с MongoDB."""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
            self.db = self.client[settings.mongo_db]
            self.conversations = self.db[settings.mongo_collection]
            self.training_data = self.db["training_data"]
            logger.info(f"Connected to MongoDB: {settings.mongo_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def create_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """
        Создание новой беседы в базе данных.
        
        Args:
            conversation_data: Данные о беседе
            
        Returns:
            str: ID созданной беседы
        """
        try:
            # Добавляем метаданные
            conversation_data.update({
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            result = await self.conversations.insert_one(conversation_data)
            conversation_id = str(result.inserted_id)
            logger.info(f"Created new conversation with ID: {conversation_id}")
            return conversation_id
        except PyMongoError as e:
            logger.error(f"Error creating conversation in MongoDB: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение беседы по ID.
        
        Args:
            conversation_id: ID беседы
            
        Returns:
            Dict: Данные о беседе или None, если беседа не найдена
        """
        try:
            conversation = await self.conversations.find_one({"_id": ObjectId(conversation_id)})
            if conversation:
                conversation["id"] = str(conversation.pop("_id"))
                return conversation
            return None
        except PyMongoError as e:
            logger.error(f"Error getting conversation from MongoDB: {e}")
            raise
    
    async def update_conversation(self, conversation_id: str, message: Dict[str, str]) -> bool:
        """
        Добавление нового сообщения в существующую беседу.
        
        Args:
            conversation_id: ID беседы
            message: Данные о новом сообщении
            
        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            message["timestamp"] = datetime.utcnow()
            result = await self.conversations.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            success = result.modified_count > 0
            if success:
                logger.info(f"Added new message to conversation {conversation_id}")
            else:
                logger.warning(f"Failed to add message to conversation {conversation_id}")
            return success
        except PyMongoError as e:
            logger.error(f"Error updating conversation in MongoDB: {e}")
            raise
    
    async def get_user_conversations(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Получение списка бесед пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество бесед
            skip: Количество пропускаемых бесед (для пагинации)
            
        Returns:
            List[Dict]: Список бесед пользователя
        """
        try:
            conversations = []
            cursor = self.conversations.find({"user_id": user_id}) \
                .sort("updated_at", -1) \
                .skip(skip) \
                .limit(limit)
            
            async for conversation in cursor:
                conversation["id"] = str(conversation.pop("_id"))
                conversations.append(conversation)
            
            return conversations
        except PyMongoError as e:
            logger.error(f"Error getting user conversations from MongoDB: {e}")
            raise
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Удаление беседы.
        
        Args:
            conversation_id: ID беседы
            
        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            result = await self.conversations.delete_one({"_id": ObjectId(conversation_id)})
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted conversation {conversation_id}")
            else:
                logger.warning(f"Failed to delete conversation {conversation_id}")
            return success
        except PyMongoError as e:
            logger.error(f"Error deleting conversation from MongoDB: {e}")
            raise
    
    async def save_for_training(self, conversation_id: str, quality_score: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Сохраняет диалог для использования в дообучении модели.
        
        Args:
            conversation_id: ID беседы
            quality_score: Оценка качества диалога (опционально, от 1 до 5)
            metadata: Дополнительные метаданные о диалоге (опционально)
            
        Returns:
            bool: True, если операция выполнена успешно
        """
        try:
            # Получаем беседу
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found, cannot save for training")
                return False
                
            # Форматируем диалог для обучения
            training_entry = {
                "conversation_id": conversation_id,
                "messages": conversation.get("messages", []),
                "quality_score": quality_score,
                "saved_for_training": True,
                "saved_at": datetime.utcnow(),
                "model_version": settings.mistral_model,
                "metadata": metadata or {}
            }
            
            # Сохраняем в коллекцию для обучения
            result = await self.training_data.insert_one(training_entry)
            
            # Обновляем статус оригинальной беседы
            await self.conversations.update_one(
                {"_id": ObjectId(conversation_id)},
                {"$set": {"saved_for_training": True}}
            )
            
            logger.info(f"Saved conversation {conversation_id} for training")
            return True
        except PyMongoError as e:
            logger.error(f"Error saving conversation for training: {e}")
            raise
            
    async def get_training_data(self, limit: int = 100, min_quality_score: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получает данные для обучения модели.
        
        Args:
            limit: Максимальное количество диалогов
            min_quality_score: Минимальная оценка качества (если указана)
            
        Returns:
            List[Dict]: Список диалогов для обучения
        """
        try:
            query = {}
            if min_quality_score is not None:
                query["quality_score"] = {"$gte": min_quality_score}
                
            training_data = []
            cursor = self.training_data.find(query).limit(limit)
            
            async for entry in cursor:
                entry["id"] = str(entry.pop("_id"))
                training_data.append(entry)
                
            return training_data
        except PyMongoError as e:
            logger.error(f"Error getting training data: {e}")
            raise 