# Async-Host-Pingner
此專案目標為解決Linux環境下，使用非同步方式對多個Host執行Ping測試。

## 安裝要求
- Python > 3.9
- Linux OS

## 使用方式

配置 `ips.txt` (每行一個host)

進入root權限後執行以下指令
```
python3 main.py
```
相關執行日誌會以Json格式輸出至 `out.json`

輸出範例如下
```
[
    "[28/07/2022 12:08:17] IP: 8.8.8.8                        is up      TTL: 119     Bytes: 20   ",
    "[28/07/2022 12:08:17] IP: 8.8.4.4                        is up      TTL: 119     Bytes: 20   "
]
```
