---
title: "投資組合回測 - 月/季資料resample至日資料並轉換成module要求的Dict樣式"
date: 2025-03-18
author: "Robert Hsu"
type: "blog"
categories:
  - Backtest
  - Trading Strategy
summary: "紀錄resample的資料轉換"
---


## 如何將月, 季的交易策略，轉化成日資料訊號，並搭配我們的backtest module做回測

## 先架起流程 在優化策略
1. 建構基本策略 (我們先忽視複雜的EDA) -> ex : 連續3個月 YOY > 0, 買入並持有下一個月
2. backtest 策略 (return PnL, 年化報酬 etc...)
3. 推至telegram (ticker pool中每日的表現, 組合成portfoilo的表現, 0050的表現)


```python
import pandas as pd
from IPython.display import Markdown, display

# Ensure tabulate is installed
# !pip install tabulate

# Disable HTML representation globally
pd.set_option('display.notebook_repr_html', False)

# Set reasonable display limits
pd.set_option('display.max_rows', 20)    # Max rows shown
pd.set_option('display.max_columns', 100) # Max columns shown

# Custom Markdown representation with dimensions after table
def _repr_markdown_(self):
    rows, cols = pd.get_option('display.max_rows'), pd.get_option('display.max_columns')
    limited_df = self.iloc[:rows, :cols]

    md_table = limited_df.to_markdown(index=False)

    dims = f"\n\n**DataFrame: {self.shape[0]} rows × {self.shape[1]} columns**"

    if len(self) > rows or len(self.columns) > cols:
        return md_table + dims + '\n\n**... (data truncated)**'
    else:
        return md_table + dims
    
# Override pandas DataFrame markdown representation globally
pd.DataFrame._repr_markdown_ = _repr_markdown_

```


```python
import configparser
import sqlite3
import pandas as pd
```


```python
# 資料讀取
config_path = "../config.ini" 
config = configparser.ConfigParser()
config.read(config_path)
```




    ['../config.ini']



### 讀取月營收資料(爬蟲 -> 公開資訊站)


```python
conn = sqlite3.connect(config['data']['db_path'])  
mr_df = pd.read_sql('SELECT * FROM monthly_revenue ;', conn)
```

### 策略一: 月營收YOY連續N個月 > 0  
買入: 月營收YOY連續N個月 > 0  
買出: 月營收YOY < 0  


```python
mr_df
```




|   公司代號 | 公司名稱   |   當月營收 |   上月營收 |   去年當月營收 |   上月比較增減(%) |   去年同月增減(%) |   當月累計營收 |   去年累計營收 |   前期比較增減(%) | 年月    |
|-----------:|:-----------|-----------:|-----------:|---------------:|------------------:|------------------:|---------------:|---------------:|------------------:|:--------|
|       1101 | 台泥       |    2054868 |    1807880 |        1601454 |             13.66 |             28.31 |        2054868 |        1601454 |             28.31 | 2010-01 |
|       8921 | 沈氏藝印   |      91206 |     111721 |          60787 |            -18.36 |             50.04 |          91206 |          60787 |             50.04 | 2010-01 |
|       4702 | 中美實     |      37391 |      37578 |          24666 |             -0.49 |             51.58 |          37391 |          24666 |             51.58 | 2010-01 |
|       6182 | 合晶       |     300341 |     278700 |         211959 |              7.76 |             41.69 |         300341 |         211959 |             41.69 | 2010-01 |
|       1742 | 台蠟       |     145540 |     124851 |          19262 |             16.57 |            655.58 |         145540 |          19262 |            655.58 | 2010-01 |
|       6198 | 凌泰科技   |       9595 |       6935 |           7648 |             38.35 |             25.45 |           9595 |           7648 |             25.45 | 2010-01 |
|       9949 | 琉園       |      29370 |      34924 |          25381 |            -15.9  |             15.71 |          29370 |          25381 |             15.71 | 2010-01 |
|       8024 | 佑華       |      52640 |      68895 |          40066 |            -23.59 |             31.38 |          52640 |          40066 |             31.38 | 2010-01 |
|       8938 | 明安       |    1024209 |     557135 |         600323 |             83.83 |             70.6  |        1024209 |         600323 |             70.6  | 2010-01 |
|       8937 | 合騏工業   |      27814 |      30204 |          43006 |             -7.91 |            -35.32 |          27814 |          43006 |            -35.32 | 2010-01 |
|       8936 | 國統國際   |     183148 |      74785 |          47476 |            144.89 |            285.76 |         183148 |          47476 |            285.76 | 2010-01 |
|       8935 | 邦泰       |     128493 |      93236 |         107677 |             37.81 |             19.33 |         128493 |         107677 |             19.33 | 2010-01 |
|       8934 | 衡平       |       2678 |       3679 |           4396 |            -27.2  |            -39.08 |           2678 |           4396 |            -39.08 | 2010-01 |
|       8933 | 愛地雅     |     297428 |     297733 |         297061 |             -0.1  |              0.12 |         297428 |         297061 |              0.12 | 2010-01 |
|       8932 | 宏大拉鍊   |      47274 |      51060 |          29760 |             -7.41 |             58.85 |          47274 |          29760 |             58.85 | 2010-01 |
|       8929 | 富堡       |      89771 |     120375 |          58471 |            -25.42 |             53.53 |          89771 |          58471 |             53.53 | 2010-01 |
|       8928 | 鉅明       |     176435 |     122033 |         115891 |             44.57 |             52.24 |         176435 |         115891 |             52.24 | 2010-01 |
|       8925 | 偉盟       |     391616 |     286289 |         316559 |             36.79 |             23.71 |         391616 |         316559 |             23.71 | 2010-01 |
|       4703 | 揚華       |      40672 |      36165 |          30091 |             12.46 |             35.16 |          40672 |          30091 |             35.16 | 2010-01 |
|       8924 | 大田精密   |     423322 |     740758 |         376273 |            -42.85 |             12.5  |         423322 |         376273 |             12.5  | 2010-01 |

**DataFrame: 285235 rows × 11 columns**

**... (data truncated)**




```python
def cal_acc_diff(df, col, diff=True):
    '''
    for groupby, col須為float or int
    累積計算連續N次為正, 遇到負則歸0 
    若diff=False, 則單純比較原本column值連續正幾次
        ex : [1, 2, 7, -3, 2] -> [1, 2, 3, 0, 1]

    若diff=True, 則比較columns.diff()連續正幾次
        ex : [1, 2, 7, -3, 2] 先做diff() -> [Nan, 1, 5, -10, 5] -> [0, 1, 2, 0, 1]

    '''

    record_list = []
    count = 0
    if diff:
        loop_col = df[col].diff()
    else:
        loop_col = df[col]

    for i in loop_col:
        if i > 0:
            count += 1 
        else:
            count = 0
        record_list.append(count)
    
    if diff:
        df[f'連續N期遞增_{col}'] = record_list
    else:
        df[f'連續N期為正_{col}'] = record_list

    return df
```


```python
# N = 3 
# Ture -> 每月YOY > 前一月 統計連續次數, False -> 每月YOY > 0 統計連續次數
mr_df = mr_df.groupby('公司代號').apply(lambda df : cal_acc_diff(df, '去年同月增減(%)', True)).reset_index(level=0, drop=True)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_33111/4084614363.py:3: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      mr_df = mr_df.groupby('公司代號').apply(lambda df : cal_acc_diff(df, '去年同月增減(%)', True)).reset_index(level=0, drop=True)



```python
mr_df.columns
```




    Index(['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)',
           '當月累計營收', '去年累計營收', '前期比較增減(%)', '年月', '連續N期遞增_去年同月增減(%)'],
          dtype='object')



## Step 1. 建構簡易策略

### 簡單寫一個 連續3個月營收YOY都要增加 & 當月YOY > 0時, signal = 1的策略


```python
mr_df['YOY_signal'] = mr_df['連續N期遞增_去年同月增減(%)'].apply(lambda x : 1 if x >= 3 else 0)
mr_df['YOY_positive_signal'] = mr_df['去年同月增減(%)'].apply(lambda x : 1 if x > 0 else 0)
```


```python
# 直接看看哪些公司符合
mask1 = (mr_df['YOY_signal']==1)
mask2 = (mr_df['年月']=='2025-01')
mask3 = (mr_df['YOY_positive_signal']==1)
mr_tickers = set(mr_df.loc[mask1 & mask2 & mask3, '公司代號'])
```


```python
len(mr_tickers)
```




    63



### 最大的問題是 -> 這個訊號轉換成我們backtest module的 gap
1. resmaple 至日資料
2. 從dataframe -> dict

最後我們進backtest的dict格式如下   
{  
    'trading_date' : [tuple('ticker', ratio), tuple('ticker', ratio), etc...],  
    'trading_date' : [tuple('ticker', ratio), tuple('ticker', ratio), etc...]  
}  

ex :  
{  
    '20240719' : [tuple(['2330', 0.02]), tuple(['2454', 0.05]), etc...]  
    '20240720' : [tuple(['2330', 0.03]), tuple(['2454', 0]), etc...]  
    etc...  
}  


```python
mr_df['signal'] = 0
mr_df.loc[mask1 & mask3, 'signal'] = 1
```

### 每個月符合filter的ticker數量不定，為簡化實際操作，在符合訊號的ticker數量 > 20時，我們依據營收YOY排序，取前20來操作


```python
def select_top_20(df):
    # Create a copy to avoid changing the original df
    df = df.copy()

    # Apply the logic month-by-month
    def process_month(group):
        # Check if more than 20 tickers have signal=1
        if group['signal'].sum() > 20:
            # Rank revenue growth in descending order and pick top 20
            top_20_idx = group[group['signal'] == 1].nlargest(20, '去年同月增減(%)').index
            # Set all signals to 0 first
            group['signal'] = 0
            # Set signal to 1 for top 20 tickers
            group.loc[top_20_idx, 'signal'] = 1
        return group

    # Apply the function to each month separately
    result = df.groupby('年月', group_keys=False).apply(process_month)
    return result
```


```python
mr_df = select_top_20(mr_df)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_33111/1024270045.py:18: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      result = df.groupby('年月', group_keys=False).apply(process_month)



```python
mr_df.columns
```




    Index(['公司代號', '公司名稱', '當月營收', '上月營收', '去年當月營收', '上月比較增減(%)', '去年同月增減(%)',
           '當月累計營收', '去年累計營收', '前期比較增減(%)', '年月', '連續N期遞增_去年同月增減(%)', 'YOY_signal',
           'YOY_positive_signal', 'signal'],
          dtype='object')




```python
mr_df.loc[mr_df['signal']==1, ['年月', '公司代號', '連續N期遞增_去年同月增減(%)', '去年同月增減(%)', 'signal']]
```




| 年月    |   公司代號 |   連續N期遞增_去年同月增減(%) |   去年同月增減(%) |   signal |
|:--------|-----------:|------------------------------:|------------------:|---------:|
| 2024-11 |       1101 |                             3 |             87.8  |        1 |
| 2010-11 |       1102 |                             3 |             63.77 |        1 |
| 2012-03 |       1102 |                             4 |             26.1  |        1 |
| 2012-06 |       1103 |                             3 |            303.61 |        1 |
| 2012-07 |       1103 |                             4 |            414.08 |        1 |
| 2023-06 |       1103 |                             3 |             51.34 |        1 |
| 2015-02 |       1108 |                             3 |             40.44 |        1 |
| 2011-06 |       1109 |                             3 |             57.34 |        1 |
| 2017-09 |       1110 |                             5 |            178.33 |        1 |
| 2024-08 |       1110 |                             4 |            104.24 |        1 |
| 2024-06 |       1213 |                             3 |            594.44 |        1 |
| 2024-07 |       1213 |                             4 |           6686.19 |        1 |
| 2014-11 |       1220 |                             3 |             68.78 |        1 |
| 2020-04 |       1227 |                             3 |             67.59 |        1 |
| 2010-12 |       1234 |                             3 |             67.78 |        1 |
| 2011-01 |       1234 |                             4 |             85.08 |        1 |
| 2011-10 |       1234 |                             3 |             52.11 |        1 |
| 2016-01 |       1234 |                             4 |             58.5  |        1 |
| 2016-10 |       1234 |                             3 |             82.33 |        1 |
| 2019-12 |       1234 |                             4 |             97.67 |        1 |

**DataFrame: 3575 rows × 5 columns**

**... (data truncated)**



## Step 2. 推斷公告日期, 將月資料resample至日

### 我們只有每個月的營收，我們推斷他的公佈日期為下個月12號(考慮遇到假日遞延的情況 12日通常能確定上個月的營收已公布)  
### 先將每個月轉換成下個月12號('2025-12' -> '2026-01-12') 可以得到每一隻ticker在每一個日期裡 holding 是 0 or 1
### 在用這些日期做resample 就可以將signal 放大到每日


```python
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_next_month_12th(yyyy_mm: str) -> str:
    """Given 'YYYY-MM', return the next month's 12th as 'YYYY-MM-DD'."""
    date_obj = datetime.strptime(yyyy_mm, "%Y-%m")
    next_month = date_obj + relativedelta(months=1)
    result_date = next_month.replace(day=12)
    return result_date.strftime("%Y-%m-%d")

# Example usage
print(get_next_month_12th("2025-12"))  # Output: "2025-04-12"

```


```python
# 直接用數值轉換日期 較快
def get_next_month_12th(yyyy_mm: str) -> str:
    """Given 'YYYY-MM', return the next month's 12th as 'YYYY-MM-DD' using fast arithmetic."""
    year, month = map(int, yyyy_mm.split("-"))

    # Increment month, handle year rollover
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1

    # Format with zero-padding for consistent output
    return f"{year:04d}-{month:02d}-12"
```


```python
mr_df['年月'].apply(get_next_month_12th)
```




    0         2010-02-12
    2305      2010-03-12
    3625      2010-04-12
    4981      2010-05-12
    6358      2010-06-12
                 ...    
    276516    2024-11-12
    279310    2024-12-12
    281072    2025-01-12
    281802    2025-02-12
    283570    2025-03-12
    Name: 年月, Length: 285235, dtype: object




```python
mr_df['推斷公告日'] = mr_df['年月'].apply(get_next_month_12th)
```


```python
mr_df['日期_dt'] = pd.to_datetime(mr_df['推斷公告日'])
```


```python
def resample_df(df):
    df = df.reset_index().set_index("日期_dt")  # Ensure '日期' is the index
    df = df.loc[~df.index.duplicated()] # 避免某些資料有誤報錯
    df = df.resample('D').ffill() 
    df.reset_index(drop=False, inplace=True)
    return df
```


```python
mr_df.reset_index(drop=True, inplace=True)
mr_df['公司代號'] = mr_df['公司代號'].astype(str)
```


```python
# 將月資料 resample至日
resample_mr_df = mr_df[['日期_dt', '年月', '推斷公告日', '公司代號', 'signal']].groupby('公司代號').apply(resample_df).reset_index(drop=True)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_33111/2657914633.py:2: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      resample_mr_df = mr_df[['日期_dt', '年月', '推斷公告日', '公司代號', 'signal']].groupby('公司代號').apply(resample_df).reset_index(drop=True)



```python
resample_mr_df[(resample_mr_df['年月']=='2024-11') & (resample_mr_df['公司代號']=='1101')]
```




| 日期_dt             |   index | 年月    | 推斷公告日   |   公司代號 |   signal |
|:--------------------|--------:|:--------|:-------------|-----------:|---------:|
| 2024-12-12 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-13 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-14 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-15 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-16 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-17 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-18 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-19 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-20 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-21 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-22 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-23 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-24 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-25 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-26 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-27 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-28 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-29 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-30 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |
| 2024-12-31 00:00:00 |     178 | 2024-11 | 2024-12-12   |       1101 |        1 |

**DataFrame: 31 rows × 6 columns**

**... (data truncated)**



### 可以看到 2024-11, 1101的signal = 1 
### 設定推斷公告日後進行resample之後 在2024-12-12 ~ 2025-01-11 的signal = 1 (資料被trancate 只顯示top 20 rows) 

## Step 3. 將日資料 轉換成backtest module的dict格式


```python
## 這樣同樣的日期只要轉換一次就好
unique_datetime = resample_mr_df['日期_dt'].unique().tolist()
transform_dict = {}
for d in unique_datetime:
    transform_dict[d] = d.strftime('%Y%m%d')
```


```python
resample_mr_df['日期'] = resample_mr_df['日期_dt'].map(transform_dict)
```


```python
date_dict = resample_mr_df.groupby("日期").apply(lambda x: list(zip(x["公司代號"], x["signal"]))).to_dict()
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_33111/2633007352.py:1: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      date_dict = resample_mr_df.groupby("日期").apply(lambda x: list(zip(x["公司代號"], x["signal"]))).to_dict()



```python
# 如果我們只保留singal == 1的data backtest還是正確的嗎? -> 還是正確得 我們只要紀錄ticker有持有的日期
# 若是下一個交易日他不在持有名單中 會全部出清
date_dict_ratio = {}

for d in date_dict.keys():
    month_tickers_count = len([data[0] for data in date_dict[d] if data[-1]==1])
    date_dict_ratio[d] = [
    tuple([data[0], 1 / month_tickers_count]) 
    for data in date_dict[d] if data[-1] == 1 
    ]
```


```python
# 可以看到 1101 在 2024-12-14中有持有 因為一次是選top 20, 故其持股比例佔投組為 5%
date_dict_ratio['20241214']
```




    [('1101', 0.05),
     ('1470', 0.05),
     ('2211', 0.05),
     ('2230', 0.05),
     ('2363', 0.05),
     ('2881', 0.05),
     ('2891', 0.05),
     ('2905', 0.05),
     ('3056', 0.05),
     ('3447', 0.05),
     ('3563', 0.05),
     ('4946', 0.05),
     ('5398', 0.05),
     ('5490', 0.05),
     ('6142', 0.05),
     ('6658', 0.05),
     ('6691', 0.05),
     ('6692', 0.05),
     ('6877', 0.05),
     ('8176', 0.05)]




```python
# 將dict 存成pickle 就大功告成了
import pickle

with open('test_YOY.pkl', 'wb') as handle:
        pickle.dump(date_dict_ratio, handle, protocol=pickle.DEFAULT_PROTOCOL)
```
