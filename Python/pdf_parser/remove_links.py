import fitz  # PyMuPDF
import os

def delete_links_from_pdf(pdf_path, new_pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc[page_num]
        # Получаем все ссылки на странице
        links = page.get_links()
        for link in links:
            # Удаляем каждую ссылку
            page.delete_link(link)
    doc.save(new_pdf_path)
    doc.close()

if __name__ == "__main__":
    dir_path = "C:\\Users\\Igor\\Downloads\\drive-download-20250324T090620Z-001\\"
    cleared_dir = os.path.join(dir_path, "cleared")

    # Создаем папку, если она не существует
    if not os.path.exists(cleared_dir):
        os.makedirs(cleared_dir)

    # Проходим по всем файлам в директории
    for filename in os.listdir(dir_path):
        if filename.endswith(".pdf"):  # Проверяем, что файл имеет расширение .pdf
            doc_path = os.path.join(dir_path, filename)
            new_name = filename
            new_pdf_path = os.path.join(cleared_dir, new_name)

            delete_links_from_pdf(doc_path, new_pdf_path)
            print(f"Гиперссылки успешно удалены из: {filename}. Новый файл сохранен как: {new_name}")
