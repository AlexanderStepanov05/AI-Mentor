#!/bin/bash
# Скрипт для запуска периодического процесса дообучения модели
# Рекомендуется запускать через cron, например:
# 0 3 * * 0 /path/to/schedule_training.sh > /path/to/logs/training_$(date +\%Y\%m\%d).log 2>&1

# Переходим в директорию проекта
cd "$(dirname "$0")/../.."
BASE_DIR=$(pwd)

# Устанавливаем переменные окружения
export PYTHONPATH="$BASE_DIR"
source .env

# Директории для данных и моделей
export TRAINING_DATA_DIR="$BASE_DIR/app/training/data"
export MODELS_DIR="$BASE_DIR/app/models"

# Создаем директории, если они не существуют
mkdir -p "$TRAINING_DATA_DIR"
mkdir -p "$MODELS_DIR"

# Текущее время для логов
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Запуск процесса дообучения модели"

# Активируем виртуальное окружение, если оно используется
if [ -d "venv_new" ]; then
    source venv_new/bin/activate
    echo "[$TIMESTAMP] Активировано виртуальное окружение: venv_new"
fi

# Запускаем процесс дообучения
echo "[$TIMESTAMP] Запуск скрипта обучения..."
python -m app.training.train_model --min_dialogs 50 --min_quality 3

# Проверяем результат выполнения
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Процесс дообучения модели завершен успешно"
else
    echo "[$TIMESTAMP] Ошибка при дообучении модели"
    exit 1
fi

# Обновляем конфигурацию (в реальном проекте здесь могла бы быть 
# дополнительная логика для обновления конфигурации)
echo "[$TIMESTAMP] Обновление конфигурации модели..."

# Деактивируем виртуальное окружение, если оно было активировано
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
    echo "[$TIMESTAMP] Деактивировано виртуальное окружение"
fi

echo "[$TIMESTAMP] Процесс дообучения модели и обновления конфигурации завершен"
exit 0 