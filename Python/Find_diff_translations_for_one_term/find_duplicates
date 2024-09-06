import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import PatternFill

# Путь к файлу Excel
file_path = "C:/Users/Igor/Downloads/MwE_Глоссарий.xlsx"

# Загрузка данных из файла Excel
all_sheets = pd.read_excel(file_path, sheet_name=None)

# Подготовка списка столбцов с переводами
translation_columns = ['zh', 'fr', 'de', 'es', 'it', 'ja', 'ko']

# Объединение данных из всех вкладок в один DataFrame
dfs = []
for sheet_name, df in all_sheets.items():
    df['source_sheet'] = sheet_name  # Добавляем столбец для отслеживания источника данных
    dfs.append(df)
combined_df = pd.concat(dfs, ignore_index=True)

# Группировка данных по столбцу 'en' и проверка наличия разных переводов
grouped = combined_df.groupby('en').apply(lambda group: any(group[lang].nunique() > 1 for lang in translation_columns))

# Получение списка терминов, у которых есть разные переводы
terms_with_different_translations = grouped[grouped].index

# Выборка строк, соответствующих этим терминам
filtered_df = combined_df[combined_df['en'].isin(terms_with_different_translations)]

# Создание Excel-файла и применение цветовой стилизации
output_file_path = "C:/Users/Igor/Downloads/Результаты2.xlsx"
wb = Workbook()
ws = wb.active

# Копирование данных из DataFrame в Excel
for row in dataframe_to_rows(filtered_df, index=False, header=True):
    ws.append(row)


# Сохранение файла
wb.save(output_file_path)
print("Результаты сохранены в файл:", output_file_path)
