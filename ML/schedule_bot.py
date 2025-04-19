#!/usr/bin/env python3
"""
Бот для ответов на вопросы о расписании с использованием Mistral AI API.
Бот обогащает запрос пользователя контекстом из файла расписания.
"""

import os
import csv
import json
import argparse
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse
import urllib.error
import ssl
import json

# API-ключ Mistral AI
MISTRAL_API_KEY = "5on1LpVk7OysL7d3jWhtzqKwjkqFwr69"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def load_csv_data(file_path: str) -> List[Dict[str, str]]:
    """
    Загружает данные из CSV-файла.
    
    Args:
        file_path: Путь к CSV-файлу с расписанием
        
    Returns:
        List[Dict]: Список строк из CSV-файла
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        print(f"Загружено {len(data)} строк из файла {file_path}")
        return data
    except Exception as e:
        print(f"Ошибка при загрузке CSV-файла: {e}")
        return []

def load_text_data(file_path: str) -> str:
    """
    Загружает дополнительные данные из текстового файла.
    
    Args:
        file_path: Путь к текстовому файлу
        
    Returns:
        str: Содержимое файла
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Загружен файл {file_path}")
        return content
    except Exception as e:
        print(f"Ошибка при загрузке текстового файла: {e}")
        return ""

def format_csv_to_text(csv_data: List[Dict[str, str]]) -> str:
    """
    Преобразует данные из CSV в текстовый формат для лучшего понимания моделью.
    
    Args:
        csv_data: Список строк из CSV-файла
        
    Returns:
        str: Текстовое представление расписания
    """
    text = "РАСПИСАНИЕ ЗАНЯТИЙ:\n\n"
    
    current_day = None
    
    for row in csv_data:
        day = row.get("День", "")
        time = row.get("Время", "")
        
        if day and day != current_day:
            text += f"\n==== {day.upper()} ====\n\n"
            current_day = day
        
        if time:
            text += f"{time}:\n"
        
        for direction in ["Север", "Юг", "Запад", "Восток"]:
            if direction in row and row[direction]:
                text += f"- {direction}: {row[direction]}\n"
        
        text += "\n"
    
    return text

def create_prompt(query: str, csv_data: List[Dict[str, str]], 
                 description: str, faq: str) -> str:
    """
    Создает запрос для модели с контекстом расписания.
    
    Args:
        query: Вопрос пользователя
        csv_data: Данные расписания из CSV
        description: Описание структуры расписания
        faq: Часто задаваемые вопросы
        
    Returns:
        str: Запрос для модели
    """
    # Форматируем CSV в текст
    schedule_text = format_csv_to_text(csv_data)
    
    # Создаем контекст
    context = f"""Ты - ассистент, который помогает отвечать на вопросы о расписании занятий. 
У тебя есть следующая информация о расписании:

{description}

Вот само расписание:
{schedule_text}

Часто задаваемые вопросы и ответы на них:
{faq}

Используй эту информацию для ответа на вопрос пользователя. Отвечай четко, точно и по существу.
"""
    
    prompt = f"""Используй контекст расписания для ответа на вопрос пользователя.

Контекст:
{context}

Вопрос пользователя: {query}

Дай развернутый и точный ответ, основываясь на предоставленном контексте."""
    
    return prompt

def call_mistral_api(prompt: str, max_tokens: int = 1024, 
                    temperature: float = 0.7) -> str:
    """
    Вызывает API Mistral AI для генерации ответа.
    
    Args:
        prompt: Запрос для модели
        max_tokens: Максимальное количество токенов в ответе
        temperature: Температура генерации
        
    Returns:
        str: Ответ модели
    """
    # Создаем JSON-данные для запроса
    data = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # Преобразуем данные в JSON-строку
    data = json.dumps(data).encode('utf-8')
    
    # Создаем HTTP-запрос
    req = urllib.request.Request(MISTRAL_API_URL, data=data)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    req.add_header('Authorization', f'Bearer {MISTRAL_API_KEY}')
    
    # Игнорируем проверку SSL-сертификата (не рекомендуется для производственной среды)
    context = ssl._create_unverified_context()
    
    try:
        # Отправляем запрос и получаем ответ
        with urllib.request.urlopen(req, context=context) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        print(f"Ошибка при вызове API Mistral: {e}")
        return f"Произошла ошибка при обработке запроса: {str(e)}"
    except json.JSONDecodeError as e:
        print(f"Ошибка при декодировании JSON: {e}")
        return f"Произошла ошибка при обработке ответа: {str(e)}"
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return f"Произошла неизвестная ошибка: {str(e)}"

def main():
    """Основная функция для запуска бота."""
    parser = argparse.ArgumentParser(description="Бот для ответов на вопросы о расписании")
    parser.add_argument("--csv", type=str, default="data/tabs.csv", 
                      help="Путь к CSV-файлу с расписанием")
    parser.add_argument("--description", type=str, default="data/schedule_description.txt", 
                      help="Путь к файлу с описанием расписания")
    parser.add_argument("--faq", type=str, default="data/schedule_faq.txt", 
                      help="Путь к файлу с часто задаваемыми вопросами")
    
    args = parser.parse_args()
    
    # Загрузка данных
    csv_data = load_csv_data(args.csv)
    description = load_text_data(args.description)
    faq = load_text_data(args.faq)
    
    if not csv_data:
        print("Ошибка: Не удалось загрузить данные расписания")
        return
    
    print("\nБот для ответов на вопросы о расписании")
    print("Введите 'выход' для завершения работы\n")
    
    while True:
        # Получаем вопрос пользователя
        query = input("Ваш вопрос: ")
        
        if query.lower() in ["выход", "exit", "quit", "q"]:
            print("До свидания!")
            break
        
        # Создаем запрос для модели
        prompt = create_prompt(query, csv_data, description, faq)
        
        # Вызываем API Mistral
        print("\nОбрабатываю запрос...")
        answer = call_mistral_api(prompt)
        
        # Выводим ответ
        print(f"\nОтвет: {answer}\n")

if __name__ == "__main__":
    main() 