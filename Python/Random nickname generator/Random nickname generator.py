# импортируем все зависимости
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
file_path = 'C:/Users/Igor/Desktop/работа/database of mythical creatures.xlsx'

seed_value = 42  # Пример значения seed
temperature_value = 9
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
    'Aquatic', 'Bahamut', 'Bake', 'Cetus', 'Devil', 'Encantado', 'Glashtyn', 'Makara', 'Mug', 'Sea', 'Selkie', 'Water',
    'Water', 'Ceffyl', 'Each', 'Enbarr', 'Hippocampus', 'Ichthyocentaurs', 'Kelpie', 'Morvarc', 'Nixie', 'Nuckelavee', 'Nuggle',
    'Tangie', 'Arthropods', 'Anansi', 'Arachne', 'Carbuncle', 'Gold', 'Iktomi', 'Jor', 'Karkinos', 'Khepri', 'Mothman',
    'Myrmecoleon', 'Myrmidons', 'Pabilsag', 'Scorpion', 'Selket', 'Tsuchigumo', 'Bats', 'Balayang', 'Camazotz', 'Leutogi',
    'Minyades', 'Tjinimin', 'Vetala', 'Birds', 'Ababil', 'Adarna', 'Avalerion', 'Alicanto', 'Anqa', 'Anz', 'Bare', 'Bird',
    'Alkonost', 'Gumy', 'Harpy', 'Aello', 'Ocypete', 'Celaeno', 'Podarge', 'Horus', 'Inmyeonjo', 'Kalavinka', 'Karura',
    'Kinnara', 'Siren', 'Achelois', 'Aglaonoe', 'Agalaope', 'Leucosia', 'Ligeia', 'Parthenope', 'Pisinoe', 'Thelxino',
    'Swan', 'Caladrius', 'Chalkydri', 'Chamrosh', 'Cinnamon', 'Devil', 'Gagana', 'Gandabherunda', 'Gamayun', 'Garuda',
    'Hakawai', 'Hudhud', 'Huginn', 'Itsumade', 'Jingwei', 'Lamassu', 'Luan', 'Minokawa', 'Nachtkrapp', 'Nine', 'Oozlum',
    'Pamola', 'Peng', 'Phoenix', 'Bennu', 'Chol', 'Firebird', 'Fenghuang', 'Huma', 'Konrul', 'Vermilion', 'Piasa', 'Qingniao',
    'Ra', 'Rain', 'Rar', 'Roc', 'Shangyang', 'Shedu', 'Simurgh', 'Stymphalian', 'Tengu', 'Three', 'Thunderbird', 'Thoth',
    'Turul', 'Ve', 'Vucub', 'Wampum', 'Yatagarasu', 'Zhenniao', 'Chickens', 'Alectryon', 'Basan', 'Cockatrice', 'Gallic',
    'Gullinkambi', 'Rooster', 'Sarimanok', 'V', 'Eagles', 'Aethon', 'Griffin', 'Hippogriff', 'Hr', 'Poukai', 'Shahbaz',
    'Triple', 'Wuchowsen', 'Ziz', 'Zu', 'Owls', 'Nyctimene', 'Owlman', 'Sirin', 'Strix', 'Carnivorans', 'Bears',
    'Bjarndyrakongur', 'Bugbear', 'Callisto', 'Stiff', 'Canines', 'Adlet', 'Amarok', 'Anubis', 'Aralez', 'Asena',
    'Axehandle', 'Black', 'Beast', 'Carbuncle', 'Cerberus', 'Chupacabra', 'Cu', 'Crocotta', 'Cynocephaly', 'Dogs',
    'Fenrir', 'Gelert', 'Hellhound', 'Huli', 'Huodou', 'Kludde', 'Orthrus', 'Penghou', 'Psoglav', 'Salawa', 'Sigbin',
    'Sky', 'Shug', 'Tanuki', 'Tulikettu', 'V', 'Werewolf', 'Felines', 'Bael', 'Ball', 'Cactus', 'Canaima', 'Cat',
    'Cath', 'Carbuncle', 'Demon', 'Kaiby', 'Bakeneko', 'Kasha', 'Nekomata', 'Nue', 'Panther', 'Phantom', 'Blue',
    'Glawackus', 'Tyger', 'Underwater', 'Vapula', 'Wampus', 'White', 'Winged', 'Lions', 'Arimanius', 'Ammit', 'Barong',
    'Beast', 'Brunswick', 'Chimera', 'Chinese', 'Komainu', 'Shisa', 'Sin', 'Xiezhi', 'Dawon', 'Egyptian', 'Aker',
    'Apedemak', 'Bast', 'Hert', 'Ipy', 'Maahes', 'Matit', 'Mehit', 'Menhit', 'Pakhet', 'Repyt', 'Sekhmet', 'Seret',
    'Shesmetet', 'Taweret', 'Tefnut', 'Tutu', 'Urit', 'Griffin', 'Lamassu', 'Lampago', 'Leo', 'Lion', 'Nemean', 'Lion',
    'Manticore', 'Manussiha', 'Merlion', 'Narasimha', 'Nian', 'Nongsh', 'Pixiu', 'Questing', 'Sea', 'Serpopard',
    'Sharabha', 'Simhamukha', 'Snow', 'Sphinx', 'Criosphinx', 'Gopaitioshah', 'Hieracosphinx', 'Stratford', 'Tigris',
    'Vaikuntha', 'Winged', 'Yali', 'Yagh', 'Yaldabaoth', 'Hyenas', 'Werehyena', 'Kishi', 'Musteloids', 'Azeban',
    'Gef', 'Ichneumon', 'Kamaitachi', 'Kushtaka', 'Mujina', 'Ramidreju', 'Raij', 'Procyonids', 'Azeban', 'Fish',
    'Fish', 'Mermaid', 'Water', 'Undine', 'Abaia', 'Gurangatch', 'Hippocamp', 'Ika', 'Il', 'Isonade', 'Namazu',
    'Ningyo', 'Kun', 'Salmon', 'Shachihoko', 'Insectivores', 'Lavellan', 'Marsupials', 'Drop', 'Bunyip', 'Molluscs',
    'Akkorokamui', 'Carbuncle', 'Lou', 'Kraken', 'Shen', 'Primates', 'Agropelter', 'Bigfoot', 'Hibagon', 'Ju',
    'Satori', 'Sh', 'Shug', 'Sun', 'Vanara', 'Yeren', 'Yeti', 'Yowie', 'Rabbits', 'Al', 'Jackalope', 'Moon', 'Skvader',
    'Wisakedjak', 'Wolpertinger', 'Reptiles', 'Agoa', 'Ammut', 'Bakunawa', 'Basilisk', 'Black', 'Chalkydri', 'Chinese',
    'Cipactli', 'Dragon', 'Dungavenhooter', 'Knucker', 'Kurma', 'Loch', 'Loveland', 'Makara', 'Mokele', 'Mo', 'Morgawr',
    'Mungoon', 'Peluda', 'Reptilian', 'Sewer', 'Sobek', 'Taniwha', 'Whowie', 'Wyvern', 'Zaratan', 'Reptiles', 'Alicante',
    'Amphisbaena', 'Amphithere', 'Apep', 'Azhi', 'Basilisk', 'Bakonawa', 'Biscione', 'Cockatrice', 'Dragon', 'Drake',
    'Echidna', 'F', 'Feathered', 'Garafena', 'Gorgon', 'Hoop', 'Indus', 'Hydra', 'Jaculus', 'Jasconius', 'J', 'Lamia',
    'Lindworm', 'Madame', 'Meretseger', 'Mongolian', 'Naga', 'N', 'Orm', 'Ouroboros', 'Python', 'Rainbow', 'Sea',
    'Tarasque', 'Tsuchinoko', 'Typhon', 'Ur', 'Wyvern', 'Yamata', 'Zilant', 'Rodents', 'Afanc', 'Ratatoskr', 'Rat',
    'Wolpertinger', 'Ungulates', 'Antelopes', 'Actaeon', 'Ceryneian', 'Deer', 'Eik', 'Goldhorn', 'Jackalope', 'Keresh',
    'Peryton', 'Qilin', 'Tarand', 'White', 'Xeglun', 'Bovines', 'Au', 'Bai', 'Kujata', 'Bicorn', 'Bonnacon', 'Hodag',
    'Minotaur', 'Nandi', 'Sarangay', 'Shedu', 'Ushi', 'Camelids', 'Allocamelus', 'Heavenly', 'Caprids', 'Amalthea',
    'Aries', 'Barometz', 'Capricornus', 'Chimera', 'Dahu', 'Faun', 'Goldhorn', 'Hei', 'Khnum', 'Satyr', 'Sidehill',
    'Tanngrisnir', 'Chrysomallos', 'Equines', 'Main', 'Anggitay', 'Arion', 'Balius', 'Buraq', 'Centaur', 'Cheval',
    'Cheval', 'Chiron', 'Chollima', 'Drap', 'Gytrash', 'Haizum', 'Hippogriff', 'Ipotane', 'Karkadann', 'Kotobuki',
    'Longma', 'Mankayia', 'Onocentaur', 'Pegasus', 'Pooka', 'Sleipnir', 'Simurgh', 'Sihuanaba', 'Tikbalang', 'Uchchaihshravas',
    'Unicorn', 'Winged', 'Water', 'Ceffyl', 'Each', 'Enbarr', 'Hippocampus', 'Ichthyocentaurs', 'Kelpie', 'Morvarc',
    'Nixie', 'Nuckelavee', 'Nuggle', 'Tangie', 'White', 'Pachyderms', 'Abath', 'Baku', 'Behemoth', 'Quugaarpak', 'Taweret',
    'Pigs', 'Calydonian', 'Erymanthian', 'Zhu', 'Xenarthrans', 'Mapinguari', 'Megafauna', 'Giants', 'Artificial', 'This',
    'Automaton', 'Blodeuwedd', 'Brazen', 'Doll', 'Frankenstein', 'Galatea', 'Gingerbread', 'Golem', 'Homunculus', 'Nephele',
    'Shabti', 'Tokeloshe', 'Tilberi', 'Tsukumogami', 'Tulpa', 'Tupilaq', 'Ushabti', 'Various', 'Body', 'Blood', 'Alan',
    'Chupacabra', 'Dhampir', 'Preta', 'Golden', 'Kappa', 'Kekkai', 'Lamia', 'Manananggal', 'Mandurugo', 'Redcap', 'Rokurokubi',
    'Sigbin', 'Vampire', 'Werewolf', 'Yuki', 'Bone', 'Bloody', 'Gashadokuro', 'Grim', 'Skeleton', 'Eye', 'Argus', 'Basilisk',
    'Catoblepas', 'Cockatrice', 'Cyclopes', 'Gorgon', 'Hitotsume', 'Lamia', 'Lynx', 'Mokumokuren', 'One', 'Main', 'Face', 'Asura',
    'Deva', 'Noppera', 'Hair', 'Futakuchi', 'Harionago', 'Mavka', 'Medusa', 'Head', 'Amphisbaena', 'Cerberus', 'Chimera',
    'Chonchon', 'Double', 'Dullahan', 'Hekatonkheires', 'Hydra', 'Lernaean', 'Nine', 'Nukekubi', 'Rokurokubi', 'Orthrus',
    'Shesha', 'Penanggalan', 'Wany', 'Xing', 'Yacuruna', 'Yamata', 'Limbs', 'Asura', 'Deva', 'Hekatonkheires', 'Hinkypunk',
    'Kui', 'O', 'Sleipnir', 'Three', 'Mouth', 'Futakuchi', 'Kuchisake', 'Skin', 'Selkie', 'Skin', 'Swan', 'Tail', 'Bakeneko',
    'Kitsune', 'Yamata', 'Kumiho', 'Hulder', 'Nguruvilu', 'Neck', 'Serpopard', 'Rokurokubi', 'Vampire', 'Torso', 'Manananggal',
    'Geryon', 'Abdomen', 'Pixiu', 'Concepts', 'Battle', 'Androktasiai', 'Erinyes', 'Hipag', 'Hysminai', 'Keres', 'Lemures',
    'Makhai', 'Onry', 'Phonoi', 'Valkyrie', 'Vengeful', 'Birth', 'Phoenix', 'Ubume', 'Death', 'Ammit', 'Banshee', 'Demon',
    'Devil', 'Dullahan', 'Ghost', 'Grim', 'Ox', 'Phoenix', 'Undead', 'Valkyrie', 'Vampire', 'Dream', 'Alp', 'Baku', 'Carbuncle',
    'Devil', 'Drude', 'Incubus', 'Mermaid', 'Nightmare', 'Nue', 'Oni', 'Sandman', 'Satori', 'Zduha', 'Evil', 'Basilisk', 'Balor',
    'Catoblepas', 'Cockatrice', 'Gorgon', 'Medusa', 'Euryale', 'Stheno', 'Fertility', 'Abatwa', 'Alan', 'Boto', 'Faun',
    'Gancanagh', 'German', 'Incubus', 'Maenad', 'Nymph', 'Pombero', 'Popobawa', 'Satyr', 'Sileni', 'Unicorn', 'Zemyna',
    'Simurgh', 'Fortune', 'Carbuncle', 'Dwarf', 'Egbere', 'Genie', 'Leib', 'Leprechaun', 'Matagot', 'Pixiu', 'Sarimanok',
    'Sigbin', 'Yaksha', 'Light', 'Angel', 'Chalkydri', 'Deity', 'Lampetia', 'Will', 'Dragon', 'Love', 'Cupid', 'Gancanagh',
    'Selkie', 'Swan', 'Madame', 'Melusine', 'Tennin', 'Undine', 'Sound', 'Banshee', 'Encantado', 'Fenghuang', 'Fossegrim',
    'Mermaid', 'Nue', 'Siren', 'Speech', 'Note', 'Gef', 'Satan', 'Time', 'Chronos', 'Father', 'Gremlin', 'Wisdom', 'Baba',
    'Bai', 'Griffin', 'Salmon', 'Sphinx', 'Valravn', 'Demons', 'Elements', 'Aether', 'Chalkydri', 'Deity', 'Elemental',
    'Spirit', 'Angel', 'Demon', 'Devil', 'Yokai', 'Nymph', 'Elf', 'Fairy', 'Air', 'Ala', 'Elemental', 'Feldgeister', 'Zduha',
    'Darkness', 'Black', 'Bogeyman', 'Ghost', 'Grim', 'Wechuge', 'Wendigo', 'Shadow', 'Vampire', 'Werewolf', 'Oni', 'Gashadokuro',
    'Camazotz', 'Wild', 'Hell', 'Earth', 'Asag', 'Bluecap', 'Elemental', 'Dwarf', 'Earth', 'Gargoyle', 'Giant', 'Gnome', 'Goblin',
    'Golem', 'Monopod', 'Nymph', 'Ogre', 'Oread', 'Ten', 'Troll', 'Fire', 'Further', 'Basan', 'Bluecap', 'Cherufe', 'Chimera',
    'Dragon', 'Elemental', 'Ifrit', 'Hellhound', 'Lampad', 'Phoenix', 'Salamander', 'Light', 'Angel', 'Chalkydri', 'Light',
    'Rainbow', 'Rainbow', 'Metal', 'Alicanto', 'Pixiu', 'Carbunclo', 'Chrysomallos', 'Cyclopes', 'Griffin', 'Gnome', 'Leprechaun',
    'Bulgasari', 'Thunder', 'Chinese', 'Cyclopes', 'Feldgeister', 'Kitsune', 'Raij', 'Thunderbird', 'Valkyrie', 'Water', 'Afanc',
    'Amefurikoz', 'Aspidochelone', 'Bloody', 'Buggane', 'Bunyip', 'Camenae', 'Capricorn', 'Cetus', 'Charybdis', 'Chinese', 'Cai',
    'Crinaeae', 'Davy', 'Draug', 'Each', 'Elemental', 'Fish', 'Fossegrim', 'Fur', 'Gargouille', 'Grindylow', 'Haetae', 'Hippocamp',
    'Hydra', 'Ichthyocentaur', 'Jasconius', 'Jengu', 'Kappa', 'Kelpie', 'Kraken', 'Lake', 'Lavellan', 'Leviathan', 'Loch',
    'Lorelei', 'Lusca', 'Makara', 'Melusine', 'Mami'
]


situations = [
    'in the distant cosmos', 'at the office', 'at the Olympic Games', 'in a haunted house', 'on a deserted island', 'in a medieval castle',
    'at a rock concert', 'in a virtual reality game', 'at a wedding', 'in a secret laboratory', 'at a crime scene', 'in a bustling marketplace',
    'at a fashion show', 'in a snowstorm', 'at a children\'s birthday party', 'in a tropical jungle', 'at a political debate', 'in a futuristic city',
    'at a book signing', 'in a submarine', 'at a rodeo', 'in a desert oasis', 'at a film festival', 'in a parallel universe', 'at a space station',
    'in a time machine', 'at a magic show', 'in a haunted forest', 'at a chess tournament', 'in a post-apocalyptic world'
]


few_shot_nicknames = """My task is to create 15 new funny words related to me. Use all your creativity and create 10 new words. 
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
        for i in range(4):
            sample_list = make_sample(path, 4, 8)
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
