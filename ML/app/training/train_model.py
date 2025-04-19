#!/usr/bin/env python3
"""
Скрипт для дообучения модели на основе сохраненных диалогов пользователей.
Запускается как периодическая задача (например, раз в сутки или неделю).
"""

import os
import logging
import asyncio
import argparse
import subprocess
from datetime import datetime
from typing import Optional

from app.database.mongodb import MongoDBService
from app.training.training_service import TrainingService
from app.config.settings import settings

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def run_training(min_dialogs: int = 100, min_quality_score: int = 3) -> bool:
    """
    Запуск процесса дообучения модели.
    
    Args:
        min_dialogs: Минимальное количество диалогов для запуска обучения
        min_quality_score: Минимальная оценка качества диалогов
        
    Returns:
        bool: True, если обучение выполнено успешно
    """
    try:
        # Инициализируем сервисы
        mongodb_service = MongoDBService()
        training_service = TrainingService(mongodb_service)
        
        # Подготавливаем данные для обучения
        training_data_path = await training_service.prepare_training_data(
            limit=5000,  # Максимальное количество диалогов
            min_quality_score=min_quality_score
        )
        
        if not training_data_path:
            logger.warning("No training data available or insufficient data")
            return False
            
        # Определяем папки и имена файлов для обучения
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.environ.get("MODELS_DIR", "app/models"), f"finetuned_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Формируем команду для запуска обучения
        # Пример для Mistral, может отличаться в зависимости от используемого фреймворка
        command = [
            "python", "-m", "app.training.finetune",
            "--data_path", training_data_path,
            "--output_dir", output_dir,
            "--base_model", settings.mistral_model,
            "--epochs", "3",
            "--learning_rate", "2e-5",
            "--batch_size", "4",
            "--gradient_accumulation_steps", "8"
        ]
        
        # Запускаем процесс обучения
        logger.info(f"Starting model training with command: {' '.join(command)}")
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode != 0:
            logger.error(f"Training failed: {process.stderr}")
            return False
        
        logger.info(f"Model training completed successfully. Model saved to {output_dir}")
        
        # Обновляем конфигурацию, чтобы использовать новую модель
        # В реальности здесь была бы логика для обновления указателя на текущую модель
        # и, возможно, системы A/B тестирования
        
        return True
    except Exception as e:
        logger.error(f"Error during model training: {e}", exc_info=True)
        return False

async def main():
    """Основная функция для запуска процесса дообучения."""
    parser = argparse.ArgumentParser(description="Запуск дообучения модели")
    parser.add_argument("--min_dialogs", type=int, default=100, 
                      help="Минимальное количество диалогов для запуска обучения")
    parser.add_argument("--min_quality", type=int, default=3, 
                      help="Минимальная оценка качества диалогов (1-5)")
    parser.add_argument("--force", action="store_true", 
                      help="Принудительный запуск обучения даже при недостатке данных")
    
    args = parser.parse_args()
    
    logger.info("Starting model training process")
    
    # Запускаем обучение
    success = await run_training(
        min_dialogs=0 if args.force else args.min_dialogs,
        min_quality_score=args.min_quality
    )
    
    if success:
        logger.info("Model training completed successfully")
    else:
        logger.warning("Model training failed or was skipped")

if __name__ == "__main__":
    asyncio.run(main()) 