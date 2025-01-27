from google.cloud import language_v1
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Путь к файлу OAuth 2.0 ключа
credentials_path = "{PATH_TO_OATH_2.0}"

# Области доступа для Natural Language API
SCOPES = ['https://www.googleapis.com/auth/cloud-language']

# Запуск процесса аутентификации
flow = InstalledAppFlow.from_client_secrets_file(
    credentials_path,
    scopes=SCOPES
)

# Запуск локального сервера для авторизации
credentials = flow.run_local_server(port=0)

# Создаем клиента с учетными данными
client = language_v1.LanguageServiceClient(credentials=credentials)

# Текст для анализа
text = "Google was founded in 1998 by Larry Page and Sergey Brin while they were Ph.D. students at Stanford University in California."
document = language_v1.types.Document(
    content=text, type_=language_v1.types.Document.Type.PLAIN_TEXT
)

# Определяем тональность текста
sentiment = client.analyze_sentiment(
    request={"document": document}
).document_sentiment

print(f"Текст: {text}")
print(f"Тональность: {sentiment.score}, {sentiment.magnitude}")

# Анализируем именованные сущности
entities_response = client.analyze_entities(
    request={"document": document}
)

# Выводим результаты анализа сущностей
print("\nИменованные сущности:")
for entity in entities_response.entities:
    print(f"Сущность: {entity.name}")
    print(f"Тип: {language_v1.Entity.Type(entity.type_).name}")
    print(f"Метаданные: {entity.metadata}")
    print(f"Степень уверенности: {entity.salience}")
    print("---")
