import logging
from typing import List, Dict, Any, Optional

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from app.config.settings import settings
from app.schemas.conversation import ConversationCreate

logger = logging.getLogger(__name__)

class MistralAIService:
    """Сервис для работы с Mistral AI API."""
    
    def __init__(self):
        """Инициализация клиента Mistral AI."""
        self.client = MistralClient(api_key=settings.mistral_api_key)
        self.model = settings.mistral_model
        logger.info(f"Initialized Mistral AI client with model: {self.model}")
    
    async def process_query(self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Обработка запроса пользователя с использованием Mistral AI.
        
        Args:
            query: Текст запроса пользователя
            conversation_history: История предыдущих сообщений в формате [{role: user/assistant, content: text}]
            
        Returns:
            str: Ответ модели
        """
        try:
            messages = []
            
            # Добавляем историю беседы, если она есть
            if conversation_history:
                for msg in conversation_history:
                    messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
            
            # Добавляем текущий запрос пользователя
            messages.append(ChatMessage(role="user", content=query))
            
            logger.debug(f"Sending request to Mistral AI with {len(messages)} messages")
            
            # Вызов API Mistral
            chat_response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            
            # Извлечение ответа
            response_text = chat_response.choices[0].message.content
            
            logger.debug(f"Received response from Mistral AI: {response_text[:100]}...")
            return response_text
            
        except Exception as e:
            logger.error(f"Error processing query with Mistral AI: {e}")
            raise
    
    async def create_conversation(self, query: str) -> Dict[str, Any]:
        """
        Создание новой беседы с первым запросом пользователя.
        
        Args:
            query: Первый запрос пользователя
            
        Returns:
            Dict: Информация о созданной беседе
        """
        response = await self.process_query(query)
        
        conversation_data = {
            "messages": [
                {"role": "user", "content": query},
                {"role": "assistant", "content": response}
            ]
        }
        
        return conversation_data
    
    async def continue_conversation(self, conversation_id: str, query: str, 
                                   conversation_history: List[Dict[str, str]]) -> str:
        """
        Продолжение существующей беседы.
        
        Args:
            conversation_id: ID существующей беседы
            query: Новый запрос пользователя
            conversation_history: История сообщений
            
        Returns:
            str: Ответ модели
        """
        return await self.process_query(query, conversation_history) 