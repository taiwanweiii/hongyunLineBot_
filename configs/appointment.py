from classes.db import *

userName = ""


def getUserName(getUserName):
    global userName
    userName = getUserName


bot_configsDB = MYSQLDB('bot_configs')

# 選擇日期時顯示的數量
num_dates = 30 * 86400

#選擇顯示頁面數量
datapage = 7
timepage = 5

#設定底下button名稱
# def underButtonSendMessageList(userphone):
#     return bot_configsDB.TableOneSearch('companyphone',userphone)[0]['underButtonSendMessageList']

underButtonSendMessageList = [
    '預約練習場', '預約維修', '預約高爾夫球', '預約打蠟', '預約包磨', '預約烤漆'
]

# def underButtonLableList(userphone):
#     return bot_configsDB.TableOneSearch('companyphone',userphone)[0]['underButtonLableList']

underButtonLableList = ['維修', '洗車', '鍍膜', '打蠟', '包磨', '烤漆']

# 接受預約的時間段，
# {
# 星期: [開始~結束(時:分)]
# }
print('===================appointment===============')
print(userName)

print('===================appointment===============')


# print(bot_configsDB.TableOneSearch('companyphone','0987654321')[0]['activeTimes'])
def activeTimes(userphone):
    return bot_configsDB.TableOneSearch('companyphone',
                                        userphone)[0]['activeTimes']


# activeTimestest = {
#     '1': ['8:30 ~ 12:00', '13:00 ~ 17:00'],
#     '2': ['8:30 ~ 12:00', '13:00 ~ 17:00'], # [[8,30], [12,00]]
#     '3': ['8:30 ~ 12:00', '13:00 ~ 17:00'],
#     '4': ['8:30 ~ 12:00', '13:00 ~ 17:00'],
#     '5': ['8:30 ~ 12:00', '13:00 ~ 17:00'],
#     '6': ['8:30 ~ 12:00'],
#     '7': [],
# }

# 預約時間間隔 (分鐘)
interval = 30

# 預約提前時間 (分鐘)
offset = 15

# 自訂休假日
deniedDates = ['1/1', '8/8']

#每人預約次數
reserveCount = 999

#notify token
NOTIFYTOKEN = 'RYNSyiqBYJN0XSfSPlQA2h3lEi4X5pYkFFzju7PsPxQ'

#專案預約延後
day = 86400
