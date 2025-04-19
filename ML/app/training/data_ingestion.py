import os
import json
import logging
import argparse
from typing import List, Dict, Any, Optional
import pandas as pd
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import time
import csv

from app.training.train_utils import TrainingUtils

logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    """
    Пайплайн для импорта и подготовки данных для обучения модели.
    """
    
    def __init__(self, output_dir: str = "app/data"):
        """
        Инициализация пайплайна для импорта данных.
        
        Args:
            output_dir: Директория для сохранения импортированных данных
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def ingest_from_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        Импорт данных из CSV-файла.
        
        Args:
            csv_path: Путь к CSV-файлу
            
        Returns:
            List[Dict]: Список импортированных документов
        """
        try:
            documents = []
            df = pd.read_csv(csv_path)
            
            # Предполагаем, что CSV-файл содержит колонки 'title' и 'content'
            for _, row in df.iterrows():
                document = {
                    "title": row["title"] if "title" in df.columns else "",
                    "text": row["content"] if "content" in df.columns else row["text"],
                    "source": "csv",
                    "source_url": csv_path
                }
                documents.append(document)
            
            self.logger.info(f"Ingested {len(documents)} documents from CSV: {csv_path}")
            return documents
        except Exception as e:
            self.logger.error(f"Error ingesting data from CSV: {e}")
            raise
            
    def ingest_from_text_files(self, directory: str) -> List[Dict[str, Any]]:
        """
        Импорт данных из текстовых файлов в директории.
        
        Args:
            directory: Путь к директории с текстовыми файлами
            
        Returns:
            List[Dict]: Список импортированных документов
        """
        try:
            documents = []
            
            for filename in os.listdir(directory):
                if filename.endswith(".txt"):
                    file_path = os.path.join(directory, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    document = {
                        "title": os.path.splitext(filename)[0],
                        "text": content,
                        "source": "text_file",
                        "source_url": file_path
                    }
                    documents.append(document)
            
            self.logger.info(f"Ingested {len(documents)} documents from directory: {directory}")
            return documents
        except Exception as e:
            self.logger.error(f"Error ingesting data from text files: {e}")
            raise
            
    def ingest_from_web(self, urls: List[str], delay: int = 1) -> List[Dict[str, Any]]:
        """
        Импорт данных с веб-страниц.
        
        Args:
            urls: Список URL-адресов для импорта
            delay: Задержка между запросами в секундах
            
        Returns:
            List[Dict]: Список импортированных документов
        """
        try:
            documents = []
            
            for url in urls:
                try:
                    # Задержка между запросами для предотвращения блокировки
                    time.sleep(delay)
                    
                    response = requests.get(url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    })
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Удаление ненужных тегов
                    for tag in soup(["script", "style", "meta", "link", "noscript"]):
                        tag.decompose()
                    
                    # Получение заголовка страницы
                    title = soup.title.text if soup.title else urlparse(url).netloc
                    
                    # Получение основного текста
                    text = " ".join([p.text for p in soup.find_all("p")])
                    
                    document = {
                        "title": title,
                        "text": text,
                        "source": "web",
                        "source_url": url
                    }
                    documents.append(document)
                    
                    self.logger.info(f"Ingested document from URL: {url}")
                except Exception as e:
                    self.logger.error(f"Error ingesting data from URL {url}: {e}")
            
            return documents
        except Exception as e:
            self.logger.error(f"Error ingesting data from web: {e}")
            raise
            
    def save_documents(self, documents: List[Dict[str, Any]], filename: str = "ingested_data.json") -> str:
        """
        Сохранение импортированных документов в файл.
        
        Args:
            documents: Список документов для сохранения
            filename: Имя файла для сохранения
            
        Returns:
            str: Путь к сохраненному файлу
        """
        try:
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved {len(documents)} documents to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error saving documents: {e}")
            raise
            
    def process_and_train(self, documents: List[Dict[str, Any]], model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Обработка импортированных документов и обучение модели.
        
        Args:
            documents: Список документов для обучения
            model_name: Название модели для эмбеддингов
        """
        try:
            # Инициализация утилит для обучения
            training_utils = TrainingUtils(model_name=model_name)
            
            # Обучение на импортированных документах
            training_utils.train_on_documents(documents)
            
            self.logger.info(f"Trained model on {len(documents)} documents")
        except Exception as e:
            self.logger.error(f"Error processing and training: {e}")
            raise
            
def main():
    """Точка входа для запуска импорта данных из командной строки."""
    parser = argparse.ArgumentParser(description="Data ingestion pipeline for mentor model training")
    
    parser.add_argument("--csv", type=str, help="Path to CSV file for ingestion")
    parser.add_argument("--text-dir", type=str, help="Path to directory with text files for ingestion")
    parser.add_argument("--urls", type=str, help="Path to file with URLs for ingestion (one URL per line)")
    parser.add_argument("--output-dir", type=str, default="app/data", help="Output directory for ingested data")
    parser.add_argument("--train", action="store_true", help="Train model on ingested data")
    parser.add_argument("--model-name", type=str, default="all-MiniLM-L6-v2", help="Model name for embeddings")
    
    args = parser.parse_args()
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    pipeline = DataIngestionPipeline(output_dir=args.output_dir)
    documents = []
    
    # Импорт данных из различных источников
    if args.csv:
        csv_documents = pipeline.ingest_from_csv(args.csv)
        documents.extend(csv_documents)
        
    if args.text_dir:
        text_documents = pipeline.ingest_from_text_files(args.text_dir)
        documents.extend(text_documents)
        
    if args.urls:
        with open(args.urls, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
        web_documents = pipeline.ingest_from_web(urls)
        documents.extend(web_documents)
    
    if documents:
        # Сохранение импортированных документов
        pipeline.save_documents(documents)
        
        # Обучение модели, если указан флаг --train
        if args.train:
            pipeline.process_and_train(documents, model_name=args.model_name)
    else:
        logger.warning("No data was ingested. Please provide at least one data source.")

if __name__ == "__main__":
    main() 