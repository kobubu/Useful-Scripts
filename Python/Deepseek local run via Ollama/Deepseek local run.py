import requests

# URL для локального сервера OLLAMA
url = "http://localhost:11434/api/generate"

# Параметры запроса
payload = {
    "model": "deepseek-r1:8b",  # Имя модели
    "prompt": "Hello! How can I help you today?",
    "stream": False
}

# Отправка запроса
response = requests.post(url, json=payload)

# Получение ответа
if response.status_code == 200:
    generated_text = response.json()["response"]
    print("Generated text:\n", generated_text)
else:
    print("Error:", response.status_code, response.text)
