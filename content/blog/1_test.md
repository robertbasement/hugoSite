---
title: "未來的todo list"
date: 2025-03-10
author: "Robert Hsu"
type: "blog"
categories:
  - Branding
  - Design
summary: "每日基本課題, 中長期計畫"
---

## 每日基本課題

1. 關注的ticker pool追蹤
(每日推出csv至telegram 計算關注ticker的DCF估值, 最新營收etc 方便我一次總覽)
2. 量化關注整體市場

## 各產業估值變動
### Goal 檢視產業估值變化，試圖理解資金在哪些產業做輪轉
1. 用最新四季EPS搭配股價去估算現在該公司的本益比(去除EPS < 0)
2. 依據市值做產業加總
3. 得到圖表(顯示最近估值變化) & 表格數據 (過去一段時間的最高/最低/avg 本益比為何)

## 月營收相關策略
### Goal 希望能以交易策略`持續`在市場中獲利
每個月選出5隻以內做觀察 並篩出一兩隻做實際投入

## 目前狀況

已經建好基本的database, 網頁查找 但資料較不齊全

我感覺 還是得先搞交易策略 -> 定期推有梗的ticker
(每個月選一批 並在那個月定期追蹤) & (追蹤選出來的投資組合 vs 0050)

先建立workflow

1. fetching
2. anaylsis(EDA)
3. backtest (baseline model vs 0050)
4. backtest (ML) 
5. daily report for tracking