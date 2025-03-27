import pandas as pd
import requests
import os
import time
from tqdm import tqdm
from datetime import datetime

# Конфигурация путей
INPUT_FILE = r'D:\models\модели 2025\only_positive.xlsx'
OUTPUT_FILE = r'D:\models\модели 2025\generated_texts.xlsx'
LOG_FILE = r'D:\models\модели 2025\generation_log.txt'

# Настройки OLLAMA
OLLAMA_URL = "http://localhost:11434/api/generate"
TIMEOUT = 120
MAX_RETRIES = 3
RETRY_DELAY = 10


def setup_environment():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n=== New session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")


def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)


def safe_ollama_request(payload):
    """Безопасный запрос к OLLAMA"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            log_message(f"Attempt {attempt + 1}: HTTP Error {response.status_code}")
        except Exception as e:
            log_message(f"Attempt {attempt + 1}: Connection Error - {str(e)}")

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
    return None


def generate_prompt(text, idx):
    return f"""Generate a rewritten version of this game review (ID:{idx}). 
Keep the same meaning but use different wording and style.
Original review: {text}"""


def process_reviews():
    setup_environment()

    # Загрузка данных
    try:
        df = pd.read_excel(INPUT_FILE)
        log_message(f"Loaded input file with {len(df)} reviews")

        # Удаление дубликатов
        initial_count = len(df)
        df = df.drop_duplicates(subset=['text'])
        log_message(f"Removed {initial_count - len(df)} duplicates")
    except Exception as e:
        log_message(f"Error loading input file: {str(e)}")
        return

    # Инициализация файла результатов
    if os.path.exists(OUTPUT_FILE):
        try:
            result_df = pd.read_excel(OUTPUT_FILE)
            log_message(f"Loaded existing results with {len(result_df)} entries")

            # Проверка наличия столбца original_id
            if 'original_id' not in result_df.columns:
                result_df['original_id'] = None
                log_message("Added missing 'original_id' column")
        except:
            result_df = pd.DataFrame(columns=['original_id', 'original_text', 'generated_text', 'timestamp'])
            log_message("Created new results dataframe")
    else:
        result_df = pd.DataFrame(columns=['original_id', 'original_text', 'generated_text', 'timestamp'])

    # Обработка отзывов
    processed_count = 0
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        text = str(row['text']).strip()
        if not text:
            continue

        # Пропуск уже обработанных
        if idx in result_df['original_id'].values:
            continue

        try:
            prompt = generate_prompt(text, idx)
            payload = {
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9}
            }

            response = safe_ollama_request(payload)
            if not response or not response.get('response'):
                continue

            generated_text = response['response'].strip()
            if not generated_text:
                continue

            # Добавление результата
            new_entry = pd.DataFrame([{
                'original_id': idx,
                'original_text': text,
                'generated_text': generated_text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }])

            result_df = pd.concat([result_df, new_entry], ignore_index=True)
            processed_count += 1

            # Пошаговое сохранение
            if processed_count % 5 == 0:
                result_df.to_excel(OUTPUT_FILE, index=False)
                log_message(f"Saved {processed_count} results")

        except Exception as e:
            log_message(f"Error processing review {idx}: {str(e)}")
            continue

    # Финальное сохранение
    result_df.to_excel(OUTPUT_FILE, index=False)
    log_message(f"Processing complete. Total processed: {processed_count}")
    log_message(f"Results saved to {OUTPUT_FILE}")

    # Проверка результатов
    if os.path.exists(OUTPUT_FILE):
        final_df = pd.read_excel(OUTPUT_FILE)
        duplicates = final_df.duplicated(subset=['original_id']).sum()
        log_message(f"Final check: {duplicates} duplicates found in results")
    else:
        log_message("Error: Output file was not created")


if __name__ == "__main__":
    try:
        process_reviews()
    except Exception as e:
        log_message(f"Critical error: {str(e)}")
        raise
