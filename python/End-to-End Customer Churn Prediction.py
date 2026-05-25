## preduct_customer_churn_with_python
## Author : Naphaphon Phayakkapes 
## link : https://colab.research.google.com/drive/1Z4Y6waYXG2BxfeoNsYwKEtXvMIsPUrdf?usp=sharing
## website : https://naphaphayak.wordpress.com/2026/05/26/end-to-end-customer-churn-prediction-%e0%b8%aa%e0%b8%a3%e0%b9%89%e0%b8%b2%e0%b8%87%e0%b9%82%e0%b8%a1%e0%b9%80%e0%b8%94%e0%b8%a5%e0%b8%97%e0%b8%b3%e0%b8%99%e0%b8%b2%e0%b8%a2-customer-churn-%e0%b8%94/
## source : https://www.kaggle.com/datasets/ankitverma2010/ecommerce-customer-churn-analysis-and-prediction/data

# ==========================================
# 1. Imports libraries 
# ==========================================

# Data Manipulation & Analysis
import numpy as np   
import pandas as pd  

# Visualization
import matplotlib.pyplot as plt  
import seaborn as sns           
import plotly.express as px     
import missingno as msno         

# Preprocessing & Feature Engineering
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import imblearn.over_sampling    

# Model Selection & Evaluation Metrics
from sklearn.model_selection import train_test_split, GridSearchCV, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, ConfusionMatrixDisplay
)

# Machine Learning Algorithms
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV, RidgeClassifierCV, SGDClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor, AdaBoostClassifier,
    GradientBoostingClassifier, BaggingClassifier, VotingClassifier
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

# Boosting Libraries
import xgboost as xgb
from xgboost import XGBClassifier
import lightgbm as lgb

from sklearn.feature_selection import SelectFromModel
from imblearn.over_sampling import SMOTE


## import dataset and cleaning 
# Read excel file 
df = pd.read_excel('E_Commerce_Dataset.xlsx',sheet_name="E Comm")
# Change column names to lowercase
df.columns = [col.lower() for col in df.columns]
# Drop columns 
df.drop(columns="customerid", inplace=True)



# ==========================================
# 2. EDA (Exploratory Data Analysis)
# ==========================================

df.shape         
df.head()        
df.info()       
df.describe()    
df.isnull().sum() 
df.duplicated().sum() 


# Analysis of the distribution of Categorical Features
cat_col = ['churn', 'preferredlogindevice', 'citytier',
        'preferredpaymentmode', 'gender', 'hourspendonapp',
       'numberofdeviceregistered', 'preferedordercat', 'satisfactionscore',
       'maritalstatus', 'numberofaddress', 'complain',
       'orderamounthikefromlastyear', 'couponused', 'ordercount']

plt.figure(figsize=(15,40))
plot_num = 1
for col in cat_col:
    plt.subplot(10,2,plot_num)
    sns.countplot(data=df, x=col, color = 'gray')
    plot_num += 1
    plt.tight_layout()

# Analysis of the distribution of Numeric Features 
num_col = ['tenure', 'warehousetohome', 'daysincelastorder', 'cashbackamount']

plt.figure(figsize=(15,40))
plot_num = 1
for col in num_col:
    plt.subplot(10,2,plot_num)
    sns.histplot(data=df, x=col, bins = 25, color = 'olive', alpha = 0.6)
    plot_num += 1
    plt.tight_layout()

# Analyze the relationship with Churn
plt.figure(figsize=(15,40))
plot_num = 1
for col in cat_col:
    if df[col].nunique() <= 8 and col != "churn":
        plt.subplot(10,2,plot_num)
        sns.countplot(data=df, x=col, hue="churn", palette=['cyan', 'blue'], alpha = 0.6)
        plot_num += 1
        plt.tight_layout()


def plot_features(columns, plot_type='count'):
    plt.figure(figsize=(15, 25))
    for i, col in enumerate(columns, 1):
        plt.subplot(8, 2, i)
        if plot_type == 'count':
            sns.countplot(data=df, x=col)
        elif plot_type == 'hist':
            sns.histplot(data=df, x=col, bins=25, kde=True, color = 'pink', alpha =0.6)
        elif plot_type == 'churn':
            sns.countplot(data=df, x=col, hue="churn")
        plt.tight_layout()
    plt.show()

#plot_features(cat_col, 'count')
plot_features(num_col, 'hist')



# ==========================================
# 3. Data processing 
# ==========================================

# Split dataset 
X = df.drop(columns=["churn"])  
y = df["churn"]                 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fill missing values
## Encode missing values in categorical Columns.
num_imputer = SimpleImputer(strategy='mean')
X_train[num_col] = num_imputer.fit_transform(X_train[num_col])
X_test[num_col]  = num_imputer.transform(X_test[num_col])

## Impute missing values in Numeric Columns.
cat_to_encode = X_train.select_dtypes(include=['object']).columns.tolist()
X_train = pd.get_dummies(X_train, columns=cat_to_encode)
X_test  = pd.get_dummies(X_test,  columns=cat_to_encode)
X_test = X_test.reindex(columns=X_train.columns, fill_value=0)

X_train.head()


# ==========================================
# 4. Feature selection 
# ==========================================

# Train Scout Model to explore Feature Importance.
scout_model = XGBClassifier(random_state=42)
scout_model.fit(X_train, y_train)

importance_df = pd.DataFrame({
    "feature": X_train.columns,   
    "importance": scout_model.feature_importances_
}).sort_values("importance", ascending=False)
print(importance_df)


# Automatic Feature Selection using SelectFromModel
selector = SelectFromModel(scout_model, threshold=0.01, prefit=True)

X_train_selected = selector.transform(X_train)
X_test_selected  = selector.transform(X_test)

selected_features_mask = selector.get_support()
selected_columns = X_train.columns[selected_features_mask].tolist() 
print(f"เหลือ {len(selected_columns)} features ได้แก่: {selected_columns}")

# Impute after Feature Selection
imputer = SimpleImputer(strategy='mean')
X_train_selected = imputer.fit_transform(X_train_selected)  
X_test_selected  = imputer.transform(X_test_selected)       



# ==========================================
# 5. Model comparison, SMOTE and Cross-validation
# ==========================================

# model comparison
names = ["Logistic Regression", "Nearest Neighbors", "Naive Bayes", "Linear SVM", "RBF SVM", "Decision Tree", "Random Forest", "AdaBoost", "Gradient Boosting", "LDA", "QDA", "Neural Net", "XGBoost" ]
classifiers = [
    LogisticRegression(),
    KNeighborsClassifier(5),
    GaussianNB(),
    SVC(kernel="linear", C=0.025),
    SVC(kernel = "rbf", gamma=2, C=1),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GradientBoostingClassifier(),
    LinearDiscriminantAnalysis(),
    QuadraticDiscriminantAnalysis(),
    MLPClassifier(alpha=1, max_iter=1000),
    xgb.XGBClassifier()
   ]

accuracy_scores = []
for name, clf in zip(names, classifiers):
    clf.fit(X_train_selected, y_train)
    score = clf.score(X_test_selected, y_test)
    score = round(score, 4)
    accuracy_scores.append(score)
    print(name ,' : ' , score)

classifiers_performance = pd.DataFrame({"Classifiers": names, "Accuracy Scores": accuracy_scores})
classifiers_performance
classifiers_performance.sort_values(by = 'Accuracy Scores' , ascending = False)[['Classifiers', 'Accuracy Scores']]


## Slove problem Class Imbalance by SMOTE
print('Before SMOTE — label 0: {}'.format(sum(y_train == 0)))
print('Before SMOTE — label 1: {}'.format(sum(y_train == 1)))

sm = SMOTE(sampling_strategy=1, random_state=1)
X_train_s, y_train_s = sm.fit_resample(X_train_selected, y_train)

print('After SMOTE — label 0: {}'.format(sum(y_train_s == 0)))
print('After SMOTE — label 1: {}'.format(sum(y_train_s == 1)))


# Model Evaluation via 5-Fold Cross-Validation
models = [
    AdaBoostClassifier(),
    BaggingClassifier(),
    GradientBoostingClassifier(),
    RandomForestClassifier(),
    LogisticRegressionCV(max_iter=1000),
    RidgeClassifierCV(),
    KNeighborsClassifier(),
    XGBClassifier()
]

metrics_cols = ['model_name','test_accuracy','test_precision','test_recall','test_f1']
model_name=[]
test_acuracy=[]
test_precision=[]
test_recall=[]
test_f1=[]

scoring = ['accuracy', 'precision', 'recall', 'f1']
for model in models:
    cv_results = cross_validate(model, X_train_s, y_train_s, cv=5,
                                scoring=scoring, return_train_score=True)
    model_name.append(model.__class__.__name__)
    test_acuracy.append(round(cv_results['test_accuracy'].mean(), 3) * 100)
    test_precision.append(round(cv_results['test_precision'].mean(), 3) * 100)
    test_recall.append(round(cv_results['test_recall'].mean(), 3) * 100)
    test_f1.append(round(cv_results['test_f1'].mean(), 3) * 100)


metrics_data = [model_name, test_acuracy, test_precision, test_recall, test_f1]
m = {n:m for n,m in zip(metrics_cols,metrics_data)}

model_metrics = pd.DataFrame(m)
model_metrics = model_metrics.sort_values('test_accuracy', ascending=False)
metrics_styled = model_metrics.style.background_gradient(subset=['test_accuracy', 'test_f1'], cmap='summer')
metrics_styled


# ==========================================
# 6. Model Selection + Final Evaluation
# ==========================================

# choose the best model after comparison
best_model_name = model_metrics.iloc[0]['model_name']
print(f"🏆 Selected best model: {best_model_name}")
model_map = {model.__class__.__name__: model for model in models}
final_model = model_map[best_model_name]


print(f"กำลังฝึกสอนโมเดล {best_model_name}...")
final_model.fit(X_train_s, y_train_s)
y_pred = final_model.predict(X_test_selected)
print(f"Final Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))


# Train and Evaluate the Final Model
test_pred = final_model.predict(X_test_selected)
final_model.score(X_test_selected, y_test)


# Confusion Matrix for Error Pattern
cm = confusion_matrix(y_test, test_pred, labels=final_model.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=final_model.classes_)
disp.plot()
plt.title(f'Confusion Matrix of {final_model.__class__.__name__}')
plt.show()


# ==========================================
# 7. Feature Importance
# ==========================================


## Feature Importance แบบ Gain
print("Feature Importance Gain")

if hasattr(final_model, 'get_booster'):
    feature_important = final_model.get_booster().get_score(importance_type="gain")
    keys   = list(feature_important.keys())
    values = list(feature_important.values())
    data = pd.DataFrame(
        data=values, index=keys, columns=["score"]
    ).sort_values(by="score", ascending=False)
    data.nlargest(20, columns="score").plot(kind='barh', figsize=(20, 10))
else:
    print(f"โมเดล {best_model_name} ไม่รองรับ Feature Importance แบบ Gain")
    if hasattr(final_model, 'feature_importances_'):
        importance_series = pd.Series(
            final_model.feature_importances_,
            index=selected_columns  
        ).sort_values(ascending=False)
        importance_series.head(20).plot(kind='barh', figsize=(10, 8))


## Feature Importance แบบ Weight
print("Feature Importance Weight")
if hasattr(final_model, 'get_booster'):
    feature_important = final_model.get_booster().get_score(importance_type='weight')
    keys = list(feature_important.keys())
    values = list(feature_important.values())
    data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by="score", ascending=False)
    data.nlargest(20, columns="score").plot(kind='barh', figsize=(20, 10))
    plt.title("Feature Importance (Weight) - XGBoost")
    plt.tight_layout()
    plt.show()
else:
    print(f"⚠️ โมเดล '{best_model_name}' ไม่มีแนวคิด Feature Importance แบบ Weight")
    print("   เนื่องจากไม่ใช่ XGBoost จึงไม่สามารถนับจำนวนครั้งที่ feature ถูก split ได้")
    print("   กราฟ Gain ด้านบนคือ Feature Importance ที่เหมาะสมที่สุดสำหรับโมเดลนี้")


# ==========================================
# 8. Deploy
# ==========================================


import pickle
import json

pickle.dump(
    final_model,
    open('end_to_end_deployment/models/churn_prediction_model.pkl', 'wb'))
columns = {'data_columns': selected_columns}

with open("end_to_end_deployment/models/columns.json", "w") as f:
    f.write(json.dumps(columns))


