# # from datetime import datetime

# # active = [[['00:00', '00:30'], [None, None]], [['00:00', '16:30'], [None, None]], [['10:00', '19:00'], [None, None]], [['12:30', '17:00'], [None, None]], [['16:00', '17:00'], [None, None]], [['14:30', '17:00'], [None, None]], [['15:00', '17:00'], [None, None]]]

# # def convert_to_timestamps(active_list):
# #     converted_active = []

# #     for time_range in active_list:
# #         converted_range = []
# #         for time_point in time_range:
# #             if time_point[0] is not None:
# #                 start_time_str, end_time_str = time_range[0]
# #                 start_time = int(start_time_str.split(':')[0]) * 60 * 60 + int(start_time_str.split(':')[1])*60
# #                 end_time = int(end_time_str.split(':')[0]) * 60 * 60 + int(end_time_str.split(':')[1])*60
# #                 converted_range.append([int(start_time), int(end_time)] if time_range[0] is not None else [None, None])
# #             else:
# #                 converted_range.append([None, None])

# #         converted_active.append(converted_range)

# #     return converted_active

# # converted_active = convert_to_timestamps(active)
# # print(converted_active)
# # # for time_range in converted_active:
# #     # print(time_range)
# # import datetime
# # current_timestamp = datetime.datetime.timestamp(datetime.datetime.now())

# # data=[{'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1700875800, 'project': '維修', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 11, 23, 9, 31, 57), 'ID': 30, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1701050400, 'project': '打蠟', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 11, 23, 9, 32, 40), 'ID': 31, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1700787600, 'project': '高爾夫球', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 11, 23, 9, 33, 5), 'ID': 32, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1701306000, 'project': '維修', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 11, 29, 14, 24, 55), 'ID': 33, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1701399600, 'project': '練習場', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 11, 30, 6, 51, 44), 'ID': 34, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1701736200, 'project': '練習場', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 11, 30, 7, 14, 10), 'ID': 35, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1701738000, 'project': '維修', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 11, 30, 7, 14, 41), 'ID': 36, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1702765803, 'project': '一', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 12, 14, 1, 44, 58), 'ID': 37, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1702681200, 'project': '一', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 12, 14, 2, 11, 42), 'ID': 38, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1702679400, 'project': '一', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 12, 14, 2, 12, 9), 'ID': 39, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1702683000, 'project': '一', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 12, 14, 2, 29, 25), 'ID': 40, 'company': '0987654321'}, {'userId': 'Ue9a11eeae110fc8a29da9d00d3ebe5cb', 'dataTime': 1703548800, 'project': '項目二', 'status': '1', 'auto_updae_time': datetime.datetime(2023, 12, 16, 2, 35, 41), 'ID': 41, 'company': '0987654321'}]
# # filtered_data = [item for item in data if item['dataTime'] > current_timestamp]
# # print(filtered_data)
# # from flask import Flask, request
# # from linebot import LineBotApi, WebhookHandler
# # from linebot.models import TextSendMessage

# # app = Flask(__name__)

# # @app.route("/")
# # def home():
# #   line_bot_api = LineBotApi('ubNXeiTb/ckQXAQaemiRTVjsfNJ+t21QVNnY4XoAZrzZAYbz+mshUzFktAHhLgkE1kKq3/Gf8YBYNwVEAOjP1E/8DNKG6cwwpTuq4o1Vyfw7NrPyDSSTtV/s69mBH9BTzC9fyWKOooAK6P5bl7jmHwdB04t89/1O/w1cDnyilFU=')
# #   try:
# #     # 網址被執行時，等同使用 GET 方法發送 request，觸發 LINE Message API 的 push_message 方法
# #     line_bot_api.push_message('U8ae6ce9b2edb104526fed1e3202b8172', TextSendMessage(text='Hello World!!!'))
# #     return 'OK'
# #   except:
# #     print('error')

# # if __name__ == "__main__":
# #     app.run(debug=True, host='0.0.0.0', port=85, )



# filterBlackTimeUnix = [1, 2, 3, 4, 5, 6]
# historyDataTime = [2, 4, 4]
# # filterTimeUnix=[]
# # # 使用字典來追蹤每個元素的出現次數
# # element_count = {}

# # # 遍歷 filterBlackTimeUnix 中的每個元素
# # for x in historyDataTime:
# #     element_count[x] = element_count.get(x, 0) + 1
# # filterTimeUnix = [x for x in filterBlackTimeUnix if element_count.get(x, 0) < 2]
# for item in filterBlackTimeUnix:
#     print(item)

a = {'項目一': 2, '項目三': 4, '項目四': 1}
b = {'項目二': 4, '項目三': 3, '項目四': 2}

result = {}

# 將 a 的鍵值對加入 result
for key, value in a.items():
    result[key] = value

# 將 b 的鍵值對加入 result，如果鍵已經存在，則相加
for key, value in b.items():
    print('---key---')
    print(value)
    print('---key---')

    if key in result:
        result[key] += value
    else:
        result[key] = value

print(result)