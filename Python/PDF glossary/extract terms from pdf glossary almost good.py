import fitz  # PyMuPDF
import pandas as pd
import re


def parse_pdf_to_tree(doc_path, output_excel):
    # Открываем PDF
    doc = fitz.open(doc_path)

    # Инициализация переменных
    text_data = []
    for page_num in range(8, 394):  # C 9-й по 394-ю страницы
        page = doc.load_page(page_num)
        text = page.get_text("text")
        # Убираем заголовки и футеры
        lines = text.split('\n')
        if len(lines) > 3:
            lines = lines[2:-1]
        text = '\n'.join(lines)
        text_data.append(text)

    # Объединяем все страницы в один текст
    full_text = '\n'.join(text_data)

    # Разбиение на строки
    lines = full_text.splitlines()

    # Структура данных для дерева
    tree = []
    stack = [tree]  # Стек для отслеживания текущего уровня в дереве
    current_root = None

    for line in lines:
        line = line.lstrip()

        # Определяем уровень вложенности на основе количества символов "~"
        level = 0
        while line.startswith('~'):
            level += 1
            line = line[1:].lstrip()

        # Используем регулярное выражение для разделения на RU и EN
        match = re.match(r"^(.*?)\s{2,}([a-zA-Z\s\-\(\)\d]+)$", line)
        if match:
            ru = match.group(1).strip()
            en = match.group(2).strip()
        else:
            ru = line.strip()
            en = ''

        # Обработка структуры вложенности
        while len(stack) > level + 1:
            stack.pop()

        # Добавляем текущий термин в структуру
        node = {'RU': ru, 'EN': en, 'children': []}
        stack[-1].append(node)

        # Добавляем список детей для текущего узла в стек
        stack.append(node['children'])

    # Плоское представление дерева для записи в Excel
    def flatten_tree(nodes, parent_ru=None):
        for node in nodes:
            yield {'RU': node['RU'], 'EN': node['EN'], 'Parent RU': parent_ru}
            yield from flatten_tree(node['children'], parent_ru=node['RU'])

    # Собираем все записи
    records = list(flatten_tree(tree))

    # Создаем DataFrame
    df = pd.DataFrame(records)

    # Сохраняем результат в Excel
    df.to_excel(output_excel, index=False)
    print(f"Результат сохранен в {output_excel}")


# Использование
if __name__ == "__main__":
    dir = "C:\\Users\\Igor\\Desktop\\работа\\pdf\\"
    doc_name = "Глоссарий_РЖД.pdf"
    output_excel = "parsed_glossary_tree.xlsx"
    doc_path = dir + doc_name

    parse_pdf_to_tree(doc_path, dir+output_excel)
