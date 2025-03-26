import torch
from transformers import (
    RobertaTokenizer,
    RobertaForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd
import numpy as np

# Установите tensorboard если еще не установлен
try:
    from torch.utils.tensorboard import SummaryWriter
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorboard"])
    from torch.utils.tensorboard import SummaryWriter

# Проверка GPU
print("Проверка устройств...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Используемое устройство: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Память GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# Загрузка данных
print("\nЗагрузка данных...")
df = pd.read_excel(r'D:\models\модели 2025\localization_report.xlsx')
df_russian = df[df['language'] == 'russian'].copy()
df_russian['label'] = df_russian['has_localization_issues'].astype(int)

# Балансировка данных
df_pos = df_russian[df_russian['label'] == 1]
df_neg = df_russian[df_russian['label'] == 0]
print(f"Распределение:\nПоложительных: {len(df_pos)}\nОтрицательных: {len(df_neg)}")

df_pos_upsampled = pd.concat([df_pos] * 4)
df_neg_sampled = df_neg.sample(n=min(len(df_neg), len(df_pos)*4), random_state=42)
df_balanced = pd.concat([df_pos_upsampled, df_neg_sampled]).sample(frac=1, random_state=42)

# Подготовка Dataset
tokenizer = RobertaTokenizer.from_pretrained("RussianNLP/ruRoBERTa-large-rucola")

class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]),
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'][0].to(device),
            'attention_mask': encoding['attention_mask'][0].to(device),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long).to(device)
        }

# Разделение данных
X_train, X_test, y_train, y_test = train_test_split(
    df_balanced['text'].astype(str).tolist(),
    df_balanced['label'].values,
    test_size=0.1,
    random_state=42,
    stratify=df_balanced['label']
)

train_dataset = CustomDataset(X_train, y_train, tokenizer)
eval_dataset = CustomDataset(X_test, y_test, tokenizer)

# Инициализация модели на GPU
model = RobertaForSequenceClassification.from_pretrained(
    "RussianNLP/ruRoBERTa-large-rucola",
    num_labels=2
).to(device)

# Конфигурация обучения (с исправленным eval_strategy вместо устаревшего evaluation_strategy)
training_args = TrainingArguments(
    output_dir="./gpu_results",
    eval_strategy="steps",  # Исправлено здесь
    eval_steps=100,
    logging_steps=50,
    save_steps=200,
    learning_rate=3e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    num_train_epochs=5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    fp16=True,
    report_to="tensorboard",
    optim="adamw_torch",
    logging_dir="./logs"
)

def compute_metrics(pred):
    labels = pred.label_ids.cpu()
    preds = pred.predictions.argmax(-1).cpu()
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='binary', zero_division=0
    )
    return {
        'accuracy': accuracy_score(labels, preds),
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# Обучение
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

print("\nСтарт обучения на GPU...")
trainer.train()

# Сохранение модели
model.save_pretrained("./best_gpu_model")
tokenizer.save_pretrained("./best_gpu_model")

# Оценка
results = trainer.evaluate()
print("\nФинальные метрики:")
print(f"Accuracy: {results['eval_accuracy']:.4f}")
print(f"F1: {results['eval_f1']:.4f}")
print(f"Precision: {results['eval_precision']:.4f}")
print(f"Recall: {results['eval_recall']:.4f}")
