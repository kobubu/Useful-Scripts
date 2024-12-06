import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    # Открываем PDF-документ
    doc = fitz.open(pdf_path)

    # Извлекаем текст со всех страниц
    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        full_text += text + "\n"

    return full_text



if __name__ == "__main__":
    dir = "C:\\Users\\Igor\\Desktop\\работа\\pdf\\"
    doc_name = "Глоссарий_РЖД.pdf"
    doc_path = dir + doc_name

    # Извлекаем текст из PDF
    full_text = extract_text_from_pdf(doc_path)

    # Сохраняем текст в файл
    with open(dir + "extracted_text.txt", "w", encoding="utf-8") as text_file:
        text_file.write(full_text)

    print("Текст успешно извлечен и сохранен в extracted_text.txt")
