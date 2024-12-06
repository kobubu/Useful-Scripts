import fitz  # PyMuPDF
import pandas as pd
import re


class Term:
    def __init__(self, source: str, target: str):
        """
        Инициализация объекта Term.

        :param source: Исходное слово или фраза.
        :param target: Целевое слово или фраза.
        """
        self.source = source
        self.target = target

    def __str__(self):
        """
        Возвращает строковое представление объекта Term.

        :return: Строка, представляющая объект Term.
        """
        return f"Term(source='{self.source}', target='{self.target}')"

    def __repr__(self):
        """
        Возвращает "официальное" строковое представление объекта Term.

        :return: Строка, представляющая объект Term.
        """
        return self.__str__()


def parse_text(text: str) -> list:
    """
    Парсит текст и создает экземпляры класса Term.

    :param text: Текст для парсинга.
    :return: Список экземпляров класса Term.
    """
    terms = []
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Ищем русские и английские слова
        match = re.match(r'([А-я~\s_-]*)([A-z_\s-]*)', line)
        if match:
            source = match.group(1).strip()
            target = match.group(2).strip()
            terms.append(Term(source, target))
        else:
            # Если не нашли разделение, пытаемся разделить по другим символам
            parts = re.split(r'\s+', line)
            if len(parts) > 1:
                ru_parts = []
                en_parts = []
                for part in parts:
                    if re.match(r'[А-я~\s_-]*', part):
                        ru_parts.append(part)
                    elif re.match(r'[A-z_\s-]*', part):
                        en_parts.append(part)
                if ru_parts and en_parts:
                    source = ' '.join(ru_parts).strip()
                    target = ' '.join(en_parts).strip()
                    terms.append(Term(source, target))

    return terms


def parse_pdf_to_text(doc_path):
    # Open the PDF document
    doc = fitz.open(doc_path)

    # Extract text from pages 9 to 394 (0-based: pages 8 to 393)
    text_data = []
    for page_num in range(8, 394):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        text_data.append(text)

    # Объединяем текст из всех страниц
    full_text = '\n'.join(text_data)
    return full_text


if __name__ == "__main__":
    dir = "C:\\Users\\Igor\\Desktop\\работа\\pdf\\"
    doc_name = "Глоссарий_РЖД.pdf"
    output_excel = dir + "parsed_glossary_tree.xlsx"
    doc_path = dir + doc_name

    # Извлекаем текст из PDF
    full_text = parse_pdf_to_text(doc_path)

    # Парсим текст и создаем экземпляры Term
    terms = parse_text(full_text)

    # Создаем DataFrame и сохраняем в Excel
    df = pd.DataFrame([(term.source, term.target) for term in terms], columns=['Source', 'Target'])
    df.to_excel(output_excel, index=False)

    # Выводим результаты
    for term in terms:
        print(term)
