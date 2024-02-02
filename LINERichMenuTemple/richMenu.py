
import requests
import json
##---------------取得richmenuId-----------------
Accesstoken='ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU='
headers = {f'Authorization':'Bearer {Accesstoken}','Content-Type':'application/json'}
# body = {
#     'size': {'width': 2500, 'height': 1686},   # 設定尺寸
#     'selected': 'true',                        # 預設是否顯示
#     'name': 'First',                   # 選單名稱
#     'chatBarText': '基本功能',            # 選單在 LINE 顯示的標題
#     'areas':[                                  # 選單內容
#         {
#           'bounds': {'x': 136, 'y': 42, 'width': 987, 'height': 222}, # 選單位置與大小
#           'action': {'type': 'message', 'text': '基本功能'}                # 點擊後傳送文字
#         },
#         {
#           'bounds': {'x': 1357, 'y': 42, 'width': 965, 'height': 222},
#           'action': {'type': 'message', 'text': '預約功能'}
#         },
#         {
#           'bounds': {'x': 965, 'y': 324, 'width':591, 'height': 637},
#           'action': {'type': 'message', 'text': '會員查詢'}
#         },
#         {
#           'bounds': {'x': 1754, 'y': 324, 'width': 591, 'height': 637},
#           'action': {'type': 'message', 'text': '聯絡我們'}
#         },
#         {
#           'bounds': {'x': 960, 'y': 1016, 'width': 591, 'height': 637},
#           'action': {'type': 'message', 'text': '商家資訊'}
#         },
#         {
#           'bounds': {'x': 1316, 'y': 1016, 'width': 591, 'height': 637},
#           'action': {'type': 'message', 'text': '社群粉專'}
#         },
#     ]
#   }
# # 向指定網址發送 request
def buttonTemple(headers,body):
  req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
    headers=headers,data=json.dumps(body).encode('utf-8'))
  print(req.text)
  return req.text
##---------------取得richmenuId-----------------

from linebot import (
    LineBotApi, WebhookHandler
)
# richMenuID='richmenu-06613611845f14bb1db2a1ff7aef7162'
token='ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU='
# 鴻運token
# token='nC8KEvZ7uN5aZOQE7DiqXmauvGcP9nzYwEk3sYKMrPtX6YKstpSAHTl/ec8uEp7od/pZ2lQ0TT6U6PXaifFatcVJiDXDLzvwO6m3my/2fNfnQxkiDtt7uavw7xL0PJme/DpsEATb9hCaGlQrdaLsxQdB04t89/1O/w1cDnyilFU='
##---------------列印richmenuId-----------------
line_bot_api = LineBotApi(token)
rich_menu_list = line_bot_api.get_rich_menu_list()
for rich_menu in rich_menu_list:
    print(f'Rich Menu ID: {rich_menu.rich_menu_id}')
#---------------列印richmenuId-----------------


##---------------加入圖片-----------------
# with open('/Users/choushi/Desktop/line預約/line_bot_fullVersion/line_bot_main_v1/LINE.jpg', 'rb') as f:
#   line_bot_api.set_rich_menu_image(richMenuID, 'image/jpeg', f)
##---------------加入圖片-----------------
headers = {'Authorization':'Bearer ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU='}

# req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/richmenu-06613611845f14bb1db2a1ff7aef7162', headers=headers)

# print(req.text)


# rich_menu_list = line_bot_api.get_rich_menu_list("richmenu-6a63d37de83d49ad015f44e79431a5ac")
for rich_menu in rich_menu_list:
  line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)
