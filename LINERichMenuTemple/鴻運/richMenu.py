
import requests
import json
from linebot import (
    LineBotApi, WebhookHandler
)
aaarichMenuID='richmenu-dcdf63ea871128555720f8ef1ee1bd8b'
richMenuID='richmenu-dd9e735a0d5aecbf9b13388cc8ee344f'
token='ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(token)
# ##---------------取得richmenuId-----------------
# headers = {f'Authorization':'Bearer ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}
# body = {
#     'size': {'width': 2500, 'height': 1686},   # 設定尺寸
#     'selected': 'true',                        # 預設是否顯示
#     'name': 'aaa',                   # 選單名稱
#     'chatBarText': '基本功能',            # 選單在 LINE 顯示的標題
#     'areas':[                                  # 選單內容
#         {
#           'bounds': {'x': 136, 'y': 42, 'width': 987, 'height': 222}, # 選單位置與大小
#           'action': {'type': 'postback', 'data': 'no-data'}                # 點擊後傳送文字
#         },
#         {
#           'bounds': {'x': 1357, 'y': 42, 'width': 965, 'height': 222},
#           'action': {'type': 'richmenuswitch', 'richMenuAliasId': 'aaa', 'data':'changeB'}



#         },        
#         {
#           'bounds': {'x': 90, 'y': 663, 'width': 779, 'height': 797},
#           'action': {'type': 'message', 'text': '#個人狀況'}
#         },
#         {
#           'bounds': {'x': 965, 'y': 324, 'width':591, 'height': 637},
#           'action': {'type': 'message', 'text': '#會員查詢'}
#         },
#         {
#           'bounds': {'x': 1754, 'y': 324, 'width': 591, 'height': 637},
#           'action': {'type': 'message', 'text': '#聯絡我們'}
#         },
#         {
#           'bounds': {'x': 960, 'y': 1016, 'width': 591, 'height': 637},
#           'action': {'type': 'message', 'text': '#商家資訊'}
#         },
#         {
#           'bounds': {'x': 1754, 'y': 1015, 'width': 615, 'height': 611},
#           'action': {'type': 'message', 'text': '#社群粉專'}
#         },
#     ]
#   }

# # # # 向指定網址發送 request

# req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
#   headers=headers,data=json.dumps(body).encode('utf-8'))
# print(req.text)
# print('0000000000')
##---------------取得richmenuId-----------------


# # ##---------------列印richmenuId-----------------

rich_menu_list = line_bot_api.get_rich_menu_list()
print(rich_menu_list)
for rich_menu in rich_menu_list:
    print(f'Rich Menu ID: {rich_menu.rich_menu_id}')
##---------------列印richmenuId-----------------

##---------------加入圖片-----------------
# with open('/Users/choushi/Desktop/line預約/line_bot_fullVersion/line_bot_main_v1/LINERichMenuTemple/鴻運/1.jpg', 'rb') as f:
#   line_bot_api.set_rich_menu_image(aaarichMenuID, 'image/jpeg', f)
##---------------加入圖片-----------------

##---------------將圖文選單 id 和別名 Alias id 綁定-----------------
# headers = {'Authorization':'Bearer ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU=','Content-Type':'application/json'}
# body = {
#     "richMenuAliasId":"aaa",
#     "richMenuId":aaarichMenuID
# }
# req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu/alias',
#                       headers=headers,data=json.dumps(body).encode('utf-8'))
# print(req.text)
##---------------將圖文選單 id 和別名 Alias id 綁定-----------------


# headers = {"Authorization":"Bearer ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU=","Content-Type":"application/json"}
# req = requests.request('POST', f'https://api.line.me/v2/bot/user/all/richmenu/richmenu-dcdf63ea871128555720f8ef1ee1bd8b', headers=headers)
# print(req.text)


# headers = {'Authorization':'Bearer ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU='}

# req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/richmenu-06613611845f14bb1db2a1ff7aef7162', headers=headers)

# print(req.text)

##---------------刪除功能-----------------

# rich_menu_list = line_bot_api.get_rich_menu_list()
# line_bot_api.delete_rich_menu("richmenu-e8f0eafb920c40bfd3c86d0338d226f5")
# for rich_menu in rich_menu_list:
#   line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)
