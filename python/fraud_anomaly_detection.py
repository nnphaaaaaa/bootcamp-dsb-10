import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (precision_score, recall_score, f1_score,
                             confusion_matrix, classification_report,
                             roc_auc_score, average_precision_score)
from sklearn.utils import compute_class_weight
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.svm import OneClassSVM

import tensorflow as tf

# Reproducibility
# ล็อค seed เพื่อให้ผลลัพธ์เดิมเสมอเมื่อนำไปรันใหม่
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
tf.random.set_seed(RANDOM_STATE)
df = pd.read_csv("creditcard.csv")
# df.info()
# df.describe()
print("Total missing values:", int(df.isnull().sum().sum()))
print(f"Original dataset shape: {df.shape}")
df.drop_duplicates(inplace=True)
print(f"After removing duplicates: {df.shape}")
print(f"Fraud ratio: {df['Class'].mean():.4%}")

sns.countplot(x='Class', data=df)
plt.title('Class Distribution (0 = Normal, 1 = Fraud)')
plt.show()

##split train test
X = df.drop('Class', axis=1)
y = df['Class']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

## preprocessing
amount_scaler = StandardScaler()
time_scaler = StandardScaler()

X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

# Fit บน Train เท่านั้น ( กัน data leakage)
X_train_scaled['Amount'] = amount_scaler.fit_transform(X_train[['Amount']])
X_test_scaled['Amount'] = amount_scaler.transform(X_test[['Amount']])

X_train_scaled['Time'] = time_scaler.fit_transform(X_train[['Time']])
X_test_scaled['Time'] = time_scaler.transform(X_test[['Time']])

print(f"\nTrain set: {X_train.shape[0]} samples | Fraud: {int(y_train.sum())}")
print(f"Test set:  {X_test.shape[0]} samples | Fraud: {int(y_test.sum())}")

## class weight compute on TRAIN only
weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weight = {0: weights[0], 1: weights[1]}
print(f"\nClass weights: Normal={class_weight[0]:.4f}, Fraud={class_weight[1]:.4f}")


## Helper function
## store_result() เพิ่มพารามิเตอร์ model_type
##เพื่อแยก supervised / unsupervised ตอนเปรียบเทียบ
results = {}

def evaluate_model(y_true, y_pred, y_score=None):
    """Print metrics, classification report, and confusion matrix.
    Pass y_score (probabilities / anomaly scores) to also get AUC metrics."""
    print(f"  Precision: {precision_score(y_true, y_pred):.4f}")
    print(f"  Recall:    {recall_score(y_true, y_pred):.4f}")
    print(f"  F1 Score:  {f1_score(y_true, y_pred):.4f}")
    if y_score is not None:
        print(f"  ROC-AUC:   {roc_auc_score(y_true, y_score):.4f}")
        print(f"  PR-AUC:    {average_precision_score(y_true, y_score):.4f}")
    print(f"\n  Classification Report:\n{classification_report(y_true, y_pred)}")
    print(f"  Confusion Matrix:\n{confusion_matrix(y_true, y_pred)}\n")


def store_results(name, y_true, y_pred, y_score=None, model_type='Supervised'):
    """Save metrics to the results dict for the final comparison table.
    model_type ('Supervised'/'Unsupervised') lets us compare like-with-like:
    supervised models saw fraud labels during training, unsupervised models
    did not, so ranking them in one combined list would be misleading."""
    results[name] = {
        'Type': model_type,
        'Precision': precision_score(y_true, y_pred),
        'Recall': recall_score(y_true, y_pred),
        'F1': f1_score(y_true, y_pred),
        'ROC_AUC': roc_auc_score(y_true, y_score) if y_score is not None else np.nan,
        'PR_AUC': average_precision_score(y_true, y_score) if y_score is not None else np.nan,
    }


# ============================================================
##  Logistic Regression Baseline + 5-Fold CV
# ============================================================
print("=" * 50)
print("BASELINE: Logistic Regression + 5-Fold Stratified CV")
print("=" * 50)

scale_cols = ['Time', 'Amount']
preprocessor = ColumnTransformer(
    transformers=[('scale', StandardScaler(), scale_cols)],
    remainder='passthrough'  # leave V1..V28 untouched
)

# Pipeline จะช่วยให้การทำ CV ปลอดภัยจาก Leakage
lr_pipe = Pipeline([
    ('prep', preprocessor),
    ('clf', LogisticRegression(class_weight='balanced', max_iter=1000))
])

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
cv_results = cross_validate(
    lr_pipe, X, y,  # RAW data -> pipeline scales per fold
    cv=skf,
    scoring=['f1', 'recall', 'precision', 'average_precision'],
    return_train_score=False
)

for i in range(5):
    print(f"  Fold {i + 1}: F1={cv_results['test_f1'][i]:.4f} | "
          f"Recall={cv_results['test_recall'][i]:.4f} | "
          f"Precision={cv_results['test_precision'][i]:.4f}")
print(f"\n  F1:        {cv_results['test_f1'].mean():.4f} ± {cv_results['test_f1'].std():.4f}")
print(f"  Recall:    {cv_results['test_recall'].mean():.4f} ± {cv_results['test_recall'].std():.4f}")
print(f"  Precision: {cv_results['test_precision'].mean():.4f} ± {cv_results['test_precision'].std():.4f}")
print(f"  PR-AUC:    {cv_results['test_average_precision'].mean():.4f} ± "
      f"{cv_results['test_average_precision'].std():.4f}")
print(f"  F1 spread (max-min): "
      f"{cv_results['test_f1'].max() - cv_results['test_f1'].min():.4f}\n")

# Fit the LR baseline once on the held-out split for the comparison table.
lr_pipe.fit(X_train, y_train)  # X_train is RAW -> no double scaling
lr_pred = lr_pipe.predict(X_test)
lr_score = lr_pipe.predict_proba(X_test)[:, 1]
evaluate_model(y_test, lr_pred, lr_score)
store_results('Logistic Regression', y_test, lr_pred, lr_score, model_type='Supervised')


# ============================================================
# MODEL 1: Neural Network (Keras)
# ============================================================
print("=" * 50)
print("MODEL 1: Neural Network")
print("=" * 50)

X_tr, X_val, y_tr, y_val = train_test_split(
    X_train_scaled, y_train,
    test_size=0.2, random_state=RANDOM_STATE, stratify=y_train
)

model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(X_train_scaled.shape[1],)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation='sigmoid'),
])
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
model.compile(
    loss='binary_crossentropy',
    optimizer=optimizer,
    # Track PR-AUC during training, not just accuracy.
    metrics=['accuracy', tf.keras.metrics.AUC(name='pr_auc', curve='PR')]
)
history = model.fit(
    X_tr, y_tr,
    epochs=10,
    batch_size=32,
    validation_data=(X_val, y_val),  # validation, NOT test
    class_weight=class_weight,
    verbose=1
)
# .ravel() flattens the (n, 1) output to (n) so sklearn metrics don't warn.
nn_score = model.predict(X_test_scaled).ravel()
y_pred_nn = (nn_score > 0.5).astype(int)
evaluate_model(y_test, y_pred_nn, nn_score)
store_results('Neural Network', y_test, y_pred_nn, nn_score, model_type='Supervised')
# Training history
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(history.history['loss'], label='Train Loss')
axes[0].plot(history.history['val_loss'], label='Val Loss')
axes[0].set_title('Loss Over Epochs')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss')
axes[0].legend()

axes[1].plot(history.history['accuracy'], label='Train Accuracy')
axes[1].plot(history.history['val_accuracy'], label='Val Accuracy')
axes[1].set_title('Accuracy Over Epochs')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Accuracy')
axes[1].legend()

plt.suptitle('Neural Network Training History', fontsize=14)
plt.tight_layout()
plt.show()

X_train_normal = X_train_scaled[y_train == 0]
print(f"\nTraining anomaly models on {X_train_normal.shape[0]} normal transactions only\n")
X_train_normal = X_train[y_train == 0]
print(f"\nTraining anomaly detection models on {X_train_normal.shape[0]} normal transactions only\n")

print("=" * 50)
print("MODEL 2: Isolation Forest")
print("=" * 50)
# Derive the expected anomaly rate from the data instead of hard-coding
# 0.00173 (in production you would not know the true fraud rate up front).
contamination = float(y_train.mean())
if_model = IsolationForest(contamination=contamination, random_state=RANDOM_STATE)
if_model.fit(X_train_normal)

if_raw = if_model.predict(X_test_scaled)
if_preds = np.where(if_raw == -1, 1, 0)  # -1 anomaly -> fraud(1), 1 normal -> 0
# decision_function: higher = more normal. Negate so higher = more fraud-like.
if_score = -if_model.decision_function(X_test_scaled)
evaluate_model(y_test, if_preds, if_score)
store_results('Isolation Forest', y_test, if_preds, if_score, model_type='Unsupervised')

print("=" * 50)
print("MODEL 3: K-Means Clustering")
print("=" * 50)
kmeans_model = KMeans(n_clusters=2, random_state=RANDOM_STATE, n_init=10)
kmeans_model.fit(X_train_scaled.values)
kmeans_preds = kmeans_model.predict(X_test_scaled.values)
if np.sum(kmeans_preds == 0) < np.sum(kmeans_preds == 1):
    kmeans_preds = 1 - kmeans_preds
evaluate_model(y_test, kmeans_preds)                     # no score -> AUC = NaN
store_results('K-Means', y_test, kmeans_preds, model_type='Unsupervised')

print("=" * 50)
print("MODEL 4: One-Class SVM")
print("=" * 50)
svm_train = X_train_normal.sample(
    n=min(20000, len(X_train_normal)), random_state=RANDOM_STATE
)
svm_model = OneClassSVM(kernel='rbf', nu=0.01, gamma='scale')
svm_model.fit(svm_train)

svm_raw = svm_model.predict(X_test_scaled)
svm_preds = np.where(svm_raw == -1, 1, 0)
svm_score = -svm_model.decision_function(X_test_scaled)  # higher = more fraud-like
evaluate_model(y_test, svm_preds, svm_score)
store_results('One-Class SVM', y_test, svm_preds, svm_score, model_type='Unsupervised')


print("=" * 50)
print("MODEL COMPARISON (grouped, sorted by PR-AUC within group)")
print("=" * 50)
results_df = pd.DataFrame(results).T
type_rank = {'Supervised': 0, 'Unsupervised': 1}
results_df['_type_rank'] = results_df['Type'].map(type_rank)
results_df = results_df.sort_values(
    ['_type_rank', 'PR_AUC'], ascending=[True, False]
).drop(columns='_type_rank')

for group in ['Supervised', 'Unsupervised']:
    block = results_df[results_df['Type'] == group].drop(columns='Type')
    print(f"\n--- {group} ---")
    print(block.to_string())
plot_metrics = ['Precision', 'Recall', 'F1', 'PR_AUC']
plot_df = results_df[plot_metrics].astype(float)

fig, ax = plt.subplots(figsize=(13, 6))
plot_df.plot(kind='bar', ax=ax, colormap='viridis', alpha=0.85)
n_supervised = int((results_df['Type'] == 'Supervised').sum())
ax.axvline(n_supervised - 0.5, color='gray', linestyle='--', linewidth=1.5)
ax.text((n_supervised - 1) / 2, 1.02, 'Supervised',
        ha='center', va='bottom', fontsize=11, fontweight='bold',
        transform=ax.get_xaxis_transform())
ax.text(n_supervised + (len(results_df) - n_supervised - 1) / 2, 1.02, 'Unsupervised',
        ha='center', va='bottom', fontsize=11, fontweight='bold',
        transform=ax.get_xaxis_transform())

ax.set_title('Model Comparison: Supervised vs Unsupervised (PR-AUC included)')
ax.set_ylabel('Score')
ax.set_xlabel('Model')
ax.set_ylim(0, 1)
plt.xticks(rotation=15)
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()

print("\n✅ Fraud Detection Pipeline Complete!")

import joblib
import os
os.makedirs('deployment', exist_ok=True)
model.save('deployment/fraud_nn_model.keras')
joblib.dump(amount_scaler, 'deployment/amount_scaler.pkl')
joblib.dump(time_scaler, 'deployment/time_scaler.pkl')
joblib.dump(list(X.columns), 'deployment/feature_columns.pkl')
print("\n✅ Saved model + scalers + column order to deployment/")


def predict_transaction(raw_transaction: dict) -> dict:
    # Load artifacts (in production these are loaded once at startup, not per call)
    nn = tf.keras.models.load_model('deployment/fraud_nn_model.keras')
    amt_scaler = joblib.load('deployment/amount_scaler.pkl')
    tm_scaler = joblib.load('deployment/time_scaler.pkl')
    cols = joblib.load('deployment/feature_columns.pkl')

    # Build a one-row frame and apply the SAME scaling learned at training time
    row = pd.DataFrame([raw_transaction])
    row['Amount'] = amt_scaler.transform(row['Amount'].values.reshape(-1, 1))
    row['Time'] = tm_scaler.transform(row['Time'].values.reshape(-1, 1))
    row = row[cols]  # enforce identical column order

    prob = float(nn.predict(row, verbose=0)[0][0])
    return {'fraud_probability': round(prob, 4), 'is_fraud': prob > 0.5}


# Demo: score one real test transaction by reversing the scaling back to raw,
# so the function receives the kind of unscaled input it would see in production.
sample_scaled = X_test.iloc[[0]].copy()
sample_raw = sample_scaled.copy()
sample_raw['Amount'] = amount_scaler.inverse_transform(sample_raw['Amount'].values.reshape(-1, 1))
sample_raw['Time'] = time_scaler.inverse_transform(sample_raw['Time'].values.reshape(-1, 1))

result = predict_transaction(sample_raw.iloc[0].to_dict())
print(f"\nDemo prediction on one transaction: {result}")
print(f"Actual label for that transaction: {int(y_test.iloc[0])}")
