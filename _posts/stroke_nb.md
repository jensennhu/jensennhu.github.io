---
layout: post
title: Modeling the Occurrence of Stroke - Binary Classification with Python's Scikit Learn
---



```python
# packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
```


    ---------------------------------------------------------------------------

    ModuleNotFoundError                       Traceback (most recent call last)

    <ipython-input-10-6d7c1745ed9f> in <module>
          4 import matplotlib.pyplot as plt
          5 import seaborn as sns
    ----> 6 import missingno as msno # missing data
    

    ModuleNotFoundError: No module named 'missingno'

Dataset : Stroke Prediction Data
Date: 2/6/2022
Shape: 5110 rows, 12 columns

```python
# read stroke data
stroke = pd.read_csv("healthcare-dataset-stroke-data.csv")
```


```python
stroke.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>gender</th>
      <th>age</th>
      <th>hypertension</th>
      <th>heart_disease</th>
      <th>ever_married</th>
      <th>work_type</th>
      <th>Residence_type</th>
      <th>avg_glucose_level</th>
      <th>bmi</th>
      <th>smoking_status</th>
      <th>stroke</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>9046</td>
      <td>Male</td>
      <td>67.0</td>
      <td>0</td>
      <td>1</td>
      <td>Yes</td>
      <td>Private</td>
      <td>Urban</td>
      <td>228.69</td>
      <td>36.6</td>
      <td>formerly smoked</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>51676</td>
      <td>Female</td>
      <td>61.0</td>
      <td>0</td>
      <td>0</td>
      <td>Yes</td>
      <td>Self-employed</td>
      <td>Rural</td>
      <td>202.21</td>
      <td>NaN</td>
      <td>never smoked</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>31112</td>
      <td>Male</td>
      <td>80.0</td>
      <td>0</td>
      <td>1</td>
      <td>Yes</td>
      <td>Private</td>
      <td>Rural</td>
      <td>105.92</td>
      <td>32.5</td>
      <td>never smoked</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>60182</td>
      <td>Female</td>
      <td>49.0</td>
      <td>0</td>
      <td>0</td>
      <td>Yes</td>
      <td>Private</td>
      <td>Urban</td>
      <td>171.23</td>
      <td>34.4</td>
      <td>smokes</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1665</td>
      <td>Female</td>
      <td>79.0</td>
      <td>1</td>
      <td>0</td>
      <td>Yes</td>
      <td>Self-employed</td>
      <td>Rural</td>
      <td>174.12</td>
      <td>24.0</td>
      <td>never smoked</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>




```python
stroke.shape
```




    (5110, 12)




```python
stroke.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 5110 entries, 0 to 5109
    Data columns (total 12 columns):
     #   Column             Non-Null Count  Dtype  
    ---  ------             --------------  -----  
     0   id                 5110 non-null   int64  
     1   gender             5110 non-null   object 
     2   age                5110 non-null   float64
     3   hypertension       5110 non-null   int64  
     4   heart_disease      5110 non-null   int64  
     5   ever_married       5110 non-null   object 
     6   work_type          5110 non-null   object 
     7   Residence_type     5110 non-null   object 
     8   avg_glucose_level  5110 non-null   float64
     9   bmi                4909 non-null   float64
     10  smoking_status     5110 non-null   object 
     11  stroke             5110 non-null   int64  
    dtypes: float64(3), int64(4), object(5)
    memory usage: 479.2+ KB
    

Notes:  
- id - shown as numeric, but should probably be binary obj
- Hypertension and Heart Disease should character vars
- Work type, Residence, Smoking_status are categorical
- bmi has missing values, needs to be imputed or removed



```python
#convert variables
stroke['id'] = stroke['id'].astype(str)
stroke.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 5110 entries, 0 to 5109
    Data columns (total 12 columns):
     #   Column             Non-Null Count  Dtype  
    ---  ------             --------------  -----  
     0   id                 5110 non-null   object 
     1   gender             5110 non-null   object 
     2   age                5110 non-null   float64
     3   hypertension       5110 non-null   int64  
     4   heart_disease      5110 non-null   int64  
     5   ever_married       5110 non-null   object 
     6   work_type          5110 non-null   object 
     7   Residence_type     5110 non-null   object 
     8   avg_glucose_level  5110 non-null   float64
     9   bmi                4909 non-null   float64
     10  smoking_status     5110 non-null   object 
     11  stroke             5110 non-null   int64  
    dtypes: float64(3), int64(3), object(6)
    memory usage: 479.2+ KB
    


```python
# missing data 
sns.heatmap(stroke.isnull(), cbar=False)
```




    <AxesSubplot:>




    
![png](output_8_1.png)
    



```python
# review missing data (BMI)
stroke.loc[stroke['bmi'].isna(), 'bmi_missing'] = 1
stroke.loc[-stroke['bmi'].isna(), 'bmi_missing'] = 0

# check to see if missing data is correlated
corr_matrix = stroke.corr()
corr_matrix['bmi_missing'].sort_values(ascending = False)
```




    bmi_missing          1.000000
    stroke               0.141238
    heart_disease        0.098621
    hypertension         0.093046
    avg_glucose_level    0.091957
    age                  0.078956
    bmi                       NaN
    Name: bmi_missing, dtype: float64




```python

```


```python
stroke.hist(figsize = (12, 10))
plt.show()
```


    
![png](output_11_0.png)
    



```python
stroke.columns
```


```python
cat = ['gender', 'hypertension', 'heart_disease', 'ever_married',
       'work_type', 'Residence_type', 'smoking_status']
for c in cat:
    print(stroke[c].value_counts())
```


```python
# train test split our dataset
from sklearn.model_selection import train_test_split
train_set, test_set = train_test_split(stroke, test_size = 0.2, random_state = 42)
```


```python
train_set.shape
```


```python
test_set.shape
```


```python
# explore data with a copy of the train set 
explore = train_set.copy()
```


```python
# check out correlations
corr_matrix = explore.corr()
```


```python
corr_matrix['stroke'].sort_values(ascending = False)
```


```python
explore['hypertension'] = explore['hypertension'].astype(str)
explore['heart_disease'] = explore['heart_disease'].astype(str)
explore['stroke'] = explore['stroke'].astype(str)
```


```python
explore.info()
```


```python

```


```python
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy = "median")
explore_num = explore[['age', 'avg_glucose_level', 'stroke']]
imputer.fit(explore_num)
imputer.statistics_
```


```python

```


```python

```


```python

```


```python

```


```python

```
