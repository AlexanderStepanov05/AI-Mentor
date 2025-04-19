#!/bin/bash

# Скрипт для запуска обучения модели на собственных данных
# Использование: ./train_model.sh [опции]

# Установка переменных по умолчанию
DATA_DIR="data"
MODEL_NAME="all-MiniLM-L6-v2"
TRAIN=false

# Обработка аргументов командной строки
while [[ $# -gt 0 ]]; do
  case $1 in
    --csv)
      CSV_PATH="$2"
      shift 2
      ;;
    --text-dir)
      TEXT_DIR="$2"
      shift 2
      ;;
    --urls)
      URLS_FILE="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --model-name)
      MODEL_NAME="$2"
      shift 2
      ;;
    --train)
      TRAIN=true
      shift
      ;;
    *)
      echo "Неизвестный аргумент: $1"
      exit 1
      ;;
  esac
done

# Создание директории для данных, если она не существует
mkdir -p $DATA_DIR

# Формирование команды запуска
CMD="python -m app.training.data_ingestion"

if [ "$TRAIN" = true ]; then
  CMD="$CMD --train"
fi

CMD="$CMD --model-name $MODEL_NAME"

if [ ! -z "$CSV_PATH" ]; then
  CMD="$CMD --csv $CSV_PATH"
fi

if [ ! -z "$TEXT_DIR" ]; then
  CMD="$CMD --text-dir $TEXT_DIR"
fi

if [ ! -z "$URLS_FILE" ]; then
  CMD="$CMD --urls $URLS_FILE"
fi

if [ ! -z "$OUTPUT_DIR" ]; then
  CMD="$CMD --output-dir $OUTPUT_DIR"
else
  CMD="$CMD --output-dir $DATA_DIR"
fi

# Запуск команды
echo "Запуск обучения модели..."
echo $CMD
eval $CMD

# Проверка результата выполнения
if [ $? -eq 0 ]; then
  echo "Обучение модели успешно завершено!"
  echo "Индекс FAISS сохранен в директории: app/models/"
else
  echo "Произошла ошибка при обучении модели."
  exit 1
fi 