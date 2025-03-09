
---
title: "9 tickers dive in"
date: 2025-02-16
author: "Robert Hsu"
type: "industry_project"
categories:
  - Branding
  - Design
summary: "選出來的ticker 做特化策略"
---




## 9 tickers 轉折

first look 如何定義轉折
1. 趨勢拆分 -> 上漲/盤整/下跌 可以用一條趨勢線(均線)來判斷
2. 轉折建立在趨勢之上 轉折就是趨勢的改變 上漲->盤整/下跌, 下跌-> 盤整/上漲, 盤整->上漲/下跌  
技術類分析最重要的是 訊號統計的時間長短 就像長天期均線的長期趨勢, 短天期的短期趨勢 也可能會有背離的情況


## Default setting -> keep holding


```python
import re
import pickle

import pandas as pd
import matplotlib.pyplot as plt


```


```python
price_df = pd.read_feather('/Users/roberthsu/Documents/TrendForce_project/cmoney_warehouse/daily/org_price.ftr')
```


```python
price0050 = price_df[price_df['股票代號']=='0050']
price0050['日期_dt'] = pd.to_datetime(price0050['日期'])
price0050.sort_values('日期_dt', inplace=True, ascending=True)
price0050.reset_index(drop=True, inplace=True)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_6936/2447510086.py:2: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      price0050['日期_dt'] = pd.to_datetime(price0050['日期'])
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_6936/2447510086.py:3: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      price0050.sort_values('日期_dt', inplace=True, ascending=True)



```python
SUB_TICKERS = ['2059', '3529', '2383', '2330', '8069', '5274', '3008', '2454', '3533']
```


```python
price_df = price_df[price_df['股票代號'].isin(SUB_TICKERS)]
```


```python
price_df['日期_dt'] = pd.to_datetime(price_df['日期'])
price_df.sort_values('日期_dt', inplace=True, ascending=True)
price_df.reset_index(drop=True, inplace=True)
```


```python
def holding_nDays(df):
    for n in [5, 10, 20, 60, 120]:
        df[f'hold_{n}Days_ret'] = (df['收盤價'].shift(-n) / df['收盤價']) - 1
        df[f'hold_{n}Days_ret'] = df[f'hold_{n}Days_ret'].shift(-1) # 實際上隔日才能操作
        df[f'last_{n}Days_ret'] = df[f'hold_{n}Days_ret'].shift(n + 2) # 實際上隔日才能操作

        df[f'hold_{n}Days_winrate'] = df[f'hold_{n}Days_ret'].apply(lambda x : 1 if x > 0 else 0)
    return df
```


```python
price_df = price_df.groupby('股票代號').apply(holding_nDays).reset_index(drop=True)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_6936/392270890.py:1: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      price_df = price_df.groupby('股票代號').apply(holding_nDays).reset_index(drop=True)



```python
price0050 = price0050.groupby('股票代號').apply(holding_nDays).reset_index(drop=True)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_6936/2395123834.py:1: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      price0050 = price0050.groupby('股票代號').apply(holding_nDays).reset_index(drop=True)


### 可不可以 給一個策略當作input df (w/ signal columns) -> output buy&hold/ signal based trading result & pkl for backtesting

即使buy&hold 的勝率多次贏過本身 但是考慮手續費之後 PnL仍是輸  
若是使用betting的方式 需要開槓桿 但槓桿太大前期爆掉 最終仍是輸  
也許勝率不是那麼重要 期望報酬要高過一般日子才行 


```python
price_df = price_df.merge(price0050, how='left', left_on=(['日期_dt']), right_on=(['日期_dt']), suffixes=('', '_0050'))
```


```python
price_df['signal'] = 0
price_df.loc[(price_df['股票代號'].isin(['2330', '8069'])), 'signal'] = 1
```


```python
price_df['5MA'] = price_df.groupby('股票代號')['收盤價'].rolling(5).mean().reset_index(drop=True)
price_df['10MA'] = price_df.groupby('股票代號')['收盤價'].rolling(10).mean().reset_index(drop=True)
price_df['20MA'] = price_df.groupby('股票代號')['收盤價'].rolling(20).mean().reset_index(drop=True)
price_df['60MA'] = price_df.groupby('股票代號')['收盤價'].rolling(60).mean().reset_index(drop=True)
price_df['400MA'] = price_df.groupby('股票代號')['收盤價'].rolling(20*20).mean().reset_index(drop=True)
price_df['1200MA'] = price_df.groupby('股票代號')['收盤價'].rolling(60*20).mean().reset_index(drop=True)

```


```python
price_df['signal'] = 0
price_df.loc[(price_df['60MA']>price_df['400MA']) & (price_df['20MA']>price_df['60MA']) & (price_df['5MA']>price_df['20MA']), 'signal'] = 1
```


```python
tmp = price_df[(price_df['股票代號']=='2330') & (price_df['日期_dt']>='20150101')]
```


```python
for ticker in SUB_TICKERS:
    tmp = price_df[(price_df['股票代號']==ticker) & (price_df['日期_dt']>='20150101')]
    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(111)

    ax1.plot(tmp['日期_dt'], tmp['本益比(近四季)'], label='PE')
    ax2 = ax1.twinx()
    ax2.plot(tmp['日期_dt'], tmp['收盤價'],color='orange', label='price')
    ax1.set_title(ticker)
    ax1.legend()
    ax2.legend()
    

```


    
![png](/images/industry_project/9tickers_trend_19_0.png)
    



    
![png](/images/industry_project/9tickers_trend_19_1.png)
    



    
![png](/images/industry_project/9tickers_trend_19_2.png)
    



    
![png](/images/industry_project/9tickers_trend_19_3.png)
    



    
![png](/images/industry_project/9tickers_trend_19_4.png)
    



    
![png](/images/industry_project/9tickers_trend_19_5.png)
    



    
![png](/images/industry_project/9tickers_trend_19_6.png)
    



    
![png](/images/industry_project/9tickers_trend_19_7.png)
    



    
![png](/images/industry_project/9tickers_trend_19_8.png)
    


## 想法1.
我們就做長期 依據財報, PE等方式去做一個長期策略 -> 一次bet 一季 只要能避開大跌的期間 以60~70 time in markets 去beat buy&hold挺有機會的  
至少我們交易的很不頻繁
## 想法2.
短期的策略 就以輔助的方式搭配 不要求訊號數量, 次數, 集中度 單純以buy&hold勝率為依歸 這樣一定可以增加組合策略的勝率


```python
tmp['']
```


```python
price_df.loc[price_df['股票代號']=='2330', ['收盤價', 'hold_5Days_ret', 'last_5Days_ret']].iloc[-20::]
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
      <th>收盤價</th>
      <th>hold_5Days_ret</th>
      <th>last_5Days_ret</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>12443</th>
      <td>1075.0</td>
      <td>-0.028302</td>
      <td>0.038278</td>
    </tr>
    <tr>
      <th>12444</th>
      <td>1060.0</td>
      <td>-0.033019</td>
      <td>0.004673</td>
    </tr>
    <tr>
      <th>12445</th>
      <td>1060.0</td>
      <td>-0.023474</td>
      <td>0.014354</td>
    </tr>
    <tr>
      <th>12446</th>
      <td>1065.0</td>
      <td>0.000000</td>
      <td>0.024155</td>
    </tr>
    <tr>
      <th>12447</th>
      <td>1050.0</td>
      <td>0.019231</td>
      <td>-0.018433</td>
    </tr>
    <tr>
      <th>12448</th>
      <td>1040.0</td>
      <td>0.033981</td>
      <td>-0.032258</td>
    </tr>
    <tr>
      <th>12449</th>
      <td>1030.0</td>
      <td>0.063415</td>
      <td>-0.032558</td>
    </tr>
    <tr>
      <th>12450</th>
      <td>1025.0</td>
      <td>0.043269</td>
      <td>-0.028302</td>
    </tr>
    <tr>
      <th>12451</th>
      <td>1040.0</td>
      <td>0.000000</td>
      <td>-0.033019</td>
    </tr>
    <tr>
      <th>12452</th>
      <td>1050.0</td>
      <td>-0.023585</td>
      <td>-0.023474</td>
    </tr>
    <tr>
      <th>12453</th>
      <td>1060.0</td>
      <td>-0.028169</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>12454</th>
      <td>1065.0</td>
      <td>-0.050459</td>
      <td>0.019231</td>
    </tr>
    <tr>
      <th>12455</th>
      <td>1090.0</td>
      <td>-0.055300</td>
      <td>0.033981</td>
    </tr>
    <tr>
      <th>12456</th>
      <td>1085.0</td>
      <td>-0.009524</td>
      <td>0.063415</td>
    </tr>
    <tr>
      <th>12457</th>
      <td>1050.0</td>
      <td>NaN</td>
      <td>0.043269</td>
    </tr>
    <tr>
      <th>12458</th>
      <td>1035.0</td>
      <td>NaN</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>12459</th>
      <td>1035.0</td>
      <td>NaN</td>
      <td>-0.023585</td>
    </tr>
    <tr>
      <th>12460</th>
      <td>1035.0</td>
      <td>NaN</td>
      <td>-0.028169</td>
    </tr>
    <tr>
      <th>12461</th>
      <td>1025.0</td>
      <td>NaN</td>
      <td>-0.050459</td>
    </tr>
    <tr>
      <th>12462</th>
      <td>1040.0</td>
      <td>NaN</td>
      <td>-0.055300</td>
    </tr>
  </tbody>
</table>
</div>




```python
margin_df = pd.read_feather('/Users/roberthsu/Documents/TrendForce_project/cmoney_warehouse/daily/dayMarginTrading.ftr', columns=['日期', '股票代號', '資餘', '券餘', '券資比', '當沖比率', '融資成本(推估)', '融券成本(推估)', '融資維持率(%)', '融券維持率(%)','整體維持率(%)'])
```


```python
price_df = price_df.merge(margin_df, how='left', left_on=(['日期', '股票代號']), right_on=(['日期', '股票代號']))
```


```python
price_df['維持率反推融資平均損益'] = ((price_df['融資維持率(%)'] * 0.6) - 100) /100
```


```python
price_df['signal'] = 0
mask = (price_df['維持率反推融資平均損益']<-0.1)
price_df.loc[mask, 'signal'] = 1
```




```python
1085/1040
```




    1.0432692307692308




```python
price_df['signal'] = 0
price_df.loc[(price_df['10MA']>price_df['20MA']), 'signal'] = 1
```


```python
price_df['signal'] = 0
price_df.loc[(price_df['5MA']>price_df['10MA']), 'signal'] = 1
```


```python
price_df['signal'] = 0
price_df.loc[(price_df['last_5Days_ret']>price_df['last_5Days_ret_0050']), 'signal'] = 1
```


```python
price_df['signal'] = 0
price_df.loc[(price_df['last_60Days_ret']>price_df['last_60Days_ret_0050']) & (price_df['last_60Days_ret']>0), 'signal'] = 1
```


```python
price_df['signal'] = 0
mask1 = (price_df['last_5Days_ret']>price_df['last_5Days_ret_0050'])
mask2 = (price_df['last_10Days_ret']>price_df['last_10Days_ret_0050'])
mask3 = (price_df['last_20Days_ret']<price_df['last_20Days_ret_0050'])
mask4 = (price_df['20MA']<price_df['60MA'])
price_df.loc[mask1 & mask2 & mask3 & mask4 , 'signal'] = 1
```


```python
price_df['signal'] = 0
mask1 = (price_df['last_5Days_ret']>price_df['last_5Days_ret_0050'])
mask2 = (price_df['last_10Days_ret']>price_df['last_10Days_ret_0050'])
mask3 = (price_df['last_20Days_ret']<price_df['last_20Days_ret_0050'])
mask4 = (price_df['20MA']<price_df['60MA'])
price_df.loc[mask4 , 'signal'] = 1
```


```python

ret_cols = [f'hold_{n}Days_ret' for n in [5, 10, 20, 60, 120]]
winrate_cols = [f'hold_{n}Days_winrate' for n in [5, 10, 20, 60, 120]]
```


```python
price_df[(price_df['股票代號']=='2330') & (price_df['signal']==0) & (price_df['日期_dt']>='20150101')]
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
      <th>日期</th>
      <th>股票代號</th>
      <th>股票名稱</th>
      <th>開盤價</th>
      <th>最高價</th>
      <th>最低價</th>
      <th>收盤價</th>
      <th>漲跌</th>
      <th>漲幅(%)</th>
      <th>振幅(%)</th>
      <th>...</th>
      <th>last_120Days_ret_0050</th>
      <th>hold_120Days_winrate_0050</th>
      <th>5MA</th>
      <th>10MA</th>
      <th>20MA</th>
      <th>60MA</th>
      <th>1200MA</th>
      <th>3600MA</th>
      <th>signal</th>
      <th>400MA</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>10058</th>
      <td>20150109</td>
      <td>2330</td>
      <td>台積電</td>
      <td>101.33</td>
      <td>101.70</td>
      <td>99.83</td>
      <td>100.58</td>
      <td>-4.0</td>
      <td>-2.90</td>
      <td>1.81</td>
      <td>...</td>
      <td>0.009136</td>
      <td>1.0</td>
      <td>101.930</td>
      <td>103.468</td>
      <td>102.6055</td>
      <td>101.035500</td>
      <td>63.860808</td>
      <td>39.046314</td>
      <td>0</td>
      <td>85.582325</td>
    </tr>
    <tr>
      <th>10059</th>
      <td>20150112</td>
      <td>2330</td>
      <td>台積電</td>
      <td>99.45</td>
      <td>100.20</td>
      <td>99.08</td>
      <td>99.08</td>
      <td>-2.0</td>
      <td>-1.49</td>
      <td>1.12</td>
      <td>...</td>
      <td>0.003945</td>
      <td>1.0</td>
      <td>100.804</td>
      <td>102.943</td>
      <td>102.4930</td>
      <td>101.141833</td>
      <td>63.911775</td>
      <td>39.066189</td>
      <td>0</td>
      <td>85.635450</td>
    </tr>
    <tr>
      <th>10060</th>
      <td>20150113</td>
      <td>2330</td>
      <td>台積電</td>
      <td>98.33</td>
      <td>99.83</td>
      <td>97.95</td>
      <td>99.45</td>
      <td>0.5</td>
      <td>0.38</td>
      <td>1.89</td>
      <td>...</td>
      <td>-0.010910</td>
      <td>1.0</td>
      <td>100.654</td>
      <td>102.492</td>
      <td>102.3615</td>
      <td>101.223167</td>
      <td>63.963258</td>
      <td>39.086139</td>
      <td>0</td>
      <td>85.688600</td>
    </tr>
    <tr>
      <th>10061</th>
      <td>20150114</td>
      <td>2330</td>
      <td>台積電</td>
      <td>99.45</td>
      <td>99.83</td>
      <td>97.58</td>
      <td>97.58</td>
      <td>-2.5</td>
      <td>-1.89</td>
      <td>2.26</td>
      <td>...</td>
      <td>-0.012295</td>
      <td>1.0</td>
      <td>100.054</td>
      <td>101.667</td>
      <td>102.2490</td>
      <td>101.285833</td>
      <td>64.013708</td>
      <td>39.105628</td>
      <td>0</td>
      <td>85.740650</td>
    </tr>
    <tr>
      <th>10062</th>
      <td>20150115</td>
      <td>2330</td>
      <td>台積電</td>
      <td>98.70</td>
      <td>99.83</td>
      <td>98.70</td>
      <td>98.70</td>
      <td>1.5</td>
      <td>1.15</td>
      <td>1.15</td>
      <td>...</td>
      <td>-0.006631</td>
      <td>1.0</td>
      <td>99.078</td>
      <td>101.029</td>
      <td>102.2865</td>
      <td>101.317000</td>
      <td>64.064775</td>
      <td>39.125489</td>
      <td>0</td>
      <td>85.793700</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>12453</th>
      <td>20241106</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1050.00</td>
      <td>1080.00</td>
      <td>1040.00</td>
      <td>1060.00</td>
      <td>10.0</td>
      <td>0.95</td>
      <td>3.81</td>
      <td>...</td>
      <td>0.212738</td>
      <td>0.0</td>
      <td>1041.000</td>
      <td>1048.000</td>
      <td>1049.7500</td>
      <td>981.879667</td>
      <td>541.113892</td>
      <td>256.953578</td>
      <td>0</td>
      <td>697.244700</td>
    </tr>
    <tr>
      <th>12454</th>
      <td>20241107</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1050.00</td>
      <td>1075.00</td>
      <td>1050.00</td>
      <td>1065.00</td>
      <td>5.0</td>
      <td>0.47</td>
      <td>2.36</td>
      <td>...</td>
      <td>0.213704</td>
      <td>0.0</td>
      <td>1048.000</td>
      <td>1048.500</td>
      <td>1052.5000</td>
      <td>984.762833</td>
      <td>541.773317</td>
      <td>257.238703</td>
      <td>0</td>
      <td>698.680075</td>
    </tr>
    <tr>
      <th>12460</th>
      <td>20241115</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1040.00</td>
      <td>1045.00</td>
      <td>1030.00</td>
      <td>1035.00</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>1.45</td>
      <td>...</td>
      <td>0.148182</td>
      <td>0.0</td>
      <td>1048.000</td>
      <td>1054.500</td>
      <td>1056.0000</td>
      <td>996.100500</td>
      <td>545.656300</td>
      <td>258.934042</td>
      <td>0</td>
      <td>706.833775</td>
    </tr>
    <tr>
      <th>12461</th>
      <td>20241118</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1030.00</td>
      <td>1035.00</td>
      <td>1020.00</td>
      <td>1025.00</td>
      <td>-10.0</td>
      <td>-0.97</td>
      <td>1.45</td>
      <td>...</td>
      <td>0.157689</td>
      <td>0.0</td>
      <td>1036.000</td>
      <td>1053.000</td>
      <td>1053.0000</td>
      <td>997.039333</td>
      <td>546.276033</td>
      <td>259.208475</td>
      <td>0</td>
      <td>708.105975</td>
    </tr>
    <tr>
      <th>12462</th>
      <td>20241119</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1030.00</td>
      <td>1045.00</td>
      <td>1025.00</td>
      <td>1040.00</td>
      <td>15.0</td>
      <td>1.46</td>
      <td>1.95</td>
      <td>...</td>
      <td>0.121260</td>
      <td>0.0</td>
      <td>1034.000</td>
      <td>1052.000</td>
      <td>1050.7500</td>
      <td>998.228167</td>
      <td>546.904150</td>
      <td>259.486969</td>
      <td>0</td>
      <td>709.430250</td>
    </tr>
  </tbody>
</table>
<p>1408 rows × 91 columns</p>
</div>




```python
price_df['y-m'] = '{}_{}'.format(price_df['日期_dt'].dt.year, price_df['日期_dt'].dt.month)
```


```python
price_df['y-m'] 
```




    0        0        2005\n1        2005\n2        2005\n3...
    1        0        2005\n1        2005\n2        2005\n3...
    2        0        2005\n1        2005\n2        2005\n3...
    3        0        2005\n1        2005\n2        2005\n3...
    4        0        2005\n1        2005\n2        2005\n3...
                                   ...                        
    46258    0        2005\n1        2005\n2        2005\n3...
    46259    0        2005\n1        2005\n2        2005\n3...
    46260    0        2005\n1        2005\n2        2005\n3...
    46261    0        2005\n1        2005\n2        2005\n3...
    46262    0        2005\n1        2005\n2        2005\n3...
    Name: y-m, Length: 46263, dtype: object




```python
price_df['signal'] = 0
price_df.loc[(price_df['20MA']/price_df['60MA'])-1>0.15, 'signal'] = 1
```


```python
price_df[(price_df['signal']==1) & (price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean() - price_df[(price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean()
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
      <th>hold_5Days_ret</th>
      <th>hold_10Days_ret</th>
      <th>hold_20Days_ret</th>
      <th>hold_60Days_ret</th>
      <th>hold_120Days_ret</th>
    </tr>
    <tr>
      <th>股票代號</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2059</th>
      <td>0.017087</td>
      <td>0.022231</td>
      <td>-0.013430</td>
      <td>-0.065302</td>
      <td>0.068611</td>
    </tr>
    <tr>
      <th>2330</th>
      <td>-0.002699</td>
      <td>-0.006376</td>
      <td>-0.006742</td>
      <td>0.022492</td>
      <td>0.341642</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>0.014812</td>
      <td>0.029280</td>
      <td>0.050830</td>
      <td>-0.016267</td>
      <td>-0.002099</td>
    </tr>
    <tr>
      <th>2454</th>
      <td>0.010751</td>
      <td>0.023585</td>
      <td>0.037384</td>
      <td>0.012049</td>
      <td>0.211770</td>
    </tr>
    <tr>
      <th>3008</th>
      <td>-0.017594</td>
      <td>-0.026327</td>
      <td>-0.001245</td>
      <td>-0.197294</td>
      <td>-0.134270</td>
    </tr>
    <tr>
      <th>3529</th>
      <td>-0.000973</td>
      <td>0.000510</td>
      <td>-0.005509</td>
      <td>0.029531</td>
      <td>-0.027317</td>
    </tr>
    <tr>
      <th>3533</th>
      <td>-0.002149</td>
      <td>-0.011161</td>
      <td>0.020086</td>
      <td>0.030281</td>
      <td>-0.039526</td>
    </tr>
    <tr>
      <th>5274</th>
      <td>-0.007624</td>
      <td>-0.026067</td>
      <td>-0.069628</td>
      <td>-0.123144</td>
      <td>-0.144215</td>
    </tr>
    <tr>
      <th>8069</th>
      <td>-0.005366</td>
      <td>-0.011376</td>
      <td>-0.025639</td>
      <td>-0.068083</td>
      <td>0.010706</td>
    </tr>
  </tbody>
</table>
</div>




```python
price_df[['日期', '股票代號', 'signal']+ret_cols+winrate_cols].to_feather('/Users/roberthsu/Documents/TrendForce_project/TW_forwardPE/data/test_get_strategy_result/test.ftr')
```

python3 src/backtest.py /Users/roberthsu/Documents/TrendForce_project/TW_forwardPE/data/test_get_strategy_result/test_3533.pkl /Users/roberthsu/Documents/TrendForce_project/TW_forwardPE/data/ticker_pnl/3533 --capital 1000000000 --start_date 20150101 --end_date 20241014 --commission 0.000855 --rebalance 0

## 週集保


```python
weekly_depostie = pd.read_feather('/Users/roberthsu/Documents/TrendForce_project/cmoney_warehouse/weeklyDepository.ftr')
```


```python
weekly_depostie = weekly_depostie[weekly_depostie['股票代號'].isin(SUB_TICKERS)]
```


```python
weekly_depostie.sort_values('日期', inplace=True)
weekly_depostie.reset_index(drop=True, inplace=True)
```


```python
agg = weekly_depostie[weekly_depostie['持股分級'].isin(['0400001-0600000', '0600001-0800000', '0800001-1000000', '1000001以上'])].groupby(['日期', '股票代號'])['佔集保庫存數比例(%)'].sum().to_frame()
```


```python
agg.reset_index(drop=False, inplace=True)
```


```python
agg
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
      <th>日期</th>
      <th>股票代號</th>
      <th>佔集保庫存數比例(%)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>20150508</td>
      <td>2059</td>
      <td>79.619997</td>
    </tr>
    <tr>
      <th>1</th>
      <td>20150508</td>
      <td>2330</td>
      <td>93.440002</td>
    </tr>
    <tr>
      <th>2</th>
      <td>20150508</td>
      <td>2383</td>
      <td>66.119999</td>
    </tr>
    <tr>
      <th>3</th>
      <td>20150508</td>
      <td>2454</td>
      <td>79.410002</td>
    </tr>
    <tr>
      <th>4</th>
      <td>20150508</td>
      <td>3008</td>
      <td>58.770000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>4441</th>
      <td>20241115</td>
      <td>3008</td>
      <td>55.200002</td>
    </tr>
    <tr>
      <th>4442</th>
      <td>20241115</td>
      <td>3529</td>
      <td>51.480002</td>
    </tr>
    <tr>
      <th>4443</th>
      <td>20241115</td>
      <td>3533</td>
      <td>64.210001</td>
    </tr>
    <tr>
      <th>4444</th>
      <td>20241115</td>
      <td>5274</td>
      <td>36.360001</td>
    </tr>
    <tr>
      <th>4445</th>
      <td>20241115</td>
      <td>8069</td>
      <td>82.039996</td>
    </tr>
  </tbody>
</table>
<p>4446 rows × 3 columns</p>
</div>




```python
company_event = pd.read_feather('/Users/roberthsu/Documents/TrendForce_project/cmoney_warehouse/daily/company_event.ftr')
```


```python
company_event = company_event[company_event['股票代號'].isin(SUB_TICKERS)]
```


```python
date_pattern = r'^\d{8}$'
company_event = company_event[company_event['日期'].str.contains(date_pattern)]
```


```python
company_event['日期_dt'] = pd.to_datetime(company_event['日期'])
```


```python
company_event['friday_of_week'] = company_event['日期_dt'] + pd.offsets.Week(weekday=4)
company_event['adjust_week'] = 0
company_event.loc[(company_event['新股上市']==0) | (company_event['減資前']==0), 'adjust_week'] = 1
```


```python
agg['日期_dt'] = pd.to_datetime(agg['日期'])
agg['year'] = agg['日期_dt'].dt.year
```


```python
agg['週集保月線'] = agg.groupby(['股票代號'])['佔集保庫存數比例(%)'].rolling(4).mean().reset_index(level=0, drop=True)
agg['週集保半年線'] = agg.groupby(['股票代號'])['佔集保庫存數比例(%)'].rolling(24).mean().reset_index(level=0, drop=True)
```


```python
agg['週集保diff'] = agg.groupby(['股票代號'])['佔集保庫存數比例(%)'].diff().reset_index(level=0, drop=True)
```


```python
agg = agg.merge(company_event.loc[company_event['adjust_week']==1, ['friday_of_week', '股票代號', '減資前', '新股上市', 'adjust_week']], how='left', left_on=(['日期_dt', '股票代號']), right_on=(['friday_of_week', '股票代號']))
```


```python
# 有股數異動 當周週集保diff -> 0
agg.loc[agg['adjust_week']==1, '週集保diff'] = 0

```


```python
agg['週集保diff4week'] = agg.groupby(['股票代號'])['週集保diff'].rolling(4).sum().reset_index(level=0, drop=True)
```


```python
price_df = price_df.merge(agg, how='left', left_on=(['日期', '股票代號']), right_on=(['日期', '股票代號']))
```


```python
price_df.columns
```




    Index(['日期', '股票代號', '股票名稱', '開盤價', '最高價', '最低價', '收盤價', '漲跌', '漲幅(%)',
           '振幅(%)', '成交量', '成交筆數', '成交金額(千)', '均張', '成交量變動(%)', '均張變動(%)',
           '股本(百萬)', '總市值(億)', '市值比重(%)', '本益比', '股價淨值比', '本益比(近四季)', '週轉率(%)',
           '成交值比重(%)', '漲跌停', 'RTIME', '日期_dt_x', 'hold_5Days_ret',
           'last_5Days_ret', 'hold_5Days_winrate', 'hold_10Days_ret',
           'last_10Days_ret', 'hold_10Days_winrate', 'hold_20Days_ret',
           'last_20Days_ret', 'hold_20Days_winrate', 'hold_60Days_ret',
           'last_60Days_ret', 'hold_60Days_winrate', 'hold_120Days_ret',
           'last_120Days_ret', 'hold_120Days_winrate', '日期_0050', '股票代號_0050',
           '股票名稱_0050', '開盤價_0050', '最高價_0050', '最低價_0050', '收盤價_0050', '漲跌_0050',
           '漲幅(%)_0050', '振幅(%)_0050', '成交量_0050', '成交筆數_0050', '成交金額(千)_0050',
           '均張_0050', '成交量變動(%)_0050', '均張變動(%)_0050', '股本(百萬)_0050',
           '總市值(億)_0050', '市值比重(%)_0050', '本益比_0050', '股價淨值比_0050',
           '本益比(近四季)_0050', '週轉率(%)_0050', '成交值比重(%)_0050', '漲跌停_0050',
           'RTIME_0050', 'hold_5Days_ret_0050', 'last_5Days_ret_0050',
           'hold_5Days_winrate_0050', 'hold_10Days_ret_0050',
           'last_10Days_ret_0050', 'hold_10Days_winrate_0050',
           'hold_20Days_ret_0050', 'last_20Days_ret_0050',
           'hold_20Days_winrate_0050', 'hold_60Days_ret_0050',
           'last_60Days_ret_0050', 'hold_60Days_winrate_0050',
           'hold_120Days_ret_0050', 'last_120Days_ret_0050',
           'hold_120Days_winrate_0050', '佔集保庫存數比例(%)', '日期_dt_y', 'year', '週集保月線',
           '週集保半年線', '週集保diff', 'friday_of_week', '減資前', '新股上市', 'adjust_week',
           '週集保diff4week'],
          dtype='object')




```python
price_df['週集保diff4week']
```




    0             NaN
    1             NaN
    2             NaN
    3             NaN
    4             NaN
               ...   
    46258         NaN
    46259         NaN
    46260   -0.490007
    46261         NaN
    46262         NaN
    Name: 週集保diff4week, Length: 46263, dtype: float64




```python
# 近一個月 400張大戶 增加2%以上
price_df['signal'] = 0
price_df.loc[(price_df['週集保diff4week']>2), 'signal'] = 1
```


```python
price_df['日期_dt'] = pd.to_datetime(price_df['日期'])
```


```python
price_df[(price_df['signal']==1) & (price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean() - price_df[(price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean()
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
      <th>hold_5Days_ret</th>
      <th>hold_10Days_ret</th>
      <th>hold_20Days_ret</th>
      <th>hold_60Days_ret</th>
      <th>hold_120Days_ret</th>
    </tr>
    <tr>
      <th>股票代號</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2059</th>
      <td>0.023805</td>
      <td>0.044288</td>
      <td>0.045329</td>
      <td>0.040987</td>
      <td>0.022441</td>
    </tr>
    <tr>
      <th>2330</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>-0.001735</td>
      <td>0.016319</td>
      <td>0.028366</td>
      <td>-0.034411</td>
      <td>-0.029423</td>
    </tr>
    <tr>
      <th>2454</th>
      <td>-0.006445</td>
      <td>0.004016</td>
      <td>0.096133</td>
      <td>0.181828</td>
      <td>0.205832</td>
    </tr>
    <tr>
      <th>3008</th>
      <td>0.045016</td>
      <td>0.076114</td>
      <td>-0.005472</td>
      <td>-0.077484</td>
      <td>-0.089521</td>
    </tr>
    <tr>
      <th>3529</th>
      <td>0.013352</td>
      <td>0.018742</td>
      <td>-0.002352</td>
      <td>-0.027965</td>
      <td>-0.060221</td>
    </tr>
    <tr>
      <th>3533</th>
      <td>-0.005545</td>
      <td>-0.011337</td>
      <td>-0.031418</td>
      <td>-0.024718</td>
      <td>-0.064868</td>
    </tr>
    <tr>
      <th>5274</th>
      <td>-0.012302</td>
      <td>-0.018922</td>
      <td>-0.040927</td>
      <td>0.070814</td>
      <td>0.142673</td>
    </tr>
    <tr>
      <th>8069</th>
      <td>0.002974</td>
      <td>0.010994</td>
      <td>0.032438</td>
      <td>-0.019004</td>
      <td>-0.011854</td>
    </tr>
  </tbody>
</table>
</div>




```python
price_df[price_df['股票代號']=='2330']
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
      <th>日期</th>
      <th>股票代號</th>
      <th>股票名稱</th>
      <th>開盤價</th>
      <th>最高價</th>
      <th>最低價</th>
      <th>收盤價</th>
      <th>漲跌</th>
      <th>漲幅(%)</th>
      <th>振幅(%)</th>
      <th>...</th>
      <th>日期_dt_y</th>
      <th>year</th>
      <th>週集保月線</th>
      <th>週集保半年線</th>
      <th>週集保diff</th>
      <th>friday_of_week</th>
      <th>減資前</th>
      <th>新股上市</th>
      <th>adjust_week</th>
      <th>週集保diff4week</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4818</th>
      <td>19940905</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1.74</td>
      <td>1.74</td>
      <td>1.74</td>
      <td>1.74</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4819</th>
      <td>19940906</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1.86</td>
      <td>1.86</td>
      <td>1.86</td>
      <td>1.86</td>
      <td>6.5</td>
      <td>6.77</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4820</th>
      <td>19940907</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1.99</td>
      <td>1.99</td>
      <td>1.99</td>
      <td>1.99</td>
      <td>7.0</td>
      <td>6.83</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4821</th>
      <td>19940908</td>
      <td>2330</td>
      <td>台積電</td>
      <td>2.12</td>
      <td>2.12</td>
      <td>2.12</td>
      <td>2.12</td>
      <td>7.5</td>
      <td>6.85</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4822</th>
      <td>19940909</td>
      <td>2330</td>
      <td>台積電</td>
      <td>2.27</td>
      <td>2.27</td>
      <td>2.27</td>
      <td>2.27</td>
      <td>8.0</td>
      <td>6.84</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>12458</th>
      <td>20241113</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1045.00</td>
      <td>1050.00</td>
      <td>1035.00</td>
      <td>1035.00</td>
      <td>-15.0</td>
      <td>-1.43</td>
      <td>1.43</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>12459</th>
      <td>20241114</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1030.00</td>
      <td>1040.00</td>
      <td>1025.00</td>
      <td>1035.00</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>1.45</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>12460</th>
      <td>20241115</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1040.00</td>
      <td>1045.00</td>
      <td>1030.00</td>
      <td>1035.00</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>1.45</td>
      <td>...</td>
      <td>2024-11-15</td>
      <td>2024.0</td>
      <td>89.825</td>
      <td>89.810416</td>
      <td>-0.080005</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>-0.019999</td>
    </tr>
    <tr>
      <th>12461</th>
      <td>20241118</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1030.00</td>
      <td>1035.00</td>
      <td>1020.00</td>
      <td>1025.00</td>
      <td>-10.0</td>
      <td>-0.97</td>
      <td>1.45</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>12462</th>
      <td>20241119</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1030.00</td>
      <td>1045.00</td>
      <td>1025.00</td>
      <td>1040.00</td>
      <td>15.0</td>
      <td>1.46</td>
      <td>1.95</td>
      <td>...</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>7645 rows × 94 columns</p>
</div>



## hold_10Days_ret > 2% 可以beat 大盤 但不代表能beat 自己...


```python
print(price_df.groupby('股票代號')[ret_cols].mean())
print(price_df[price_df['signal']==1].groupby('股票代號')[ret_cols].mean())
```

          hold_5Days_ret  hold_10Days_ret  hold_20Days_ret  hold_60Days_ret  \
    股票代號                                                                      
    2059        0.005010         0.009969         0.020130         0.059021   
    2330        0.005216         0.010177         0.020035         0.061843   
    2383        0.005636         0.011274         0.022439         0.071093   
    2454        0.004865         0.009519         0.019327         0.061709   
    3008        0.004938         0.009546         0.019329         0.061985   
    3529        0.007856         0.015724         0.032443         0.101927   
    3533        0.007224         0.014696         0.030170         0.094578   
    5274        0.009307         0.018046         0.035860         0.108759   
    8069        0.005403         0.010970         0.022678         0.073954   
    
          hold_120Days_ret  
    股票代號                    
    2059          0.111671  
    2330          0.133989  
    2383          0.142366  
    2454          0.121948  
    3008          0.131951  
    3529          0.228197  
    3533          0.216573  
    5274          0.222019  
    8069          0.163949  
          hold_5Days_ret  hold_10Days_ret  hold_20Days_ret  hold_60Days_ret  \
    股票代號                                                                      
    2059        0.006141         0.011580         0.021498         0.061662   
    2330        0.003288         0.007023         0.013864         0.040244   
    2383        0.001164         0.003849         0.014555         0.079123   
    2454        0.004328         0.008477         0.018784         0.056963   
    3008        0.002090         0.005535         0.017011         0.060006   
    3529        0.010187         0.019267         0.038427         0.094904   
    3533        0.005359         0.013237         0.031580         0.086461   
    5274        0.013677         0.022356         0.043726         0.127794   
    8069        0.005168         0.010064         0.021985         0.065210   
    
          hold_120Days_ret  
    股票代號                    
    2059          0.136334  
    2330          0.113531  
    2383          0.154729  
    2454          0.107311  
    3008          0.088257  
    3529          0.209398  
    3533          0.189905  
    5274          0.267122  
    8069          0.121988  



```python
print(price_df[price_df['signal']==1].groupby('股票代號')[ret_cols].mean() - price_df.groupby('股票代號')[ret_cols].mean())
```

          hold_5Days_ret  hold_10Days_ret  hold_20Days_ret  hold_60Days_ret  \
    股票代號                                                                      
    2059        0.001131         0.001611         0.001367         0.002641   
    2330       -0.001929        -0.003154        -0.006171        -0.021600   
    2383       -0.004471        -0.007425        -0.007884         0.008030   
    2454       -0.000537        -0.001042        -0.000543        -0.004746   
    3008       -0.002848        -0.004011        -0.002317        -0.001979   
    3529        0.002331         0.003543         0.005984        -0.007023   
    3533       -0.001865        -0.001459         0.001410        -0.008117   
    5274        0.004370         0.004310         0.007865         0.019035   
    8069       -0.000235        -0.000906        -0.000693        -0.008743   
    
          hold_120Days_ret  
    股票代號                    
    2059          0.024663  
    2330         -0.020458  
    2383          0.012362  
    2454         -0.014637  
    3008         -0.043694  
    3529         -0.018799  
    3533         -0.026669  
    5274          0.045103  
    8069         -0.041961  



```python
price_df[['日期', '股票代號', 'signal']+ret_cols+winrate_cols].to_feather('/Users/roberthsu/Documents/TrendForce_project/TW_forwardPE/data/test_get_strategy_result/test.df')
```


```python
price_df[(price_df['股票代號']=='2330') & (price_df['signal']==1)]
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
      <th>日期</th>
      <th>股票代號</th>
      <th>股票名稱</th>
      <th>開盤價</th>
      <th>最高價</th>
      <th>最低價</th>
      <th>收盤價</th>
      <th>漲跌</th>
      <th>漲幅(%)</th>
      <th>振幅(%)</th>
      <th>...</th>
      <th>last_60Days_ret_0050</th>
      <th>hold_60Days_winrate_0050</th>
      <th>hold_120Days_ret_0050</th>
      <th>last_120Days_ret_0050</th>
      <th>hold_120Days_winrate_0050</th>
      <th>5MA</th>
      <th>10MA</th>
      <th>20MA</th>
      <th>60MA</th>
      <th>signal</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>7196</th>
      <td>20030709</td>
      <td>2330</td>
      <td>台積電</td>
      <td>22.24</td>
      <td>22.61</td>
      <td>22.05</td>
      <td>22.42</td>
      <td>-1.5</td>
      <td>-2.42</td>
      <td>2.42</td>
      <td>...</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>0.134036</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>21.990</td>
      <td>20.868</td>
      <td>20.281</td>
      <td>18.060333</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7197</th>
      <td>20030710</td>
      <td>2330</td>
      <td>台積電</td>
      <td>22.42</td>
      <td>22.42</td>
      <td>21.31</td>
      <td>21.31</td>
      <td>-3.0</td>
      <td>-4.96</td>
      <td>4.96</td>
      <td>...</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>0.150126</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>22.092</td>
      <td>21.055</td>
      <td>20.349</td>
      <td>18.161500</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7203</th>
      <td>20030718</td>
      <td>2330</td>
      <td>台積電</td>
      <td>21.13</td>
      <td>21.68</td>
      <td>21.13</td>
      <td>21.50</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>2.59</td>
      <td>...</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>0.219898</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>21.830</td>
      <td>21.978</td>
      <td>20.947</td>
      <td>18.722833</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7204</th>
      <td>20030721</td>
      <td>2330</td>
      <td>台積電</td>
      <td>21.50</td>
      <td>21.87</td>
      <td>21.13</td>
      <td>21.13</td>
      <td>-1.0</td>
      <td>-1.72</td>
      <td>3.45</td>
      <td>...</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>0.210659</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>21.646</td>
      <td>21.830</td>
      <td>21.023</td>
      <td>18.806167</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7213</th>
      <td>20030801</td>
      <td>2330</td>
      <td>台積電</td>
      <td>22.05</td>
      <td>22.42</td>
      <td>21.87</td>
      <td>22.24</td>
      <td>1.0</td>
      <td>1.69</td>
      <td>2.54</td>
      <td>...</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>0.171928</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>21.574</td>
      <td>21.406</td>
      <td>21.692</td>
      <td>19.627000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>12453</th>
      <td>20241106</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1050.00</td>
      <td>1080.00</td>
      <td>1040.00</td>
      <td>1060.00</td>
      <td>10.0</td>
      <td>0.95</td>
      <td>3.81</td>
      <td>...</td>
      <td>0.156119</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.212738</td>
      <td>0.0</td>
      <td>1041.000</td>
      <td>1048.000</td>
      <td>1049.750</td>
      <td>981.879667</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12455</th>
      <td>20241108</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1085.00</td>
      <td>1090.00</td>
      <td>1080.00</td>
      <td>1090.00</td>
      <td>25.0</td>
      <td>2.35</td>
      <td>0.94</td>
      <td>...</td>
      <td>0.157725</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.215301</td>
      <td>0.0</td>
      <td>1061.000</td>
      <td>1051.500</td>
      <td>1056.000</td>
      <td>987.432167</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12456</th>
      <td>20241111</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1080.00</td>
      <td>1090.00</td>
      <td>1070.00</td>
      <td>1085.00</td>
      <td>-5.0</td>
      <td>-0.46</td>
      <td>1.83</td>
      <td>...</td>
      <td>0.131646</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.216679</td>
      <td>0.0</td>
      <td>1070.000</td>
      <td>1053.500</td>
      <td>1058.000</td>
      <td>989.918500</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12457</th>
      <td>20241112</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1060.00</td>
      <td>1065.00</td>
      <td>1050.00</td>
      <td>1050.00</td>
      <td>-35.0</td>
      <td>-3.23</td>
      <td>1.38</td>
      <td>...</td>
      <td>0.118225</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.200844</td>
      <td>0.0</td>
      <td>1070.000</td>
      <td>1053.500</td>
      <td>1058.250</td>
      <td>991.805000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12460</th>
      <td>20241115</td>
      <td>2330</td>
      <td>台積電</td>
      <td>1040.00</td>
      <td>1045.00</td>
      <td>1030.00</td>
      <td>1035.00</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>1.45</td>
      <td>...</td>
      <td>0.064957</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.148182</td>
      <td>0.0</td>
      <td>1048.000</td>
      <td>1054.500</td>
      <td>1056.000</td>
      <td>996.100500</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>2768 rows × 88 columns</p>
</div>




```python

def vector_backtest(df):
    # input: df, 需要有signa columns, output : [[trade_data1], [trade_data2], ...] (list中包含多個list)
    # df['signal'] != df['signal'].shift(1) 會return boolean, 對此用cumsum
    # 在false的時候 就不會+1 就可以讓連續的組出現一樣的數字
    # [0  , 1, 1, 0, 0, 1, 1, 1] (df['signal'])
    # [nan, 0, 1, 1, 0, 0, 1, 1] (df['signal'].shift(1))
    # [T, T, F, T, F, T, F, F] -> [1, 2, 2, 3, 3, 4, 4, 4]
    # 然而連續組 同時包含signal==1 & signal==0 部分
    # 利用df[signal]==1 來取得signal==1的index
    if not all(col in df.columns for col in ['日期', '股票代號', '收盤價', 'signal']):
        raise KeyError("df.columns should have 日期, 股票代號, 收盤價, signal")

    df['次日收盤價'] = df['收盤價'].shift(-1)
    df['次二日收盤價'] = df['收盤價'].shift(-2)

    # 將所有連續的事件相同數字表示, 而事件轉換時, 數字不相同
    change_indices = (df['signal'] != df['signal'].shift(1)).cumsum() 
    # 只想要group signal==1的事件
    groups = df[df['signal'] == 1].groupby(change_indices[df['signal'] == 1])
    
    event_list_all = []
    for _, group in groups:
        '''
        盤後才知道訊號, 故操作都會在後續日期...
        訊號開始日期(start_date): 該日收盤後有符合訊號, 故買入價會是隔一日的收盤價
        訊號最後日期(end_date): 代表隔日收盤後就無訊號, 故賣出價是訊號最後日的隔二日收盤價
        ex: date=[10/1, 10/2, 10/3, 10/4], signal = [1, 1, 0, 0]
        則10/1為訊號開始日期 -> 10/2收盤價買入
        10/2為訊號最後日期 -> 10/3收盤才知道訊號結束 -> 10/4收盤賣出 
        '''
        com_code = group['股票代號'].iloc[-1]
        start_date = group['日期'].iloc[0]
        end_date = group['日期'].iloc[-1]
        buy_price = group['次日收盤價'].iloc[0]
        sell_price = group['次二日收盤價'].iloc[-1]
        ret = (sell_price/buy_price) - 1
        holding_days = len(group)

        event_list = [com_code, start_date, end_date, buy_price, sell_price, ret, holding_days]
        event_list_all.append(event_list)
    return event_list_all
```


```python
res_list = price_df.groupby('股票代號').apply(vector_backtest)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/406165768.py:1: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      res_list = price_df.groupby('股票代號').apply(vector_backtest)



```python
res_df = pd.DataFrame()
for data in res_list:
    tmp = pd.DataFrame(data, columns=['股票代號', '訊號開始日', '訊號結束日', '買入價格', '賣出價格', 'return', '訊號持續天數'])
    res_df = pd.concat([res_df, tmp], ignore_index=True)
```


```python
res_df.loc[res_df['return'] >= 0.1, '訊號持續天數'].describe()
```




    count    121.000000
    mean     124.033058
    std       53.726457
    min       52.000000
    25%       88.000000
    50%      112.000000
    75%      154.000000
    max      373.000000
    Name: 訊號持續天數, dtype: float64




```python
res_df.loc[(res_df['股票代號']=='5274') & (res_df['訊號開始日']>='20150101')].iloc[-20::]
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
      <th>股票代號</th>
      <th>訊號開始日</th>
      <th>訊號結束日</th>
      <th>買入價格</th>
      <th>賣出價格</th>
      <th>return</th>
      <th>訊號持續天數</th>
      <th>adjust_return</th>
      <th>winrate</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>361</th>
      <td>5274</td>
      <td>20170223</td>
      <td>20170825</td>
      <td>389.71</td>
      <td>530.66</td>
      <td>0.361679</td>
      <td>126</td>
      <td>1.355829</td>
      <td>1</td>
    </tr>
    <tr>
      <th>362</th>
      <td>5274</td>
      <td>20171013</td>
      <td>20171107</td>
      <td>557.52</td>
      <td>554.26</td>
      <td>-0.005847</td>
      <td>18</td>
      <td>0.988303</td>
      <td>0</td>
    </tr>
    <tr>
      <th>363</th>
      <td>5274</td>
      <td>20171114</td>
      <td>20171206</td>
      <td>568.91</td>
      <td>542.05</td>
      <td>-0.047213</td>
      <td>17</td>
      <td>0.946937</td>
      <td>0</td>
    </tr>
    <tr>
      <th>364</th>
      <td>5274</td>
      <td>20180102</td>
      <td>20180515</td>
      <td>580.31</td>
      <td>664.95</td>
      <td>0.145853</td>
      <td>86</td>
      <td>1.140003</td>
      <td>1</td>
    </tr>
    <tr>
      <th>365</th>
      <td>5274</td>
      <td>20180608</td>
      <td>20180710</td>
      <td>740.65</td>
      <td>583.59</td>
      <td>-0.212057</td>
      <td>22</td>
      <td>0.782093</td>
      <td>0</td>
    </tr>
    <tr>
      <th>366</th>
      <td>5274</td>
      <td>20181206</td>
      <td>20190419</td>
      <td>458.77</td>
      <td>548.87</td>
      <td>0.196395</td>
      <td>85</td>
      <td>1.190545</td>
      <td>1</td>
    </tr>
    <tr>
      <th>367</th>
      <td>5274</td>
      <td>20190703</td>
      <td>20190705</td>
      <td>533.19</td>
      <td>511.05</td>
      <td>-0.041524</td>
      <td>3</td>
      <td>0.952626</td>
      <td>0</td>
    </tr>
    <tr>
      <th>368</th>
      <td>5274</td>
      <td>20190712</td>
      <td>20200224</td>
      <td>550.23</td>
      <td>800.64</td>
      <td>0.455101</td>
      <td>149</td>
      <td>1.449251</td>
      <td>1</td>
    </tr>
    <tr>
      <th>369</th>
      <td>5274</td>
      <td>20200305</td>
      <td>20200717</td>
      <td>992.28</td>
      <td>1152.40</td>
      <td>0.161366</td>
      <td>92</td>
      <td>1.155516</td>
      <td>1</td>
    </tr>
    <tr>
      <th>370</th>
      <td>5274</td>
      <td>20200922</td>
      <td>20200928</td>
      <td>1091.75</td>
      <td>983.44</td>
      <td>-0.099208</td>
      <td>5</td>
      <td>0.894942</td>
      <td>0</td>
    </tr>
    <tr>
      <th>371</th>
      <td>5274</td>
      <td>20201007</td>
      <td>20210315</td>
      <td>1156.73</td>
      <td>1563.97</td>
      <td>0.352061</td>
      <td>104</td>
      <td>1.346211</td>
      <td>1</td>
    </tr>
    <tr>
      <th>372</th>
      <td>5274</td>
      <td>20210427</td>
      <td>20210820</td>
      <td>1763.26</td>
      <td>1841.44</td>
      <td>0.044338</td>
      <td>82</td>
      <td>1.038488</td>
      <td>1</td>
    </tr>
    <tr>
      <th>373</th>
      <td>5274</td>
      <td>20210914</td>
      <td>20220207</td>
      <td>1894.05</td>
      <td>2863.00</td>
      <td>0.511576</td>
      <td>94</td>
      <td>1.505726</td>
      <td>1</td>
    </tr>
    <tr>
      <th>374</th>
      <td>5274</td>
      <td>20220408</td>
      <td>20220504</td>
      <td>2744.62</td>
      <td>2227.27</td>
      <td>-0.188496</td>
      <td>18</td>
      <td>0.805654</td>
      <td>0</td>
    </tr>
    <tr>
      <th>375</th>
      <td>5274</td>
      <td>20220831</td>
      <td>20221007</td>
      <td>1923.84</td>
      <td>1649.71</td>
      <td>-0.142491</td>
      <td>27</td>
      <td>0.851659</td>
      <td>0</td>
    </tr>
    <tr>
      <th>376</th>
      <td>5274</td>
      <td>20221118</td>
      <td>20221230</td>
      <td>2100.07</td>
      <td>1718.24</td>
      <td>-0.181818</td>
      <td>31</td>
      <td>0.812332</td>
      <td>0</td>
    </tr>
    <tr>
      <th>377</th>
      <td>5274</td>
      <td>20230208</td>
      <td>20230713</td>
      <td>2183.29</td>
      <td>2459.64</td>
      <td>0.126575</td>
      <td>104</td>
      <td>1.120725</td>
      <td>1</td>
    </tr>
    <tr>
      <th>378</th>
      <td>5274</td>
      <td>20230913</td>
      <td>20240226</td>
      <td>2758.38</td>
      <td>2723.53</td>
      <td>-0.012634</td>
      <td>108</td>
      <td>0.981516</td>
      <td>0</td>
    </tr>
    <tr>
      <th>379</th>
      <td>5274</td>
      <td>20240402</td>
      <td>20240808</td>
      <td>3390.72</td>
      <td>4315.00</td>
      <td>0.272591</td>
      <td>87</td>
      <td>1.266741</td>
      <td>1</td>
    </tr>
    <tr>
      <th>380</th>
      <td>5274</td>
      <td>20240829</td>
      <td>20241004</td>
      <td>4930.00</td>
      <td>4360.00</td>
      <td>-0.115619</td>
      <td>24</td>
      <td>0.878531</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
res_df['adjust_return'] = res_df['return'] + 1 - 0.00585
```


```python
res_df['winrate'] = (res_df['return'] - 0.00585).apply(lambda x : 1 if x > 0 else 0)
```


```python
res_df.loc[(res_df['股票代號']=='2383') & mask, 'winrate'].mean()
```




    np.float64(0.45454545454545453)



## 我覺得目前的goal 應該是 用50%的time in market 去複製100%的 buy&hold return


```python
res_df.loc[(res_df['股票代號']=='2383'), 'adjust_return'].cumprod()
```




    117      1.810718
    118      1.665188
    119      1.443913
    120      1.407983
    121      1.391848
              ...    
    173    109.515373
    174    204.122405
    175    180.569503
    176    187.847619
    177    181.006643
    Name: adjust_return, Length: 61, dtype: float64




```python
mask = (res_df['訊號開始日']>='20150101')
for ticker in SUB_TICKERS:
    print(ticker, '-'*50)
    print(res_df.loc[(res_df['股票代號']==ticker) & mask, 'winrate'].mean())
```

    2059 --------------------------------------------------
    0.4
    3529 --------------------------------------------------
    0.55
    2383 --------------------------------------------------
    0.47619047619047616
    2330 --------------------------------------------------
    0.3888888888888889
    8069 --------------------------------------------------
    0.34782608695652173
    5274 --------------------------------------------------
    0.48
    3008 --------------------------------------------------
    0.36363636363636365
    2454 --------------------------------------------------
    0.375
    3533 --------------------------------------------------
    0.56


## 這些訊號給出來的metric, 像是勝率, return, 持有天數等 跟 他最後會不會beat 自己buy&hold 幾乎沒有關係啊



```python
mask = (res_df['訊號開始日']>='20150101')
for ticker in SUB_TICKERS:
    print(ticker, '-'*50)
    print(res_df.loc[(res_df['股票代號']==ticker) & mask, 'adjust_return'].cumprod())
```

    2059 --------------------------------------------------
    24    1.073704
    25    1.018269
    26    0.945617
    27    0.845300
    28    0.842448
    29    0.910435
    30    0.898349
    31    0.855847
    32    0.859924
    33    0.801080
    34    0.877663
    35    0.833737
    36    0.858505
    37    1.056661
    38    1.195902
    39    1.073666
    40    0.940826
    41    0.824905
    42    1.851978
    43    1.812821
    44    2.450083
    45    2.413792
    46    1.736088
    47    1.803436
    48         NaN
    Name: adjust_return, dtype: float64
    3529 --------------------------------------------------
    290    1.076862
    291    1.167435
    292    1.126389
    293    1.205862
    294    1.234166
    295    1.300546
    296    1.197866
    297    1.587103
    298    1.434322
    299    1.238858
    300    2.135981
    301    6.921280
    302    5.858060
    303    7.066384
    304    5.178796
    305    6.127953
    306    5.022745
    307    5.493311
    308    5.414622
    309         NaN
    Name: adjust_return, dtype: float64
    2383 --------------------------------------------------
    157    1.112279
    158    1.625003
    159    2.777402
    160    2.411179
    161    2.159258
    162    2.034499
    163    1.706952
    164    1.923004
    165    2.544269
    166    2.371492
    167    3.023427
    168    2.996076
    169    2.868855
    170    3.427143
    171    3.302461
    172    2.672966
    173    2.702668
    174    5.037422
    175    4.456173
    176    4.635785
    177    4.466961
    Name: adjust_return, dtype: float64
    2330 --------------------------------------------------
    99     1.001018
    100    0.951451
    101    0.914398
    102    1.073984
    103    1.359107
    104    1.228982
    105    1.201381
    106    1.191747
    107    1.494818
    108    3.089858
    109    3.087672
    110    2.853159
    111    2.624442
    112    2.417448
    113    2.496526
    114    2.387259
    115    4.267665
    116         NaN
    Name: adjust_return, dtype: float64
    8069 --------------------------------------------------
    406    0.932812
    407    0.862994
    408    0.731373
    409    0.709861
    410    0.675080
    411    0.868220
    412    0.987306
    413    1.468501
    414    1.378200
    415    1.281044
    416    1.176988
    417    1.093618
    418    0.938823
    419    0.915257
    420    1.304457
    421    2.408282
    422    3.418989
    423    3.124307
    424    2.933280
    425    2.596925
    426    2.436734
    427    2.860606
    428    3.534959
    Name: adjust_return, dtype: float64
    5274 --------------------------------------------------
    356    0.904797
    357    0.973301
    358    0.850189
    359    0.709661
    360    1.012892
    361    1.373308
    362    1.357244
    363    1.285224
    364    1.465160
    365    1.145891
    366    1.364235
    367    1.299606
    368    1.883455
    369    2.176361
    370    1.947718
    371    2.622040
    372    2.722958
    373    4.100028
    374    3.303204
    375    2.813203
    376    2.285256
    377    2.561143
    378    2.513802
    379    3.184337
    380    2.797540
    Name: adjust_return, dtype: float64
    3008 --------------------------------------------------
    258    0.841805
    259    1.122336
    260    1.459913
    261    1.414091
    262    1.437946
    263    1.217818
    264    1.412450
    265    1.504805
    266    1.385123
    267    1.499093
    268    1.486417
    269    1.344414
    270    1.223020
    271    1.147694
    272    0.994990
    273    1.185986
    274    1.176260
    275    1.089812
    276    1.004914
    277    0.980553
    278    1.132073
    279    1.130728
    Name: adjust_return, dtype: float64
    2454 --------------------------------------------------
    209    0.786954
    210    0.796381
    211    0.642395
    212    0.707082
    213    0.693239
    214    0.839686
    215    0.827908
    216    0.830901
    217    0.763173
    218    1.229403
    219    1.876080
    220    2.592754
    221    2.548452
    222    2.304537
    223    2.232255
    224    2.184971
    225    1.650349
    226    1.561482
    227    1.355056
    228    1.315666
    229    1.829784
    230    1.889384
    231    1.710543
    232         NaN
    Name: adjust_return, dtype: float64
    3533 --------------------------------------------------
    325    0.942288
    326    1.023214
    327    0.957079
    328    0.856791
    329    0.797596
    330    0.798283
    331    1.285934
    332    1.172076
    333    1.177846
    334    1.184177
    335    1.352032
    336    1.760839
    337    2.377330
    338    2.208059
    339    2.452912
    340    2.617768
    341    3.336348
    342    2.708993
    343    2.840251
    344    2.765888
    345    2.598835
    346    2.516225
    347    2.636359
    348    3.972125
    349         NaN
    Name: adjust_return, dtype: float64



```python
res_df.loc[res_df['股票代號']=='2330'].iloc[-20::]
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
      <th>股票代號</th>
      <th>訊號開始日</th>
      <th>訊號結束日</th>
      <th>買入價格</th>
      <th>賣出價格</th>
      <th>return</th>
      <th>訊號持續天數</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1145</th>
      <td>2330</td>
      <td>20240409</td>
      <td>20240419</td>
      <td>808.25</td>
      <td>747.75</td>
      <td>-0.074853</td>
      <td>9</td>
    </tr>
    <tr>
      <th>1146</th>
      <td>2330</td>
      <td>20240429</td>
      <td>20240502</td>
      <td>783.46</td>
      <td>779.49</td>
      <td>-0.005067</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1147</th>
      <td>2330</td>
      <td>20240510</td>
      <td>20240510</td>
      <td>812.22</td>
      <td>818.17</td>
      <td>0.007326</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1148</th>
      <td>2330</td>
      <td>20240514</td>
      <td>20240520</td>
      <td>832.05</td>
      <td>856.84</td>
      <td>0.029794</td>
      <td>5</td>
    </tr>
    <tr>
      <th>1149</th>
      <td>2330</td>
      <td>20240522</td>
      <td>20240528</td>
      <td>867.75</td>
      <td>831.06</td>
      <td>-0.042282</td>
      <td>5</td>
    </tr>
    <tr>
      <th>1150</th>
      <td>2330</td>
      <td>20240605</td>
      <td>20240624</td>
      <td>886.59</td>
      <td>955.73</td>
      <td>0.077984</td>
      <td>13</td>
    </tr>
    <tr>
      <th>1151</th>
      <td>2330</td>
      <td>20240628</td>
      <td>20240718</td>
      <td>963.69</td>
      <td>934.82</td>
      <td>-0.029958</td>
      <td>15</td>
    </tr>
    <tr>
      <th>1152</th>
      <td>2330</td>
      <td>20240805</td>
      <td>20240805</td>
      <td>876.08</td>
      <td>915.91</td>
      <td>0.045464</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1153</th>
      <td>2330</td>
      <td>20240807</td>
      <td>20240814</td>
      <td>892.01</td>
      <td>964.69</td>
      <td>0.081479</td>
      <td>6</td>
    </tr>
    <tr>
      <th>1154</th>
      <td>2330</td>
      <td>20240816</td>
      <td>20240816</td>
      <td>968.67</td>
      <td>968.67</td>
      <td>0.000000</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1155</th>
      <td>2330</td>
      <td>20240820</td>
      <td>20240823</td>
      <td>953.74</td>
      <td>937.81</td>
      <td>-0.016703</td>
      <td>4</td>
    </tr>
    <tr>
      <th>1156</th>
      <td>2330</td>
      <td>20240903</td>
      <td>20240904</td>
      <td>885.04</td>
      <td>913.91</td>
      <td>0.032620</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1157</th>
      <td>2330</td>
      <td>20240906</td>
      <td>20240909</td>
      <td>895.00</td>
      <td>896.99</td>
      <td>0.002223</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1158</th>
      <td>2330</td>
      <td>20240911</td>
      <td>20240927</td>
      <td>940.00</td>
      <td>972.00</td>
      <td>0.034043</td>
      <td>12</td>
    </tr>
    <tr>
      <th>1159</th>
      <td>2330</td>
      <td>20241009</td>
      <td>20241017</td>
      <td>1045.00</td>
      <td>1085.00</td>
      <td>0.038278</td>
      <td>6</td>
    </tr>
    <tr>
      <th>1160</th>
      <td>2330</td>
      <td>20241021</td>
      <td>20241023</td>
      <td>1075.00</td>
      <td>1065.00</td>
      <td>-0.009302</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1161</th>
      <td>2330</td>
      <td>20241025</td>
      <td>20241025</td>
      <td>1050.00</td>
      <td>1040.00</td>
      <td>-0.009524</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1162</th>
      <td>2330</td>
      <td>20241106</td>
      <td>20241106</td>
      <td>1065.00</td>
      <td>1090.00</td>
      <td>0.023474</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1163</th>
      <td>2330</td>
      <td>20241108</td>
      <td>20241112</td>
      <td>1085.00</td>
      <td>1035.00</td>
      <td>-0.046083</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1164</th>
      <td>2330</td>
      <td>20241115</td>
      <td>20241115</td>
      <td>1025.00</td>
      <td>1040.00</td>
      <td>0.014634</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>




```python
res_df.groupby('股票代號')['return'].mean()
```




    股票代號
    2059    0.004077
    2330    0.002834
    2383    0.004765
    2454    0.001114
    3008    0.001128
    3529    0.002985
    3533    0.008237
    5274    0.001990
    8069    0.003285
    Name: return, dtype: float64



## benchmark buy&hold all return -> start 2016


```python
price_df[(price_df['股票代號']=='2330') & (price_df['日期_dt']>='20030101')]
```

## 年化26% -> 100->1000的股票in 10y


```python
(1.26)**10
```

## 在做複雜的test 之前 我們來簡單搞一個
如果20日線 > 60日線 持有反之賣出  
我們來看這樣的持有時間長短, 最終return 並用quntstats present


```python
sub = price_df[(price_df['股票代號']=='2330') & (price_df['日期_dt']>'20030101')]
```


```python
sub
```


```python
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt

# Example stock price data
data = pd.Series([np.nan, 100, 102, 105, 99, 101, 103, 95, 96, 97, 99, 98, np.nan])

# Step 1: Identify local maxima and minima (avoid future data)
window = 2  # Window size for extrema detection
local_max_indices = argrelextrema(data.values, np.greater, order=window)[0]
local_min_indices = argrelextrema(data.values, np.less, order=window)[0]

# Extract local maxima and minima, ensuring proper alignment (avoid leakage)
local_maxima = pd.Series(data.iloc[local_max_indices].values, index=data.index[local_max_indices])
local_minima = pd.Series(data.iloc[local_min_indices].values, index=data.index[local_min_indices])

# Step 2: Compare successive maxima
max_comparisons_larger_idx = []
max_comparisons_smaller_idx = []
if len(local_maxima) > 1:
    for i in range(len(local_maxima) - 1):
        current_max = local_maxima.iloc[i]
        next_max = local_maxima.iloc[i + 1]
        if next_max > current_max:
            max_comparisons_larger_idx.append(local_maxima.index[i+1])
        else:
            max_comparisons_smaller_idx.append(local_maxima.index[i+1])

# Step 3: Compare successive minima
min_comparisons = []
if len(local_minima) > 1:
    for i in range(len(local_minima) - 1):
        current_min = local_minima.iloc[i]
        next_min = local_minima.iloc[i + 1]
        if next_min > current_min:
            min_comparisons.append(f"Min at index {local_minima.index[i+1]} is larger.")
        else:
            min_comparisons.append(f"Min at index {local_minima.index[i+1]} is smaller.")

# Step 4: Display results
print("Maxima Comparisons:")
print("\n".join(max_comparisons))

print("\nMinima Comparisons:")
print("\n".join(min_comparisons))

# Step 5: Visualize results
plt.figure(figsize=(12, 6))
plt.plot(data, label='Stock Prices', marker='o')
plt.scatter(local_maxima.index, local_maxima, color='red', label='Local Maxima', zorder=3)
plt.scatter(local_minima.index, local_minima, color='green', label='Local Minima', zorder=3)
plt.title("Stock Prices with Local Extrema")
plt.legend()
plt.show()

```

    Maxima Comparisons:



    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    Cell In[285], line 43
         41 # Step 4: Display results
         42 print("Maxima Comparisons:")
    ---> 43 print("\n".join(max_comparisons))
         45 print("\nMinima Comparisons:")
         46 print("\n".join(min_comparisons))


    NameError: name 'max_comparisons' is not defined



```python
max_comparisons_smaller_idx
```


```python
local_max_indices
```


```python
local_maxima
```


```python
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
import numpy as np
sub.reset_index(drop=True, inplace=True)
# 1. Identify Local Minima and Maxima
window = 10  # Window size for extrema detection

local_max_indices = argrelextrema(sub['收盤價'].values, np.greater, order=window)[0]
local_min_indices = argrelextrema(sub['收盤價'].values, np.less, order=window)[0]

# Extract local maxima and minima, ensuring proper alignment (avoid leakage)
local_maxima = pd.Series(sub.loc[local_max_indices, '收盤價'].values, index=local_max_indices)
local_minima = pd.Series(sub.loc[local_min_indices, '收盤價'].values, index=local_min_indices)

# Step 2: Compare successive maxima
max_comparisons_larger_idx = []
max_comparisons_smaller_idx = []
if len(local_maxima) > 1:
    for i in range(len(local_maxima) - 1):
        current_max = local_maxima.iloc[i]
        next_max = local_maxima.iloc[i + 1]
        if next_max > current_max:
            max_comparisons_larger_idx.append(local_maxima.index[i+1])
        else:
            max_comparisons_smaller_idx.append(local_maxima.index[i+1])
```


```python
def groupby_extrema(df):
    df.reset_index(drop=True, inplace=True)
    # 1. Identify Local Minima and Maxima
    window = 10  # Window size for extrema detection

    local_max_indices = argrelextrema(df['收盤價'].values, np.greater, order=window)[0]
    local_min_indices = argrelextrema(df['收盤價'].values, np.less, order=window)[0]

    # Extract local maxima and minima, ensuring proper alignment (avoid leakage)
    local_maxima = pd.Series(df.loc[local_max_indices, '收盤價'].values, index=local_max_indices)
    local_minima = pd.Series(df.loc[local_min_indices, '收盤價'].values, index=local_min_indices)

    # Step 2: Compare successive maxima
    max_comparisons_larger_idx = []
    max_comparisons_smaller_idx = []
    if len(local_maxima) > 1:
        for i in range(len(local_maxima) - 1):
            current_max = local_maxima.iloc[i]
            next_max = local_maxima.iloc[i + 1]
            if next_max > current_max:
                max_comparisons_larger_idx.append(local_maxima.index[i+1])
            else:
                max_comparisons_smaller_idx.append(local_maxima.index[i+1])
    
    df['max_comparisons_larger'] = None
    df.loc[max_comparisons_larger_idx, 'max_comparisons_larger'] = 1
    df.loc[max_comparisons_smaller_idx, 'max_comparisons_larger'] = 0
    df['max_comparisons_larger'].ffill(inplace=True)
    df['max_comparisons_larger'] = df['max_comparisons_larger'].shift(window)

    df.loc[max_comparisons_larger_idx, 'local_maxima'] = local_maxima
    df['local_maxima'].ffill(inplace=True)
    df['local_maxima'] = df['local_maxima'].shift(window)

    return df

```


```python
sub = groupby_extrema(sub)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:25: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      df['max_comparisons_larger'] = None
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:29: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      df['max_comparisons_larger'] = df['max_comparisons_larger'].shift(window)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:31: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      df.loc[max_comparisons_larger_idx, 'local_maxima'] = local_maxima
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:33: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      df['local_maxima'] = df['local_maxima'].shift(window)



```python
local_maxima
```




    31        15.45
    48        16.57
    124       22.98
    174       26.50
    187       26.31
             ...   
    5129     545.98
    5151     574.46
    5242     813.21
    5305    1075.19
    5384    1090.00
    Length: 133, dtype: float64




```python
sub['max_comparisons_larger'] = None
sub.loc[max_comparisons_larger_idx, 'max_comparisons_larger'] = 1
sub.loc[max_comparisons_smaller_idx, 'max_comparisons_larger'] = 0
sub['max_comparisons_larger'].ffill(inplace=True)
sub['max_comparisons_larger'] = sub['max_comparisons_larger'].shift(window)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2369469126.py:1: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      sub['max_comparisons_larger'] = None
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2369469126.py:4: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      sub['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2369469126.py:4: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      sub['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2369469126.py:4: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      sub['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2369469126.py:5: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame.
    Try using .loc[row_indexer,col_indexer] = value instead
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      sub['max_comparisons_larger'] = sub['max_comparisons_larger'].shift(window)



```python
sub.loc[max_comparisons_larger_idx, 'local_maxima'] = local_maxima
sub['local_maxima'].ffill(inplace=True)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/3881827340.py:2: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      sub['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/3881827340.py:2: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      sub['local_maxima'].ffill(inplace=True)



```python
price_df = price_df.groupby('股票代號').apply(groupby_extrema)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:28: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['max_comparisons_larger'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/2416033270.py:32: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_maxima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/3881079495.py:1: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      price_df = price_df.groupby('股票代號').apply(groupby_extrema)



```python
price_df.reset_index(drop=True, inplace=True)
```


```python
price_df[price_df['股票代號']=='8069']
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
      <th>日期</th>
      <th>股票代號</th>
      <th>股票名稱</th>
      <th>開盤價</th>
      <th>最高價</th>
      <th>最低價</th>
      <th>收盤價</th>
      <th>漲跌</th>
      <th>漲幅(%)</th>
      <th>振幅(%)</th>
      <th>...</th>
      <th>券資比</th>
      <th>當沖比率</th>
      <th>融資成本(推估)</th>
      <th>融券成本(推估)</th>
      <th>融資維持率(%)</th>
      <th>融券維持率(%)</th>
      <th>整體維持率(%)</th>
      <th>維持率反推融資平均損益</th>
      <th>max_comparisons_larger</th>
      <th>local_maxima</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>41176</th>
      <td>20040330</td>
      <td>8069</td>
      <td>元太科技</td>
      <td>12.69</td>
      <td>12.69</td>
      <td>12.69</td>
      <td>12.69</td>
      <td>2.1</td>
      <td>7.00</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>41177</th>
      <td>20040331</td>
      <td>8069</td>
      <td>元太科技</td>
      <td>13.56</td>
      <td>13.56</td>
      <td>13.56</td>
      <td>13.56</td>
      <td>2.2</td>
      <td>6.85</td>
      <td>0.00</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>41178</th>
      <td>20040401</td>
      <td>8069</td>
      <td>元太科技</td>
      <td>14.51</td>
      <td>14.51</td>
      <td>13.92</td>
      <td>14.51</td>
      <td>2.4</td>
      <td>7.00</td>
      <td>4.37</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>41179</th>
      <td>20040402</td>
      <td>8069</td>
      <td>元太科技</td>
      <td>14.75</td>
      <td>14.91</td>
      <td>14.43</td>
      <td>14.55</td>
      <td>0.1</td>
      <td>0.27</td>
      <td>3.27</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>41180</th>
      <td>20040405</td>
      <td>8069</td>
      <td>元太科技</td>
      <td>14.75</td>
      <td>15.54</td>
      <td>14.75</td>
      <td>15.54</td>
      <td>2.5</td>
      <td>6.79</td>
      <td>5.43</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>46258</th>
      <td>20241113</td>
      <td>8069</td>
      <td>元太</td>
      <td>289.50</td>
      <td>291.00</td>
      <td>287.00</td>
      <td>287.00</td>
      <td>-3.0</td>
      <td>-1.03</td>
      <td>1.38</td>
      <td>...</td>
      <td>6.75</td>
      <td>0.34</td>
      <td>299.151886</td>
      <td>298.879913</td>
      <td>159.896500</td>
      <td>197.864700</td>
      <td>183.255707</td>
      <td>-0.040621</td>
      <td>1.0</td>
      <td>319.0</td>
    </tr>
    <tr>
      <th>46259</th>
      <td>20241114</td>
      <td>8069</td>
      <td>元太</td>
      <td>287.00</td>
      <td>288.00</td>
      <td>273.00</td>
      <td>275.00</td>
      <td>-12.0</td>
      <td>-4.18</td>
      <td>5.23</td>
      <td>...</td>
      <td>7.21</td>
      <td>0.08</td>
      <td>297.732513</td>
      <td>289.317810</td>
      <td>153.941299</td>
      <td>199.892303</td>
      <td>181.797195</td>
      <td>-0.076352</td>
      <td>1.0</td>
      <td>319.0</td>
    </tr>
    <tr>
      <th>46260</th>
      <td>20241115</td>
      <td>8069</td>
      <td>元太</td>
      <td>277.00</td>
      <td>291.00</td>
      <td>277.00</td>
      <td>290.00</td>
      <td>15.0</td>
      <td>5.45</td>
      <td>5.09</td>
      <td>...</td>
      <td>10.28</td>
      <td>0.10</td>
      <td>297.443604</td>
      <td>289.528687</td>
      <td>162.495804</td>
      <td>189.691193</td>
      <td>179.330902</td>
      <td>-0.025025</td>
      <td>1.0</td>
      <td>319.0</td>
    </tr>
    <tr>
      <th>46261</th>
      <td>20241118</td>
      <td>8069</td>
      <td>元太</td>
      <td>290.00</td>
      <td>293.50</td>
      <td>285.50</td>
      <td>285.50</td>
      <td>-4.5</td>
      <td>-1.55</td>
      <td>2.76</td>
      <td>...</td>
      <td>10.87</td>
      <td>0.11</td>
      <td>297.282593</td>
      <td>289.165710</td>
      <td>160.060898</td>
      <td>192.439499</td>
      <td>179.989105</td>
      <td>-0.039635</td>
      <td>1.0</td>
      <td>319.0</td>
    </tr>
    <tr>
      <th>46262</th>
      <td>20241119</td>
      <td>8069</td>
      <td>元太</td>
      <td>286.50</td>
      <td>292.50</td>
      <td>284.00</td>
      <td>291.50</td>
      <td>6.0</td>
      <td>2.10</td>
      <td>2.98</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>319.0</td>
    </tr>
  </tbody>
</table>
<p>5087 rows × 108 columns</p>
</div>




```python
price_df['signal'] = 0
price_df.loc[(price_df['max_comparisons_larger']==1) & (price_df['收盤價']>price_df['local_maxima']), 'signal'] = 1
```


```python
price_df.groupby('股票代號')[ret_cols].mean()
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
      <th>hold_5Days_ret</th>
      <th>hold_10Days_ret</th>
      <th>hold_20Days_ret</th>
      <th>hold_60Days_ret</th>
      <th>hold_120Days_ret</th>
    </tr>
    <tr>
      <th>股票代號</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2059</th>
      <td>0.005010</td>
      <td>0.009969</td>
      <td>0.020130</td>
      <td>0.059021</td>
      <td>0.111671</td>
    </tr>
    <tr>
      <th>2330</th>
      <td>0.005216</td>
      <td>0.010177</td>
      <td>0.020035</td>
      <td>0.061843</td>
      <td>0.133989</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>0.005636</td>
      <td>0.011274</td>
      <td>0.022439</td>
      <td>0.071093</td>
      <td>0.142366</td>
    </tr>
    <tr>
      <th>2454</th>
      <td>0.004865</td>
      <td>0.009519</td>
      <td>0.019327</td>
      <td>0.061709</td>
      <td>0.121948</td>
    </tr>
    <tr>
      <th>3008</th>
      <td>0.004938</td>
      <td>0.009546</td>
      <td>0.019329</td>
      <td>0.061985</td>
      <td>0.131951</td>
    </tr>
    <tr>
      <th>3529</th>
      <td>0.007856</td>
      <td>0.015724</td>
      <td>0.032443</td>
      <td>0.101927</td>
      <td>0.228197</td>
    </tr>
    <tr>
      <th>3533</th>
      <td>0.007224</td>
      <td>0.014696</td>
      <td>0.030170</td>
      <td>0.094578</td>
      <td>0.216573</td>
    </tr>
    <tr>
      <th>5274</th>
      <td>0.009307</td>
      <td>0.018046</td>
      <td>0.035860</td>
      <td>0.108759</td>
      <td>0.222019</td>
    </tr>
    <tr>
      <th>8069</th>
      <td>0.005403</td>
      <td>0.010970</td>
      <td>0.022678</td>
      <td>0.073954</td>
      <td>0.163949</td>
    </tr>
  </tbody>
</table>
</div>




```python
price_df[price_df['signal']==1].groupby('股票代號')[ret_cols].mean() 
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
      <th>hold_5Days_ret</th>
      <th>hold_10Days_ret</th>
      <th>hold_20Days_ret</th>
      <th>hold_60Days_ret</th>
      <th>hold_120Days_ret</th>
    </tr>
    <tr>
      <th>股票代號</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2059</th>
      <td>0.010234</td>
      <td>0.021426</td>
      <td>0.037938</td>
      <td>0.067878</td>
      <td>0.106368</td>
    </tr>
    <tr>
      <th>2330</th>
      <td>0.009739</td>
      <td>0.019967</td>
      <td>0.036291</td>
      <td>0.107943</td>
      <td>0.172556</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>0.006633</td>
      <td>0.011365</td>
      <td>0.021769</td>
      <td>0.057707</td>
      <td>0.146857</td>
    </tr>
    <tr>
      <th>2454</th>
      <td>0.002814</td>
      <td>0.009597</td>
      <td>0.022597</td>
      <td>0.099526</td>
      <td>0.152978</td>
    </tr>
    <tr>
      <th>3008</th>
      <td>0.009887</td>
      <td>0.022666</td>
      <td>0.050017</td>
      <td>0.108828</td>
      <td>0.184070</td>
    </tr>
    <tr>
      <th>3529</th>
      <td>0.018322</td>
      <td>0.030211</td>
      <td>0.058981</td>
      <td>0.209172</td>
      <td>0.332006</td>
    </tr>
    <tr>
      <th>3533</th>
      <td>0.007822</td>
      <td>0.010388</td>
      <td>0.003051</td>
      <td>0.147018</td>
      <td>0.402058</td>
    </tr>
    <tr>
      <th>5274</th>
      <td>0.002533</td>
      <td>0.012891</td>
      <td>0.013768</td>
      <td>0.042794</td>
      <td>0.102530</td>
    </tr>
    <tr>
      <th>8069</th>
      <td>0.018205</td>
      <td>0.035424</td>
      <td>0.064889</td>
      <td>0.222567</td>
      <td>0.383674</td>
    </tr>
  </tbody>
</table>
</div>




```python
price_df[(price_df['signal']==1) & (price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean() - price_df[(price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean()
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
      <th>hold_5Days_ret</th>
      <th>hold_10Days_ret</th>
      <th>hold_20Days_ret</th>
      <th>hold_60Days_ret</th>
      <th>hold_120Days_ret</th>
    </tr>
    <tr>
      <th>股票代號</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2059</th>
      <td>0.013785</td>
      <td>0.031944</td>
      <td>0.054659</td>
      <td>0.029903</td>
      <td>-0.023299</td>
    </tr>
    <tr>
      <th>2330</th>
      <td>0.003559</td>
      <td>0.006922</td>
      <td>0.008594</td>
      <td>0.011781</td>
      <td>0.006901</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>0.000973</td>
      <td>0.002176</td>
      <td>0.001889</td>
      <td>-0.022385</td>
      <td>-0.001887</td>
    </tr>
    <tr>
      <th>2454</th>
      <td>-0.005250</td>
      <td>-0.007598</td>
      <td>-0.008038</td>
      <td>0.037411</td>
      <td>0.045153</td>
    </tr>
    <tr>
      <th>3008</th>
      <td>0.004929</td>
      <td>0.010483</td>
      <td>0.016240</td>
      <td>-0.038964</td>
      <td>-0.041388</td>
    </tr>
    <tr>
      <th>3529</th>
      <td>-0.001352</td>
      <td>-0.008921</td>
      <td>-0.010620</td>
      <td>0.015845</td>
      <td>0.008041</td>
    </tr>
    <tr>
      <th>3533</th>
      <td>-0.006262</td>
      <td>-0.013777</td>
      <td>-0.041594</td>
      <td>-0.033368</td>
      <td>-0.011141</td>
    </tr>
    <tr>
      <th>5274</th>
      <td>-0.008266</td>
      <td>-0.005330</td>
      <td>-0.020771</td>
      <td>-0.070566</td>
      <td>-0.109092</td>
    </tr>
    <tr>
      <th>8069</th>
      <td>0.001683</td>
      <td>0.003531</td>
      <td>-0.000550</td>
      <td>-0.000319</td>
      <td>0.167833</td>
    </tr>
  </tbody>
</table>
</div>




```python
print(price_df[(price_df['signal']==1) & (price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean() - price_df[(price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean())
```

          hold_5Days_ret  hold_10Days_ret  hold_20Days_ret  hold_60Days_ret  \
    股票代號                                                                      
    2059        0.013785         0.031944         0.054659         0.029903   
    2330        0.003559         0.006922         0.008594         0.011781   
    2383        0.000973         0.002176         0.001889        -0.022385   
    2454       -0.005250        -0.007598        -0.008038         0.037411   
    3008        0.004929         0.010483         0.016240        -0.038964   
    3529       -0.001352        -0.008921        -0.010620         0.015845   
    3533       -0.006262        -0.013777        -0.041594        -0.033368   
    5274       -0.008266        -0.005330        -0.020771        -0.070566   
    8069        0.001683         0.003531        -0.000550        -0.000319   
    
          hold_120Days_ret  
    股票代號                    
    2059         -0.023299  
    2330          0.006901  
    2383         -0.001887  
    2454          0.045153  
    3008         -0.041388  
    3529          0.008041  
    3533         -0.011141  
    5274         -0.109092  
    8069          0.167833  



```python
price_df[['日期', '股票代號', 'signal']+ret_cols+winrate_cols].to_feather('/Users/roberthsu/Documents/TrendForce_project/TW_forwardPE/data/test_get_strategy_result/test.df')
```


```python
sub['signal'] = 0
sub.loc[(sub['max_comparisons_larger']==1) & (sub['收盤價']>sub['local_maxima']), 'signal'] = 1
```


```python

def split_by_timeframe(data, date_col, n_splits):
    """
    Splits time series data into equal time-based chunks.
    
    Args:
        data (pd.DataFrame): Time series data.
        date_col (str): Column name containing datetime values.
        n_splits (int): Number of splits.

    Returns:
        list: A list of dataframes, each corresponding to a split.
    """
    # Ensure datetime format
    data[date_col] = pd.to_datetime(data[date_col])
    
    # Sort by date
    data = data.sort_values(by=date_col)
    
    # Compute timeframe boundaries
    start_date = data[date_col].min()
    end_date = data[date_col].max()
    timeframe = (end_date - start_date) / n_splits
    timeframes = [start_date + i * timeframe for i in range(n_splits + 1)]
    
    # Split data by timeframes
    splits = [
        data[(data[date_col] >= timeframes[i]) & (data[date_col] < timeframes[i + 1])]
        for i in range(n_splits)
    ]
    return splits
```


```python
splits = split_by_timeframe(sub, date_col='日期', n_splits=10)
```


```python
# Print the results
split_res = pd.DataFrame(columns=['benchmark_datapoints', 'benchmark_ret', 'benchmark_winrate', 'signal_datapoints', 'signal_ret', 'signal_winrate'])
for i, split in enumerate(splits):
    date_period = "{}~{}".format(split['日期'].min().strftime('%Y%m%d'), split['日期'].max().strftime('%Y%m%d'))
    split_res.loc[date_period, 'benchmark_datapoints'] = split['hold_20Days_ret'].count()
    split_res.loc[date_period, 'benchmark_ret'] = split['hold_20Days_ret'].mean()
    split_res.loc[date_period, 'benchmark_winrate'] = split['hold_20Days_winrate'].mean()

    split_res.loc[date_period, 'signal_datapoints'] = split.loc[split['signal']==1, 'hold_20Days_ret'].count()
    split_res.loc[date_period, 'signal_ret'] = split.loc[split['signal']==1, 'hold_20Days_ret'].mean()
    split_res.loc[date_period, 'signal_winrate'] = split.loc[split['signal']==1, 'hold_20Days_winrate'].mean()

split_res
    # print(f"Split {i+1}: {len(split)} rows, from {split['日期'].min()} to {split['日期'].max()}")
```


```python
sub[sub['signal']==1]
```


```python
sub.loc[max_comparisons_larger_idx]
```


```python
sub[sub['max_comparisons_larger']==1]
```


```python
sub = price_df[(price_df['日期_dt']>'20030101')]
```

## support


```python
def groupby_extrema(df):
    df.reset_index(drop=True, inplace=True)
    # 1. Identify Local Minima and Maxima
    window = 10  # Window size for extrema detection

    local_max_indices = argrelextrema(df['收盤價'].values, np.greater, order=window)[0]
    local_min_indices = argrelextrema(df['收盤價'].values, np.less, order=window)[0]

    # Extract local maxima and minima, ensuring proper alignment (avoid leakage)
    local_maxima = pd.Series(df.loc[local_max_indices, '收盤價'].values, index=local_max_indices)
    local_minima = pd.Series(df.loc[local_min_indices, '收盤價'].values, index=local_min_indices)

    # Step 2: Compare successive maxima
    max_comparisons_larger_idx = []
    max_comparisons_smaller_idx = []
    if len(local_maxima) > 1:
        for i in range(len(local_maxima) - 1):
            current_max = local_maxima.iloc[i]
            next_max = local_maxima.iloc[i + 1]
            if next_max > current_max:
                max_comparisons_larger_idx.append(local_maxima.index[i+1])
            else:
                max_comparisons_smaller_idx.append(local_maxima.index[i+1])
    
    df['max_comparisons_larger'] = None
    df.loc[max_comparisons_larger_idx, 'max_comparisons_larger'] = 1
    df.loc[max_comparisons_smaller_idx, 'max_comparisons_larger'] = 0
    df['max_comparisons_larger'].ffill(inplace=True)
    df['max_comparisons_larger'] = df['max_comparisons_larger'].shift(window)

    df.loc[max_comparisons_larger_idx, 'local_maxima'] = local_maxima
    df['local_maxima'].ffill(inplace=True)
    df['local_maxima'] = df['local_maxima'].shift(window)

    return df

```


```python
## 反向 股價跌破 local minima 又這個local minima < 上一個 在谷底的感覺
def groupby_extrema_sup(df):
    df.reset_index(drop=True, inplace=True)
    # 1. Identify Local Minima and Maxima
    window = 10  # Window size for extrema detection

    local_max_indices = argrelextrema(df['收盤價'].values, np.greater, order=window)[0]
    local_min_indices = argrelextrema(df['收盤價'].values, np.less, order=window)[0]

    # Extract local maxima and minima, ensuring proper alignment (avoid leakage)
    local_maxima = pd.Series(df.loc[local_max_indices, '收盤價'].values, index=local_max_indices)
    local_minima = pd.Series(df.loc[local_min_indices, '收盤價'].values, index=local_min_indices)

    # Step 2: Compare successive maxima
    min_comparisons_larger_idx = []
    min_comparisons_smaller_idx = []
    if len(local_minima) > 1:
        for i in range(len(local_minima) - 1):
            current_min = local_minima.iloc[i]
            next_min = local_minima.iloc[i + 1]
            if next_min < current_min:
                min_comparisons_smaller_idx.append(local_minima.index[i+1])

            else:
                min_comparisons_larger_idx.append(local_minima.index[i+1])

    
    df['min_comparisons_smaller'] = None
    df.loc[min_comparisons_smaller_idx, 'min_comparisons_smaller'] = 1
    df.loc[min_comparisons_larger_idx, 'min_comparisons_smaller'] = 0
    df['min_comparisons_smaller'].ffill(inplace=True)
    df['min_comparisons_smaller'] = df['min_comparisons_smaller'].shift(window)

    df.loc[min_comparisons_smaller_idx, 'local_minima'] = local_minima
    df['local_minima'].ffill(inplace=True)
    df['local_minima'] = df['local_minima'].shift(window)

    return df

```


```python
sub = sub.groupby('股票代號').apply(groupby_extrema)
```


```python
sub.reset_index(drop=True, inplace=True)
```


```python
sub['signal'] = 0
sub.loc[(sub['min_comparisons_smaller']==1) & (sub['收盤價']<sub['local_minima']), 'signal'] = 1
```


```python
price_df = price_df.groupby('股票代號').apply(groupby_extrema_sup).reset_index(drop=True)
```

    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:31: FutureWarning: Downcasting object dtype arrays on .fillna, .ffill, .bfill is deprecated and will change in a future version. Call result.infer_objects(copy=False) instead. To opt-in to the future behavior, set `pd.set_option('future.no_silent_downcasting', True)`
      df['min_comparisons_smaller'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/672798835.py:35: FutureWarning: A value is trying to be set on a copy of a DataFrame or Series through chained assignment using an inplace method.
    The behavior will change in pandas 3.0. This inplace method will never work because the intermediate object on which we are setting values always behaves as a copy.
    
    For example, when doing 'df[col].method(value, inplace=True)', try using 'df.method({col: value}, inplace=True)' or df[col] = df[col].method(value) instead, to perform the operation inplace on the original object.
    
    
      df['local_minima'].ffill(inplace=True)
    /var/folders/l8/m7cjxss57kbc_bplh66qpmy40000gn/T/ipykernel_1703/3042435934.py:1: DeprecationWarning: DataFrameGroupBy.apply operated on the grouping columns. This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation. Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.
      price_df = price_df.groupby('股票代號').apply(groupby_extrema_sup).reset_index(drop=True)



```python
price_df['signal'] = 0
price_df.loc[(price_df['min_comparisons_smaller']==1) & (price_df['收盤價']<price_df['local_minima']), 'signal'] = 1
```

## 統整組合訊號


```python
price_df['signal'] = 0
mask1 = (price_df['min_comparisons_smaller']==1) & (price_df['收盤價']<price_df['local_minima'])
mask2 = (price_df['max_comparisons_larger']==1) & (price_df['收盤價']>price_df['local_maxima'])
mask3 = (price_df['週集保diff4week']>2)
mask4 = (price_df['維持率反推融資平均損益']<-0.1)
price_df.loc[mask1 | mask2 | mask3 | mask4, 'signal'] = 1
```


```python
price_df['signal'] = 0
mask1 = (price_df['min_comparisons_smaller']==1) & (price_df['收盤價']<price_df['local_minima'])
mask2 = (price_df['max_comparisons_larger']==1) & (price_df['收盤價']>price_df['local_maxima'])
mask3 = (price_df['週集保diff4week']>2)
mask4 = (price_df['維持率反推融資平均損益']<-0.1)
mask5 = (price_df['股票代號']=='3529')
price_df.loc[mask2 | mask3  , 'signal'] = 1
```


```python
price_df[(price_df['signal']==1) & (price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean() - price_df[(price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean()
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
      <th>hold_5Days_ret</th>
      <th>hold_10Days_ret</th>
      <th>hold_20Days_ret</th>
      <th>hold_60Days_ret</th>
      <th>hold_120Days_ret</th>
    </tr>
    <tr>
      <th>股票代號</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2059</th>
      <td>0.013502</td>
      <td>0.030495</td>
      <td>0.053344</td>
      <td>0.029263</td>
      <td>-0.022504</td>
    </tr>
    <tr>
      <th>2330</th>
      <td>0.003559</td>
      <td>0.006922</td>
      <td>0.008594</td>
      <td>0.011781</td>
      <td>0.006901</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>0.000993</td>
      <td>0.002319</td>
      <td>0.001372</td>
      <td>-0.023712</td>
      <td>-0.001302</td>
    </tr>
    <tr>
      <th>2454</th>
      <td>-0.005257</td>
      <td>-0.007536</td>
      <td>-0.007483</td>
      <td>0.038181</td>
      <td>0.046077</td>
    </tr>
    <tr>
      <th>3008</th>
      <td>0.004804</td>
      <td>0.010460</td>
      <td>0.016046</td>
      <td>-0.039318</td>
      <td>-0.041861</td>
    </tr>
    <tr>
      <th>3529</th>
      <td>-0.000859</td>
      <td>-0.008664</td>
      <td>-0.011410</td>
      <td>0.013098</td>
      <td>0.007267</td>
    </tr>
    <tr>
      <th>3533</th>
      <td>-0.006389</td>
      <td>-0.013726</td>
      <td>-0.039826</td>
      <td>-0.035919</td>
      <td>-0.020676</td>
    </tr>
    <tr>
      <th>5274</th>
      <td>-0.008261</td>
      <td>-0.006550</td>
      <td>-0.022982</td>
      <td>-0.060384</td>
      <td>-0.088765</td>
    </tr>
    <tr>
      <th>8069</th>
      <td>0.001723</td>
      <td>0.003080</td>
      <td>-0.000205</td>
      <td>-0.004150</td>
      <td>0.146779</td>
    </tr>
  </tbody>
</table>
</div>




```python
price_df[(price_df['signal']==1) & (price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean() - price_df[(price_df['日期_dt']>='20150101')].groupby('股票代號')[ret_cols].mean()
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
      <th>hold_5Days_ret</th>
      <th>hold_10Days_ret</th>
      <th>hold_20Days_ret</th>
      <th>hold_60Days_ret</th>
      <th>hold_120Days_ret</th>
    </tr>
    <tr>
      <th>股票代號</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2059</th>
      <td>0.001145</td>
      <td>-0.001881</td>
      <td>-0.008571</td>
      <td>-0.017709</td>
      <td>0.059678</td>
    </tr>
    <tr>
      <th>2330</th>
      <td>0.001980</td>
      <td>0.013668</td>
      <td>0.038330</td>
      <td>0.010271</td>
      <td>-0.077612</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>0.014009</td>
      <td>0.029048</td>
      <td>0.072698</td>
      <td>0.141411</td>
      <td>0.100985</td>
    </tr>
    <tr>
      <th>2454</th>
      <td>-0.005632</td>
      <td>-0.009516</td>
      <td>-0.011413</td>
      <td>-0.074296</td>
      <td>-0.094389</td>
    </tr>
    <tr>
      <th>3008</th>
      <td>-0.003463</td>
      <td>-0.008336</td>
      <td>-0.003124</td>
      <td>0.022068</td>
      <td>0.091420</td>
    </tr>
    <tr>
      <th>3529</th>
      <td>0.009344</td>
      <td>0.015667</td>
      <td>0.020369</td>
      <td>0.085481</td>
      <td>0.066753</td>
    </tr>
    <tr>
      <th>3533</th>
      <td>0.000942</td>
      <td>0.005379</td>
      <td>-0.003526</td>
      <td>-0.017821</td>
      <td>-0.043257</td>
    </tr>
    <tr>
      <th>5274</th>
      <td>0.000008</td>
      <td>0.019392</td>
      <td>0.026366</td>
      <td>-0.007074</td>
      <td>0.002823</td>
    </tr>
    <tr>
      <th>8069</th>
      <td>0.012272</td>
      <td>0.044946</td>
      <td>0.078766</td>
      <td>0.135744</td>
      <td>0.059660</td>
    </tr>
  </tbody>
</table>
</div>




```python
price_df[['日期', '股票代號', 'signal']+ret_cols+winrate_cols].to_feather('/Users/roberthsu/Documents/TrendForce_project/TW_forwardPE/data/test_get_strategy_result/test.df')
```


```python
price_df[price_df['signal']==1]
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
      <th>日期</th>
      <th>股票代號</th>
      <th>股票名稱</th>
      <th>開盤價</th>
      <th>最高價</th>
      <th>最低價</th>
      <th>收盤價</th>
      <th>漲跌</th>
      <th>漲幅(%)</th>
      <th>振幅(%)</th>
      <th>...</th>
      <th>hold_120Days_winrate_0050</th>
      <th>signal</th>
      <th>20MA</th>
      <th>60MA</th>
      <th>5MA</th>
      <th>10MA</th>
      <th>max_comparisons_larger</th>
      <th>local_maxima</th>
      <th>min_comparisons_smaller</th>
      <th>local_minima</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>400</th>
      <td>20061204</td>
      <td>2059</td>
      <td>川湖</td>
      <td>79.72</td>
      <td>80.96</td>
      <td>78.74</td>
      <td>78.98</td>
      <td>-1.5</td>
      <td>-0.93</td>
      <td>2.79</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>81.3010</td>
      <td>84.617000</td>
      <td>80.068</td>
      <td>80.708</td>
      <td>1.0</td>
      <td>90.34</td>
      <td>1.0</td>
      <td>79.48</td>
    </tr>
    <tr>
      <th>401</th>
      <td>20061205</td>
      <td>2059</td>
      <td>川湖</td>
      <td>78.98</td>
      <td>80.46</td>
      <td>78.24</td>
      <td>78.98</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>2.81</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>80.9555</td>
      <td>84.526500</td>
      <td>79.820</td>
      <td>80.560</td>
      <td>1.0</td>
      <td>90.34</td>
      <td>1.0</td>
      <td>79.48</td>
    </tr>
    <tr>
      <th>402</th>
      <td>20061206</td>
      <td>2059</td>
      <td>川湖</td>
      <td>78.49</td>
      <td>79.48</td>
      <td>78.24</td>
      <td>78.98</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>1.56</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>80.7210</td>
      <td>84.452500</td>
      <td>79.424</td>
      <td>80.338</td>
      <td>1.0</td>
      <td>90.34</td>
      <td>1.0</td>
      <td>79.48</td>
    </tr>
    <tr>
      <th>403</th>
      <td>20061207</td>
      <td>2059</td>
      <td>川湖</td>
      <td>78.98</td>
      <td>78.98</td>
      <td>78.24</td>
      <td>78.49</td>
      <td>-1.0</td>
      <td>-0.63</td>
      <td>0.94</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>80.4745</td>
      <td>84.415500</td>
      <td>79.030</td>
      <td>80.067</td>
      <td>1.0</td>
      <td>90.34</td>
      <td>1.0</td>
      <td>79.48</td>
    </tr>
    <tr>
      <th>404</th>
      <td>20061208</td>
      <td>2059</td>
      <td>川湖</td>
      <td>78.49</td>
      <td>78.74</td>
      <td>75.03</td>
      <td>76.02</td>
      <td>-5.0</td>
      <td>-3.14</td>
      <td>4.72</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>80.0795</td>
      <td>84.325000</td>
      <td>78.290</td>
      <td>79.475</td>
      <td>1.0</td>
      <td>90.34</td>
      <td>1.0</td>
      <td>79.48</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>46006</th>
      <td>20231030</td>
      <td>8069</td>
      <td>元太</td>
      <td>167.00</td>
      <td>167.00</td>
      <td>165.04</td>
      <td>166.02</td>
      <td>-0.5</td>
      <td>-0.29</td>
      <td>1.18</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>173.7790</td>
      <td>181.498500</td>
      <td>166.706</td>
      <td>169.604</td>
      <td>0.0</td>
      <td>231.79</td>
      <td>1.0</td>
      <td>168.97</td>
    </tr>
    <tr>
      <th>46007</th>
      <td>20231031</td>
      <td>8069</td>
      <td>元太</td>
      <td>166.02</td>
      <td>168.47</td>
      <td>163.56</td>
      <td>165.04</td>
      <td>-1.0</td>
      <td>-0.59</td>
      <td>2.96</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>173.2145</td>
      <td>180.639000</td>
      <td>166.314</td>
      <td>168.573</td>
      <td>0.0</td>
      <td>231.79</td>
      <td>1.0</td>
      <td>168.97</td>
    </tr>
    <tr>
      <th>46008</th>
      <td>20231101</td>
      <td>8069</td>
      <td>元太</td>
      <td>166.02</td>
      <td>167.98</td>
      <td>165.04</td>
      <td>166.02</td>
      <td>1.0</td>
      <td>0.60</td>
      <td>1.79</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>172.6005</td>
      <td>179.845000</td>
      <td>165.528</td>
      <td>167.493</td>
      <td>0.0</td>
      <td>231.79</td>
      <td>1.0</td>
      <td>168.97</td>
    </tr>
    <tr>
      <th>46012</th>
      <td>20231107</td>
      <td>8069</td>
      <td>元太</td>
      <td>170.93</td>
      <td>171.42</td>
      <td>164.54</td>
      <td>165.53</td>
      <td>-4.5</td>
      <td>-2.60</td>
      <td>4.05</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>170.8820</td>
      <td>176.685333</td>
      <td>168.182</td>
      <td>167.248</td>
      <td>0.0</td>
      <td>231.79</td>
      <td>1.0</td>
      <td>168.97</td>
    </tr>
    <tr>
      <th>46013</th>
      <td>20231108</td>
      <td>8069</td>
      <td>元太</td>
      <td>167.00</td>
      <td>168.97</td>
      <td>165.53</td>
      <td>167.98</td>
      <td>2.5</td>
      <td>1.48</td>
      <td>2.08</td>
      <td>...</td>
      <td>1.0</td>
      <td>1</td>
      <td>170.3905</td>
      <td>176.136833</td>
      <td>168.574</td>
      <td>167.051</td>
      <td>0.0</td>
      <td>231.79</td>
      <td>1.0</td>
      <td>168.97</td>
    </tr>
  </tbody>
</table>
<p>3228 rows × 92 columns</p>
</div>




```python
sub['signal'] = 0
sub.loc[(sub['max_comparisons_larger']==1) & (sub['收盤價']>sub['local_maxima']), 'signal'] = 1
```


```python
splits = split_by_timeframe(sub, date_col='日期', n_splits=10)
# Print the results
split_res = pd.DataFrame(columns=['benchmark_datapoints', 'benchmark_ret', 'benchmark_winrate', 'signal_datapoints', 'signal_ret', 'signal_winrate'])
for i, split in enumerate(splits):
    date_period = "{}~{}".format(split['日期'].min().strftime('%Y%m%d'), split['日期'].max().strftime('%Y%m%d'))
    split_res.loc[date_period, 'benchmark_datapoints'] = split['hold_20Days_ret'].count()
    split_res.loc[date_period, 'benchmark_ret'] = split['hold_20Days_ret'].mean()
    split_res.loc[date_period, 'benchmark_winrate'] = split['hold_20Days_winrate'].mean()

    split_res.loc[date_period, 'signal_datapoints'] = split.loc[split['signal']==1, 'hold_20Days_ret'].count()
    split_res.loc[date_period, 'signal_ret'] = split.loc[split['signal']==1, 'hold_20Days_ret'].mean()
    split_res.loc[date_period, 'signal_winrate'] = split.loc[split['signal']==1, 'hold_20Days_winrate'].mean()
split_res
```


```python
for ticker in sub['股票代號'].unique().tolist():
    splits = split_by_timeframe(sub[sub['股票代號']==ticker], date_col='日期', n_splits=10)
    # Print the results
    split_res = pd.DataFrame(columns=['benchmark_datapoints', 'benchmark_ret', 'benchmark_winrate', 'signal_datapoints', 'signal_ret', 'signal_winrate'])
    for i, split in enumerate(splits):
        date_period = "{}~{}".format(split['日期'].min().strftime('%Y%m%d'), split['日期'].max().strftime('%Y%m%d'))
        split_res.loc[date_period, 'benchmark_datapoints'] = split['hold_20Days_ret'].count()
        split_res.loc[date_period, 'benchmark_ret'] = split['hold_20Days_ret'].mean()
        split_res.loc[date_period, 'benchmark_winrate'] = split['hold_20Days_winrate'].mean()

        split_res.loc[date_period, 'signal_datapoints'] = split.loc[split['signal']==1, 'hold_20Days_ret'].count()
        split_res.loc[date_period, 'signal_ret'] = split.loc[split['signal']==1, 'hold_20Days_ret'].mean()
        split_res.loc[date_period, 'signal_winrate'] = split.loc[split['signal']==1, 'hold_20Days_winrate'].mean()
    print(ticker, '-'*50)
    print(split_res)
    # print(f"Split {i+1}: {len(split)} rows, from {split['日期'].min()} to {split['日期'].max()}")
```


```python
splits = split_by_timeframe(sub[sub['股票代號']=='2330'], date_col='日期', n_splits=10)
# Print the results
split_res = pd.DataFrame(columns=['benchmark_datapoints', 'benchmark_ret', 'benchmark_winrate', 'signal_datapoints', 'signal_ret', 'signal_winrate'])
for i, split in enumerate(splits):
    date_period = "{}~{}".format(split['日期'].min().strftime('%Y%m%d'), split['日期'].max().strftime('%Y%m%d'))
    split_res.loc[date_period, 'benchmark_datapoints'] = split['hold_20Days_ret'].count()
    split_res.loc[date_period, 'benchmark_ret'] = split['hold_20Days_ret'].mean()
    split_res.loc[date_period, 'benchmark_winrate'] = split['hold_20Days_winrate'].mean()

    split_res.loc[date_period, 'signal_datapoints'] = split.loc[split['signal']==1, 'hold_20Days_ret'].count()
    split_res.loc[date_period, 'signal_ret'] = split.loc[split['signal']==1, 'hold_20Days_ret'].mean()
    split_res.loc[date_period, 'signal_winrate'] = split.loc[split['signal']==1, 'hold_20Days_winrate'].mean()
split_res
```

## MA


```python
def MA(df):
    df['20MA'] = df['收盤價'].rolling(20, min_periods=20).mean()
    df['60MA'] = df['收盤價'].rolling(60, min_periods=60).mean()
    df['120MA'] = df['收盤價'].rolling(120, min_periods=120).mean()

    return df
```


```python
sub = sub.groupby('股票代號').apply(MA)
```


```python
sub.reset_index(drop=True, inplace=True)
```


```python
sub['20MA'] = sub['收盤價'].rolling(20, min_periods=20).mean()
sub['60MA'] = sub['收盤價'].rolling(60, min_periods=60).mean()
```

## 直觀的趨勢有抓到 但要避開盤整區間 均線糾結 how...
用rolling 統計過去一段時間 均線交錯的次數  
ex: 過去20日均線 均線20MA向上突破 但又跌回60MA以下  -> 或簡單一點講 突破連續一段時間後再進場
避開假突破之類的情況


```python
sub['signal'] = (sub['20MA']>sub['60MA']).apply(lambda x : 1 if x else 0)
```


```python
sub['signal'] = (sub['收盤價']<sub['120MA']).apply(lambda x : 1 if x else 0)
```


```python
splits = split_by_timeframe(sub, date_col='日期', n_splits=10)
# Print the results
split_res = pd.DataFrame(columns=['benchmark_datapoints', 'benchmark_ret', 'benchmark_winrate', 'signal_datapoints', 'signal_ret', 'signal_winrate'])
for i, split in enumerate(splits):
    date_period = "{}~{}".format(split['日期'].min().strftime('%Y%m%d'), split['日期'].max().strftime('%Y%m%d'))
    split_res.loc[date_period, 'benchmark_datapoints'] = split['hold_20Days_ret'].count()
    split_res.loc[date_period, 'benchmark_ret'] = split['hold_20Days_ret'].mean()
    split_res.loc[date_period, 'benchmark_winrate'] = split['hold_20Days_winrate'].mean()

    split_res.loc[date_period, 'signal_datapoints'] = split.loc[split['signal']==1, 'hold_20Days_ret'].count()
    split_res.loc[date_period, 'signal_ret'] = split.loc[split['signal']==1, 'hold_20Days_ret'].mean()
    split_res.loc[date_period, 'signal_winrate'] = split.loc[split['signal']==1, 'hold_20Days_winrate'].mean()
split_res
```


```python

```


```python
# 單ticker
def check_series(window):
    return 1 if (window == 1).all() else 0

sub['inital_signal'] = (sub['20MA']>sub['60MA']).apply(lambda x : 1 if x else 0)
# sub['inital_signal2'] = (sub['收盤價']>sub['20MA']).apply(lambda x : 1 if x else 0)
# sub['signal'] = sub['inital_signal'] * sub['inital_signal2']
sub['signal'] = sub['inital_signal'].rolling(5).apply(check_series)
```


```python
def check_series(window):
    return 1 if (window == 1).all() else 0

def check_series_df(df):
    df['signal'] = df['combine_signal'].rolling(5).apply(check_series)
    return df

sub['inital_signal'] = (sub['20MA']>sub['60MA']).apply(lambda x : 1 if x else 0)
sub['inital_signal2'] = (sub['收盤價']>sub['20MA']).apply(lambda x : 1 if x else 0)
sub['combine_signal'] = sub['inital_signal'] * sub['inital_signal2']
sub = sub.groupby('股票代號').apply(check_series_df)
```


```python
sub[(sub['signal']==1) & (sub['inital_signal']==0) ]
```


```python
# 讓訊號嚴格一些
sub['signal'] = (sub['20MA']/sub['60MA']).apply(lambda x : 1 if x > 1 else 0)
```

## Set Signal 後...


```python
delay_signal_dict = {}
def vector_backtest(df):
    # input: df, 需要有signa columns, output : [[trade_data1], [trade_data2], ...] (list中包含多個list)
    # df['signal'] != df['signal'].shift(1) 會return boolean, 對此用cumsum
    # 在false的時候 就不會+1 就可以讓連續的組出現一樣的數字
    # [0  , 1, 1, 0, 0, 1, 1, 1] (df['signal'])
    # [nan, 0, 1, 1, 0, 0, 1, 1] (df['signal'].shift(1))
    # [T, T, F, T, F, T, F, F] -> [1, 2, 2, 3, 3, 4, 4, 4]
    # 然而連續組 同時包含signal==1 & signal==0 部分
    # 利用df[signal]==1 來取得signal==1的index
    if not all(col in df.columns for col in ['日期', '股票代號', '收盤價', 'signal']):
        raise KeyError("df.columns should have 日期, 股票代號, 收盤價, signal")

    df['次日收盤價'] = df['收盤價'].shift(-1)
    df['次二日收盤價'] = df['收盤價'].shift(-2)

    # 將所有連續的事件相同數字表示, 而事件轉換時, 數字不相同
    change_indices = (df['signal'] != df['signal'].shift(1)).cumsum() 
    # 只想要group signal==1的事件
    groups = df[df['signal'] == 1].groupby(change_indices[df['signal'] == 1])
    
    com_code = df['股票代號'].iloc[-1]
    
    delay_signal_dict[com_code] = []
    delay_days = 10
    event_list_all = []
    print(com_code, '-'*50)
    for _, group in groups:
        '''
        盤後才知道訊號, 故操作都會在後續日期...
        訊號開始日期(start_date): 該日收盤後有符合訊號, 故買入價會是隔一日的收盤價
        訊號最後日期(end_date): 代表隔日收盤後就無訊號, 故賣出價是訊號最後日的隔二日收盤價
        ex: date=[10/1, 10/2, 10/3, 10/4], signal = [1, 1, 0, 0]
        則10/1為訊號開始日期 -> 10/2收盤價買入
        10/2為訊號最後日期 -> 10/3收盤才知道訊號結束 -> 10/4收盤賣出 
        '''
        org_signal = group.index.tolist()

        if len(org_signal) <= delay_days:
            # 訊號數不足 不會進場
            continue
        else:
            print(org_signal[delay_days::])
            df.loc[com_code] += org_signal[delay_days::]
            group.reset_index(drop=True, inplace=True)
            group = group.iloc[delay_days::]
            
        
        start_date = group['日期'].iloc[0]
        end_date = group['日期'].iloc[-1]
        buy_price = group['次日收盤價'].iloc[0]
        sell_price = group['次二日收盤價'].iloc[-1]
        ret = (sell_price/buy_price) - 1
        holding_days = len(group)

        event_list = [com_code, start_date, end_date, buy_price, sell_price, ret, holding_days]
        event_list_all.append(event_list)
    return pd.DataFrame(event_list_all)
```


```python
sub.reset_index(drop=True, inplace=True)
```


```python
res_df = sub.groupby('股票代號').apply(vector_backtest)
```


```python
res_df.columns = ['股票代號', '買入日期', '賣出日期', '買入價格', '賣出價格', 'return', '持有日期']
```


```python
res_dict = vector_backtest(sub)
```


```python
delay_signal_dict.keys()
```


```python
res_dict
```


```python
res_df = pd.DataFrame(res_dict, columns=['股票代號', '買入日期', '賣出日期', '買入價格', '賣出價格', 'return', '持有日期'] )
```


```python
res_df['precision'] = res_df['return'].apply(lambda x : 1 if x > 0.00585 else 0)
```


```python
res_df[['return', 'precision','持有日期']].describe()
```


```python
res_df.groupby('股票代號')[['return', 'precision','持有日期']].mean()
```


```python

'''
Plot 不同組合的signal

'''

n_rows, n_cols = 3, 3

# Create subplots for each category in a 2x4 grid
fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 8), sharex=True)

# Flatten the axes array for easier indexing
axes = axes.flatten()

for i, ticker in enumerate(SUB_TICKERS):
    tmp = sub[sub['股票代號']==ticker]       
    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(331)

    # axes[i].set_title(f'{ticker}_0Q 80~100, 4Q 0~20')
    axes[i].set_title(f'{ticker} vs price support signal')
    
    axes[i].plot(tmp['日期_dt'], tmp['收盤價'], label='close price')

    indices = tmp.loc[tmp['signal'] == 1, '日期_dt'].values

    # Plot vertical lines
    for x in indices:
        axes[i].axvline(x=x, color='r', linestyle='--', linewidth=1, alpha=0.4)

    axes[i].legend()
    # ax2 = axes[i].twinx()
    # ax2.vlines(sub.loc[sub['signal'] == 1, '日期_dt'], ymin=0, ymax=1,  label='signal', colors='orange')
    # ax2.legend()

    

```


```python
res_df.loc[res_df['持有日期'] > 10, ['return', 'precision']].describe()
```


```python
res_df
```


```python
res_df[['return', 'precision','持有日期']].describe()
```


```python
fig = plt.figure(figsize=(16, 8))
ax1 = fig.add_subplot(111)
ax1.set_title('{} P > support & support > last support'.format(sub['股票代號'].iloc[-1]))
ax1.plot(sub['日期_dt'], sub['收盤價'], label='price')

indices = sub.loc[sub['signal'] == 1, '日期_dt'].values

# Plot vertical lines
for x in indices:
    plt.axvline(x=x, color='r', linestyle='--', linewidth=1, alpha=0.4)

ax1.legend()
```


```python
from collections import Counter

def vector_backtest_ratio(df, trading_record_dict, buyholddays):
   
    '''
    for backtest PnL ratio
    index_count 算目前在該ticker 上累積bet的數量 
    '''

    
    df.reset_index(drop=True, inplace=True)
    df['ratio'] = 0
    signal_idx = df[df['signal']==1].index
    
    all_holding_idx = []
    for idx in signal_idx:
        adding_idx = [i for i in range(idx, idx+buyholddays) if i < len(df)]
        all_holding_idx += adding_idx
        
       
    
    item_counts = Counter(all_holding_idx) # 計算每個idx 出現的次數 return dict
   
    df['index_count'] = df.index.map(item_counts)

    for _, row in df[df['index_count']!=0].iterrows():

        date = row['日期']
        if date not in trading_record_dict.keys():
            continue
        trading_record_dict[date][row['股票代號']] = row['index_count']
    return df




def final_pnL_ratio(trading_record_dict, actual_signal_dict, buyholddays):

    
    perfect_ratio_dict = {} # -> 進backtest 
    yesterday_sub_dict = {} # trading_record_dict[上一個交易日]
    daily_actual_ratio = {}
    daily_add_tickers = {} 

    # sub_list = sorted_key[0:300]
    sorted_key = sorted(trading_record_dict.keys())

    for i, k in enumerate(sorted_key):
        if i > 0:
            yesterday = sorted_key[i - 1]
        else:
            yesterday = min(sorted_key)
        today = k
        perfect_ratio_dict[today] = {}
        

        if (len(trading_record_dict[yesterday]) > 0) | len(trading_record_dict[today]) > 0:
            today_add_ticker = []
            today_subtract_ticker = []
            today_unchange_ticker = []
            today_adjust_ticker = [] # 連續signal出現次數 > buy&hold 天數 故在today_add_ticker 要增加 同時也要減少 10天前的買入權重
            today_del_ticker = []

            today_sub_dict = trading_record_dict[today]
            
            # 1. 今天第一次出現ticker count ++
            keys_only_in_today = set(today_sub_dict.keys()) - set(yesterday_sub_dict.keys()) # return set
            today_add_ticker += list(keys_only_in_today)
            
            # 2. 皆存在 但今天數量 > 昨天
            series_today = pd.Series(today_sub_dict)
            series_yesterday = pd.Series(yesterday_sub_dict)
            subtraction_result = series_today - series_yesterday
            today_add_ticker += list(subtraction_result[subtraction_result == 1].index)

            # 2. 皆存在 但今天數量 < 昨天(第一天的buy&hold結束了 但第二天沒有ticker), 減少的比例就要看
            today_subtract_ticker += list(subtraction_result[subtraction_result == -1].index)

            # 3. unchange 沒有新signal 但舊signal 仍在buy&hold 中  But 如果value = 10 還是要調整 代表第一天signal到期了 但地11天又有
            # 錯 ! 在沒經過filter以前是對的 但經過filter以後 訊號會間斷
            
            today_unchange_tickers = list(subtraction_result[subtraction_result == 0].index)
            
            for t in today_unchange_tickers:
                if (today in actual_signal_dict.keys()):
                    if t in actual_signal_dict[today]:
                        today_add_ticker += [t]
                        today_adjust_ticker += [t]
                    else:
                        today_unchange_ticker += [t]
                    
                else:
                    today_unchange_ticker += [t]


            # 昨天存在 今天不存在
            keys_only_in_yesterday = set(yesterday_sub_dict.keys()) - set(today_sub_dict.keys()) # return set
            today_del_ticker += list(keys_only_in_yesterday)
            
            # 權重調整
            if (len(today_subtract_ticker) > 0) | (len(today_adjust_ticker) > 0) :
                before_date = sorted_key[i - buyholddays] # 10 : buy&hold 10 days # using list 是對的
                if before_date in daily_actual_ratio.keys():
                    today_subtract_ratio = daily_actual_ratio[before_date]
                else:
                    today_subtract_ratio = 0
                
            else:
                today_subtract_ratio = 0
            
            if len(today_add_ticker) > 0:
                today_add_ratio = (1/buyholddays) * (1/len(today_add_ticker))
            else:
                today_add_ratio = 0
            
            daily_actual_ratio[today] = today_add_ratio
            print(today, today_add_ticker)
            for t in today_add_ticker:
                if t in yesterday_sub_dict.keys():
                    perfect_ratio_dict[today][t] = perfect_ratio_dict[yesterday][t] + today_add_ratio
                else:
                    perfect_ratio_dict[today][t] = today_add_ratio
            
            for t in today_subtract_ticker:
                perfect_ratio_dict[today][t] = perfect_ratio_dict[yesterday][t] - today_subtract_ratio
            
            for t in today_adjust_ticker:
                perfect_ratio_dict[today][t] -= today_subtract_ratio

            for t in today_del_ticker:
                perfect_ratio_dict[today][t] = 0
            
            for t in today_unchange_ticker:
                perfect_ratio_dict[today][t] = perfect_ratio_dict[yesterday][t]
            
            # # 處理被減過頭
            for ticker in perfect_ratio_dict[today]:
                if perfect_ratio_dict[today][ticker] < 0:
                    perfect_ratio_dict[today][ticker] = 0

            yesterday_sub_dict = today_sub_dict
            daily_add_tickers[today] = today_add_ticker
    return perfect_ratio_dict


            
            
            
            

```


```python
trading_record_dict = {}
for d in price_df['日期'].unique().tolist():
    if d >= '20030101':
        trading_record_dict[d] = {}
```


```python
sub.reset_index(drop=True, inplace=True)
```


```python
# buy&hold til 下週訊號出來
# 週 -> 轉日 故想要buy&hold 20日 只要填15
modify_signal_df = sub.groupby('股票代號').apply(lambda df : vector_backtest_ratio(df, trading_record_dict, 1)).reset_index(drop=True)
```


```python
modify_signal_df[(modify_signal_df['signal']==0)]
```


```python
trading_record_dict
```


```python
tmp_df = modify_signal_df.loc[modify_signal_df['signal']==1, ['日期', '股票代號', 'signal']].groupby('日期')['股票代號'].unique().to_frame()
actual_signal_dict = {}
for idx, row in tmp_df.iterrows():
    actual_signal_dict[idx] = row['股票代號']

trading_dates = modify_signal_df['日期'].unique().tolist()
keys = list(trading_record_dict.keys())
for k in keys:
    if k not in trading_dates:
        del trading_record_dict[k]

```


```python
actual_signal_dict
```


```python
perfect_ratio_dict = final_pnL_ratio(trading_record_dict, actual_signal_dict, 1)
```


```python
# 全部都延遲一天 & 限制單筆上限20%投組
sorted_key = sorted(perfect_ratio_dict.keys()) 
max_date = sorted_key[-1]
final_ratio_dict = {}

for i, date in enumerate(sorted_key):
    if date == max_date:
        break
    tomorrow = sorted_key[i + 1]
    sub = perfect_ratio_dict[date]
    if sub: # dict not empty
        final_ratio_dict[tomorrow] = []
        for s in sub.keys():
            # if sub[s] > 0.2:
            #     sub[s] = 0.2
            final_ratio_dict[tomorrow].append(tuple([s, sub[s]]))

trading_record_dict_server_version = {}
for k, v in final_ratio_dict.items(): 
    # 修改日期format -> 在server上 因為用ch的cmoney module 日期為datetime dtype
    if isinstance(k, str):
        key_parse = re.match(r'(\d{4})(\d{2})(\d{2})', k)
    else:
        key_parse = re.match(r'(\d{4})(\d{2})(\d{2})', k.strftime("%Y%m%d"))
    modify_keys = f'{key_parse[1]}{key_parse[2]}{key_parse[3]}'
    trading_record_dict_server_version[modify_keys] = v


with open('/Users/roberthsu/Documents/TrendForce_project/TW_forwardPE/data/intermid/test_9t.pkl', 'wb') as handle:
    pickle.dump(trading_record_dict_server_version, handle, protocol=pickle.DEFAULT_PROTOCOL)
```


```python

```
