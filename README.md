# 雲端平台 modal 使用免費GPU
modal給予每位用戶 $30/月 的免費計算積分，嘗試使用積分使用Jupyter啟動一個ollama的推斷伺服器，並透過ngrok穿透網路讓服務可以在自己的電腦上呼叫。
收費標準(2024-10-29 請依網站為準)
https://modal.com/pricing
| GPU Tasks          | Price      |
| ------------------ | ---------- |
| Nvidia H100        | $4.56 / h  |
| Nvidia A100, 80 GB | $3.40 / h  |
| Nvidia A100, 40 GB | $2.78 / h  |
| Nvidia A10G        | $1.10 / h  |
| Nvidia L4          | $0.80 / h  |
| Nvidia T4          | $0.59 / h| |

# Modal設定
## 安裝本機套件
在python中安裝modal套件
``` shell
pip install modal
```
## 設定API key
至[[https://modal.com/]]註冊帳號後，前往設定中的API Tokens建立新的Tokens以後使用以下指令設定
![create_api_token](image\createapitoken.jpeg)
```
modal token set --token-id ak-47N4...kF --token-secret as-CyVI...bgA
```
設定後會進行驗證
![set_api_toker](image\setapitoker.jpeg)

## 啟動Jupyter
``` shell
modal run jupyter_inside_modal.py
```
