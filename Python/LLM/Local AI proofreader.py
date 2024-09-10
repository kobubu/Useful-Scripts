# импортируем все зависимости
import os
import requests
import pandas as pd
from datetime import datetime
from llama_cpp import Llama
import re
import tensorflow as tf

local_model_path = "C:/llms/mistral-7b-instruct-v0.2.Q8_0.gguf"
CLEAN_RESPONSE = re.compile("\[INST].*\[/INST]")
REMOVE_EVERYTHING_EXCEPT_LAST = re.compile(".*Now check this translation and make a review:\n\n", re.DOTALL)

seed_value = 42  # Пример значения seed
temperature_value = 1
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

few_shot_italian = """You receive a source string in English and its translation in Italian. Point out and explain all mistakes such as missed translation, wrong grammar, mistranslation, typo, misspell, etc.
Your response should begin with "Translation is correct" or "Translation is incorrect.". Ignore anything inside this brackets {} or []. Ignore %_ and _%. Follow these examples.

Example 1:
Source: Unlocked at Level {0}.
Translation: Sbloccato al livello {0}. Сергей!
Review: Translation is incorrect.  The translation of "unlocked" should be gender-neutral when there is no object specified, сonsider using "si blocca" instead of "sbloccato" to achieve gender neutrality. Translation also has extra text in Russian "Сергей!" 

Example 2:
Source: The only way to split my soul was to have you, Alexandra. With you I could feel twice as much. See twice as far. You were to be a queen in a queen-less land. You were to be a miracle of a daughter, not a curse.
Translation: Non c'era altro modo per dividere la mia anima se non avendo te, Alexrandra. La tua presenza mi permetteva di sentire due volte di più e vedere due volte più lontano. Saresti dovuta essere una regina in una terra senza sovrane. Saresti dovuta essere un miracolo, non un castigo.
Review: Translation is incorrect. There is a grammar error: the auxiliary verb should be "avere" instead of "essere", so it should be "Avresti dovuto essere" instead of "Saresti dovuta essere" and name "Alexandra" is spelled incorrectry as it shoud be "Alexandra".

Example 3:
Source: What on earth?
Translation: Ma che diavolo?
Review: Translation is correct.

Now check this translation and make a review:
"""

few_shot_english = """You receive a source string in Russian and its translation in English. Point out and explain all mistakes such as missed translation, wrong grammar, mistranslation, typo, misspell, etc.
Your response should begin with "Translation is correct" or "Translation is incorrect.". Ignore anything inside this brackets {} or []. Ignore %_ and _%. Follow these examples.  

Example 1:
Source: У заправки сидит женщина, загримированная под жуткого клоуна: «Купи чемоданчик», — говорит она, широко улыбаясь.
Translation: A woman is standing at the gas station, her face painted like a creepy clown. "Buy a suitcase," she says with a wide smile.
Review: Translation is incorrect. The part "У заправки сидит женщина" is translated wrong, "сидит" at this context should be translated as "standing at".
Example 2:
Source: Из глубины кладбища доносится негромкий детский плач.
Translation: From the depths of the graveyard echoes the quiet laughter of a child.
Review: Translation is incorrect. "laughter" is the opposite of "плач". Consider using "crying" instead. 
Example 3
Source: Рискнуть и попробовать тихо слезть
Translation: Risk it and try to climb up quietly
Review: Translation is incorrect. "Cлезть" means "climb down"

Now check this translation and make a review:
"""

few_shot_french = """You receive a source string in English and its translation in French. Point out and explain all mistakes such as missed translation, wrong grammar, mistranslation, typo, misspell, etc.
Your response should begin with "Translation is correct" or "Translation is incorrect.". Ignore anything inside this brackets {} or []. Ignore %_ and _%. Follow these examples.  

Example 1:
Source: Mission objective requires route to Daemonic Forge. Obtain manufactorum schematic data. You are idiot, Sergei! 
Translation: L'objectif de mission nécessite un itinéraire jusqu'à la Forge Démoniaque. You are idiot, Сергей!
Review: Translation is incorrect. The part "Obtain manufactorum schematic data." is missing from the translation, "You are idiot!" is not translated and "Сергей" is written in Russian not in French.
Example 2:
Source: Navigation subroutine failed. Adjust location and reattempt. Andrew!
Translation: Échec de la sous-routine de navigation. Ajuster la position et réessayer. Andresws!
Review: Translation is incorrect. The form "Ajustez" (imperative mood) should be used instead of Ajuster (infinitive). There is a typo in the name "Andrewws" - it should be spelled as "Andrew". 
Example 3
Source: Oh no! I don't have a thing for her!
Translation: Oh, mince ! J'ai rien pensé à lui prendre !
Review: Translation is correct.

Now check this translation and make a review:
"""
few_shot_spanish = """You receive a source string in English and its translation in Spanish. Point out and explain all mistakes such as missed translation, wrong grammar, mistranslation, typo, misspell, etc. 
Your response should begin with "Translation is correct" or "Translation is incorrect.". Ignore anything inside this brackets {} or []. Ignore %_ and _%. Follow these examples.Your answer should have 1, 2 or 3 sentences.   

Example 1:
Source: Someone went and started the fun without me! You are idiot, Sergei!
Translation: ¡Alguien ha empezado la juega sin esperar a este menda!  ¡You are idiot, Сергей!
Review: Translation is incorrect. There is a typo in "juega", it should be spelled "juerga". "You are idiot!" is not translated and "Сергей" is written in Russian not in Spanish.

Example 2:
Source: Is the new PUPPET to leave? Obtain manufactorum schematic data. 
Translation: ¿La nueva MASCOTA se quiere ir ya? 
Review: Translation is incorrect. "Alexrandra" has a typo, it should be spelled "Alexandra". It should be "MARIONETA" instead of "MASCOTA" and the part "Obtain manufactorum schematic data." is missing from the translation. 

Example 3:
Source: The abyss has been unkind.
Translation: El abismo no te ha sentado bien.
Review: Translation is correct.

Now check this translation and make a review:
"""
few_shot_japanese = """You receive a source string in English and its translation in Japanese. If there is a serious mistake in translation, such as missed translation, or mistranslation, you point it out and explain it. 
You start your answer with 'Translation is correct' or 'Translation is incorrect'. Follow examples and make your review. Write that translation is incorrect only if it has severe mistakes such as mistranslation, missed text, typos or grammar mistakes in translations, etc.
Anything inside this brackets {} can't have any translation mistake.
Your answer should have 1, 2 or 3 sentences.   

Example 1:
Source: Subscribe now
Translation: 今すぐ講読する
Review: Translation might be incorrect. Wrong Kanji used to write こうどく in this context. Consider using 購 instead of 講

Example 3:
Source: Hmmm, strawberry syrup, watermelon syrup, syrupy syrup… I'm turning sweet just from the smell of these wrecks!
Translation: ううん、いちごシロップに、メロンシロップに、シロップに、シロップ... この残骸の匂いだけで僕まで甘くなっちゃいそうだ！
Review: Translation might be incorrect. Watermelon was misread as Melon. Consider using スイカ instead of メロン.

Example 4:
Source: Emery showed up in a yellow skirt
Translation: エメリーは黄色のスカートを着てきた2
Review: Translation is correct.

Example 5:
Source: You can forbid tracking, but in that case ads will be selected randomly with no concern for your interests.
Translation: また許可をいただけない場合には、広告には皆さんのご興味とは無関係のものがランダムに表示されることになります。
Review: Translation is correct.


Now check this translation and make a review:
"""
#функция проверки
def ai_review(path, few_shot_for_language):
    few_shot = few_shot_for_language
    df = pd.read_excel(path, sheet_name="Лист1")
    df['Review'] = None
    count = 1
    total = len(df)
    for index, row in df.iterrows():
        source = row['Source']  # Source text assumed to be in the column 'Source'
        target = row['Target']  # Target text assumed to be in the column 'Target'
        content = f"Source: {source}\nTranslation: {target}"
        prompt = f"{few_shot}\n{content}\n"
        print(f"Promt #{count} of {total} is sent")
        count += 1

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
            generated_text = CLEAN_RESPONSE.sub('', generated_text)
            #generated_text = REMOVE_EVERYTHING_EXCEPT_LAST.sub('', generated_text)
            df.at[index, 'Review'] = generated_text

        except Exception as e:
            print(f"Something went wrong: {e}")
            df.at[index, 'Review'] = "Error occurred during review generation"
    return df

# Функция проверки
def ai_review_gpu (path, few_shot_for_language):
    few_shot = few_shot_for_language
    df = pd.read_excel(path, sheet_name="Лист1")
    df['Review'] = None
    count = 0
    total = len(df)
    with tf.device('/GPU:0'):
        for index, row in df.iterrows():
            count += 1
            source = row['Source']  # Source text assumed to be in the column 'Source'
            target = row['Target']  # Target text assumed to be in the column 'Target'
            # Skip the row if 'Source' or 'Target' is empty
            if pd.isna(source) and pd.isna(target):
                print(f"Skipping row {index} due to empty 'Source' and 'Target'")
                continue
            content = f"Source: {source}\nTranslation: {target}"
            prompt = f"{few_shot}\n{content}"
            print(f"Promt #{count} of {total} is sent")
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
                #generated_text = CLEAN_RESPONSE.sub('', generated_text)
                #generated_text = REMOVE_EVERYTHING_EXCEPT_LAST.sub('', generated_text)

                df.at[index, 'Review'] = generated_text

            except Exception as e:
                print(f"Something went wrong: {e}")
                df.at[index, 'Review'] = "Error occurred during review generation"
        return df

def filter_results(df):
    # Check if 'Review' column exists
    if 'Review' not in df.columns:
        raise ValueError("DataFrame does not contain a 'Review' column.")

    # Filter the DataFrame based on the 'Review' column and apply the regular expressions
    filtered_df = df[df['Review'].notnull()].copy()  # Create a copy to avoid SettingWithCopyWarning
    filtered_df['Review'] = (
        filtered_df['Review']
        .apply(lambda review: CLEAN_RESPONSE.sub('', review))
        .apply(lambda review: REMOVE_EVERYTHING_EXCEPT_LAST.sub('', review))
    )

    # Filter the DataFrame to only include rows where 'Review' contains 'incorrect'
    filtered_df = filtered_df[filtered_df['Review'].str.contains('incorrect', case=False, na=False)]

    return filtered_df

#функция сохранения
def save_df_to_excel(df, output_file_name, output_dir="C:/Users/Igor/Desktop/jupyter/ai_reviews"):
    # Создаем каталог, если он не существует
    os.makedirs(output_dir, exist_ok=True)

    # Создаем полный путь к файлу, включая имя файла
    output_path = os.path.join(output_dir, output_file_name)

    # Сохраняем DataFrame в Excel файл
    df.to_excel(output_path, index=False)

file_name = "C:/Users/Igor/Desktop/работа/аналитика базы вопросов/тестирование генеративной модели/датасет для тестирования ai-редактора/20240808_ru_en_test.xlsx"
df_reviewed=ai_review_gpu(file_name, few_shot_english)

#df_reviewed=filter_results(df_reviewed)

# Save the filtered DataFrame to a new Excel file
current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file_name_filtered = f'{current_datetime}ms7b_filtered_reviewed.xlsx'
save_df_to_excel(df_reviewed, output_file_name_filtered)
print(df_reviewed)

