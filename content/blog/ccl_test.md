## CCL 產業分析 K-means

## Goal : 判讀產業趨勢，並給予預測&投資  

### Input : 財務資料, 股價資料etc...
### 資料freq : 季 
### Output : Peak, Expansion/Recovery, Low
### Metric : silhouette_score(越高則族群分的越開 但隨著加入的features越多則會越低), 每群持有至下一季財報return的差距

## Part 1. 資料整理


```python
def next_business_day_after_report(yyyyqq):
    """
    Convert 'YYYYQQ' (quarterly financial period) to the first business day after the report date.

    Parameters:
        yyyyqq (str): Year-Quarter string in 'YYYYQQ' format.
    
    Returns:
        str: First business day after the financial report in 'YYYYMMDD' format.
    """
    # Extract year and quarter
    year = int(yyyyqq[:4])
    quarter = int(yyyyqq[4:])

    # Determine the report date based on quarter rules
    if quarter == 1:
        report_date = pd.Timestamp(year, 5, 15)  # Q1 → May 15 (Same Year)
    elif quarter == 2:
        report_date = pd.Timestamp(year, 8, 15)  # Q2 → August 15 (Same Year)
    elif quarter == 3:
        report_date = pd.Timestamp(year, 11, 15)  # Q3 → November 15 (Same Year)
    elif quarter == 4:
        report_date = pd.Timestamp(year + 1, 3, 15)  # Q4 → March 15 (Next Year)
    else:
        raise ValueError("Invalid quarter. QQ must be 01, 02, 03, or 04.")

    # Find the next business day
    next_business_day = pd.offsets.BDay().rollforward(report_date + pd.Timedelta(days=1))

    # Return formatted date
    return next_business_day.strftime('%Y%m%d')
```


```python

```
