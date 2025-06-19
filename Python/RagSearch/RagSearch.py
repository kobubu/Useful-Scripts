from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import requests
import json
import os
from typing import Generator

# 1. Конфигурация
MODEL_NAME = 'all-MiniLM-L6-v2'
OLLAMA_URL = "[Secret]"
OLLAMA_MODEL = "[Secret]"
DOCUMENT_PATHS = [
    'C:\\Users\\Igor\\PycharmProjects\\Models_finetune_retrain\\Rag\\*.txt'
]

# 2. Где хранится база данных?
"""
Ваша база данных (индекс и документы) хранится:
1. Векторные представления - в оперативной памяти (объект FAISS index)
2. Исходные тексты - в переменной documents (в оперативной памяти)
3. На диске - оригинальные txt-файлы по указанным путям

Для постоянного хранения индекса можно сохранить его на диск:
"""


def save_index(index, path="faiss_index.index"):
    faiss.write_index(index, path)


def load_index(path="faiss_index.index"):
    return faiss.read_index(path)


# 3. Загрузка документов с поддержкой масок путей
def load_documents(file_paths):
    documents = []
    from glob import glob
    for pattern in file_paths:
        for path in glob(pattern):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
                print(f"Загружен документ: {path}")
            except Exception as e:
                print(f"Ошибка загрузки {path}: {str(e)}")
    return documents


# 4. Инициализация системы
print("Инициализация системы...")
documents = load_documents(DOCUMENT_PATHS)
embedding_model = SentenceTransformer(MODEL_NAME)
document_embeddings = embedding_model.encode(documents)

if os.path.exists("faiss_index.index"):
    index = load_index()
else:
    dimension = document_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(document_embeddings)
    save_index(index)


# 5. Поиск документов
def retrieve_documents(query, k=2):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, k)
    return [documents[i] for i in indices[0]]


# 6. Стриминговая генерация ответов
def stream_with_ollama(prompt) -> Generator[str, None, None]:
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True  # Включаем стриминг
    }

    try:
        with requests.post(OLLAMA_URL, json=data, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk.get("response", "")
    except Exception as e:
        yield f"Ошибка: {str(e)}"


# 7. Основная функция RAG со стримингом
def generate_response_stream(query) -> Generator[str, None, None]:
    relevant_docs = retrieve_documents(query)
    context = "\n\n".join(relevant_docs)

    prompt = f"""Ты - ассистент компании. Отвечай точно, используя документы.
Контекст:
{context}

Вопрос: {query}

Ответ:"""

    for chunk in stream_with_ollama(prompt):
        yield chunk


# 8. Интерактивный режим со стримингом
def interactive_stream_mode():
    print("\nАссистент готов (режим стриминга). Введите вопрос или 'выход':")
    while True:
        try:
            user_query = input("> ").strip()
            if user_query.lower() in ['выход', 'exit', 'quit']:
                break

            if not user_query:
                continue

            print("\nОтвет:", end=" ", flush=True)
            for chunk in generate_response_stream(user_query):
                print(chunk, end="", flush=True)
            print("\n")

        except KeyboardInterrupt:
            break


# Запуск
if __name__ == "__main__":
    interactive_stream_mode()
