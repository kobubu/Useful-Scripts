import re
import pandas as pd

dir = r'C:\\Users\\Igor\\Desktop\\работа\\аналитика базы вопросов\\датасеты для обучения\\'
file = dir+r'20241124_MASTERFILE_BA_fr_and_ja__mytona_ru-en_combined_dataset_saved_in_csv.xlsx'
df = pd.read_excel(file)

df['Cleaned Content'] = df['Content'].apply(lambda x: re.sub(r'^.*?Discussion:\n', '', x, flags=re.DOTALL))

df.to_excel(dir+'20241124_CLEANED_MASTERFILE_BA_fr_and_ja__mytona_ru-en_combined_dataset_saved_in_csv.xlsx')
print(df.tail())


