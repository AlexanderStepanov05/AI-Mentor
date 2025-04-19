from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Схема для сообщения в беседе."""
    role: str = Field(..., description="Роль отправителя (user/assistant)")
    content: str = Field(..., description="Содержание сообщения")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время отправки сообщения")

class ConversationBase(BaseModel):
    """Базовая схема для беседы."""
    user_id: Optional[str] = Field(None, description="ID пользователя")
    title: Optional[str] = Field(None, description="Название беседы")
    
class ConversationCreate(ConversationBase):
    """Схема для создания новой беседы."""
    query: str = Field(..., description="Первый запрос пользователя")

class ConversationUpdate(BaseModel):
    """Схема для обновления существующей беседы."""
    query: str = Field(..., description="Новый запрос пользователя")

class ConversationResponse(ConversationBase):
    """Схема для ответа на запрос беседы."""
    id: str = Field(..., description="ID беседы")
    messages: List[Message] = Field(..., description="Сообщения в беседе")
    created_at: datetime = Field(..., description="Время создания беседы")
    updated_at: datetime = Field(..., description="Время последнего обновления беседы")
    
    class Config:
        from_attributes = True

class MessageRequest(BaseModel):
    """Схема для запроса нового сообщения."""
    conversation_id: str = Field(..., description="ID беседы")
    query: str = Field(..., description="Запрос пользователя")

class MessageResponse(BaseModel):
    """Схема для ответа на запрос нового сообщения."""
    conversation_id: str = Field(..., description="ID беседы")
    response: str = Field(..., description="Ответ от ментора")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Время ответа") 