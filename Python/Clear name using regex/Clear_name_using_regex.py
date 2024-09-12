import re

# Регулярное выражение для поиска совпадений
PATTERN = re.compile(r'(?:(\d|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX)+[\.)] )\w+', re.IGNORECASE)

# Путь к файлу
dir = 'C:\\Users\\Igor\\Desktop\\работа\\nickname generation\\'
file_name = 'спикок ников.txt'
output_file_name = 'обработанный_список_ников.txt'

# Открываем файл и ищем совпадения
matches = []
with open(dir + file_name, encoding='utf-8') as file:
    for line in file:
        for match in PATTERN.finditer(line):
            matches.append(match.group(0))

# Сохраняем найденные совпадения в текстовый файл
with open(dir + output_file_name, 'w', encoding='utf-8') as output_file:
    for match in matches:
        output_file.write(match + '\n')

print(f"Найденные ники сохранены в файл: {dir + output_file_name}")
