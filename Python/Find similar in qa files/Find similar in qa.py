import pandas as pd
import os

# Укажите путь к файлу и столбцы для чтения
dir = r"C:\Users\Igor\Downloads\\"
filename_all = r"all_CustomQA_Jackpots.xlsx.xlsx"
file_path_all = os.path.join(dir, filename_all)

filename_only_valid = r"CustomQA_Jackpots.xlsx.xlsx"
file_path_valid = os.path.join(dir, filename_only_valid)

columns = ['Source text', 'Target text', 'Comment', 'Context', 'Source Language', 'Target Language']


# Прочитайте Excel файл в DataFrame
df_all = pd.read_excel(file_path_all, usecols=columns)
df_only_valid = pd.read_excel(file_path_valid, usecols=columns)


# Объедините два DataFrame
combined_df = pd.concat([df_all, df_only_valid], ignore_index=True)

# Удалите дубликаты из объединенного DataFrame
unique_pairs_df = combined_df.drop_duplicates(keep=False)

# Выведите новый DataFrame
print(unique_pairs_df)

# Создайте имя файла для сохранения результата
incorret_issues_filename = os.path.join(dir, f"only_incorrect_issues_in_{filename_all}.xlsx")
unique_pairs_df.to_excel(incorret_issues_filename, index=False)

# Проверьте, существует ли файл
print(os.path.exists(incorret_issues_filename))
