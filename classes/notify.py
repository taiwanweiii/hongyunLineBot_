import requests

class notify:
    def __init__(self,NOTIFYTOKEN):
        self.url = 'https://notify-api.line.me/api/notify'
        self.headers = {
            'Authorization': 'Bearer ' + NOTIFYTOKEN    # 設定權杖
        }
    def SendMessage(self,notifyMessage):
        requests.post(self.url, headers=self.headers, data={'message':notifyMessage})   # 使用 POST 方法
