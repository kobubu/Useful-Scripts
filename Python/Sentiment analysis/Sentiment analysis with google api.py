import logging
import requests
import json
import pandas as pd
import datetime
import os
from tqdm import tqdm
from google_auth_oauthlib.flow import InstalledAppFlow
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


#Настроить переменные
SCOPES = ['https://www.googleapis.com/auth/cloud-language'] #тут ничего не менять
#указать путь к ключу OAuth 2.0
CLIENT_SECRETS_FILE = r"PATH"
OUTPUT_DIR = r"C:/Users/Igor/Downloads/Telegram Desktop/"  # Папка c файлом
#Укзать имя файла
EXCEL_FILE = OUTPUT_DIR + r"FILENAME.xlsx"
#Указать язык любой из available_languages
language = "de"

available_lanuages = '''
V2 Model
Language 	ISO-639-1 Code
Chinese (Simplified) 	zh
Chinese (Traditional) 	zh-Hant
Dutch 	nl
English 	en
French 	fr
German 	de
Italian 	it
Japanese 	ja
Korean 	ko
Portuguese (Brazilian & Continental) 	pt
Russian 	ru
Spanish 	es
'''


# Настройки логирования
LOG_FILENAME = OUTPUT_DIR+'processing_log.txt'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    filemode='w', encoding='utf-8')

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
base_filename = os.path.splitext(os.path.basename(EXCEL_FILE))[0]  # Берем имя исходного файла без расширения
filtered_filename = f"{base_filename}_filtered_{timestamp}.xlsx"
full_filename = f"{base_filename}_full_{timestamp}.xlsx"
filtered_filepath = os.path.join(OUTPUT_DIR, filtered_filename)
full_filepath = os.path.join(OUTPUT_DIR, full_filename)
request_count = 0

# Получение OAuth 2.0 credentials
def get_oauth2_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

# Получаем токен
credentials = get_oauth2_credentials()
access_token = credentials.token

#ф-ция для логирования и вывода в консоль инфы
def log_and_print(message):
    logging.info(message)
    print(message)

# Функция анализа текста
def analyze_text(text, language):  # Язык задается явно
    global request_count
    url = "https://language.googleapis.com/v2/documents:annotateText"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    features = {
        "extractEntities": True,
        "extractDocumentSentiment": True,
        "classifyText": True,
        "extractEntitySentiment": True,
        "moderateText": True
    }
    document = {
        "type": "PLAIN_TEXT",
        "content": text,
        "languageCode": language
    }
    body = {
        "document": document,
        "features": features,
        "encodingType": "UTF8"
    }

    request_count += 1
    log_and_print(f"Запрос № {request_count} для текста: {text}")

    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API error: {response.text}"}

# Функция для обработки одной строки
def process_row(index, row):
    # Преобразуем значения в строки, если они не являются NaN
    word = str(row['#Word']) if not pd.isna(row['#Word']) else ""
    tips = str(row['#Tips']) if not pd.isna(row['#Tips']) else ""

    words = [(word, "Word"), (tips, "Tips")]
    results = []

    for word, source in words:
        if word.strip() == "":
            continue

        # Анализ текста (Sentiment, Classification, Entities, Moderation)
        result = analyze_text(word, language)
        if "error" in result:
            log_and_print(f"❌ Ошибка обработки '{word}': {result['error']}")
            continue

        logging.info(f"Ответ для текста '{word}': Статус - {result.get('status', 'N/A')}")

        # Извлекаем Sentiment
        sentiment_score = result.get("documentSentiment", {}).get("score", 0)
        sentiment_magnitude = result.get("documentSentiment", {}).get("magnitude", 0)

        # Извлекаем именованные сущности
        entities = result.get("entities", [])
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
            "Index": index,  # Добавляем индекс для восстановления порядка
            "#Level": row["#Level"],
            "Source": source,  # Указывает, откуда слово (Word или Tips)
            "Text": word,
            "Entities": "\n".join(f"Entity: {entity['name']}, Type: {entity['type']}" for entity in entities),
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

if "#Word" not in df.columns and "#Tips" not in df.columns and "#Level" not in df.columns:
    raise ValueError("Файл должен содержать колонки '#Level', '#Word' и '#Tips'")

df["Index"] = range(len(df))

dangerous_categories = [
    "Toxic", "Insult", "Profanity", "Derogatory", "Sexual", "Death, Harm & Tragedy",
    "Violent", "Firearms & Weapons", "Religion & Belief", "Illicit Drugs", "War & Conflict", "Politics"
]

filtered_results = []
full_results = []

log_and_print(f'Выбран язык {language}')
log_and_print(f'Выбран файл {EXCEL_FILE}')
requests_count = 0

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_row, index, row) for index, row in df.iterrows()]

    for future in tqdm(as_completed(futures), total=len(futures), desc="Обработка строк"):
        results = future.result()
        for row_data in results:
            full_results.append(row_data)
            if row_data["Sentiment Score"] <= -0.2 or row_data["Moderation"] or row_data["Is Proper Noun"] == "Yes":
                filtered_results.append(row_data)

        requests_count += 1
        time.sleep(0.1)  # Добавляем небольшую задержку, чтобы избежать превышения квоты

log_and_print(f"\nОбработано запросов: {requests_count}")

df_filtered = pd.DataFrame(filtered_results).sort_values(by="Index")
df_full = pd.DataFrame(full_results).sort_values(by="Index")

df_filtered.drop(columns=["Index"], inplace=True)
df_full.drop(columns=["Index"], inplace=True)


df_filtered.to_excel(filtered_filepath, index=False)
df_full.to_excel(full_filepath, index=False)

log_and_print(
    f"\n✅ Отфильтровано {len(df_filtered)} строк. Файлы сохранены:\n🔹 Отфильтрованный: {filtered_filepath}\n🔹 Полный: {full_filepath}\n"
)
