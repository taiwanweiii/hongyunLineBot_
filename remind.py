import time
import schedule
from main import pushRemindMessage
# 每分鐘執行一次 send_message 函式
# schedule.every(1).minutes.do(pushRemindMessage)
# schedule.every(1).seconds.do(pushRemindMessage)
pushRemindMessage()
schedule.every().day.at("20:00").do(pushRemindMessage)
while True:
    schedule.run_pending()
    time.sleep(1)
