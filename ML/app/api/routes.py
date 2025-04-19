from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from typing import List, Dict, Any, Optional

from app.ml_engine.mistral_client import MistralAIService
from app.database.mongodb import MongoDBService
from app.database.redis_cache import RedisService
from app.services.message_queue import RabbitMQService
from app.schemas.conversation import (
    ConversationCreate, ConversationResponse, 
    MessageRequest, MessageResponse,
    ConversationUpdate
)

router = APIRouter()

# Инициализация сервисов
mistral_service = MistralAIService()
mongodb_service = MongoDBService()
redis_service = RedisService()
rabbitmq_service = RabbitMQService()

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    background_tasks: BackgroundTasks
):
    """
    Создание новой беседы с первым запросом пользователя.
    """
    try:
        # Проверяем кэш для похожих запросов
        cache_key = f"query:{conversation.query.lower()[:50]}"
        cached_response = await redis_service.get(cache_key)
        
        if cached_response:
            # Используем кэшированный ответ, но все равно сохраняем беседу
            conversation_data = {
                "user_id": conversation.user_id,
                "title": conversation.title or conversation.query[:30],
                "messages": [
                    {"role": "user", "content": conversation.query},
                    {"role": "assistant", "content": cached_response["response"]}
                ]
            }
        else:
            # Отправляем запрос в Mistral AI
            conversation_data = await mistral_service.create_conversation(conversation.query)
            
            if conversation.user_id:
                conversation_data["user_id"] = conversation.user_id
            if conversation.title:
                conversation_data["title"] = conversation.title
            else:
                conversation_data["title"] = conversation.query[:30]
                
            # Кэшируем ответ
            await redis_service.set(
                cache_key, 
                {"response": conversation_data["messages"][1]["content"]},
                expire=3600  # Кэш на 1 час
            )
        
        # Сохраняем беседу в MongoDB
        conversation_id = await mongodb_service.create_conversation(conversation_data)
        
        # Подготавливаем ответ
        response_data = {
            "id": conversation_id,
            "user_id": conversation_data.get("user_id"),
            "title": conversation_data.get("title"),
            "messages": conversation_data["messages"],
            "created_at": conversation_data.get("created_at"),
            "updated_at": conversation_data.get("updated_at")
        }
        
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    message: ConversationUpdate,
    background_tasks: BackgroundTasks
):
    """
    Добавление нового сообщения в существующую беседу.
    """
    try:
        # Получаем беседу из MongoDB
        conversation = await mongodb_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Проверяем кэш для похожих запросов
        cache_key = f"query:{message.query.lower()[:50]}"
        cached_response = await redis_service.get(cache_key)
        
        if cached_response:
            # Используем кэшированный ответ
            response_text = cached_response["response"]
        else:
            # Получаем историю сообщений
            history = conversation.get("messages", [])
            
            # Отправляем запрос в Mistral AI
            response_text = await mistral_service.continue_conversation(
                conversation_id, message.query, history
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
            {"role": "user", "content": message.query}
        )
        
        # Добавляем ответ ассистента в историю
        await mongodb_service.update_conversation(
            conversation_id, 
            {"role": "assistant", "content": response_text}
        )
        
        return {
            "conversation_id": conversation_id,
            "response": response_text,
            "timestamp": conversation.get("updated_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding message: {str(e)}"
        )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    user_id: str,
    skip: int = 0,
    limit: int = 10
):
    """
    Получение списка бесед пользователя.
    """
    try:
        conversations = await mongodb_service.get_user_conversations(user_id, limit, skip)
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversations: {str(e)}"
        )

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """
    Получение беседы по ID.
    """
    try:
        conversation = await mongodb_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation: {str(e)}"
        )

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str):
    """
    Удаление беседы.
    """
    try:
        success = await mongodb_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        ) 