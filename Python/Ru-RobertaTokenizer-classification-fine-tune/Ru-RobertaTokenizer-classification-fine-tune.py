from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight
import torch
import numpy as np
import pandas as pd
from transformers import EarlyStoppingCallback

# 1. Подготовка данных
print("Подготовка данных...")
df_russian = df[df['language'] == 'russian'].copy()
df_russian['label'] = df_russian['has_localization_issues'].astype(int)

print("\nРаспределение классов:")
print(df_russian['label'].value_counts())

# 2. Вычисление весов классов
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(df_russian['label']),
    y=df_russian['label']
)
class_weights = torch.tensor(class_weights, dtype=torch.float32)
print(f"\nВеса классов: {class_weights}")

# 3. Разделение данных
X_train, X_test, y_train, y_test = train_test_split(
    df_russian['text'].values,
    df_russian['label'].values,
    test_size=0.1,
    random_state=42,
    stratify=df_russian['label']
)

# 4. Инициализация токенизатора
tokenizer = RobertaTokenizer.from_pretrained("RussianNLP/ruRoBERTa-large-rucola")

# 5. Создание датасета
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=64):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'][0],
            'attention_mask': encoding['attention_mask'][0],
            'labels': torch.tensor(label, dtype=torch.long)
        }

train_dataset = CustomDataset(X_train, y_train, tokenizer)
test_dataset = CustomDataset(X_test, y_test, tokenizer)

# 6. Кастомный Trainer с исправленным методом compute_loss
class CustomTrainer(Trainer):
    def __init__(self, class_weights, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights
        self.loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights)
    
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):  # Исправлено
        labels = inputs.get("labels")
        outputs = model(**inputs)
        loss = self.loss_fct(outputs.logits.view(-1, model.config.num_labels), 
                            labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# 7. Загрузка модели
model = RobertaForSequenceClassification.from_pretrained(
    "RussianNLP/ruRoBERTa-large-rucola",
    num_labels=2
)

# 8. Параметры обучения (актуальные)
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",  # Исправлено на актуальное имя параметра
    save_strategy="epoch",
    logging_dir='./logs',
    logging_steps=10,
    learning_rate=2e-5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    report_to="none",
    use_cpu=True,  # Явное использование CPU
    fp16=False,
    bf16=False
)

# 9. Функция вычисления метрик
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='binary', zero_division=0
    )
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'positive_rate': np.mean(preds)
    }

# 10. Обучение модели
trainer = CustomTrainer(
    class_weights=class_weights.to('cpu'),  # Веса на CPU
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

print("\nНачало обучения...")
trainer.train()

# Сохранение результатов
model.save_pretrained("./localization_model")
tokenizer.save_pretrained("./localization_model")

# Оценка модели
results = trainer.evaluate()
print("\nФинальные метрики:")
print(results)
