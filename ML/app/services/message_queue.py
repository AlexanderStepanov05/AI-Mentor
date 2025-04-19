import json
import logging
import asyncio
from typing import Dict, Any, Callable, Awaitable
import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.config.settings import settings

logger = logging.getLogger(__name__)

class RabbitMQService:
    """Сервис для работы с RabbitMQ для асинхронной обработки сообщений."""
    
    def __init__(self):
        """Инициализация соединения с RabbitMQ."""
        self.connection = None
        self.channel = None
        self.queue_name = settings.rabbitmq_queue
        self.rabbitmq_url = f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}"\
                           f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}/{settings.rabbitmq_vhost}"
        logger.info(f"Initializing RabbitMQ connection to {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    
    async def connect(self) -> None:
        """Установление соединения с RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            await self.channel.declare_queue(self.queue_name, durable=True)
            logger.info(f"Connected to RabbitMQ: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def close(self) -> None:
        """Закрытие соединения с RabbitMQ."""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
    
    async def publish_message(self, message: Dict[str, Any]) -> None:
        """
        Публикация сообщения в очередь.
        
        Args:
            message: Сообщение для публикации
        """
        if not self.connection or self.connection.is_closed:
            await self.connect()
            
        try:
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=self.queue_name
            )
            logger.debug(f"Published message to queue {self.queue_name}")
        except Exception as e:
            logger.error(f"Error publishing message to RabbitMQ: {e}")
            raise
    
    async def consume_messages(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Получение и обработка сообщений из очереди.
        
        Args:
            callback: Функция обратного вызова для обработки сообщений
        """
        if not self.connection or self.connection.is_closed:
            await self.connect()
            
        async def process_message(message: AbstractIncomingMessage) -> None:
            async with message.process():
                try:
                    message_body = json.loads(message.body.decode())
                    logger.debug(f"Received message from queue {self.queue_name}")
                    await callback(message_body)
                except Exception as e:
                    logger.error(f"Error processing message from RabbitMQ: {e}")
                    # Можно добавить логику обработки ошибок, например, отправку в очередь ошибок
        
        queue = await self.channel.declare_queue(self.queue_name, durable=True)
        await queue.consume(process_message)
        logger.info(f"Started consuming messages from queue {self.queue_name}")
        
        # Бесконечный цикл для поддержания работы консьюмера
        while True:
            await asyncio.sleep(1)
            
    async def start_worker(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Запуск воркера для обработки сообщений из очереди.
        
        Args:
            callback: Функция обратного вызова для обработки сообщений
        """
        try:
            await self.connect()
            await self.consume_messages(callback)
        except Exception as e:
            logger.error(f"Error starting worker: {e}")
            await self.close()
            raise 