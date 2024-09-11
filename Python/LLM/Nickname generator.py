import os

import numpy.random
import pandas as pd
from datetime import datetime
from llama_cpp import Llama
import re
import tensorflow as tf
import random
import time
import numpy as np

local_model_path = "C:/llms/mistral-7b-instruct-v0.2.Q8_0.gguf"
CLEAN_RESPONSE = re.compile("\[INST].*\[/INST]")
file_path = 'C:/Users/Igor/Desktop/работа/AI-Generated Nicknames （new).xlsx'

seed_value = 42  # Пример значения seed
temperature_value = 8
top_p=1
top_k=1
# Пример значения temperature

llm = Llama(
    model_path=local_model_path,
    n_ctx=32768,
    n_threads=8,
    n_gpu_layers=35,
    seed = seed_value,
    temperature = temperature_value,
    top_p=1,
    top_k=1
)

persons = [
    'pirate', 'scientist', 'detective', 'chef', 'astronaut', 'teacher', 'doctor', 'artist', 'engineer', 'journalist',
    'soldier', 'pilot', 'lawyer', 'nurse', 'writer', 'athlete', 'musician', 'programmer', 'architect', 'farmer',
    'librarian', 'firefighter', 'police officer', 'actor', 'photographer', 'mechanic', 'psychologist', 'biologist', 'economist', 'philosopher'
]


situations = [
    'in the distant cosmos', 'at the office', 'at the Olympic Games', 'in a haunted house', 'on a deserted island', 'in a medieval castle',
    'at a rock concert', 'in a virtual reality game', 'at a wedding', 'in a secret laboratory', 'at a crime scene', 'in a bustling marketplace',
    'at a fashion show', 'in a snowstorm', 'at a children\'s birthday party', 'in a tropical jungle', 'at a political debate', 'in a futuristic city',
    'at a book signing', 'in a submarine', 'at a rodeo', 'in a desert oasis', 'at a film festival', 'in a parallel universe', 'at a space station',
    'in a time machine', 'at a magic show', 'in a haunted forest', 'at a chess tournament', 'in a post-apocalyptic world'
]


few_shot_nicknames = """My task is to create 5 new funny words related to me. Use all your creativity and create 10 new words. 
Words should be funny for humans and contain only latin letters and numbers. Should not be longer than 16 characters. Here are some examples:"
"""

#RESPONSE_CLEANER = re.compile('\d\. \w+', re.IGNORECASE) todo: плохо работает

# Функция генерации
def make_sample(source, amount_of_samples, amount_of_words_per_sample):
    # Загружаем данные из файла Excel
    df = pd.read_excel(source)

    sample_list = []
    for _ in range(amount_of_samples):
        # Устанавливаем seed для генерации случайных чисел на основе текущего времени
        np.random.seed(int(time.time()))

        # Делаем случайный сэмпл из 10 строк
        sample_df = df['Previous Nicknames'].sample(amount_of_words_per_sample)

        # Добавляем строки из колонки 'Previous Nicknames' в виде строки, разделенной запятыми
        sample_list.append(', '.join(sample_df.astype(str)))

    return sample_list

def rag_randomizer():
    rag = f"I am a {numpy.random.choice(persons)} {numpy.random.choice(situations)}."
    return rag

# Функция проверки
def ai_generate_nicknames_gpu(path, few_shot):
    # Создаем пустой DataFrame с колонкой 'Result'
    df = pd.DataFrame(columns=['Result'])
    count = 0
    with tf.device('/GPU:0'):
        for i in range(100):
            sample_list = make_sample(path, 100, 8)
            print(sample_list)
            total = len(sample_list)
            count += 1
            # Проверяем, что индекс i находится в пределах длины sample_list
            if i >= len(sample_list):
                print(f"Skipping row {i} due to empty sample list")
                continue
            # Skip the row if 'few_shot_content' is empty
            if pd.isna(sample_list[i]):
                print(f"Skipping row {i} due to empty few shot content")
                continue
            RAG = rag_randomizer()
            prompt = f"{RAG}\n{few_shot}\n{sample_list[i]}"
            print(f'Sample content: {sample_list[i]}')
            print(f'Full prompt: {prompt}')
            print(f"Prompt #{count} of {total} is sent")
            try:
                # Generate the review using the language model
                output = llm(
                    prompt,
                    max_tokens=512,
                    stop=["</s>"],  # This should be the token that indicates the end of the response
                    echo=True
                )

                # Extract and print the generated text
                generated_text = output['choices'][0]['text']
                # Remove the <s> and </s> tags from the generated text
                generated_text = generated_text.replace("<s>", "").replace("</s>", "").strip()
                #generated_text = re.findall(RESPONSE_CLEANER, generated_text)

                # Добавляем сгенерированный текст в DataFrame
                df.at[i, 'Result'] = generated_text

            except Exception as e:
                print(f"Something went wrong: {e}")
                df.at[i, 'Result'] = "Error occurred during review generation"
        return df

#функция сохранения
def save_df_to_excel(df, output_file_name, output_dir="C:/Users/Igor/Desktop/jupyter/ai_reviews"):
    # Создаем каталог, если он не существует
    os.makedirs(output_dir, exist_ok=True)

    # Создаем полный путь к файлу, включая имя файла
    output_path = os.path.join(output_dir, output_file_name)

    # Сохраняем DataFrame в Excel файл
    df.to_excel(output_path, index=False)

file_name = "C:/Users/Igor/Desktop/работа/аналитика базы вопросов/тестирование генеративной модели/датасет для тестирования ai-редактора/20240808_ru_en_test.xlsx"
df_reviewed=ai_generate_nicknames_gpu(file_path, few_shot_nicknames)


# Save the filtered DataFrame to a new Excel file
current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file_name_filtered = f'{current_datetime}ms7b_nicknames.xlsx'
save_df_to_excel(df_reviewed, output_file_name_filtered)
print(df_reviewed)

