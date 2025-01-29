import requests
import json
import pandas as pd
import datetime
import os
from tqdm import tqdm
from google_auth_oauthlib.flow import InstalledAppFlow
from concurrent.futures import ThreadPoolExecutor, as_completed

# Настройки OAuth 2.0
SCOPES = ['https://www.googleapis.com/auth/cloud-language']
CLIENT_SECRETS_FILE = r"C:/дамп базы/client_secret_988095010670-ga9ucce0koo8ddac4g7fc0huggj5fvre.apps.googleusercontent.com.json"  # Укажи свой путь
EXCEL_FILE = r"C:/Users/Igor/Downloads/Telegram Desktop/IN_1926_UI_Crossword_Master_Проверка_уровней_161_200_FR_part3_800-1177.xlsx"  # Укажи свой путь
OUTPUT_DIR = r"C:/Users/Igor/Downloads/Telegram Desktop/"  # Папка для сохранения

# Генерируем имена файлов с датой и временем
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
base_filename = os.path.splitext(os.path.basename(EXCEL_FILE))[0]  # Берем имя исходного файла без расширения
filtered_filename = f"{base_filename}_filtered_{timestamp}.xlsx"
full_filename = f"{base_filename}_full_{timestamp}.xlsx"
filtered_filepath = os.path.join(OUTPUT_DIR, filtered_filename)
full_filepath = os.path.join(OUTPUT_DIR, full_filename)

# Получение OAuth 2.0 credentials
def get_oauth2_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

# Получаем токен
credentials = get_oauth2_credentials()
access_token = credentials.token

# Функция анализа текста (Sentiment, Classification, Moderation, Entities)
def analyze_text(text):
    url = "https://language.googleapis.com/v2/documents:annotateText"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    features = {
        "extractEntities": True,  # Извлекаем сущности
        "extractDocumentSentiment": True,  # Извлекаем сентимент
        "classifyText": True,  # Извлекаем классификацию
        "extractEntitySentiment": True,  # Извлекаем сентимент сущностей
        "moderateText": True  # Модерация текста
    }
    document = {
        "type": "PLAIN_TEXT",
        "content": text,
        "languageCode": "fr"  # Задаем французский язык явно
    }
    body = {
        "document": document,
        "features": features,
        "encodingType": "UTF8"
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API error: {response.text}"}

# Функция для обработки одной строки
def process_row(row):
    words = [(row['#Word'], "Word"), (row['#Tips'], "Tips")]
    results = []

    for word, source in words:
        if pd.isna(word) or word.strip() == "":
            continue  # Пропускаем пустые значения

        # Анализ текста (Sentiment, Classification, Entities, Moderation)
        result = analyze_text(word)
        if "error" in result:
            print(f"❌ Ошибка обработки '{word}': {result['error']}")
            continue

        # Извлекаем Sentiment
        sentiment_score = result.get("documentSentiment", {}).get("score", 0)
        sentiment_magnitude = result.get("documentSentiment", {}).get("magnitude", 0)

        # Извлекаем сущности
        entities = result.get("entities", [])
        # Проверяем, является ли слово именем собственным
        is_proper_noun = any(entity.get("type") == "PROPER" for entity in entities)

        # Извлекаем категории (Classification)
        categories = [f"{category['name']} ({round(category['confidence'], 3)})"
                      for category in result.get("categories", [])]

        # Извлекаем метки модерации (Moderation)
        moderation = [f"{mod['name']} ({round(mod['confidence'], 3)})"
                      for mod in result.get("moderationCategories", [])
                      if mod["name"] in dangerous_categories and mod["confidence"] >= 0.1]

        # Формируем строку данных
        row_data = {
            "#Level": row["#Level"],
            "Source": source,  # Указывает, откуда слово (Word или Tips)
            "Text": word,
            "Entities": ", ".join(entity["name"] for entity in entities),
            "Is Proper Noun": "Yes" if is_proper_noun else "No",
            "Sentiment Score": sentiment_score,
            "Sentiment Magnitude": sentiment_magnitude,
            "Categories": ", ".join(categories),
            "Moderation": ", ".join(moderation)
        }
        results.append(row_data)

    return results

# Загружаем Excel-файл
df = pd.read_excel(EXCEL_FILE)

# Проверяем, есть ли нужные колонки
if "#Word" not in df.columns or "#Tips" not in df.columns or "#Level" not in df.columns:
    raise ValueError("Файл должен содержать колонки '#Level', '#Word' и '#Tips'")

# Опасные категории, которые проверяем
dangerous_categories = [
    "Toxic", "Insult", "Profanity", "Derogatory", "Sexual", "Death, Harm & Tragedy",
    "Violent", "Firearms & Weapons", "Religion & Belief", "Illicit Drugs", "War & Conflict", "Politics"
]

# Создаем DataFrame для результатов
filtered_results = []
full_results = []

# Распараллеливаем обработку строк
with ThreadPoolExecutor(max_workers=10) as executor:  # Увеличь max_workers, если нужно больше потоков
    futures = [executor.submit(process_row, row) for _, row in df.iterrows()]

    # Используем tqdm для отображения прогресса
    for future in tqdm(as_completed(futures), total=len(futures), desc="Обработка строк"):
        results = future.result()
        for row_data in results:
            full_results.append(row_data)
            # Условия для фильтрации:
            # 1. Если Sentiment Score <= -0.2
            # 2. Если есть проблемы с модерацией
            # 3. Если сущность является именем собственным
            if row_data["Sentiment Score"] <= -0.2 or row_data["Moderation"] or row_data["Is Proper Noun"] == "Yes":
                filtered_results.append(row_data)

# Преобразуем в DataFrame
df_filtered = pd.DataFrame(filtered_results)
df_full = pd.DataFrame(full_results)

# Сохраняем обработанные файлы
df_filtered.to_excel(filtered_filepath, index=False)
df_full.to_excel(full_filepath, index=False)

print(
    f"\n✅ Отфильтровано {len(df_filtered)} строк. Файлы сохранены:\n🔹 Отфильтрованный: {filtered_filepath}\n🔹 Полный: {full_filepath}"
)
