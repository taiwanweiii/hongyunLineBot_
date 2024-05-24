from flask import Flask, request, jsonify, Blueprint
import requests
from datetime import datetime, timedelta, time, timezone
import pytz
import copy
import json
import configs.line
import configs.appointment
import api.preOrder
import admin.url as webUrl
import re
from urllib.parse import quote

# from classes.event import *
from classes.db import *
from classes.posdb import *
from classes.line import *
from classes.notify import *

from functions import member
from functions import functionTemplate
from functions import reserve

from admin import webhook

import time

TZ = pytz.timezone("Asia/Taipei")


def getDatetime():
    return datetime.now(TZ)


prefix = "/Linebotv1"

appointmentsDB = DB("appointments")

app = Flask(__name__)
app.register_blueprint(api.preOrder.PreOrderBlueprint,
                       url_prefix=f"{prefix}/api")


@app.route(prefix)
def hello():
    return "Hello, World!"


@app.route("/test/<username>/<hi>")
def user(username, hi):
    return f"username:{username} \nhi:{hi}"


clientWebhook = [
    list(entry.values())[0] for entry in webhook.client
    if isinstance(entry, dict) and entry
]
print("-------clientWebhook------")
print(clientWebhook)
print("-------clientWebhook------")


@app.route("/Linebotv1/<company>", methods=["POST"])
def LineBotv1(company):
    (
        liffID,
        configsSearchDBProjectList,
        LineToken,
        ballRollNumber,
        searchBallRollfillterTrue,
        projectDetails,
        projectList,
        projectNameList,
        projectsActiveList,
        projectsDayList,
        projectsintervalList,
        publicBlackTimeList,
        projectsoffsetList,
        projectsblockTimeList,
        projectSnumberOfAppointmentsList,
        projectGroupReserveStatusList,
        projectGroupNameList,
        isNotify,
    ) = getIsProject(company)
    line = LineToken

    configs.appointment.getUserName(company)
    if company in clientWebhook:
        data = request.get_json()
        print("===============data==================")
        print(data)
        print("===============data==================")

        # try:
        # start
        if "events" not in data:
            return print("events not exists.")
        for event in data["events"]:
            # init
            event = line.setEvent(event)

            user_status = member.isMember(event.uid, company)
            memberBasicInformation = memberData(company, event.uid)
            memberRole = ""
            memberIsCurotRecore = ""
            if len(memberBasicInformation) > 0:
                memberRole = memberBasicInformation[0]["role"]
                memberIsCurotRecore = memberBasicInformation[0][
                    "course_record"]

            match event.type:
                case "follow":
                    template = line.flexTemplate("first")
                    template["hero"]["action"][
                        "uri"] = f"https://liff.line.me/{liffID}?url=login"
                    line.doubleReplyFlexMessageText("歡迎您加入此帳號🤩", template,
                                                    "註冊訊息")
                case "message":
                    underButtonLableList = projectNameList
                    reserved_items = ["預約" + item for item in projectNameList]

                    underButtonSendMessageList = reserved_items
                    # memberBasicInformation=memberData(company,event.uid)
                    memberRegistertemplate = line.flexTemplate(
                        "memberRegister")
                    if memberBasicInformation:
                        memberBasicInformation = memberBasicInformation[0]
                        if memberBasicInformation["name"]:
                            memberRegistertemplate["hero"]["contents"][1][
                                "contents"][0]["contents"][0]["contents"][1][
                                    "text"] = memberBasicInformation["phone"]
                        if memberBasicInformation["phone"]:
                            memberRegistertemplate["hero"]["contents"][1][
                                "contents"][0]["contents"][1]["contents"][1][
                                    "text"] = memberBasicInformation["name"]
                        if memberBasicInformation["sex"]:
                            memberRegistertemplate["hero"]["contents"][1][
                                "contents"][0]["contents"][2]["contents"][1][
                                    "text"] = memberBasicInformation["sex"]
                    if event.message == "#測試":
                        template = line.flexTemplate("first")
                        line.replyFlex(template)
                    if user_status == "nouser":
                        template = line.flexTemplate("first")
                        template["hero"]["action"][
                            "uri"] = f"https://liff.line.me/{liffID}?url=login"
                        line.replyFlex(template)
                    if user_status == "phone":
                        if member.isPhone(event.message) == False:
                            print("---------------")
                            line.replyText("電話號碼格式錯誤，請再輸入1次(Ex:0987654321)")
                        else:
                            histroyPhones = member.isPhoneRepeat(company)

                            if event.message in histroyPhones:
                                line.doubleReplyMessageText(
                                    f"電話:{event.message} 已重複註冊",
                                    "請嘗試重新輸入10碼電話號碼",
                                )
                            else:
                                member.memberDB.updateTwoSearchWhere(
                                    "phone",
                                    event.message,
                                    "userId",
                                    event.uid,
                                    "company",
                                    company,
                                )
                            # member.update(event.uid,{'phone': event.message})
                            if member.isMember(event.uid, company) == True:
                                line.replyText("電話號碼更新完成")

                            elif member.isMember(event.uid, company) == "name":
                                memberRegistertemplate["hero"]["contents"][1][
                                    "contents"][0]["contents"][0]["contents"][
                                        1]["text"] = event.message
                                line.doubleMessageTextReplyFlex(
                                    "請於下方小鍵盤，輸入會員姓名",
                                    memberRegistertemplate,
                                    "會員姓名輸入",
                                )
                    elif user_status == "name":
                        if len(event.message) > 50:
                            line.replyText("使用者名稱過長,請嘗試重新輸入")
                        else:
                            member.memberDB.updateTwoSearchWhere(
                                "name",
                                event.message,
                                "userId",
                                event.uid,
                                "company",
                                company,
                            )

                            # member.update(event.uid,{'name': event.message})
                            user_status = member.isMember(event.uid, company)
                            if user_status == "sex":
                                # memberRegistertemplate = line.flexTemplate('memberRegister')
                                memberRegistertemplate["hero"]["contents"][1][
                                    "contents"][0]["contents"][0]["contents"][
                                        1]["text"] = memberBasicInformation[
                                            "phone"]
                                memberRegistertemplate["hero"]["contents"][1][
                                    "contents"][0]["contents"][1]["contents"][
                                        1]["text"] = event.message
                                template = functionTemplate.buttonTemplate(
                                    ["🙋🏻‍♂️男性", "🙋🏻‍♀️女性"],
                                    ["男", "女"],
                                    "🥰請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女",
                                )
                                line.doubleReplyTwoFlex(
                                    memberRegistertemplate, template)
                            elif user_status == "phone":
                                memberRegistertemplate["hero"]["contents"][1][
                                    "contents"][0]["contents"][0]["contents"][
                                        1]["text"] = event.message
                                template = functionTemplate.buttonTemplate(
                                    ["🙋🏻‍♂️男性", "🙋🏻‍♀️女性"],
                                    ["男", "女"],
                                    "🥰請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女",
                                )
                                line.doubleReplyTwoFlex(
                                    memberRegistertemplate, template)
                            else:
                                print(user_status)
                                line.replyText("會員資料更新完成")
                    elif user_status == "sex":
                        if event.message == "男" or event.message == "女":
                            memberRegistertemplate["hero"]["contents"][1][
                                "contents"][0]["contents"][2]["contents"][1][
                                    "text"] = event.message

                            member.memberDB.updateTwoSearchWhere(
                                "sex",
                                event.message,
                                "userId",
                                event.uid,
                                "company",
                                company,
                            )
                            reserve.reserveDB.Insert(
                                (
                                    "userId",
                                    "company",
                                ),
                                (
                                    event.uid,
                                    company,
                                ),
                            )
                            user_status = member.isMember(event.uid, company)

                            line.doubleReplyFlexMessageText(
                                "會員資料更新完成", memberRegistertemplate, "註冊完成")

                            # line.replyText("會員資料更新完成")
                        else:
                            template = functionTemplate.buttonTemplate(
                                ["🙋🏻‍♂️男性", "🙋🏻‍♀️女性"],
                                ["男", "女"],
                                "🥰請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女",
                            )
                            # templateTwo = line.flexTemplate('memberRegister')
                            line.doubleReplyTwoFlex(memberRegistertemplate,
                                                    template)
                    elif user_status == True:
                        # before
                        # isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
                        # before
                        if event.message == "#個人狀況":
                            if memberRole >= 2:
                                template = copy.deepcopy(
                                    line.flexTemplate("carousel"))
                                reserveList = copy.deepcopy(
                                    line.flexTemplate("reserveList"))
                                templateAdd = copy.deepcopy(
                                    reserveList["contents"][0])
                                print("---underButtonLableList---")
                                projectlist = ["球桿數據", "揮桿數據"]
                                imageUrl = [
                                    "https://i.imgur.com/nIByphE.png",
                                    "https://i.imgur.com/3PgjXM1.png",
                                ]

                                i = 0
                                while i < len(projectlist):
                                    templateAdd["hero"]["contents"][0][
                                        "url"] = (imageUrl[i])
                                    templateAdd["hero"]["contents"][1][
                                        "contents"][0]["text"] = "鴻運高爾夫工坊"
                                    templateAdd["hero"]["contents"][2][
                                        "contents"][1]["contents"][0][
                                            "text"] = f"點擊查看{projectlist[i]}"
                                    templateAdd["hero"]["action"][
                                        "data"] = f"personalData:{projectlist[i]}"
                                    templateAdd["hero"]["action"][
                                        "displayText"] = f"{projectlist[i]}查詢"
                                    template["contents"].append(
                                        copy.deepcopy(templateAdd))
                                    i += 1
                                line.replyFlex(template)
                            else:
                                line.doubleReplyMessageText(
                                    f"🙇‍♂️權限不足！！", "☎️如有疑問請致電｜0919-102-803")

                        elif (event.message in underButtonSendMessageList
                              and reserve.isReserveDBState(
                                  event.uid, company) == "noProject"):
                            event.message = str(event.message)
                            reserve.reserveDB.updateThreeSearchWhere(
                                "project",
                                event.message[2:],
                                "userId",
                                event.uid,
                                "status",
                                "0",
                                "company",
                                company,
                            )

                            projectNameIdx = projectNameList.index(
                                event.message[2:])
                            projectName = projectNameList[projectNameIdx]
                            projectsDay = projectsDayList[projectNameIdx]
                            projectsActive = projectsActiveList[projectNameIdx]
                            projectsoffset = projectsoffsetList[projectNameIdx]
                            projectsinterval = projectsintervalList[
                                projectNameIdx]
                            current_datetime = datetime.now()
                            current = current_datetime.replace(hour=0,
                                                               minute=0,
                                                               second=0,
                                                               microsecond=0)

                            nowtimestamp = current.timestamp()
                            todayTimestamp = nowtimestamp + projectsDay + 86400
                            nextTimestamp = todayTimestamp + projectsoffset
                            # print('---------------projectsoffset=====')
                            # print(projectsDayList)
                            # print(projectsDay)
                            # print('---------------projectsoffset=====')

                            # 打印結果

                            dayList = []
                            print("---------------publicBlackTimeList=====")
                            print(publicBlackTimeList)
                            print("---------------projectsoffset=====")
                            print("---------------projectsoffset=====")
                            print("---------------projectsoffset=====")
                            print("---------------projectsoffset=====")

                            # dayList.append(todayTimestamp)
                            ranges = [(start, start + 86400 - 1)
                                      for start in publicBlackTimeList]
                            while todayTimestamp < nextTimestamp:
                                if not any(start <= todayTimestamp <= end
                                           for start, end in ranges):
                                    dayList.append(todayTimestamp)
                                todayTimestamp += 86400

                            template = copy.deepcopy(
                                line.flexTemplate("appointmentNow"))
                            template_item = copy.deepcopy(
                                template["contents"][0]["body"]["contents"])
                            template_page_item = copy.deepcopy(
                                template["contents"][0])
                            template["contents"][0]["body"]["contents"] = []
                            datapage = configs.appointment.datapage
                            blackweekday = []
                            weekday_chinese = [
                                "一", "二", "三", "四", "五", "六", "日"
                            ]
                            for i in range(7):
                                if (projectsActive[i][0][0] == "00:00" and
                                        projectsActive[i][0][1] == "00:00"):
                                    blackweekday.append(weekday_chinese[i])
                            idex = 1
                            for idx, ts in enumerate(dayList):
                                dt = datetime.fromtimestamp(ts)
                                # date_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S%z")
                                # 取得年、月、日
                                year = dt.year
                                month = dt.month
                                day = dt.day
                                # print(ts)
                                # 輸出結果
                                # print(f'{dt.weekday()}')
                                # print(f'測試看看黑名單{blackweekday[0]}')
                                # print(f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})")
                                # print(ts)

                                if not weekday_chinese[
                                        dt.weekday()] in blackweekday:
                                    typePage = ((idex / datapage) + 1 if idex %
                                                datapage > 0 else
                                                (idex / datapage))
                                    typePage = int(typePage)

                                    # print("==================pyage")
                                    # print(f"idx: {idx}  typepage: {typePage}  page:{datapage}")
                                    if len(template["contents"]) < typePage:
                                        template["contents"].append(
                                            copy.deepcopy(
                                                template["contents"][0]))
                                        template["contents"][
                                            typePage -
                                            1]["body"]["contents"] = []
                                    template_item[0]["contents"][0][
                                        "text"] = f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})"
                                    template_item[0]["contents"][1]["action"][
                                        "data"] = f"appointment_choose_time:{int(ts)} project:{projectName}"
                                    template["contents"][
                                        typePage -
                                        1]["body"]["contents"].append(
                                            copy.deepcopy(template_item[0]))
                                    template["contents"][
                                        typePage -
                                        1]["body"]["contents"].append(
                                            copy.deepcopy(template_item[1]))
                                    idex += 1
                                else:
                                    print(weekday_chinese[dt.weekday()])
                                # print(projectNameList[projectNameIdx])
                                # activeTimes = configs.appointment.activeTimes

                            line.replyFlex(template)
                        elif event.message == "#會員查詢":
                            urlList = [
                                "https://i.imgur.com/HD83R4p.png",
                                "https://i.imgur.com/ekSGB7U.png",
                                "https://i.imgur.com/HYbdtoZ.png",
                            ]
                            template = copy.deepcopy(
                                line.flexTemplate("carousel"))
                            flex = copy.deepcopy(
                                line.flexTemplate("otherFlexText"))
                            i = 0
                            nameList = ["會員資料", "購買紀錄", "簽到記錄"]
                            if nameList:
                                for key, value in enumerate(nameList):
                                    k = i % 3
                                    flex["hero"]["contents"][0]["contents"][0][
                                        "url"] = urlList[k]
                                    flex["hero"]["contents"][0]["contents"][1][
                                        "text"] = value
                                    flex["hero"]["contents"][1]["contents"][0][
                                        "action"]["text"] = f"#{value}"
                                    template["contents"].append(
                                        copy.deepcopy(flex))
                                    i += 1
                                line.replyFlex(template)
                            else:
                                line.doubleReplyMessageText(
                                    f"👨‍💻尚未開放", "☎️如有疑問請致電｜0919-102-803")
                        elif event.message == "#會員資料":
                            template = copy.deepcopy(
                                line.flexTemplate("mebersearch"))
                            templateAdd = copy.deepcopy(
                                line.flexTemplate("memberAddtemplates"))
                            template["hero"]["contents"][1]["contents"][0][
                                "contents"][1]["contents"][1][
                                    "text"] = member.memberDB.dynamicTableSearch(
                                        {
                                            "userId": event.uid,
                                            "company": company
                                        })[0]["name"]
                            template["hero"]["contents"][1]["contents"][0][
                                "contents"][2]["contents"][1][
                                    "text"] = member.memberDB.dynamicTableSearch(
                                        {
                                            "userId": event.uid,
                                            "company": company
                                        })[0]["phone"]
                            try:
                                memberdate = member.memberDB.dynamicTableSearch(
                                    {
                                        "userId": event.uid,
                                        "company": company
                                    })
                            finally:
                                member.memberDB.closeConnection()
                            reserveDBSearch = MYSQLDB("reserve")

                            historySearchStatusUserId = (
                                reserveDBSearch.dynamicTableSearch({
                                    "userId":
                                    event.uid,
                                    "company":
                                    company,
                                    "status":
                                    1,
                                }))
                            nowTimeUnix = datetime.timestamp(datetime.now())

                            filtered_data = [
                                item for item in historySearchStatusUserId
                                if item["dataTime"] > nowTimeUnix
                            ]
                            sortFilteredDataTime = sorted(
                                filtered_data, key=lambda x: x["dataTime"])

                            if len(sortFilteredDataTime) > 0:
                                # reserveDateTimeformatYYYYMMDDhhmm=(datetime.fromtimestamp(int(sortFilteredDataTime[0]["dataTime"]),TZ)).strftime('20%y年%m月%d日%H:%M')

                                # template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[0]))
                                # template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[1]))
                                # template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[2]))
                                for correctData in sortFilteredDataTime:
                                    unixTime = correctData["dataTime"]
                                    formattedYYYYMMDDhhmm = datetime.fromtimestamp(
                                        unixTime,
                                        tz=TZ).strftime("%Y年%m月%d日 %H:%M")
                                    templateAdd[0]["contents"][1][
                                        "text"] = correctData["project"]
                                    templateAdd[1]["contents"][1][
                                        "text"] = formattedYYYYMMDDhhmm
                                    template["hero"]["contents"][1][
                                        "contents"][1]["contents"].append(
                                            copy.deepcopy(templateAdd[0]))
                                    template["hero"]["contents"][1][
                                        "contents"][1]["contents"].append(
                                            copy.deepcopy(templateAdd[1]))
                                    template["hero"]["contents"][1][
                                        "contents"][1]["contents"].append(
                                            copy.deepcopy(templateAdd[2]))

                                print("--------template=======")
                            else:
                                templateAdd[0]["contents"][1]["text"] = "尚未預約"
                                templateAdd[1]["contents"][1]["text"] = "-"
                                template["hero"]["contents"][1]["contents"][1][
                                    "contents"].append(
                                        copy.deepcopy(templateAdd[0]))
                                template["hero"]["contents"][1]["contents"][1][
                                    "contents"].append(
                                        copy.deepcopy(templateAdd[1]))
                                template["hero"]["contents"][1]["contents"][1][
                                    "contents"].append(
                                        copy.deepcopy(templateAdd[2]))

                            # print('=====historySearchStatusUserId====')
                            # print(historySearchStatusUserId)
                            # print('====historySearchStatusUserId====')
                            # nowTime=getDatetime()
                            # nowTimeUinx=int(nowTime.timestamp())
                            # filtered_list = [item for item in historySearchStatusUserId if 'dataTime' in item and item['dataTime'] > nowTimeUinx]
                            # print(len(filtered_list))
                            # if len(filtered_list)>0:
                            # 	reserveDateTimeformatYYYYMMDDhhmm=(datetime.fromtimestamp(int(filtered_list[0]["dataTime"]),TZ)).strftime('20%y年%m月%d日%H:%M')
                            # 	template['body']['contents'][3]['contents'][1]['contents'][1]['text']='已預約'
                            # 	template['body']['contents'][3]['contents'][2]['contents'][1]['text']=reserveDateTimeformatYYYYMMDDhhmm
                            # else:
                            # 	template['body']['contents'][3]['contents'][1]['contents'][1]['text']='尚未預約'
                            # 	template['body']['contents'][3]['contents'][2]['contents'][1]['text']="-"

                            # # print(reserveDateTimeformatYYYYMMDDhhmm)
                            line.replyFlex(template)
                        elif event.message == "#商家資訊":
                            line.replyTextAndImage(
                                """地址:台南市東區裕文路376號
📍Google Map:https://maps.app.goo.gl/g3S5iD1Woo7a2SZF8

📱電話：0919-102-803

🌻週一
      下午13:30 至 晚上21:00
🌻週二至週五
      早上10:00至晚上21:00
🌻週六早上10:00至下午6:00

🌷週日和例假日公休
													""",
                                "https://i.imgur.com/KTOITqS.png",
                            )
                        elif event.message == "#簽到記錄":
                            template = copy.deepcopy(
                                line.flexTemplate("checkinRecord"))
                            templateAdd = copy.deepcopy(
                                template["body"]["contents"][1]["contents"][0])
                            template["body"]["contents"][1]["contents"] = []
                            nameList = []
                            end_time = datetime.now().strftime("%Y-%m-%d")
                            # 前三十天
                            start_time = (
                                datetime.now() -
                                timedelta(days=30)).strftime("%Y-%m-%d")
                            timeRange = [start_time, end_time]
                            print("--start_time--")
                            print(start_time)
                            reserveDBSearch = MYSQLDB("reserve")
                            historySearchStatusUserId = (
                                reserveDBSearch.dynamicTableSearch({
                                    "userId":
                                    event.uid,
                                    "company":
                                    company,
                                    "status":
                                    1,
                                }))

                            for item in historySearchStatusUserId:
                                datetimeItem = item.get("dataTime")
                                formatted_date = datetime.fromtimestamp(
                                    datetimeItem, tz=TZ).strftime("%Y/%m/%d")
                                projectName = item.get("project")
                                nameList.append([projectName, formatted_date])

                            print(len(nameList))
                            i = 0
                            if len(nameList) > 0:
                                nameListReverse = nameList[::-1]
                                while i < len(nameList):
                                    print(i)
                                    templateAdd["contents"][0]["text"] = (
                                        nameListReverse[i - 1][0])
                                    templateAdd["contents"][1]["text"] = (
                                        nameListReverse[i - 1][1])
                                    template["body"]["contents"][1][
                                        "contents"].append(
                                            copy.deepcopy(templateAdd))
                                    print("----nameListReverse----")
                                    print(nameListReverse[i - 1][0])
                                    print("----nameListReverse----")
                                    i = i + 1
                                line.replyFlex(template)
                            else:
                                line.replyText("尚無簽到紀錄😉")
                        elif event.message == "#團練/比賽專區":
                            template = copy.deepcopy(
                                line.flexTemplate("houngyunPKAndGroup"))

                            line.replyFlex(template)
                        elif event.message == "#購買紀錄":
                            template = copy.deepcopy(
                                line.flexTemplate("buysellHistory"))
                            templateAdd = copy.deepcopy(
                                template["body"]["contents"][1]["contents"][0])
                            template["body"]["contents"][1]["contents"] = []
                            nameList = []
                            end_time = datetime.now().strftime("%Y-%m-%d")
                            # 前三十天
                            start_time = (
                                datetime.now() -
                                timedelta(days=30)).strftime("%Y-%m-%d")
                            timeRange = [start_time, end_time]
                            print("--start_time--")
                            print(start_time)
                            phone = member.memberDB.dynamicTableSearch({
                                "userId":
                                event.uid,
                                "company":
                                company
                            })[0]["phone"]
                            posMember = posDB("customers")
                            posMemberId = posMember.dynamicTableSearch(
                                {"phone": phone})[0]["id"]
                            ordersDb = posDB("orders")
                            ordersDataList = ordersDb.sellBuyHistory(
                                posMemberId, timeRange)
                            for item in ordersDataList:
                                content = item.get("content")
                                datetimeItem = item.get("datetime")
                                formatted_date = datetimeItem.strftime(
                                    "%Y/%m/%d")

                                if not isinstance(content, dict):
                                    try:
                                        content = json.loads(content)
                                        content = content["products"]
                                    except ValueError:
                                        print("content 無法將變量轉換為字典")
                                else:
                                    content = content["products"]
                                for nameItems in content:
                                    if (nameItems.get("price")) > 0:
                                        projectName = nameItems.get("name")
                                        nameList.append(
                                            [projectName, formatted_date])
                                        # nameList.append({nameItems.get('name')})
                            print(len(nameList))
                            i = 0
                            if len(nameList) > 0:
                                nameListReverse = nameList[::-1]
                                while i < len(nameList):
                                    print(i)
                                    templateAdd["contents"][0]["text"] = (
                                        nameListReverse[i - 1][0])
                                    templateAdd["contents"][1]["text"] = (
                                        nameListReverse[i - 1][1])
                                    template["body"]["contents"][1][
                                        "contents"].append(
                                            copy.deepcopy(templateAdd))
                                    print("----nameListReverse----")
                                    print(nameListReverse[i - 1][0])
                                    print("----nameListReverse----")
                                    i = i + 1
                                line.replyFlex(template)
                            else:
                                line.replyText("尚無購買紀錄😉")
                        elif event.message == "#培訓專區":
                            if memberRole >= 2:
                                photoList = [
                                    "https://i.imgur.com/HD83R4p.png",
                                    "https://i.imgur.com/ekSGB7U.png",
                                    "https://i.imgur.com/HYbdtoZ.png",
                                ]
                                webUrlList = webUrl.training(liffID)
                                print("---webUrlList----")
                                print(webUrlList)

                                print("---webUrlList----")

                                template = copy.deepcopy(
                                    line.flexTemplate("carousel"))
                                flex = copy.deepcopy(
                                    line.flexTemplate("otherFlexUrl"))
                                i = 0
                                nameList = [
                                    "團練專區",
                                    "比賽專區",
                                    "個人成績紀錄",
                                    "比賽成績紀錄",
                                ]
                                if nameList:
                                    for key, value in enumerate(nameList):
                                        k = i % 3
                                        flex["hero"]["contents"][0][
                                            "contents"][0]["url"] = photoList[
                                                k]
                                        flex["hero"]["contents"][0][
                                            "contents"][1]["text"] = value
                                        flex["hero"]["contents"][1][
                                            "contents"][0]["action"][
                                                "uri"] = f"{webUrlList[key]}"
                                        template["contents"].append(
                                            copy.deepcopy(flex))
                                        i += 1
                                    line.replyFlex(template)
                            else:
                                line.doubleReplyMessageText(
                                    f"🙇‍♂️權限不足！！", "☎️如有疑問請致電｜0919-102-803")
                        elif event.message == "#教練課程":
                            photoList = [
                                "https://i.imgur.com/HD83R4p.png",
                                "https://i.imgur.com/ekSGB7U.png",
                                "https://i.imgur.com/HYbdtoZ.png",
                            ]
                            webUrlList = webUrl.training
                            template = copy.deepcopy(
                                line.flexTemplate("carousel"))
                            flex = copy.deepcopy(
                                line.flexTemplate("otherFlexPostback"))
                            i = 0
                            nameList = ["單人教練預約", "團體教練預約"]
                            print("----webUrlList----")
                            if nameList:
                                for key, value in enumerate(nameList):
                                    k = i % 3
                                    flex["hero"]["contents"][0]["contents"][0][
                                        "url"] = photoList[k]
                                    flex["hero"]["contents"][0]["contents"][1][
                                        "text"] = value
                                    flex["hero"]["contents"][1]["contents"][0][
                                        "action"][
                                            "data"] = f"postReserveProject:{value}"
                                    template["contents"].append(
                                        copy.deepcopy(flex))
                                    i += 1
                                line.replyFlex(template)
                            else:
                                line.doubleReplyMessageText(
                                    f"👨‍💻尚未開放", "☎️如有疑問請致電｜0919-102-803")
                        elif event.message == "#球具維修預約":
                            photoList = [
                                "https://i.imgur.com/HD83R4p.png",
                                "https://i.imgur.com/ekSGB7U.png",
                                "https://i.imgur.com/HYbdtoZ.png",
                            ]
                            webUrlList = webUrl.training
                            template = copy.deepcopy(
                                line.flexTemplate("carousel"))
                            flex = copy.deepcopy(
                                line.flexTemplate("otherFlexPostback"))
                            i = 0
                            nameList = ["維修調整預約", "握把更換預約"]
                            nameShowList = ["維修/調整", "握把更換預約"]
                            print("----webUrlList----")
                            if nameList:
                                for key, value in enumerate(nameList):
                                    k = i % 3
                                    flex["hero"]["contents"][0]["contents"][0][
                                        "url"] = photoList[k]
                                    flex["hero"]["contents"][0]["contents"][1][
                                        "text"] = nameShowList[key]
                                    flex["hero"]["contents"][1]["contents"][0][
                                        "action"][
                                            "data"] = f"postReserveProject:{value}"
                                    template["contents"].append(
                                        copy.deepcopy(flex))
                                    i += 1
                                line.replyFlex(template)
                        elif event.message.startswith("#球場預約:"):
                            if memberRole >= 2:
                                pattern = r"球場:(.*?)\n日期:(.*?)\n時間:(.*)"
                                matches = re.search(pattern, event.message)

                                if matches:
                                    place = matches.group(1)
                                    date = matches.group(2)
                                    time = matches.group(3)
                                    given_datetime = datetime.strptime(
                                        f"{date} {time}", "%Y-%m-%d %H:%M")
                                    current_datetime = (
                                        (datetime.now()) +
                                        timedelta(weeks=1)).replace(hour=0,
                                                                    minute=0,
                                                                    second=0)
                                    courtList = courtPlaceDB(company)
                                    if len(courtList) > 0:
                                        filtered_courts = [
                                            court for court in courtList
                                            if court["place"] == place
                                            and court["status"] == 0
                                        ]
                                        if len(filtered_courts) > 0:
                                            if given_datetime > current_datetime:
                                                memberList = (
                                                    member.memberDB.
                                                    dynamicTableSearch({
                                                        "userId":
                                                        event.uid,
                                                        "company":
                                                        company,
                                                    }))
                                                memberList = memberList[0]
                                                filtered_courts = filtered_courts[
                                                    0]
                                                notifyFunction = notify(
                                                    filtered_courts["notify"])
                                                if isNotify == 1:
                                                    notifyFunction.SendMessage(
                                                        f'\n姓名:{memberList["name"]}\n電話:{memberList["phone"]}\n日期:{date}\n時間:{time}'
                                                    )
                                                line.replyText(f"{place}已預約")
                                            else:
                                                given_formatted_datetime = (
                                                    given_datetime.strftime(
                                                        "%Y-%m-%d %H:%M"))
                                                current_formatted_datetime = (
                                                    current_datetime.strftime(
                                                        "%Y-%m-%d %H:%M"))
                                                line.replyText(
                                                    f"可預約時間:{given_formatted_datetime}\n預約時間:{current_formatted_datetime}\n預約僅開放一個禮拜後"
                                                )
                            else:
                                line.doubleReplyMessageText(
                                    f"🙇‍♂️權限不足！！", "☎️如有疑問請致電｜0919-102-803")

                        elif event.message == "#球場預約":
                            photoList = [
                                "https://i.imgur.com/HD83R4p.png",
                                "https://i.imgur.com/ekSGB7U.png",
                                "https://i.imgur.com/HYbdtoZ.png",
                            ]
                            courtList = courtPlaceDB(company)
                            if len(courtList) > 0:
                                webUrlstr = webUrl.courtReserve
                                nameList = [
                                    court["place"] for court in courtList
                                    if court["status"] == 0
                                ]
                                notifyList = [
                                    court["notify"] for court in courtList
                                    if court["status"] == 0
                                ]
                                urlList = [
                                    webUrlstr + quote(court["place"])
                                    for court in courtList
                                    if court["status"] == 0
                                ]
                                template = copy.deepcopy(
                                    line.flexTemplate("carousel"))
                                flex = copy.deepcopy(
                                    line.flexTemplate("otherFlexUrl"))
                                i = 0
                                if nameList:
                                    for key, value in enumerate(nameList):
                                        k = i % 3
                                        flex["hero"]["contents"][0][
                                            "contents"][0]["url"] = photoList[
                                                k]
                                        flex["hero"]["contents"][0][
                                            "contents"][1]["text"] = value
                                        flex["hero"]["contents"][1][
                                            "contents"][0]["action"][
                                                "uri"] = urlList[key]
                                        template["contents"].append(
                                            copy.deepcopy(flex))
                                        i += 1
                                    line.replyFlex(template)

                            else:
                                line.doubleReplyMessageText(
                                    f"👨‍💻尚未開放", "☎️如有疑問請致電｜0919-102-803")

                # postback
                case "postback":
                    match event.postback:
                    # 選擇小時
                        case data if data.startswith(
                            "appointment_confirm_reserve:"):
                            # isReserveFunction=reserve.isReserveDBState(event.uid)
                            # if isReserveFunction.isShortReserveDBState()==True:
                            if len(data.split(":")) > 1:
                                reserveTimeUnix = int(
                                    data.split(":")[1].strip())
                                projectName = data.split(":")

                                # print(reserveTimeUnix)
                            reserve.reserveDB.updateThreeSearchWhere(
                                "dataTime",
                                reserveTimeUnix,
                                "userId",
                                event.uid,
                                "status",
                                "0",
                                "company",
                                company,
                            )
                            if reserve.isReserveDBState(event.uid,
                                                        company) == True:
                                memberSearchData = member.dbSearch(
                                    event.uid, company)
                                template = copy.deepcopy(
                                    line.flexTemplate(
                                        "appointment confirmation"))
                                template["body"]["contents"][0]["contents"][0][
                                    "contents"][1]["text"] = memberSearchData[
                                        "name"]
                                template["body"]["contents"][0]["contents"][2][
                                    "contents"][1]["text"] = memberSearchData[
                                        "phone"]

                                # timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(isReserveFunction.shortDBSearch()[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")
                                timeFormatYYYYMMDDhhmm = (
                                    datetime.fromtimestamp(
                                        reserve.reserveDB.dynamicTableSearch({
                                            "userId":
                                            event.uid,
                                            "status":
                                            "0",
                                            "company":
                                            company,
                                        })[0]["dataTime"],
                                        TZ,
                                    )).strftime("%Y年%m月%d日 %H:%M")

                                print(timeFormatYYYYMMDDhhmm)
                                # template['body']['contents'][2]['contents'][4]['contents'][1]['text']=isReserveFunction.shortDBSearch()[0]['project']
                                reserveProjectName = (
                                    reserve.reserveDB.dynamicTableSearch({
                                        "userId":
                                        event.uid,
                                        "status":
                                        "0",
                                        "company":
                                        company,
                                    })[0]["project"])
                                template["body"]["contents"][0]["contents"][4][
                                    "contents"][1]["text"] = reserveProjectName
                                template["body"]["contents"][1]["contents"][1][
                                    "action"][
                                        "data"] = f"ConfirmReservation:{projectName}"

                                template["body"]["contents"][0]["contents"][6][
                                    "contents"][1][
                                        "text"] = timeFormatYYYYMMDDhhmm
                                line.replyFlex(template)

                                # template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
                                # template['contents'][0]['header']['contents'][0]['text']=dateFormatYYYYMMDD
                                # template['contents'][0]['body']['contents'] = []
                        # 預約單確認專案
                        case data if data.startswith("ConfirmReservation:"):
                            if memberRole >= 1:
                                reserveCount = configs.appointment.reserveCount
                                # isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
                                NOTIFYTOKEN = configs.appointment.NOTIFYTOKEN
                                # historySearchStatusUserId=isReserveFunction.historyDBSearchStatusUserId()
                                historySearchStatusUserId = (
                                    reserve.reserveDB.dynamicTableSearch({
                                        "userid":
                                        event.uid,
                                        "status":
                                        "1",
                                        "company":
                                        company,
                                    }))
                                getReserveTimeList = [
                                    item["dataTime"]
                                    for item in historySearchStatusUserId
                                ]
                                nowTime = getDatetime()
                                nowTimeUinx = int(nowTime.timestamp())
                                count = len({
                                    x
                                    for x in getReserveTimeList
                                    if x is not None and x > int(nowTimeUinx)
                                })
                                result = reserve.reserveDB.execute_query(
                                    f"SELECT * FROM reserve WHERE userId = '{event.uid}' AND status='0' AND dataTime IS NOT NULL AND project IS NOT NULL AND company = '{company}'"
                                )
                                if result:
                                    if count < reserveCount:
                                        # userReservedate=isReserveFunction.historyDBAdd()
                                        userReservedate = reserve.reserveDB.rdbmsSearch(
                                            company, event.uid)[0]
                                        notifyFunction = notify(NOTIFYTOKEN)
                                        print((userReservedate["dataTime"]))
                                        print(type(userReservedate))
                                        print(
                                            '-datetime.fromtimestamp(userReservedate["dataTime"])----'
                                        )
                                        # print((userReservedate))
                                        # print(reserve.reser)
                                        lnumber = reserve.reserveDB.dynamicTableSearch(
                                            {
                                                "project":
                                                "模擬器預約",
                                                "status":
                                                "1",
                                                "company":
                                                company,
                                                "dataTime":
                                                userReservedate["dataTime"],
                                            })
                                        lnumber = len(lnumber)

                                        if userReservedate[
                                                "project"] == "模擬器預約":
                                            lnumber = (reserve.reserveDB.
                                                       dynamicTableSearch({
                                                           "project":
                                                           "模擬器預約",
                                                           "status":
                                                           "1",
                                                           "company":
                                                           company,
                                                           "dataTime":
                                                           userReservedate[
                                                               "dataTime"],
                                                       }))
                                            tnumber = (reserve.reserveDB.
                                                       dynamicTableSearch({
                                                           "project":
                                                           "單人教練預約",
                                                           "status":
                                                           "1",
                                                           "company":
                                                           company,
                                                           "dataTime":
                                                           userReservedate[
                                                               "dataTime"],
                                                       }))
                                            onumber = (reserve.reserveDB.
                                                       dynamicTableSearch({
                                                           "project":
                                                           "團體教練預約",
                                                           "status":
                                                           "1",
                                                           "company":
                                                           company,
                                                           "dataTime":
                                                           userReservedate[
                                                               "dataTime"],
                                                       }))
                                            onumber = len(onumber)
                                            tnumber = len(tnumber)

                                            lnumber = len(lnumber)
                                            sumNumber = (onumber +
                                                         (tnumber * 2) +
                                                         lnumber)
                                            if sumNumber >= 2:
                                                line.replyText(
                                                    f"此確認無效，目前時段預約已滿，請重新預約")
                                            else:
                                                notifyTime = (
                                                    datetime.fromtimestamp(
                                                        userReservedate[
                                                            "dataTime"])
                                                ).strftime("%Y年%m月%d日 %H:%M")
                                                if isNotify == 1:
                                                    notifyFunction.SendMessage(
                                                        f'\n姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}\n點擊預約時間\n{userReservedate["auto_updae_time"]}\n'
                                                    )
                                                line.replyText(
                                                    f'姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}'
                                                )
                                                reserve.reserveDB.updateThreeSearchWhere(
                                                    "status",
                                                    "1",
                                                    "userId",
                                                    event.uid,
                                                    "status",
                                                    "0",
                                                    "company",
                                                    company,
                                                )
                                                reserve.reserveDB.Insert(
                                                    (
                                                        "userId",
                                                        "company",
                                                    ),
                                                    (
                                                        event.uid,
                                                        company,
                                                    ),
                                                )
                                        else:
                                            notifyTime = (
                                                datetime.fromtimestamp(
                                                    userReservedate["dataTime"]
                                                )).strftime("%Y年%m月%d日 %H:%M")
                                            if isNotify == 1:
                                                notifyFunction.SendMessage(
                                                    f'\n姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}\n點擊預約時間\n{userReservedate["auto_updae_time"]}\n'
                                                )
                                            line.replyText(
                                                f'姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}'
                                            )
                                            reserve.reserveDB.updateThreeSearchWhere(
                                                "status",
                                                "1",
                                                "userId",
                                                event.uid,
                                                "status",
                                                "0",
                                                "company",
                                                company,
                                            )
                                            reserve.reserveDB.Insert(
                                                (
                                                    "userId",
                                                    "company",
                                                ),
                                                (
                                                    event.uid,
                                                    company,
                                                ),
                                            )
                                    else:
                                        line.replyText(
                                            "系統自動判斷目前您已有預約時段,請點擊會員查詢確認時段是否預約,若無預約煩請致電～"
                                        )
                                    # isReserveFunction.historyDBUpdate(memberDate)

                                    # isReserveFunction.shortDBDelete()
                                    # print("確認預約")
                                else:
                                    line.replyText("目前系統尚無預約資料，請重新預約！！！")
                            else:
                                line.doubleReplyMessageText(
                                    f"🙇‍♂️權限不足！！", "☎️如有疑問請致電｜0919-102-803")
                        case "CancelReservation":
                            line.doubleReplyMessageText(
                                f"取消請聯絡我們", "☎️請致電｜0919-102-803")

                            # # isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
                            # try:
                            #     if (reserve.reserveDB.TableTwoSearch('userId',event.uid,'status','0')):
                            #         reserve.reserveDB.updateTwoSearchWhere("dataTime",None,"userId","Ue9a11eeae110fc8a29da9d00d3ebe5cb","status","0")
                            #         reserve.reserveDB.updateTwoSearchWhere("project",None,"userId","Ue9a11eeae110fc8a29da9d00d3ebe5cb","status","0")
                            # # if isReserveFunction.shortDBcontains():
                            # # 	isReserveFunction.shortDBDelete()
                            # # 	reserve.add(event.uid)
                            # except:print()
                            # pass
                        case "updateuserId":
                            memberDB = MYSQLDB("member")

                            memberDB.updateTwoSearchWhere(
                                "name", None, "company", company, "userId",
                                event.uid)
                            # member.update(event.uid,{'name':None})
                            line.replyText("請輸入使用者暱稱")
                        case "updateUserPhone":
                            memberDB = MYSQLDB("member")

                            # memberDB.updateTwoSearchWhere('phone',None,'company',company,'userId',event.uid)
                            line.replyText("若要更動電話號碼請聯繫店家")
                        case data if data.startswith("ReserveProject"):
                            print(data)
                        case "firstviewTutoril":
                            template = functionTemplate.videoTemplate(
                                "https://imgur.com/XVmZmIE",
                                "https://img.ttshow.tw/images/media/frontcover/2020/08/06/6.jpg",
                            )
                            line.replyMessage(template)
                        case "registerNow":
                            user_status = member.isMember(event.uid, company)
                            if user_status == "nouser":
                                member.memberDB.Insert(("userId", "company"),
                                                       (event.uid, company))
                                line.replyText("請輸入使用者名稱")
                            elif user_status == "name":
                                line.replyText("請先輸入使用者名稱")
                            elif user_status == "phone":
                                line.replyText("請先輸入電話號碼")
                        case "register":
                            memberDB = MYSQLDB("member")
                            if not memberDB.TableOneSearchAddField(
                                    "userId", "userId", event.uid, "company",
                                    company):
                                memberDB.insertMember(event.uid, company)
                                template = line.flexTemplate("memberRegister")

                                line.doubleMessageTextReplyFlex(
                                    "請於下方小鍵盤，輸入會員電話",
                                    template,
                                    "使用者電話輸入",
                                )

                            else:
                                user_status = member.isMember(
                                    event.uid, company)
                                if user_status == "name":
                                    line.replyText("請先輸入使用者名稱")
                                elif user_status == "phone":
                                    line.replyText("請先輸入電話號碼")
                                elif user_status == "sex":
                                    line.replyText(
                                        "請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女")
                        case data if data.startswith("personalData:"):
                            personalData = (data.split(":"))[1]
                            isData = False
                            if personalData == "球桿數據":
                                clubDataDB = MYSQLDB("clubData")
                                clubDataSearch = clubDataDB.clubTableSearch(
                                    "clubData.ballHead,clubData.clubHead,clubData.shaftWeightStiffness,clubData.gripWeight,clubData.swingWeight,clubData.clubfaceAngle,clubData.lieAngle,clubData.remark",
                                    "clubData",
                                    event.uid,
                                )
                                if clubDataSearch:
                                    isData = True
                                template = copy.deepcopy(
                                    line.flexTemplate("carousel"))
                                templateAdd = copy.deepcopy(
                                    line.flexTemplate("clubInformation"))
                                # 球桿名稱
                                for index, value in enumerate(clubDataSearch):
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][1][
                                            "contents"][0]["contents"][1][
                                                "text"] = value["ballHead"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][1][
                                            "contents"][1]["contents"][1][
                                                "text"] = value["clubHead"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][2][
                                            "contents"][0]["contents"][1][
                                                "text"] = value[
                                                    "shaftWeightStiffness"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][2][
                                            "contents"][1]["contents"][1][
                                                "text"] = value["gripWeight"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][3][
                                            "contents"][0]["contents"][1][
                                                "text"] = value["swingWeight"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][3][
                                            "contents"][1]["contents"][1][
                                                "text"] = value[
                                                    "clubfaceAngle"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][4][
                                            "contents"][0]["contents"][1][
                                                "text"] = value["lieAngle"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][5][
                                            "contents"][0]["contents"][1][
                                                "text"] = value["remark"]
                                    template["contents"].append(
                                        copy.deepcopy(templateAdd))
                            if personalData == "揮桿數據":
                                playclubDB = MYSQLDB("playclubData")
                                playclubSearch = playclubDB.clubTableSearch(
                                    "playclubData.name,playclubData.speed,playclubData.averageToTalDistance,playclubData.averageFlightDistance,playclubData.takeoffAngle,playclubData.ballSpeed,playclubData.remark",
                                    "playclubData",
                                    event.uid,
                                )
                                if playclubSearch:
                                    isData = True
                                template = copy.deepcopy(
                                    line.flexTemplate("carousel"))
                                templateAdd = copy.deepcopy(
                                    line.flexTemplate("playclubInformation"))
                                for index, value in enumerate(playclubSearch):
                                    templateAdd["body"]["contents"][0][
                                        "contents"][0]["text"] = value["name"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][1][
                                            "contents"][0]["contents"][1][
                                                "text"] = value["speed"]
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][1][
                                            "contents"][1]["contents"][1][
                                                "text"] = f"{value['averageToTalDistance']}y"
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][2][
                                            "contents"][0]["contents"][1][
                                                "text"] = f"{value['averageFlightDistance']}y"
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][2][
                                            "contents"][1]["contents"][1][
                                                "text"] = f"{value['takeoffAngle']}°"
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][3][
                                            "contents"][0]["contents"][1][
                                                "text"] = f"{value['ballSpeed']}"
                                    templateAdd["body"]["contents"][0][
                                        "contents"][1]["contents"][4][
                                            "contents"][0]["contents"][1][
                                                "text"] = value["remark"]
                                    template["contents"].append(
                                        copy.deepcopy(templateAdd))
                            print(f"isData::{isData}")
                            if isData:
                                line.replyFlex(template)
                            else:
                                line.replyText(
                                    f"Sorry🙇‍♂️\n{personalData}尚未有資料")
                        case data if data.startswith(
                            "postReserveProject:") and (user_status == True):
                            if memberRole >= 1:
                                reserveProjectName = (data.split(":"))[1]
                                # reserve.reserveDB.updateThreeSearchWhere('project',reserveProjectName,'userId',event.uid,'status','0',"company",company)
                                reserve.reserveDB.updateThreeSearchWhere(
                                    "dataTime",
                                    None,
                                    "userId",
                                    event.uid,
                                    "status",
                                    "0",
                                    "company",
                                    company,
                                )
                                reserve.reserveDB.updateThreeSearchWhere(
                                    "project",
                                    None,
                                    "userId",
                                    event.uid,
                                    "status",
                                    "0",
                                    "company",
                                    company,
                                )
                                if reserveProjectName in projectNameList:
                                    projectNameIdx = projectNameList.index(
                                        reserveProjectName)
                                    projectName = projectNameList[
                                        projectNameIdx]
                                    projectsDay = projectsDayList[
                                        projectNameIdx]
                                    projectsActive = projectsActiveList[
                                        projectNameIdx]
                                    projectsoffset = projectsoffsetList[
                                        projectNameIdx]
                                    projectsinterval = projectsintervalList[
                                        projectNameIdx]
                                    current_datetime = datetime.now()
                                    current = current_datetime.replace(
                                        hour=0,
                                        minute=0,
                                        second=0,
                                        microsecond=0)
                                    nowtimestamp = current.timestamp()
                                    todayTimestamp = nowtimestamp + projectsDay
                                    projectNameIdx = projectNameList.index(
                                        reserveProjectName)
                                    nextTimestamp = todayTimestamp + projectsoffset
                                    dayList = []
                                    ranges = [(start, start + 86400 - 1)
                                              for start in publicBlackTimeList]

                                    while todayTimestamp < nextTimestamp:
                                        if not any(
                                                start <= todayTimestamp <= end
                                                for start, end in ranges):
                                            dayList.append(todayTimestamp)
                                        todayTimestamp += 86400
                                    template = copy.deepcopy(
                                        line.flexTemplate("appointmentNow"))
                                    template_item = copy.deepcopy(
                                        template["contents"][0]["body"]
                                        ["contents"])
                                    template_page_item = copy.deepcopy(
                                        template["contents"][0])
                                    template["contents"][0]["body"][
                                        "contents"] = []
                                    datapage = configs.appointment.datapage
                                    blackweekday = []
                                    weekday_chinese = [
                                        "一",
                                        "二",
                                        "三",
                                        "四",
                                        "五",
                                        "六",
                                        "日",
                                    ]
                                    template["contents"][0]["header"][
                                        "contents"][0][
                                            "text"] = f"{reserveProjectName}-請選擇日期"
                                    for i in range(7):
                                        if (projectsActive[i][0][0] == "00:00"
                                                and projectsActive[i][0][1]
                                                == "00:00"):
                                            blackweekday.append(
                                                weekday_chinese[i])
                                    idex = 1
                                    for idx, ts in enumerate(dayList):
                                        dt = datetime.fromtimestamp(ts)
                                        year = dt.year
                                        month = dt.month
                                        day = dt.day
                                        if (not weekday_chinese[dt.weekday()]
                                                in blackweekday):
                                            typePage = ((idex / datapage) +
                                                        1 if idex %
                                                        datapage > 0 else
                                                        (idex / datapage))
                                            typePage = int(typePage)
                                            if len(template["contents"]
                                                   ) < typePage:
                                                template["contents"].append(
                                                    copy.deepcopy(
                                                        template["contents"]
                                                        [0]))
                                                template["contents"][
                                                    typePage - 1]["body"][
                                                        "contents"] = []
                                            template_item[0]["contents"][0][
                                                "text"] = f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})"
                                            template_item[0]["contents"][1][
                                                "action"][
                                                    "data"] = f"appointment_choose_time:{int(ts)}:project:{projectName}"
                                            template["contents"][
                                                typePage -
                                                1]["body"]["contents"].append(
                                                    copy.deepcopy(
                                                        template_item[0]))
                                            template["contents"][
                                                typePage -
                                                1]["body"]["contents"].append(
                                                    copy.deepcopy(
                                                        template_item[1]))
                                            idex += 1
                                            # print(int(ts))
                                        else:
                                            print(
                                                weekday_chinese[dt.weekday()])
                                    line.replyFlex(template)
                                else:
                                    line.doubleReplyMessageText(
                                        f"👨‍💻{reserveProjectName}尚未開放",
                                        "☎️如有疑問請致電｜0919-102-803",
                                    )
                            else:
                                line.doubleReplyMessageText(
                                    f"🙇‍♂️權限不足！！", "☎️如有疑問請致電｜0919-102-803")
                        case data if data.startswith(
                            "appointment_choose_time:") and "project:" in data:
                            parts = data.split(":")
                            timeUnix = parts[1]
                            projectName = parts[3]
                            reserve.reserveDB.updateThreeSearchWhere(
                                "project",
                                projectName,
                                "userId",
                                event.uid,
                                "status",
                                "0",
                                "company",
                                company,
                            )

                            if (reserve.isReserveDBState(
                                    event.uid, company) == "noDataTime"):
                                projectNameIdx = projectNameList.index(
                                    projectName)
                                # 單人預約
                                projectName = projectNameList[projectNameIdx]
                                projectsDay = projectsDayList[projectNameIdx]
                                projectsActive = projectsActiveList[
                                    projectNameIdx]
                                projectsoffset = projectsoffsetList[
                                    projectNameIdx]
                                projectsinterval = projectsintervalList[
                                    projectNameIdx]
                                # 群組數量
                                projectSumberOfAppointments = (
                                    projectSnumberOfAppointmentsList[
                                        projectNameIdx])
                                # print('--------projectGroupReserveStatusList---------')
                                # print(projectGroupReserveStatusList)
                                projectGroupReserveStatus = (
                                    projectGroupReserveStatusList[
                                        projectNameIdx])

                                ALLprojectList = configsSearchDBProjectList[
                                    1:-1].split(",")

                                AllProjectIndex = ALLprojectList.index(
                                    projectName)
                                filterTimeUnix = []
                                element_count = {}
                                # print('*************test****************************')
                                # print(projectName)
                                # print(projectsDay)
                                # print(projectsActive)
                                # print(projectsoffset)
                                # print(projectsinterval)
                                # print(projectSumberOfAppointments)

                                # print('*************test****************************')

                                # if projectsblockTimeList[projectNameIdx]:

                                projectsblockTime = projectsblockTimeList[
                                    AllProjectIndex]

                                def convert_to_timestamps(active_list):
                                    converted_active = []
                                    for time_range in active_list:
                                        converted_range = []
                                        for time_point in time_range:
                                            if time_point[0] is not None:
                                                start_time_str, end_time_str = (
                                                    time_point)
                                                start_time = (int(
                                                    start_time_str.split(":")
                                                    [0]) * 60 * 60 + int(
                                                        start_time_str.split(
                                                            ":")[1]) * 60)
                                                end_time = (int(
                                                    end_time_str.split(":")[0]
                                                ) * 60 * 60 + int(
                                                    end_time_str.split(":")[1])
                                                            * 60)
                                                converted_range.append(
                                                    [
                                                        int(start_time),
                                                        int(end_time)
                                                    ] if time_range[0] is
                                                    not None else [None, None])
                                            else:
                                                converted_range.append(
                                                    [None, None])
                                        converted_active.append(
                                            converted_range)
                                    return converted_active

                                weekday_chinese = [
                                    "一",
                                    "二",
                                    "三",
                                    "四",
                                    "五",
                                    "六",
                                    "日",
                                ]
                                dt = datetime.fromtimestamp(int(timeUnix))
                                print(
                                    f"{dt.year}/{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})"
                                )
                                unixActive = convert_to_timestamps(
                                    projectsActive)

                                unixTimeActive = []
                                print(timeUnix)
                                # 8 * 60 * 60
                                current_time = datetime.now()
                                current_date = current_time.date()
                                currentUnixTime = (
                                    int(current_time.timestamp()) +
                                    projectsinterval)
                                midnight = datetime.combine(
                                    current_date, datetime.min.time())
                                # midnight_utc = midnight.replace(tzinfo=timezone.utc)
                                todayhourminZeroUnixTimestamp = str(
                                    int(midnight.timestamp()))
                                print(
                                    f"one:{currentUnixTime-projectsinterval}")
                                print(f"currentUnixTime:{currentUnixTime}")
                                print(f"projectsinterval:{projectsinterval}")

                                if timeUnix == todayhourminZeroUnixTimestamp:
                                    if (unixActive[dt.weekday()]
                                        )[1][0] == None:
                                        while (
                                                unixActive[dt.weekday()][0][0]
                                        ) < (unixActive[dt.weekday()][0][1]):
                                            if (unixActive[dt.weekday()][0][0]
                                                ) + (int(dt.timestamp())
                                                     ) > currentUnixTime:
                                                unixTimeActive.append(
                                                    (unixActive[dt.weekday()]
                                                     [0][0]) +
                                                    (int(dt.timestamp())))
                                            unixActive[dt.weekday(
                                            )][0][0] += projectsinterval
                                            # timestamp = datetime.strptime(date_string, date_format).timestamp()
                                            print((unixActive[dt.weekday()][0]
                                                   [0]) +
                                                  (int(dt.timestamp())))
                                    else:
                                        while (
                                                unixActive[dt.weekday()][0][0]
                                        ) < (unixActive[dt.weekday()][0][1]):
                                            if (unixActive[dt.weekday()][0][0]
                                                ) + (int(dt.timestamp())
                                                     ) > currentUnixTime:
                                                unixTimeActive.append(
                                                    (unixActive[dt.weekday()]
                                                     [0][0]) +
                                                    (int(dt.timestamp())))
                                            unixActive[dt.weekday(
                                            )][0][0] += projectsinterval
                                        while (
                                                unixActive[dt.weekday()][1][0]
                                        ) < (unixActive[dt.weekday()][1][1]):
                                            if (unixActive[dt.weekday()][1][0]
                                                ) + (int(dt.timestamp())
                                                     ) > currentUnixTime:
                                                unixTimeActive.append(
                                                    (unixActive[dt.weekday()]
                                                     [1][0]) +
                                                    (int(dt.timestamp())))
                                            unixActive[dt.weekday(
                                            )][1][0] += projectsinterval
                                else:
                                    if (unixActive[dt.weekday()]
                                        )[1][0] == None:
                                        while (
                                                unixActive[dt.weekday()][0][0]
                                        ) < (unixActive[dt.weekday()][0][1]):
                                            unixTimeActive.append(
                                                (unixActive[dt.weekday()][0][0]
                                                 ) + (int(dt.timestamp())))
                                            unixActive[dt.weekday(
                                            )][0][0] += projectsinterval
                                        # timestamp = datetime.strptime(date_string, date_format).timestamp()
                                    else:
                                        while (
                                                unixActive[dt.weekday()][0][0]
                                        ) < (unixActive[dt.weekday()][0][1]):
                                            unixTimeActive.append(
                                                (unixActive[dt.weekday()][0][0]
                                                 ) + (int(dt.timestamp())))
                                            unixActive[dt.weekday(
                                            )][0][0] += projectsinterval
                                        while (
                                                unixActive[dt.weekday()][1][0]
                                        ) < (unixActive[dt.weekday()][1][1]):
                                            unixTimeActive.append(
                                                (unixActive[dt.weekday()][1][0]
                                                 ) + (int(dt.timestamp())))
                                            unixActive[dt.weekday(
                                            )][1][0] += projectsinterval
                                uniqueUnixTimeActive = list(
                                    set(unixTimeActive))
                                sortedUnixTimeActive = sorted(
                                    uniqueUnixTimeActive)

                                filterBlackTimeUnix = [
                                    timestamp
                                    for timestamp in sortedUnixTimeActive
                                    if not any(
                                        range_item[0] <= timestamp <=
                                        range_item[1]
                                        for range_item in projectsblockTime)
                                ]
                                if filterBlackTimeUnix:
                                    isMaxCount = False

                                    if projectGroupReserveStatus == "own":
                                        historydate = (reserve.reserveDB.
                                                       dynamicTableSearch({
                                                           "project":
                                                           projectName,
                                                           "status":
                                                           "1",
                                                           "company":
                                                           company,
                                                       }))
                                        historyDataTime = [
                                            item["dataTime"]
                                            for item in historydate
                                        ]
                                        # historyDataTimeFormatYYYYMMDD=(datetime.fromtimestamp(int(historyDataTime),TZ)).strftime('20%y年%m月%d日')
                                        # if
                                        # print('-----x-x--xx--x-x')
                                        # print(historyDataTime)
                                        for x in historyDataTime:
                                            element_count[x] = (
                                                element_count.get(x, 0) + 1)
                                        print(element_count)
                                        filterTimeUnix = [
                                            x for x in filterBlackTimeUnix
                                            if element_count.get(x, 0) <
                                            projectSumberOfAppointments
                                        ]

                                    if projectGroupReserveStatus == "groupReserve":
                                        groupProjectList = []
                                        # numberAppointments=''
                                        projectMaxAppointments = 999
                                        for (
                                                group,
                                                details,
                                        ) in projectGroupNameList.items():
                                            if (f"project{AllProjectIndex+1}"
                                                    in details["projectList"]):
                                                for item in details[
                                                        "projectList"]:
                                                    groupProjectList.append(
                                                        item)
                                                # print(f"project{projectNameIdx+1} is in group {group}")
                                                numberAppointments = details[
                                                    "numberAppointments"]
                                                projectMaxAppointments = details.get(
                                                    "maxNumberOfAppointments",
                                                    999)
                                        # print(f'groupProjectList:{groupProjectList}')
                                        # print('projectDetails------')
                                        # print(projectDetails)
                                        # print(projectDetails[groupProjectList[0]])

                                        element_count = {
                                        }  # 确保 element_count 已初始化
                                        groupProjectName = [
                                        ]  # 初始化 groupProjectName 列表

                                        # 遍历 groupProjectList 来构建 groupProjectName 列表
                                        for projectNumber in groupProjectList:
                                            groupProjectName.append({
                                                projectDetails[projectNumber]["name"]:
                                                projectDetails[projectNumber]
                                                ["numberOfAppointments"]
                                            })
                                        print(groupProjectName)

                                        # 遍历 groupProjectName 列表中的每个项目
                                        for item in groupProjectName:
                                            for projectOneName, number in item.items(
                                            ):
                                                # 进行数据库查询
                                                searchGroupHistoryUnixTime = reserve.reserveDB.dynamicTableSearch(
                                                    {
                                                        "project":
                                                        projectOneName,
                                                        "status": "1",
                                                        "company": company,
                                                    })

                                                if searchGroupHistoryUnixTime:
                                                    # 确保 searchGroupHistoryUnixTime 是一个列表
                                                    if isinstance(
                                                            searchGroupHistoryUnixTime,
                                                            str):
                                                        searchGroupHistoryUnixTime = json.loads(
                                                            searchGroupHistoryUnixTime
                                                        )

                                                    for data in searchGroupHistoryUnixTime:
                                                        # 确保 data 是字典
                                                        if isinstance(
                                                                data, str):
                                                            data = json.loads(
                                                                data)

                                                        found = False
                                                        for entryTime, entryNumber in element_count.items(
                                                        ):
                                                            if data["dataTime"] == entryTime:
                                                                element_count[data[
                                                                    "dataTime"]] += number
                                                                found = True
                                                                break

                                                        if not found:
                                                            element_count[data[
                                                                "dataTime"]] = number

                                        # 过滤时间戳
                                        filterTimeUnix = [
                                            x for x in filterBlackTimeUnix
                                            if element_count.get(x, 0) <=
                                            int(numberAppointments) -
                                            int(projectSumberOfAppointments)
                                        ]
                                        print("----filterTimeUnix----")
                                        isMaxCount = False
                                        # 检查是否达到最大预约数
                                        if data and "dataTime" in data:  # 确保 data 存在且包含 'dataTime'
                                            isMaxCount = element_count[
                                                data["dataTime"]] < int(
                                                    projectMaxAppointments)

                                    if filterTimeUnix:
                                        # filterTimeUnix = [x for x in filterBlackTimeUnix if x not in historyDataTime]
                                        filterTimeYYYYDDList = []
                                        # print(f'filterTimeUnix:{filterTimeUnix}')
                                        dateFormatYYYYMMDD = (
                                            datetime.fromtimestamp(
                                                int(filterTimeUnix[0]),
                                                TZ)).strftime("20%y年%m月%d日")

                                        for filterTimeYYYYDD in filterTimeUnix:
                                            dt = datetime.fromtimestamp(
                                                filterTimeYYYYDD,
                                                TZ).strftime("%H:%M")
                                            filterTimeYYYYDDList.append(dt)

                                        # if len(filterTimeYYYYDDList)<1:
                                        # line.replyText(f'({})當日預約已滿請上方從選擇日期')
                                        # else:
                                        template = copy.deepcopy(
                                            line.flexTemplate(
                                                "appointmentNow"))
                                        template_item = copy.deepcopy(
                                            template["contents"][0]["body"]
                                            ["contents"])
                                        template["contents"][0]["header"][
                                            "contents"][0][
                                                "text"] = dateFormatYYYYMMDD
                                        template["contents"][0]["body"][
                                            "contents"] = []
                                        timepage = configs.appointment.timepage
                                        for idx, ts in enumerate(
                                                filterTimeYYYYDDList):
                                            idx += 1
                                            typePage = ((idx / timepage) +
                                                        1 if idx %
                                                        timepage > 0 else
                                                        (idx / timepage))
                                            typePage = int(typePage)
                                            if len(template["contents"]
                                                   ) < typePage:
                                                template["contents"].append(
                                                    copy.deepcopy(
                                                        template["contents"]
                                                        [0]))
                                                template["contents"][
                                                    typePage - 1]["body"][
                                                        "contents"] = []
                                            template_item[0]["contents"][0][
                                                "text"] = ts
                                            template_item[0]["contents"][1][
                                                "action"][
                                                    "data"] = f"appointment_confirm_reserve:{filterTimeUnix[idx-1]}:projectName:{projectName}"
                                            template["contents"][
                                                typePage -
                                                1]["body"]["contents"].append(
                                                    copy.deepcopy(
                                                        template_item[0]))
                                            template["contents"][
                                                typePage -
                                                1]["body"]["contents"].append(
                                                    copy.deepcopy(
                                                        template_item[1]))
                                        # print(template)
                                        line.replyFlex(template)
                                    else:
                                        line.replyText("預約時間已滿\n請改期預約!!!")

                                else:
                                    line.replyText(
                                        f"👷項目:{projectName}\n⌚時間：{dt.year}/{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})\n✉️提醒訊息:預約時段已滿"
                                    )
                        case data if data.startswith("buyBallRoll:") and (
                            user_status == True):
                            if memberRole >= 1:
                                reserve.reserveDB.updateThreeSearchWhere(
                                    "dataTime",
                                    None,
                                    "userId",
                                    event.uid,
                                    "status",
                                    "0",
                                    "company",
                                    company,
                                )
                                reserve.reserveDB.updateThreeSearchWhere(
                                    "project",
                                    None,
                                    "userId",
                                    event.uid,
                                    "status",
                                    "0",
                                    "company",
                                    company,
                                )
                                urlList = [
                                    "https://i.imgur.com/HD83R4p.png",
                                    "https://i.imgur.com/ekSGB7U.png",
                                    "https://i.imgur.com/HYbdtoZ.png",
                                ]
                                template = copy.deepcopy(
                                    line.flexTemplate("carousel"))
                                ballRoll = copy.deepcopy(
                                    line.flexTemplate("ballRoll"))
                                i = 0
                                if searchBallRollfillterTrue:
                                    for key, value in searchBallRollfillterTrue.items(
                                    ):
                                        k = i % 3
                                        ballRoll["hero"]["contents"][0][
                                            "contents"][0]["url"] = urlList[k]
                                        ballRoll["hero"]["contents"][0][
                                            "contents"][1]["text"] = value[
                                                "courtName"]
                                        ballRoll["hero"]["contents"][1][
                                            "contents"][0]["action"][
                                                "data"] = f"chooseBallRoll:{value['courtName']}"

                                        template["contents"].append(
                                            copy.deepcopy(ballRoll))
                                        i += 1
                                    line.replyFlex(template)
                                else:
                                    line.doubleReplyMessageText(
                                        f"👨‍💻球卷尚未開放",
                                        "☎️如有疑問請致電｜0919-102-803",
                                    )
                            else:
                                line.doubleReplyMessageText(
                                    f"🙇‍♂️權限不足！！", "☎️如有疑問請致電｜0919-102-803")
                        case data if data.startswith("chooseBallRoll:"):
                            currentDate = datetime.now()
                            first_day_of_month = currentDate.replace(
                                day=1,
                                hour=0,
                                minute=0,
                                second=0,
                                microsecond=0)
                            unix_timestamp = int(
                                first_day_of_month.timestamp())

                            parts = data.split(":")
                            ballRollName = parts[1] if len(parts) > 1 else None
                            for key, value in searchBallRollfillterTrue.items(
                            ):
                                if value.get("courtName") == ballRollName:
                                    monthNumber = value.get("monthNumber", {})
                            filtered_month_number = {
                                key: value
                                for key, value in monthNumber.items()
                                if int(key) >= unix_timestamp
                            }

                            # 新增只顯示球卷數量大於0的月份
                            historySearchStatusUserId = (
                                reserve.reserveDB.dynamicTableSearch({
                                    "userid":
                                    event.uid,
                                    "status":
                                    "ballRoll",
                                    "company":
                                    company,
                                }))

                            getReserveTimeList = [
                                item["dataTime"]
                                for item in historySearchStatusUserId
                            ]
                            nowTime = getDatetime()
                            nowTimeUinx = int(nowTime.timestamp())
                            ballRollDataList = []
                            ballRollList = []
                            for key, value in searchBallRollfillterTrue.items(
                            ):
                                ballRollDataList.append(value["courtName"])
                                if value["courtName"] == ballRollName:
                                    ballRollList.append(value)
                            ballRollList = ballRollList[0]
                            if not isinstance(ballRollList, dict):
                                try:
                                    ballRollList = dict(ballRollList)
                                except (TypeError, ValueError):
                                    print("無法轉換為字典")

                            filtered_month_number = {
                                key: value
                                for key, value in monthNumber.items()
                                if int(ballRollList["monthNumber"][str(int(
                                    key))]) > 0 and int(key) >= unix_timestamp
                            }

                            # filtered_month_number = {key: value for key, value in filtered_month_number.items() if value > 0}
                            yearMonthDict = [
                                datetime.utcfromtimestamp(
                                    (int(timestamp) + 86400)).strftime("%Y/%m")
                                for timestamp in filtered_month_number.keys()
                            ]
                            yearMonthValueDict = []
                            underButtonTextList = []
                            underButtonData = []
                            for key, value in filtered_month_number.items():
                                yearMonthValueDict.append(value)
                            for i in range(ballRollNumber):
                                underButtonTextList.append(yearMonthDict[i])
                                underButtonData.append(
                                    f"ballRollunixTime:{yearMonthDict[i]}:ballRollnumber:{yearMonthValueDict[i]}:ballRollName:{ballRollName}"
                                )
                            print("-----underButtonTextList----")
                            print(underButtonTextList)
                            print(type(underButtonData))
                            template = functionTemplate.postUnderTemplate(
                                underButtonTextList,
                                underButtonData,
                                f"目前已選擇{ballRollName}\n請於下方選擇月份",
                            )
                            line.replyMessage(template)

                            # reserve.reserveDB.updateThreeSearchWhere("project",ballRollName,"userId",event.uid,"status","0","company",company)
                        case data if data.startswith("ballRollunixTime:") and (
                            "ballRollnumber:" in data) and ("ballRollName:"
                                                            in data):

                            parts = data.split(":")
                            unixTime = parts[1]
                            number = parts[3]
                            name = parts[5]
                            input_date = datetime.strptime(unixTime, "%Y/%m")
                            first_day_of_month = input_date.replace(day=1,
                                                                    hour=0,
                                                                    minute=0,
                                                                    second=0)
                            unix_timestamp = int(
                                first_day_of_month.timestamp())

                            underButtonTextList = ["1張", "2張", "3張", "4張"]
                            underButtonData = [
                                f"ballRollunixTime:{unixTime}:number:{1}:ballRollName:{name}",
                                f"ballRollunixTime:{unixTime}:number:{2}:ballRollName:{name}",
                                f"ballRollunixTime:{unixTime}:number:{3}:ballRollName:{name}",
                                f"ballRollunixTime:{unixTime}:number:{4}:ballRollName:{name}",
                            ]
                            template = functionTemplate.postUnderTemplate(
                                underButtonTextList, underButtonData, f"請選擇數量")

                            print(template)

                            ballRollDataList = []
                            ballRollList = []
                            for key, value in searchBallRollfillterTrue.items(
                            ):
                                ballRollDataList.append(value["courtName"])
                                if value["courtName"] == name:
                                    ballRollList.append(value)
                            ballRollList = ballRollList[0]
                            if not isinstance(ballRollList, dict):
                                try:
                                    ballRollList = dict(ballRollList)
                                except (TypeError, ValueError):
                                    print("無法轉換為字典")
                            isBallRollSearch = reserve.reserveDB.dynamicTableSearch(
                                {
                                    "userid": event.uid,
                                    "status": "ballRoll",
                                    "company": company,
                                    "dataTime": unix_timestamp,
                                    "project": name,
                                })
                            isBallRollHistoryNumber = (0 if isBallRollSearch
                                                       == "" else
                                                       len(isBallRollSearch))
                            unix_timestamp_str = str(unix_timestamp)
                            print(unix_timestamp_str)
                            print("----unix_timestamp---1704038400----")
                            print(ballRollList)
                            configsNumber = ballRollList["monthNumber"][
                                unix_timestamp_str]
                            configsNumber = int(configsNumber)

                            line.doubleReplyFlexMessageText(
                                f"目前剩餘球卷數量：{configsNumber-isBallRollHistoryNumber}",
                                template)
                        case data if data.startswith("ballRollunixTime:") and (
                            "number:" in data) and ("ballRollName:" in data):
                            parts = data.split(":")
                            unixTime = parts[1]
                            number = parts[3]
                            name = parts[5]
                            date_object = datetime.strptime(unixTime, "%Y/%m")
                            first_day_of_month = date_object.replace(day=1,
                                                                     hour=0,
                                                                     minute=0,
                                                                     second=0)
                            unix_timestamp = int(
                                first_day_of_month.timestamp())
                            reserve.reserveDB.updateThreeSearchWhere(
                                "project",
                                name,
                                "userId",
                                event.uid,
                                "status",
                                "0",
                                "company",
                                company,
                            )

                            memberSearchData = member.dbSearch(
                                event.uid, company)
                            template = copy.deepcopy(
                                line.flexTemplate("appointment confirmation"))
                            template["body"]["contents"][0]["contents"][0][
                                "contents"][1]["text"] = memberSearchData[
                                    "name"]
                            template["body"]["contents"][0]["contents"][2][
                                "contents"][1]["text"] = memberSearchData[
                                    "phone"]
                            template["body"]["contents"][1]["contents"][1][
                                "action"][
                                    "data"] = f"ballRollConfirmf:ballRollunixTime:{unixTime}:number:{number}:ballRollName:{name}"
                            template["body"]["contents"][1]["contents"][0][
                                "action"]["data"] = "CancelBallRollReservation"
                            # timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(isReserveFunction.shortDBSearch()[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")
                            # timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(reserve.reserveDB.TableThreeSearch('userId',event.uid,'status','0',"company",company)[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")
                            reserveProjectName = reserve.reserveDB.dynamicTableSearch(
                                {
                                    "userId": event.uid,
                                    "status": "0",
                                    "company": company
                                })[0]["project"]
                            template["body"]["contents"][0]["contents"][4][
                                "contents"][1]["text"] = name

                            template["body"]["contents"][0]["contents"][6][
                                "contents"][1]["text"] = unixTime
                            template["header"]["contents"][0]["text"] = "球卷確認單"
                            line.replyFlex(template)
                        case data if data.startswith(
                            "ballRollConfirmf:ballRollunixTime:") and (
                                "number:" in data) and ("ballRollName:"
                                                        in data):
                            if memberRole >= 2:
                                reserveCount = configs.appointment.reserveCount
                                # isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
                                NOTIFYTOKEN = configs.appointment.NOTIFYTOKEN
                                # historySearchStatusUserId=isReserveFunction.historyDBSearchStatusUserId()
                                parts = data.split(":")
                                unixTime = parts[2]
                                number = parts[4]
                                name = parts[6]

                                date_object = datetime.strptime(
                                    unixTime, "%Y/%m")
                                first_day_of_month = date_object.replace(
                                    day=1, hour=0, minute=0, second=0)
                                unix_timestamp = int(
                                    first_day_of_month.timestamp())
                                # for i in number:
                                # 	reserve.reserveDB.updateThreeSearchWhere("project",name,"userId",event.uid,"status","0","company",company)
                                # 	reserve.reserveDB.updateThreeSearchWhere("dataTime",unix_timestamp,"userId",event.uid,"status","0","company",company)
                                # 	reserve.reserveDB.TableThreeSearch('userid',event.uid,'status','ballRoll','company',company)
                                historySearchStatusUserId = (
                                    reserve.reserveDB.dynamicTableSearch({
                                        "userid":
                                        event.uid,
                                        "status":
                                        "ballRoll",
                                        "company":
                                        company,
                                    }))

                                getReserveTimeList = [
                                    item["dataTime"]
                                    for item in historySearchStatusUserId
                                ]
                                nowTime = getDatetime()
                                nowTimeUinx = int(nowTime.timestamp())
                                ballRollDataList = []
                                ballRollList = []
                                for key, value in searchBallRollfillterTrue.items(
                                ):
                                    ballRollDataList.append(value["courtName"])
                                    if value["courtName"] == name:
                                        ballRollList.append(value)
                                ballRollList = ballRollList[0]
                                if not isinstance(ballRollList, dict):
                                    try:
                                        ballRollList = dict(ballRollList)
                                    except (TypeError, ValueError):
                                        print("無法轉換為字典")

                                isBallRollSearch = reserve.reserveDB.dynamicTableSearch(
                                    {
                                        "userid": event.uid,
                                        "status": "ballRoll",
                                        "company": company,
                                        "dataTime": unix_timestamp,
                                        "project": name,
                                    })
                                isBallRollHistoryNumber = (
                                    0 if isBallRollSearch == "" else
                                    len(isBallRollSearch))
                                unix_timestamp_str = str(unix_timestamp)
                                print(unix_timestamp_str)
                                print("----unix_timestamp---1704038400----")
                                print(ballRollList)
                                configsNumber = ballRollList["monthNumber"][
                                    unix_timestamp_str]
                                configsNumber = int(configsNumber)
                                if (isBallRollHistoryNumber +
                                        int(number)) > configsNumber:
                                    line.replyText(
                                        f"球場：{name}\n球卷數量不足\n剩餘數量：{configsNumber-isBallRollHistoryNumber}\n您選擇數量{number}"
                                    )
                                else:
                                    count = len({
                                        x
                                        for x in getReserveTimeList if
                                        x is not None and x > int(nowTimeUinx)
                                    })
                                    if (reserve.reserveDB.execute_query(
                                            f"SELECT * FROM reserve WHERE userId = '{event.uid}' AND (dataTime IS NULL AND project IS NOT NULL AND status='0') AND company = '{company}'"
                                    ) and name in ballRollDataList):
                                        if count < reserveCount:
                                            # userReservedate=isReserveFunction.historyDBAdd()
                                            for i in range(int(number)):
                                                reserve.reserveDB.Insert(
                                                    (
                                                        "userId",
                                                        "company",
                                                        "project",
                                                        "dataTime",
                                                        "status",
                                                    ),
                                                    (
                                                        event.uid,
                                                        company,
                                                        name,
                                                        unix_timestamp,
                                                        "ballRoll",
                                                    ),
                                                )
                                            userReservedate = (
                                                reserve.reserveDB.
                                                ballRollrdbmsSearch(
                                                    company, event.uid)[0])
                                            reserve.reserveDB.updateThreeSearchWhere(
                                                "project",
                                                None,
                                                "userId",
                                                event.uid,
                                                "status",
                                                "0",
                                                "company",
                                                company,
                                            )

                                            notifyFunction = notify(
                                                NOTIFYTOKEN)
                                            # print((userReservedate))
                                            # print(reserve.reser)
                                            unixTime = (int(
                                                userReservedate["dataTime"]) +
                                                        8 * 60 * 60)
                                            date_object = datetime.utcfromtimestamp(
                                                unixTime)
                                            year_month_str = date_object.strftime(
                                                "%Y/%m")

                                            notifyTime = (
                                                datetime.fromtimestamp(
                                                    userReservedate["dataTime"]
                                                )).strftime("%Y年%m月%d日 %H:%M")
                                            if isNotify == 1:
                                                notifyFunction.SendMessage(
                                                    f'\n姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n球場:{userReservedate["project"]}\n球卷月份:{year_month_str}\n點擊預約時間\n{userReservedate["auto_updae_time"]}\n張數:{number}'
                                                )
                                            line.replyText(
                                                f'姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n球場:{userReservedate["project"]}\n球卷月份:{year_month_str}\n張數:{number}'
                                            )
                                        else:

                                            line.replyText(
                                                "系統自動判斷目前您已有預約時段,請點擊會員查詢確認時段是否預約,若無預約煩請致電～"
                                            )
                                        # isReserveFunction.historyDBUpdate(memberDate)

                                        # isReserveFunction.shortDBDelete()
                                        # print("確認預約")
                                    else:

                                        line.replyText("目前系統尚無預約資料，請重新預約！！！")
                            else:
                                line.doubleReplyMessageText(
                                    f"🙇‍♂️權限不足！！", "☎️如有疑問請致電｜0919-102-803")
                        case data if (user_status != True) and (
                            data.startswith("postReserveProject:")
                            or data.startswith("buyBallRoll:")):
                            template = line.flexTemplate("first")
                            template["hero"]["action"][
                                "uri"] = f"https://liff.line.me/{liffID}?url=login"
                            line.doubleReplyFlexMessageText(
                                "您尚未註冊會員下方功能無法使用", template, "註冊訊息")
        # when error
        # except Exception as error:
        # 	print("Error [main]: ", type(error).__name__, " - ", error)
        # 	return jsonify({'status': 500})
        # end
        return jsonify({"status": "OK"})
    else:
        return print("無此公司")


def getIsProject(phone):
    testDb = MYSQLDB("bot_configs")
    company_dataDb = MYSQLDB("company_data")
    company_dataSearchAll = company_dataDb.dynamicTableSearch(
        {"company_phone": phone})
    liffID = company_dataSearchAll[0]["liffID"]
    botConfigsSearchAll = testDb.dynamicTableSearch({"companyphone": phone})
    if isinstance(botConfigsSearchAll,
                  list) and botConfigsSearchAll is not None:
        LineToken = botConfigsSearchAll[0]["lineConfig"]
        if not isinstance(LineToken, list):
            LineToken_dict = json.loads(LineToken)
        line = Line(
            CHANNEL_ACCESS_TOKEN=LineToken_dict["CHANNEL_ACCESS_TOKEN"],
            CHANNEL_SECRET=LineToken_dict["CHANNEL_SECRET"],
        )

        print("-----LineToken----")
        print(LineToken)
        publicData = botConfigsSearchAll[0]["deniedDates"]
        if not isinstance(publicData, list) and publicData is not None:
            publicData_dict = json.loads(publicData)

        publicBlackTimeList = []
        if publicData is not None:
            publicBlackTimeList = [
                item["deniedDates"] for item in publicData_dict
                if item["status"] == 0
            ]

        searchBallRoll_dict = botConfigsSearchAll[0]["ballRoll"]

        if (not isinstance(searchBallRoll_dict, list)
                and searchBallRoll_dict is not None):
            searchBallRoll_dict = json.loads(searchBallRoll_dict)

        if searchBallRoll_dict:
            searchBallRollfillterTrue = {
                key: value
                for key, value in searchBallRoll_dict.items()
                if value.get("status") == "True"
            }
        else:
            searchBallRollfillterTrue = ""
        ballRollNumber = botConfigsSearchAll[0]["ballRollTime"]

        rusult = botConfigsSearchAll[0]["projectactivetimesblacktime"]
        if not isinstance(rusult, list):
            result_dict = json.loads(rusult)
        else:
            result_dict = rusult

        projects_with_status_1 = [
            project for project, details in result_dict.items()
            if details.get("status") == 1 and details.get("name") is not None
            and len(details.get("name")) > 0
        ]
        print("Status 为 1 的项目有：", projects_with_status_1)
        projectsName = [
            details.get("name") for project, details in result_dict.items()
            if details.get("status") == 1 and details.get("name")
        ]

        projectsShowText = [
            details.get("showText")
            for project, details in result_dict.items()
            if details.get("status") == 1 and details.get("showText")
        ]
        # print('===projectsShowText====')
        # print(projectsShowText)
        projectsActive = [
            details.get("active") for project, details in result_dict.items()
            if details.get("status") == 1 and details.get("active")
        ]
        # print('===projectsactive====') [0]星期一 [1]星期二 [2]星期三
        # print(projectsActive)
        # 專案往後日期
        projectsDay = [
            details.get("day") for project, details in result_dict.items()
            if details.get("status") == 1
        ]

        # 專案預約時間
        projectsinterval = [
            details.get("interval")
            for project, details in result_dict.items()
            if details.get("status") == 1 and details.get("interval")
        ]
        # print('--=-----c-----')
        # print(projectsinterval)
        projectsoffset = [
            details.get("offset") for project, details in result_dict.items()
            if details.get("status") == 1 and details.get("offset")
        ]
        # print('=======result_dict======')
        # print(result_dict)
        # print('=======result_dict======')
        reserveProjectListStr = botConfigsSearchAll[0]["projectList"]
        if (not isinstance(reserveProjectListStr, list)
                and reserveProjectListStr is not None):
            list(reserveProjectListStr)
        else:
            print("CONFIG_BOT設定檔案ProjectList欄位為必填")
        # projectsblockTime = [details.get('blockTime') for project, details in result_dict.items() if details.get('status') == 1 and details.get('blockTime') else []]

        projectsblockTime = []
        for project, details in result_dict.items():
            if details.get("status") == 1 and details.get("blockTime"):
                projectsblockTime.append(details.get("blockTime"))
            else:
                projectsblockTime.append([])

        projectSnumberOfAppointments = []
        for project, details in result_dict.items():
            if details.get("status") == 1 and details.get(
                    "numberOfAppointments"):
                projectSnumberOfAppointments.append(
                    details.get("numberOfAppointments"))
            # else:
            # projectSnumberOfAppointments.append([])

        projectGroupReserveStatus = []
        for project, details in result_dict.items():
            if details.get("status") == 1 and details.get(
                    "groupReserveStatus"):
                projectGroupReserveStatus.append(
                    details.get("groupReserveStatus"))

        projectGroupNameList = result_dict["projectGroupName"]

        isNotify = botConfigsSearchAll[0]["isNotify"]

        return (
            liffID,
            reserveProjectListStr,
            line,
            ballRollNumber,
            searchBallRollfillterTrue,
            result_dict,
            projects_with_status_1,
            projectsName,
            projectsActive,
            projectsDay,
            projectsinterval,
            publicBlackTimeList,
            projectsoffset,
            projectsblockTime,
            projectSnumberOfAppointments,
            projectGroupReserveStatus,
            projectGroupNameList,
            isNotify,
        )
    else:
        return "getIsProject Function Error"


def courtPlaceDB(phone):
    company_dataDb = MYSQLDB("court_place_reserve")
    companyDataList = company_dataDb.dynamicTableSearch(
        {"company_phone": phone})
    return companyDataList


def memberData(phone, userId):
    memberDB = MYSQLDB("member")
    memberData = memberDB.dynamicTableSearch({
        "company": phone,
        "userId": userId
    })
    if memberData:
        memberData[0]
    return memberData


print("test================")


def pushRemindMessage():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    start_of_day = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0,
                            0)
    end_of_day = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59,
                          59)
    start_unix_timestamp = int(start_of_day.timestamp())
    end_unix_timestamp = int(end_of_day.timestamp())
    current_unix_time = int(time.time())
    template = copy.deepcopy(line.flexTemplate("reserveRemind"))
    # if reserve.reserveDB.TableTwoSearch('dataTime',current_unix_time,'status','1'):
    reserveList = reserve.reserveDB.dynamicTableSearch({"status": "1"})
    print(start_unix_timestamp)
    print(end_unix_timestamp)
    for index, item in enumerate(reserveList):
        if (item["dataTime"] < end_unix_timestamp
                and item["dataTime"] > start_unix_timestamp):
            datetime_object = datetime.fromtimestamp(item["dataTime"], TZ)
            formattedDate = datetime_object.strftime("%Y/%m/%d %H:%M")
            template["body"]["contents"][1]["contents"][0]["text"] = item[
                "project"]
            template["body"]["contents"][2]["contents"][0][
                "text"] = formattedDate
            line.pushFlexMessage(item["userId"], template)

    # reserve.reserveDB.TableOneSearch('dataTime')


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=85)
