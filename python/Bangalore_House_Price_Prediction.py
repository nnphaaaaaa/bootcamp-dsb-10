## https://colab.research.google.com/drive/1A0GSOpeyWm5yquK_hFqutZFmqwlt7umI?usp=sharing

# Project :Bangalore House Price Prediction

## Author : Naphaphon Phayakkapes

## Language : Python

## Article : 

## 1. Library & Data Loading

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from sklearn.model_selection import train_test_split, ShuffleSplit, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.tree import DecisionTreeRegressor
import pickle
import json

  ## Data load
df1 = pd.read_csv("Bengaluru_House_Data.csv")
df1.head()

  ## Data Cleaning
    # ตัดคอลัมน์ที่ไม่จำเป็นออก
df2 = df1.drop(['area_type','society','balcony','availability'], axis='columns')
    # ลบแถวที่มีค่าว่าง
df3 = df2.dropna().copy()

## 2. Feature Engineering
  # แปลงขนาดห้อง (BHK)
df3['bhk'] = df3['size'].apply(lambda x: int(x.split(' ')[0]))

  # แปลง Total Sqft ให้เป็นตัวเลขเดียว
def convert_sqft_to_num(x):
    tokens = x.split('-')
    if len(tokens) == 2:
        return (float(tokens[0]) + float(tokens[1])) / 2
    try:
        return float(x)
    except:
        return None

df4 = df3.copy()
df4['total_sqft'] = df4['total_sqft'].apply(convert_sqft_to_num)
df4 = df4[df4.total_sqft.notnull()]



## 3. Outlier Removal 
  # outlier พื้นที่ต่อห้องนอน
df6 = df4[~(df4.total_sqft / df4.bhk < 300)]

  # outlier Location โดยใช้ Mean และ Standard Deviation
def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf.price / subdf.total_sqft) # คำนวณราคากลางต่อพื้นที่ในแต่ละทำเล
        st = np.std(subdf.price / subdf.total_sqft)
        reduced_df = subdf[(subdf.price/subdf.total_sqft > (m-st)) & (subdf.price/subdf.total_sqft <= (m+st))]
        df_out = pd.concat([df_out, reduced_df], ignore_index=True)
    return df_out
df7 = remove_pps_outliers(df6)

  # Outlier ราคาต่อตารางฟุต
df7['price_per_sqft'] = df7['price'] * 100000 / df7['total_sqft'] # หน่วยเป็น Lakh เลยคูณ 1แสน

  # Outlier ราคาที่ไม่สมเหตุสมผล
      # หาความผิดปกติ โดย Scatter plot 
def plot_scatter_chart(df, location):
    bhk2 = df[(df.location == location) & (df.bhk == 2)]
    bhk3 = df[(df.location == location) & (df.bhk == 3)]
    matplotlib.rcParams['figure.figsize'] = (15, 10)
    plt.scatter(bhk2.total_sqft, bhk2.price, color='blue', label='2 BHK', s=50)
    plt.scatter(bhk3.total_sqft, bhk3.price, marker='+', color='green', label='3 BHK', s=50)
    plt.xlabel("Total Square Feet Area")
    plt.ylabel("Price (Lakh Indian Rupees)")
    plt.title(location)
    plt.legend()

plot_scatter_chart(df7,"Rajaji Nagar")
plt.show()
plot_scatter_chart(df7, "Hebbal")
plt.show()

  # สร้างฟังก์ชั่น remove_bhk_outliers เพื่อกำจัดข้อมูลที่ "ราคาไม่สมเหตุสมผล" ตามที่เห็นใน Scatter Chart
  def remove_bhk_outliers(df):
    exclude_indices = np.array([])
    for location, location_df in df.groupby('location'):
        bhk_stats = {}
        for bhk, bhk_df in location_df.groupby('bhk'):
            bhk_stats[bhk] = {
                'mean': np.mean(bhk_df.price_per_sqft),
                'std': np.std(bhk_df.price_per_sqft),
                'count': bhk_df.shape[0]
            }
        for bhk, bhk_df in location_df.groupby('bhk'):
            stats = bhk_stats.get(bhk - 1)
            if stats and stats['count'] > 5:
                exclude_indices = np.append(exclude_indices,
                                            bhk_df[bhk_df.price_per_sqft < (stats['mean'])].index.values)
    return df.drop(exclude_indices, axis='index')

df8 = remove_bhk_outliers(df7)
print(df8.shape)
      # Let's check it plot same scatter chart to visualize
plot_scatter_chart(df8,"Rajaji Nagar")
plt.show()
plot_scatter_chart(df8,"Hebbal")
plt.show()

  # outlier Bathroom ที่ผิดปกติ
plt.hist(df8.bath,rwidth=0.8)
plt.xlabel("Number of bathrooms")
plt.ylabel("Count")
plt.show()

df8[df8.bath>10]

    # การกำจัดคอลัมน์ที่เป็น "ส่วนเกิน"
df9 = df8[df8.bath<df8.bhk+2]
df10 = df9.drop(['size','price_per_sqft'],axis='columns')
df10.head()

## 4. Pre-processing
dummies = pd.get_dummies(df10.location)
df11 = pd.concat([df10,dummies.iloc[:,1:]],axis='columns')
df12 = df11.drop('location',axis='columns')

## 5. Modeling & Evaluation 

X = df12.drop(['price'],axis='columns')
y = df12.price
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

lr_clf = LinearRegression()
lr_clf.fit(X_train,y_train)
lr_clf.score(X_test,y_test)

  ## Use K Fold cross validation to measure accuracy of our LinearRegression model
cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
cross_val_score(LinearRegression(), X, y, cv=cv)
        #a score above 80% all the time. This is pretty good but we want to test few other algorithms for regression to see if we can get even better score. We will use GridSearchCV for this purpose

  ## Find best model using GridSearchCV
def find_best_model_using_gridsearchcv(X,y):
    algos = {
        'linear_regression' : {
            'model': LinearRegression(),
            'params': {
                'fit_intercept': [True, False]
            }
        },
        'lasso': {
            'model': Lasso(),
            'params': {
                'alpha': [1,2],
                'selection': ['random', 'cyclic']
            }
        },
        'decision_tree': {
            'model': DecisionTreeRegressor(),
            'params': {
                'criterion' : ['squared_error','friedman_mse'],
                'splitter': ['best','random']
            }
        }
    }
    
    scores = []
    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    for algo_name, config in algos.items():
        gs =  GridSearchCV(config['model'], config['params'], cv=cv, return_train_score=False)
        gs.fit(X,y)
        scores.append({
            'model': algo_name,
            'best_score': gs.best_score_,
            'best_params': gs.best_params_
        })

    return pd.DataFrame(scores,columns=['model','best_score','best_params'])

find_best_model_using_gridsearchcv(X,y)
      # Based on above results we can say that LinearRegression gives the best score.


## 6. Prediction & Export 

  # ฟังก์ชันสำหรับกรอกข้อมูลบ้าน แล้วให้โมเดลประเมินราคาออกมา
def predict_price(location,sqft,bath,bhk):
    loc_index = np.where(x.columns==location)[0][0] 
    x_input = np.zeros(len(x.columns)) 
    x_input[0] = sqft
    x_input[1] = bath
    x_input[2] = bhk
    if loc_index >= 0:
        x_input[loc_index] = 1
    return lr_clf.predict([x_input])[0]

#### (bonus) Export the test model from pickle
with open('banglore_home_prices_model.pickle','wb') as f:
    pickle.dump(lr_clf,f)

#### (bonus) Export location and column information to a file
columns = {
    'data_columns' : [col.lower() for col in X.columns]
}
with open("columns.json","w") as f:
    f.write(json.dumps(columns))
