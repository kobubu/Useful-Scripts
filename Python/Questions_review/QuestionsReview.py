# Импорт стандартных библиотек Python
import hashlib  # Модуль для хеширования данных (используется SHA-256)
import requests  # Библиотека для выполнения HTTP-запросов (к API Ollama)
import datetime  # Модуль для работы с датой и временем (для логов)
from pathlib import Path  # Современный ООП-интерфейс для работы с путями файлов
from typing import Dict, Any  # Аннотации типов для статического анализа кода
from google.oauth2 import service_account  # Аутентификация Google через сервисный аккаунт
from googleapiclient.discovery import build  # Клиент Google API
import sys  # Системные функции (используется для перенаправления stdout/stderr)

# ====================== CONFIG ======================

# Словарь конфигурации приложения (все настройки в одном месте)
CONFIG = {
    # Путь к JSON-файлу сервисного аккаунта Google
    "service_account_file": "[]",

    # Конфиг для таблицы "Мастерфайл"
    "masterfile": {
        "spreadsheet_id": "[]",  # ID в URL таблицы
        "sheet_name": "Мастерфайл",  # Название листа в таблице
    },
    # Конфиг для таблицы "Мастервопросник"
    "questionnaire": {
        "spreadsheet_id": "[]",  # ID таблицы
        "sheet_name": "[]",  # Название листа
    },
    # Области доступа Google API (только к таблицам)
    "scopes": [""],
    # URL локального сервера Ollama
    "ollama_url": "",
    # Название используемой модели (qwen2.5 32B параметров)
    "ollama_model": ""
}

# Шаблон промпта для LLM с двумя примерами ожидаемого вывода
BASE_PROMPT = '''
You receive a translator-reviewer discussion. Please follow these 2 examples

[содержимое промпта сокращено для читаемости]
'''

# ====================== CLASSES ======================

# Класс-клиент для работы с Google Sheets API
class GoogleSheetClient:
    # Конструктор класса (инициализация клиента)
    def __init__(self, creds_path: str, scopes: list):
        # Загрузка учетных данных из JSON-файла
        self.creds = service_account.Credentials.from_service_account_file(
            creds_path, 
            scopes=scopes
        )
        # Создание сервиса Google Sheets API v4
        self.service = build('sheets', 'v4', credentials=self.creds)
        # Сокращенная ссылка на ресурс spreadsheets
        self.sheet = self.service.spreadsheets()

    # Метод получения данных из колонки
    def get_column(self, spreadsheet_id: str, sheet_name: str, range_suffix: str):
        # Вызов API для получения значений
        result = self.sheet.values().get(
            spreadsheetId=spreadsheet_id,  # ID таблицы
            range=f"{sheet_name}!{range_suffix}"  # Диапазон (например "A2:A")
        ).execute()
        # Возврат значений или пустого списка
        return result.get('values', [])

    # Метод пакетного обновления ячеек
    def batch_update(self, spreadsheet_id: str, updates: list):
        # Проверка, что есть что обновлять
        if updates:
            # Тело запроса к API
            body = {
                "valueInputOption": "RAW",  # Без преобразования значений
                "data": updates  # Список обновлений
            }
            # Вызов API для пакетного обновления
            self.sheet.values().batchUpdate(
                spreadsheetId=spreadsheet_id, 
                body=body
            ).execute()

    # Метод обновления одной ячейки
    def update_cell(self, spreadsheet_id: str, sheet_name: str, cell: str, value: str):
        # Вызов API для обновления значения
        self.sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!{cell}",  # Координаты ячейки
            valueInputOption="RAW",  # Сырые данные
            body={"values": [[value]]}  # Данные в формате Google Sheets API
        ).execute()

# Класс для работы с Ollama API
class OllamaClient:
    # Конструктор (инициализация параметров подключения)
    def __init__(self, url: str, model: str):
        self.url = url  # URL API endpoint
        self.model = model  # Идентификатор модели

    # Метод генерации текста
    def generate_summary(self, prompt: str) -> str:
        # POST-запрос к API Ollama
        response = requests.post(
            self.url,
            json={
                "model": self.model,  # Указание модели
                "prompt": prompt,  # Текст промпта
                "stream": False  # Не потоковый ответ
            },
            timeout=60  # Таймаут 60 секунд
        )
        # Проверка статуса ответа
        response.raise_for_status()
        # Возврат текста ответа
        return response.json()["response"]

# ====================== MAIN LOGIC ======================

# Функция обработки листа "Мастерфайл"
def summarize_masterfile(sheet_client: GoogleSheetClient, ollama: OllamaClient):
    # Информационное сообщение в лог
    print(f"\n📘 Обработка Мастерфайла...")
    
    # Получение ID таблицы и имени листа из конфига
    spreadsheet_id = CONFIG["masterfile"]["spreadsheet_id"]
    sheet_name = CONFIG["masterfile"]["sheet_name"]

    # Чтение данных из трех колонок:
    a_values = sheet_client.get_column(spreadsheet_id, sheet_name, "A2:A")  # Исходный текст
    b_values = sheet_client.get_column(spreadsheet_id, sheet_name, "B2:B")  # Статус (Fixed/нет)
    h_values = sheet_client.get_column(spreadsheet_id, sheet_name, "H2:H")  # Summary (результат)

    # Обработка строк (начиная со 2-й, так как 1-я - заголовок)
    for i in range(2, max(len(a_values), len(b_values), len(h_values)) + 2):
        # Получение значений с проверкой на существование
        a_row = a_values[i-2][0].strip() if i-2 < len(a_values) and a_values[i-2] else ''
        b_row = b_values[i-2][0].strip() if i-2 < len(b_values) and b_values[i-2] else ''
        h_row = h_values[i-2][0].strip() if i-2 < len(h_values) and h_values[i-2] else ''

        # Пропуск если: нет исходного текста, нет статуса или уже есть summary
        if not a_row or not b_row or h_row:
            continue

        # Определение нуждается ли текст в исправлении
        needs_correction = 'true' if b_row.lower() == 'fixed' else 'false'
        # Формирование промпта для LLM
        prompt = f"{BASE_PROMPT}\n\"{a_row}\"\n\nExpected summary (needs_correction = {needs_correction}):"

        try:
            # Логирование процесса обработки
            print(f"🧠 Строка {i}...")
            # Генерация summary через LLM
            summary = ollama.generate_summary(prompt)
            # Запись результата в колонку H
            sheet_client.update_cell(spreadsheet_id, sheet_name, f"H{i}", summary)
            # Сообщение об успехе
            print(f"✅ Записано в H{i}")
        except Exception as e:
            # Сообщение об ошибке
            print(f"❌ Ошибка в строке {i}: {e}")

# Функция хеширования вопросов
def hash_questionnaire(sheet_client: GoogleSheetClient):
    print(f"\n📘 Обработка Мастервопросника...")
    # Получение ID таблицы и имени листа из конфига
    spreadsheet_id = CONFIG["questionnaire"]["spreadsheet_id"]
    sheet_name = CONFIG["questionnaire"]["sheet_name"]

    # Чтение колонок (ограничение 1000 строк):
    a_values = sheet_client.get_column(spreadsheet_id, sheet_name, "A2:A1000")  # Текст вопроса
    i_values = sheet_client.get_column(spreadsheet_id, sheet_name, "I2:I1000")  # Хеш

    # Подготовка списка обновлений
    updates = []
    # Обработка пар строк (вопрос + хеш)
    for idx, (a_row, i_row) in enumerate(zip(a_values, i_values), start=2):
        # Пропуск пустых вопросов
        if not a_row or not a_row[0].strip():
            break
        # Пропуск если хеш уже есть
        if i_row and i_row[0].strip():
            continue

        # Получение текста вопроса
        text = a_row[0]
        # Генерация SHA-256 хеша
        hash_val = hashlib.sha256(text.encode('utf-8')).hexdigest()
        # Добавление в список обновлений
        updates.append({
            "range": f"{sheet_name}!I{idx}",  # Ячейка для обновления
            "values": [[hash_val]]  # Значение хеша
        })

    # Массовое обновление если есть что обновлять
    if updates:
        sheet_client.batch_update(spreadsheet_id, updates)
        print(f"🔐 Обновлено {len(updates)} хэшей.")
    else:
        print("ℹ️ Нет хэшей для обновления.")

# ====================== ENTRY ======================

# Главная функция
def main():
    # Создание временной метки в формате ГГГГ-ММ-ДД_ЧЧ-ММ-СС
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Путь к лог-файлу (в той же папке что и скрипт)
    log_path = Path(__file__).parent / "last_run.log"
    
    # Перенаправление вывода в лог-файл
    with open(log_path, "w") as log_file:
        sys.stdout = log_file  # Перенаправление stdout
        sys.stderr = log_file  # Перенаправление stderr

        # Заголовок в логе
        print(f"\n=== 🚀 Запуск {datetime.datetime.now()} ===")
        # Инициализация клиента Google Sheets
        sheet_client = GoogleSheetClient(CONFIG["service_account_file"], CONFIG["scopes"])
        # Инициализация клиента Ollama
        ollama = OllamaClient(CONFIG["ollama_url"], CONFIG["ollama_model"])

        # Вызов функций обработки
        summarize_masterfile(sheet_client, ollama)  # Анализ обсуждений
        hash_questionnaire(sheet_client)  # Хеширование вопросов

# Стандартная точка входа Python
if __name__ == "__main__":
    main()
