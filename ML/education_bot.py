#!/usr/bin/env python3
"""
Бот для ответов на вопросы о расписании и курсах с использованием Mistral AI API.
Бот обогащает запрос пользователя контекстом из файлов с расписанием и описаниями курсов.
"""

import os
import csv
import json
import argparse
import re
import random
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse
import urllib.error
import ssl
import json

# API-ключ Mistral AI
MISTRAL_API_KEY = "5on1LpVk7OysL7d3jWhtzqKwjkqFwr69"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Приветствия
GREETINGS = [
    "Привет! Я образовательный ассистент. Чем могу помочь?",
    "Здравствуйте! Я готов ответить на ваши вопросы о расписании и курсах.",
    "Добрый день! Спрашивайте о расписании или курсах, и я с радостью помогу вам.",
    "Приветствую! Я помогу вам разобраться с расписанием занятий и содержанием курсов."
]

# Фразы для продолжения диалога
FOLLOW_UP_PHRASES = [
    "Могу ли я помочь вам еще с чем-нибудь?",
    "У вас есть еще вопросы по этой теме?",
    "Вам нужна дополнительная информация?",
    "Интересует ли вас что-то еще по этому курсу или расписанию?",
    "Есть ли у вас другие вопросы, на которые я могу ответить?"
]

def load_csv_data(file_path: str) -> List[Dict[str, str]]:
    """
    Загружает данные из CSV-файла.
    
    Args:
        file_path: Путь к CSV-файлу
        
    Returns:
        List[Dict]: Список строк из CSV-файла
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Очищаем значения от специальных символов
                cleaned_row = {k: clean_text(v) for k, v in row.items()}
                data.append(cleaned_row)
        print(f"Загружено {len(data)} строк из файла {file_path}")
        return data
    except Exception as e:
        print(f"Ошибка при загрузке CSV-файла: {e}")
        return []

def clean_text(text: str) -> str:
    """
    Очищает текст от специальных символов и лишних пробелов.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Очищенный текст
    """
    if not isinstance(text, str):
        return str(text)
    
    # Заменяем специальные символы
    text = text.replace("*", "").replace("#", "")
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_text_data(file_path: str) -> str:
    """
    Загружает данные из текстового файла.
    
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

def format_schedule_to_text(csv_data: List[Dict[str, str]]) -> str:
    """
    Преобразует данные из CSV с расписанием в текстовый формат.
    
    Args:
        csv_data: Список строк из CSV-файла с расписанием
        
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

def format_handbook_to_text(csv_data: List[Dict[str, str]]) -> str:
    """
    Преобразует данные из CSV со справочником курсов в текстовый формат.
    
    Args:
        csv_data: Список строк из CSV-файла со справочником
        
    Returns:
        str: Текстовое представление справочника курсов
    """
    text = "СПРАВОЧНИК КУРСОВ:\n\n"
    
    for row in csv_data:
        predmet = row.get("Предмет", "")
        if predmet:
            text += f"==== {predmet.upper()} ====\n\n"
            
            for key, value in row.items():
                if key != "Предмет" and value:
                    text += f"{key}: {value}\n\n"
            
            text += "----------\n\n"
    
    return text

def create_prompt(query: str, schedule_data: List[Dict[str, str]], 
                 schedule_description: str, schedule_faq: str,
                 handbook_data: List[Dict[str, str]],
                 handbook_description: str, handbook_faq: str,
                 conversation_history: List[Dict[str, str]] = None) -> str:
    """
    Создает запрос для модели с контекстом расписания и справочника курсов.
    
    Args:
        query: Вопрос пользователя
        schedule_data: Данные расписания из CSV
        schedule_description: Описание структуры расписания
        schedule_faq: Часто задаваемые вопросы о расписании
        handbook_data: Данные справочника курсов из CSV
        handbook_description: Описание структуры справочника
        handbook_faq: Часто задаваемые вопросы о курсах
        conversation_history: История диалога
        
    Returns:
        str: Запрос для модели
    """
    # Форматируем данные в текст
    schedule_text = format_schedule_to_text(schedule_data)
    handbook_text = format_handbook_to_text(handbook_data)
    
    # Формируем историю диалога
    conversation_text = ""
    if conversation_history:
        conversation_text = "История диалога:\n"
        for message in conversation_history:
            role = message.get("role", "")
            content = message.get("content", "")
            conversation_text += f"{role.capitalize()}: {content}\n"
        conversation_text += "\n"
    
    # Создаем контекст
    context = f"""Ты - дружелюбный образовательный ассистент по имени Эду, который помогает отвечать на вопросы о расписании занятий и содержании курсов. 
Твоя задача - предоставлять точную информацию в человечной и доброжелательной манере. 

У тебя есть следующая информация:

=== РАСПИСАНИЕ ЗАНЯТИЙ ===
{schedule_description}

{schedule_text}

=== СПРАВОЧНИК КУРСОВ ===
{handbook_description}

{handbook_text}

=== ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ О РАСПИСАНИИ ===
{schedule_faq}

=== ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ О КУРСАХ ===
{handbook_faq}

{conversation_text}

Используй эту информацию для ответа на вопрос пользователя. 
В конце каждого ответа задавай уточняющий вопрос, чтобы продолжить диалог.
Твои ответы должны быть дружелюбными, персонализированными и помогающими.
"""
    
    prompt = f"""Используй контекст для ответа на вопрос пользователя.

Контекст:
{context}

Вопрос пользователя: {query}

Дай развернутый, точный и дружелюбный ответ, основываясь на предоставленном контексте.
Если вопрос касается расписания, используй данные из расписания.
Если вопрос касается содержания курсов, системы оценивания или требований, используй данные из справочника курсов.
В конце ответа обязательно добавь уточняющий вопрос, например "Интересует ли вас что-то еще по этой теме?" или предложи помощь с чем-то еще.
Твои ответы должны быть человечными и персонализированными."""
    
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

def add_follow_up(answer: str) -> str:
    """
    Добавляет уточняющий вопрос в конец ответа, если его там нет.
    
    Args:
        answer: Исходный ответ
        
    Returns:
        str: Ответ с уточняющим вопросом
    """
    # Проверяем, есть ли уже вопрос в конце ответа
    has_question = re.search(r'[?]\s*$', answer)
    
    if not has_question:
        follow_up = random.choice(FOLLOW_UP_PHRASES)
        answer = f"{answer.rstrip()} {follow_up}"
    
    return answer

def main():
    """Основная функция для запуска бота."""
    parser = argparse.ArgumentParser(description="Образовательный бот для ответов на вопросы о расписании и курсах")
    
    # Аргументы для расписания
    parser.add_argument("--schedule-csv", type=str, default="data/tabs.csv", 
                      help="Путь к CSV-файлу с расписанием")
    parser.add_argument("--schedule-description", type=str, default="data/schedule_description.txt", 
                      help="Путь к файлу с описанием расписания")
    parser.add_argument("--schedule-faq", type=str, default="data/schedule_faq.txt", 
                      help="Путь к файлу с часто задаваемыми вопросами о расписании")
    
    # Аргументы для справочника курсов
    parser.add_argument("--handbook-csv", type=str, default="data/handbook.csv", 
                      help="Путь к CSV-файлу со справочником курсов")
    parser.add_argument("--handbook-description", type=str, default="data/handbook_description.txt", 
                      help="Путь к файлу с описанием справочника курсов")
    parser.add_argument("--handbook-faq", type=str, default="data/handbook_faq.txt", 
                      help="Путь к файлу с часто задаваемыми вопросами о курсах")
    
    args = parser.parse_args()
    
    # Загрузка данных о расписании
    schedule_data = load_csv_data(args.schedule_csv)
    schedule_description = load_text_data(args.schedule_description)
    schedule_faq = load_text_data(args.schedule_faq)
    
    # Загрузка данных о курсах
    handbook_data = load_csv_data(args.handbook_csv)
    handbook_description = load_text_data(args.handbook_description)
    handbook_faq = load_text_data(args.handbook_faq)
    
    if not schedule_data or not handbook_data:
        print("Ошибка: Не удалось загрузить необходимые данные")
        return
    
    print("\n🎓 Образовательный ассистент готов помочь вам! 🎓")
    print("Введите 'выход' для завершения работы\n")
    
    # Выбираем случайное приветствие
    greeting = random.choice(GREETINGS)
    print(f"Ассистент: {greeting}\n")
    
    # История диалога
    conversation_history = []
    
    while True:
        # Получаем вопрос пользователя
        query = input("Ваш вопрос: ")
        
        if query.lower() in ["выход", "exit", "quit", "q"]:
            print("\nАссистент: Было приятно помочь вам! Если у вас возникнут еще вопросы, обращайтесь. До свидания!")
            break
        
        # Добавляем вопрос в историю диалога
        conversation_history.append({"role": "user", "content": query})
        
        # Создаем запрос для модели
        prompt = create_prompt(
            query, 
            schedule_data, schedule_description, schedule_faq,
            handbook_data, handbook_description, handbook_faq,
            conversation_history
        )
        
        # Вызываем API Mistral
        print("\nОбрабатываю запрос...")
        answer = call_mistral_api(prompt)
        
        # Проверяем, есть ли уточняющий вопрос в ответе, и добавляем его, если нет
        answer = add_follow_up(answer)
        
        # Добавляем ответ в историю диалога
        conversation_history.append({"role": "assistant", "content": answer})
        
        # Ограничиваем размер истории диалога последними 6 сообщениями
        if len(conversation_history) > 6:
            conversation_history = conversation_history[-6:]
        
        # Выводим ответ
        print(f"\nАссистент: {answer}\n")

if __name__ == "__main__":
    main() 