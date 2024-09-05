import pandas as pd
from openpyxl import Workbook

dir = "C:\\Users\\Igor\\Desktop\\работа\\excel parser\\"
name = "Project R & Inlingo_TM Update-RU_20240903.xlsx"
# Загрузка данных из Excel файла
df = pd.read_excel(dir+name, sheet_name=None)

wb = Workbook()
ws = wb.active

headers = ['source', 'target', 'ID', 'Extra']
ws.append(headers)

for sheet_name, sheet_data in df.items():
    for index, row in sheet_data.iterrows():
        # Сбор данных из колонок CHS, ru и ID
        source = row['CHS']
        target = row['ru']
        id = row['ID']
        extra = row['Extra']


        ws.append([source, target, id, extra])

wb.save(dir + name + '_output.xlsx')

print(f"Данные успешно записаны в {dir}{name}_output.xlsx")