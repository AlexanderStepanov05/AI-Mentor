import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
import torch

logger = logging.getLogger(__name__)

class TrainingUtils:
    """Утилиты для обучения и настройки модели на основе собственных данных."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", 
                 index_path: str = "app/models/knowledge_index"):
        """
        Инициализация утилит для обучения.
        
        Args:
            model_name: Название модели Sentence Transformer для эмбеддингов
            index_path: Путь для сохранения индекса
        """
        self.model_name = model_name
        self.index_path = index_path
        self.embedder = None
        self.index = None
        self.documents = []
        self.logger = logging.getLogger(__name__)
        
    def load_embedding_model(self) -> None:
        """Загрузка модели для создания эмбеддингов."""
        try:
            self.embedder = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
            
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Создание эмбеддингов для текстов.
        
        Args:
            texts: Список текстов для эмбеддинга
            
        Returns:
            np.ndarray: Массив эмбеддингов
        """
        if not self.embedder:
            self.load_embedding_model()
            
        try:
            embeddings = self.embedder.encode(texts, show_progress_bar=True, 
                                             convert_to_numpy=True)
            logger.info(f"Created embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
            
    def build_faiss_index(self, embeddings: np.ndarray) -> None:
        """
        Создание FAISS индекса для быстрого поиска по эмбеддингам.
        
        Args:
            embeddings: Массив эмбеддингов
        """
        try:
            # Нормализация векторов для использования с L2 расстоянием
            faiss.normalize_L2(embeddings)
            
            # Создание индекса
            vector_dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(vector_dimension)  # Используем скалярное произведение
            self.index.add(embeddings)
            
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors of dimension {vector_dimension}")
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            raise
            
    def save_index(self) -> None:
        """Сохранение FAISS индекса на диск."""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            with open(f"{self.index_path}_documents.json", 'w') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved FAISS index to {self.index_path}.faiss")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            raise
            
    def load_index(self) -> None:
        """Загрузка FAISS индекса с диска."""
        try:
            self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            with open(f"{self.index_path}_documents.json", 'r') as f:
                self.documents = json.load(f)
                
            logger.info(f"Loaded FAISS index from {self.index_path}.faiss with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            raise
            
    def train_on_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Обучение модели на основе документов.
        
        Args:
            documents: Список документов для обучения
        """
        try:
            # Извлечение текстов из документов
            texts = []
            processed_documents = []
            
            for doc in documents:
                if isinstance(doc, Dict) and 'text' in doc:
                    texts.append(doc['text'])
                    processed_documents.append(doc)
                elif isinstance(doc, str):
                    texts.append(doc)
                    processed_documents.append({'text': doc})
                    
            self.documents = processed_documents
            
            # Создание эмбеддингов и индекса
            if not self.embedder:
                self.load_embedding_model()
                
            embeddings = self.create_embeddings(texts)
            self.build_faiss_index(embeddings)
            self.save_index()
            
            logger.info(f"Trained on {len(texts)} documents")
        except Exception as e:
            logger.error(f"Error training on documents: {e}")
            raise
            
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск документов, похожих на запрос.
        
        Args:
            query: Текст запроса
            top_k: Количество результатов
            
        Returns:
            List[Dict]: Список найденных документов
        """
        try:
            if not self.index:
                self.load_index()
                
            if not self.embedder:
                self.load_embedding_model()
                
            # Создание эмбеддинга для запроса
            query_embedding = self.embedder.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Поиск похожих документов
            distances, indices = self.index.search(query_embedding, top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    results.append({
                        'document': self.documents[idx],
                        'similarity': float(distances[0][i])
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            raise
            
    def augment_prompt_with_context(self, query: str, max_context_length: int = 1000) -> str:
        """
        Дополнение запроса контекстом на основе похожих документов.
        
        Args:
            query: Исходный запрос пользователя
            max_context_length: Максимальная длина контекста
            
        Returns:
            str: Дополненный запрос
        """
        try:
            similar_docs = self.search_similar(query, top_k=3)
            
            context = ""
            for doc in similar_docs:
                if 'text' in doc['document']:
                    context += doc['document']['text'] + "\n\n"
                    
            # Обрезаем контекст, если он слишком длинный
            if len(context) > max_context_length:
                context = context[:max_context_length] + "..."
                
            # Формируем обогащенный запрос
            augmented_query = f"""Используй следующую информацию для ответа на вопрос пользователя.
            
Контекст:
{context}

Вопрос пользователя: {query}

Дай развернутый и точный ответ, основываясь на предоставленном контексте."""
            
            return augmented_query
        except Exception as e:
            logger.error(f"Error augmenting prompt with context: {e}")
            # В случае ошибки просто возвращаем исходный запрос
            return query 