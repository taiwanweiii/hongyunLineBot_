from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta, time,timezone
import pytz
import copy
import json
import configs.line
import configs.appointment

# from classes.event import *
from classes.db import *
from classes.line import *
from classes.notify import *

from functions import member
from functions import functionTemplate
from functions import reserve

from admin import webhook

import schedule
import time
TZ = pytz.timezone('Asia/Taipei')
def getDatetime(): return datetime.now(TZ)
# datetime.fromtimestamp(getDatetime().timestamp())
# getDatetime().strftime('%H:%M')

# line = Line(
# 	CHANNEL_ACCESS_TOKEN = configs.line.CHANNEL_ACCESS_TOKEN,
# 	CHANNEL_SECRET = configs.line.CHANNEL_SECRET
# )

appointmentsDB = DB('appointments')

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"
"""
原始檔案
@app.route('/callback', methods=['POST'])
def callback():

	data = request.get_json()
	print('===============data==================')
	print(data)
	print('===============data==================')
	# try:
	# start
	if 'events' not in data: return print('events not exists.')
	for event in data["events"]:
		# init
		
		event = line.setEvent(event)

		# 
		match event.type:
			# message
			case "follow":
				template = line.flexTemplate('first')
				line.replyFlex(template)
			case 'message':
				# configs
				underButtonSendMessageList = configs.appointment.underButtonSendMessageList
				underButtonLableList = configs.appointment.underButtonLableList

				user_status = member.isMember(event.uid)
				if user_status == 'name':
					if len(event.message) > 50:
						line.replyText("使用者名稱過長,請嘗試重新輸入")
					else:
						member.memberDB.updateOneSearchWhere("name",event.message,"userId",event.uid)
						# member.update(event.uid,{'name': event.message})
						user_status = member.isMember(event.uid)
						if user_status == 'phone':
							line.replyText("請於下方訊息框輸入電話:")
						else:
							print(user_status)
							line.replyText("會員資料更新完成")
				elif user_status == 'phone':
					if member.isPhone(event.message) == False:
						line.replyText("電話號碼格式錯誤，請再輸入1次(Ex:0987654321)")
					else:
						member.memberDB.updateOneSearchWhere("phone",event.message,"userId",event.uid)
						# member.update(event.uid,{'phone': event.message})
						line.replyText("請輸入性別，🙋🏻‍♂️男性請輸入男，🙋🏻‍♀️女性請輸入女")
				elif user_status == 'sex':
					if event.message=="男" or event.message=='女':
						member.memberDB.updateOneSearchWhere("sex",event.message,"userId",event.uid)
						reserve.reserveDB.Insert(("userId",),(event.uid,))
						line.replyText("會員資料更新完成")
					else:
						line.replyText("輸入錯誤請從新輸入性別，🙋🏻‍♂️男性請輸入男，🙋🏻‍♀️女性請輸入女")
				elif user_status ==True:
					# before
					# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
					# before
					if event.message =='🔥我要預約🔥':
						template=functionTemplate.buttonTemplate(underButtonLableList,underButtonSendMessageList)
						reserve.reserveDB.updateTwoSearchWhere("dataTime",None,"userId","Ue9a11eeae110fc8a29da9d00d3ebe5cb","status","0")
						reserve.reserveDB.updateTwoSearchWhere("project",None,"userId","Ue9a11eeae110fc8a29da9d00d3ebe5cb","status","0")
						
						# if isReserveFunction.shortDBcontains():
							# isReserveFunction.shortDBDelete()
							# reserve.add(event.uid)
						# else:
							# reserve.add(event.uid)
						line.replyMessage(template)

					elif event.message in underButtonSendMessageList and reserve.isReserveDBState(event.uid)=='noProject':
						reserve.reserveDB.updateTwoSearchWhere('project',event.message[2:4],'userId',event.uid,'status','0')
						activeTimes = configs.appointment.activeTimes
						num_dates = configs.appointment.num_dates
						deniedDates = configs.appointment.deniedDates
						offset = configs.appointment.offset
						datapage = configs.appointment.datapage
						# 
						def timeRange2Arr(timeRange):
							tmp = timeRange.replace('～','~').replace(' ','').replace('：',':').split('~')
							for idx, t in enumerate(tmp):
								tmp[idx] = t.split(':')
								tmp[idx][0] = int(tmp[idx][0])
								tmp[idx][1] = int(tmp[idx][1])
							return tmp
						# 
						ck_datetime = getDatetime()
						ck_datetime += timedelta(minutes=offset)
						dateList = []
						# 
						while len(dateList) < num_dates:
							ck_weekday = ck_datetime.isoweekday()
							ck_date = ck_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
							timeRanges = activeTimes[str(ck_weekday)]
							for idx, timeRange in enumerate(timeRanges):
								timeRange = timeRange2Arr(timeRange)
								ck_end_datetime = ck_date + timedelta(hours=timeRange[1][0], minutes=timeRange[1][1])
								if not ck_datetime.strftime("%m/%d") in deniedDates and activeTimes[str(ck_weekday)] and ck_datetime < ck_end_datetime:
									dateList.append(int(ck_datetime.timestamp()))
									break
							ck_datetime = ck_datetime.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
						# 
						# for d in dateList:
						# 	print(datetime.fromtimestamp(d, TZ))

						# render
						template = copy.deepcopy(line.flexTemplate('appointmentNow'))
						template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
						template_page_item=copy.deepcopy(template['contents'][0])
						template['contents'][0]['body']['contents'] = []
						# 
						items = []
						for idx,ts in enumerate(dateList):
							dt = datetime.fromtimestamp(ts, TZ)
							weekday_chinese = ['一', '二', '三', '四', '五', '六', '日']
							print(f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})")
							print(ts)
							idx+=1
							typePage = (idx / datapage) + 1 if idx % datapage > 0 else (idx / datapage)
							typePage = int(typePage)
							print("==================pyage")
							print(f"idx: {idx}  typepage: {typePage}  page:{datapage}")
							if len(template['contents'])<typePage:
								template['contents'].append(copy.deepcopy(template['contents'][0]))
								template['contents'][typePage-1]['body']['contents'] = []
							template_item[0]['contents'][0]['text'] = f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})"
							template_item[0]['contents'][1]['action']['data'] = f"appointment_choose_time:{int(ts)}"
							template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[0]))
							template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[1]))
						# print(template)

						line.replyFlex(template)
					elif event.message == '會員查詢🙇\u200d♂️':
						isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
						template = copy.deepcopy(line.flexTemplate('memberSearch'))
						template['body']['contents'][1]['contents'][1]['contents'][1]['text']=member.search(event.uid)[0]['name']
						template['body']['contents'][1]['contents'][2]['contents'][1]['text']=member.search(event.uid)[0]['phone']
						historySearchStatusUserId=isReserveFunction.historyDBSearchStatusUserId()
						nowTime=getDatetime()
						nowTimeUinx=int(nowTime.timestamp())
						filtered_list = [item for item in historySearchStatusUserId if 'dataTime' in item and item['dataTime'] > nowTimeUinx]
						print(len(filtered_list))
						if len(filtered_list)>0:
							reserveDateTimeformatYYYYMMDDhhmm=(datetime.fromtimestamp(int(filtered_list[0]["dataTime"]),TZ)).strftime('20%y年%m月%d日%H:%M')
							template['body']['contents'][3]['contents'][1]['contents'][1]['text']='已預約'
							template['body']['contents'][3]['contents'][2]['contents'][1]['text']=reserveDateTimeformatYYYYMMDDhhmm
						else:
							template['body']['contents'][3]['contents'][1]['contents'][1]['text']='尚未預約'
							template['body']['contents'][3]['contents'][2]['contents'][1]['text']="-"

						# print(reserveDateTimeformatYYYYMMDDhhmm)
						line.replyFlex(template)


			# postback
			case 'postback':
				match event.postback:
					case data if data.startswith('appointment_choose_time:'):
						# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
						if reserve.isReserveDBState(event.uid)=='noDataTime':
							a_date = datetime.fromtimestamp(int(data.split(':')[1]), TZ)
							unix_data = int(a_date.timestamp())
							print('test=========================')
							print(a_date)
							print(unix_data)
							print('test=========================')

							if len(data.split(":")) > 1:
								dataUnix = data.split(":")[1].strip()
							dateFormatYYYYMMDD=(datetime.fromtimestamp(int(dataUnix),TZ)).strftime('20%y年%m月%d日')
							# isReserveFunction.shortDBUpdate({'dataTime':dataUnix})
							reserve.reserveDB.updateTwoSearchWhere("dataTime",dataUnix,"userId",event.uid,'status','0')

							interval= configs.appointment.interval
							activeTimes=configs.appointment.activeTimes
							timepage= configs.appointment.timepage

							timeList=[]
							unixTimeList=[]
							filterTimeYYYYDDList=[]
							weekday=activeTimes[str((a_date.weekday())+1)]


							for i in range(len(weekday)):
								start_time_str, end_time_str = weekday[i].split(' ~ ')

								start_time = datetime.strptime(start_time_str, '%H:%M')
								end_time = datetime.strptime(end_time_str, '%H:%M')

								intervaltime=timedelta(minutes=interval)
								while start_time<end_time:
									# print(start_time.strftime(start_time,'%H:%M'))
									timeList.append(datetime.strftime(start_time,'%H:%M'))
									start_time+=intervaltime
							print('======================timeList=================')
							print(timeList)
							print('======================timeList=================')
							for timeLists in timeList:
								# mac
								# unixTime = (datetime.strptime(timeLists, '%H:%M')).timestamp()
								# unixTimeList.append(int(unixTime)+int(2209017600)+unix_data)
								#windows
								unixTime=(datetime.strptime(timeLists, '%H:%M')-datetime(1970, 1, 1)).total_seconds()
								unixTimeList.append(int(unixTime)+int(2208988800)+unix_data)
								print(unixTime)
							print('======================unixTimeList=================')
							print(unixTimeList)
							print('======================unixTimeList=================')

							# print(reserve.all())
							# historydate=isReserveFunction.historyDBSearch()
							historydate = reserve.reserveDB.TableTwoSearch('userId',event.uid,'status','1')
							historyDataTime = [item['dataTime'] for item in historydate]
							# historyDataTimeFormatYYYYMMDD=(datetime.fromtimestamp(int(historyDataTime),TZ)).strftime('20%y年%m月%d日')
							filterTimeUnix = [x for x in unixTimeList if x not in historyDataTime]
							for filterTimeYYYYDD in filterTimeUnix:
								dt = datetime.fromtimestamp(filterTimeYYYYDD,TZ).strftime('%H:%M')
								filterTimeYYYYDDList.append(dt)
							print(filterTimeYYYYDDList)
							
							if len(filterTimeYYYYDDList)<1:
								line.replyText(f'({dateFormatYYYYMMDD})當日預約已滿請上方從選擇日期')
							else:
								template = copy.deepcopy(line.flexTemplate('appointmentNow'))
								template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
								template['contents'][0]['header']['contents'][0]['text']=dateFormatYYYYMMDD
								template['contents'][0]['body']['contents'] = []

								for idx,ts in enumerate(filterTimeYYYYDDList):
									idx+=1
									typePage = (idx / timepage) + 1 if idx % timepage > 0 else (idx / timepage)
									typePage = int(typePage)
									if len(template['contents'])<typePage:
										template['contents'].append(copy.deepcopy(template['contents'][0]))
										template['contents'][typePage-1]['body']['contents'] = []
									template_item[0]['contents'][0]['text'] = ts
									template_item[0]['contents'][1]['action']['data'] = f"appointment_confirm_reserve:{filterTimeUnix[idx-1]}"
									template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[0]))
									template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[1]))
								# print(template)
								line.replyFlex(template)

					case data if data.startswith('appointment_confirm_reserve'):
						# isReserveFunction=reserve.isReserveDBState(event.uid)
						# if isReserveFunction.isShortReserveDBState()==True:
						if reserve.isReserveDBState(event.uid) == True:
							if len(data.split(":")) > 1:
								a_date = int(data.split(":")[1].strip())
							print(a_date)
							# isReserveFunction.shortDBUpdate({"dataTime":a_date})
							reserve.reserveDB.updateTwoSearchWhere("dataTime",a_date,"userId",event.uid,"status","0")
							# print(dateTime)
							template = copy.deepcopy(line.flexTemplate('appointment confirmation'))
							# template['body']['contents'][2]['contents'][0]['contents'][1]['text']=member.search(event.uid)[0]['name']
							# template['body']['contents'][2]['contents'][2]['contents'][1]['text']=member.search(event.uid)[0]['phone']
							template['body']['contents'][2]['contents'][0]['contents'][1]['text']=member.memberDB.TableOneSearch('userId',event.uid)[0]['name']
							template['body']['contents'][2]['contents'][2]['contents'][1]['text']=member.memberDB.TableOneSearch('userId',event.uid)[0]['phone']

							# timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(isReserveFunction.shortDBSearch()[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")
							timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(reserve.reserveDB.TableTwoSearch('userId',event.uid,'status','0')[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")

							print(timeFormatYYYYMMDDhhmm)
							# template['body']['contents'][2]['contents'][4]['contents'][1]['text']=isReserveFunction.shortDBSearch()[0]['project']
							template['body']['contents'][2]['contents'][4]['contents'][1]['text']=reserve.reserveDB.TableTwoSearch('userId',event.uid,'status','0')[0]['project']

							template['body']['contents'][2]['contents'][6]['contents'][1]['text']=timeFormatYYYYMMDDhhmm
							line.replyFlex(template)

							# template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
							# template['contents'][0]['header']['contents'][0]['text']=dateFormatYYYYMMDD
							# template['contents'][0]['body']['contents'] = []

					case 'ConfirmReservation':
						reserveCount= configs.appointment.reserveCount
						# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
						NOTIFYTOKEN=configs.appointment.NOTIFYTOKEN
						# historySearchStatusUserId=isReserveFunction.historyDBSearchStatusUserId()
						historySearchStatusUserId = reserve.reserveDB.TableTwoSearch('userid',event.uid,'status','1')
						getReserveTimeList = [item['dataTime'] for item in historySearchStatusUserId]
						nowTime=getDatetime()
						nowTimeUinx=int(nowTime.timestamp())
						count = len({x for x in getReserveTimeList if x is not None and x > int(nowTimeUinx)})
						if not reserve.reserveDB.execute_query(f"SELECT * FROM reserve WHERE userId = 'Ue9a11eeae110fc8a29da9d00d3ebe5cb' AND (dataTime IS NULL OR project IS NULL)"):
							if count< reserveCount:
								# userReservedate=isReserveFunction.historyDBAdd()
								reserve.reserveDB.updateTwoSearchWhere('status','1','userId',event.uid,'status','0')
								reserve.reserveDB.Insert(("userId",),(event.uid,))

								userReservedate=reserve.reserveDB.rdbmsSearch('member.name,member.phone,member.userId,reserve.dataTime,reserve.project,reserve.auto_updae_time','member','userId','userId','status=1')[0]
								print(userReservedate["dataTime"])
								notifyFunction=notify(NOTIFYTOKEN)
								notifyTime=(datetime.fromtimestamp(userReservedate["dataTime"])).strftime('%Y年%m月%d日 %H:%M')
								notifyFunction.SendMessage(f'\n姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}\n點擊預約時間\n{userReservedate["auto_updae_time"]}\n')
								line.replyText(f'姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}\n')
							else:
								line.replyText('系統自動判斷目前您以有預約時段,請點擊會員查詢確認時段是否預約,若無預約煩請致電～')
							# isReserveFunction.historyDBUpdate(memberDate)

							# isReserveFunction.shortDBDelete()
							# print("確認預約")
						else:
							line.replyText('目前系統尚無預約資料，請從新預約！！！')

					case 'CancelReservation':
						# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
						try:
							if (reserve.reserveDB.TableTwoSearch('userId',event.uid,'status','0')):
								reserve.reserveDB.updateTwoSearchWhere("dataTime",None,"userId","Ue9a11eeae110fc8a29da9d00d3ebe5cb","status","0")
								reserve.reserveDB.updateTwoSearchWhere("project",None,"userId","Ue9a11eeae110fc8a29da9d00d3ebe5cb","status","0")
						# if isReserveFunction.shortDBcontains():
						# 	isReserveFunction.shortDBDelete()
						# 	reserve.add(event.uid)
						except:print()
						pass
					case 'updateuserId':
						member.update(event.uid,{'name':None})
						line.replyText("請輸入使用者暱稱")
					case 'updateUserPhone':
						member.update(event.uid,{'phone':None})
						line.replyText("請輸入使用者電話")

					case 'firstviewTutoril':
						template=functionTemplate.videoTemplate('https://imgur.com/XVmZmIE','https://img.ttshow.tw/images/media/frontcover/2020/08/06/6.jpg')
						line.replyMessage(template)
					case 'registerNow':
						user_status = member.isMember(event.uid)
						if user_status == 'nouser':
							member.memberDB.Insert(('userId','company'),(event.uid,'TEST公司'))
							line.replyText("請輸入使用者名稱")
						elif user_status == 'name':
							line.replyText("請先輸入使用者名稱")
						elif user_status == 'phone':
							line.replyText("請先輸入電話號碼")

	# when error
	# except Exception as error:
	# 	print("Error [main]: ", type(error).__name__, " - ", error)
	# 	return jsonify({'status': 500})
	# end
	return jsonify({"status": "OK"})
"""
# print('test================')
# for test in webhook.client:
	# for a in test.values():
# print('test================')

@app.route('/test/<username>/<hi>')
def user(username,hi):
	return f"username:{username} \nhi:{hi}"

clientWebhook = [list(entry.values())[0] for entry in webhook.client if isinstance(entry, dict) and entry]
print('-------clientWebhook------')
print(clientWebhook)
print('-------clientWebhook------')

@app.route('/Linebotv1/<company>', methods=['POST'])
def LineBotv1(company):
	configsSearchDBProjectList,LineToken,ballRollNumber,searchBallRollfillterTrue,projectDetails,projectList,projectNameList,projectsActiveList,projectsDayList,projectsintervalList,publicBlackTimeList,projectsoffsetList,projectsblockTimeList,projectSnumberOfAppointmentsList,projectGroupReserveStatusList,projectGroupNameList=getIsProject(company)
	line = Line(
		CHANNEL_ACCESS_TOKEN = LineToken["CHANNEL_ACCESS_TOKEN"],
		CHANNEL_SECRET = LineToken["CHANNEL_SECRET"]
	)
	print('===============projectNameList==================')
	print(projectNameList)
	print('===============projectNameList==================')
	configs.appointment.getUserName(company)
	if company in clientWebhook:
		data = request.get_json()
		print('===============data==================')
		print(data)
		print('===============data==================')


		# try:
		# start
		if 'events' not in data: return print('events not exists.')
		for event in data["events"]:
			# init
			
			event = line.setEvent(event)
			user_status = member.isMember(event.uid,company)

			# 
			match event.type:
				# message
				case "follow":
					template = line.flexTemplate('first')
					# member.memberDB.insertMember(event.uid,company)
					# line.replyFlex(template)
					line.doubleReplyFlexMessageText('歡迎您加入此帳號🤩',template,'註冊訊息')
				case 'message':
					# configs
					# underButtonSendMessageList = configs.appointment.underButtonSendMessageList

					# underButtonSendMessageListStr = configs.appointment.underButtonSendMessageList(company)

					# underButtonSendMessageList=eval(underButtonSendMessageListStr)

					configsSearchDBProjectList,LineToken,ballRollNumber,searchBallRollfillterTrue,projectDetails,projectList,projectNameList,projectsActiveList,projectsDayList,projectsintervalList,publicBlackTimeList,projectsoffsetList,projectsblockTimeList,projectSnumberOfAppointmentsList,projectGroupReserveStatusList,projectGroupNameList=getIsProject(company)
					# underButtonLableList = configs.appointment.underButtonLableList
					# underButtonSendMessageList = configs.appointment.underButtonSendMessageList
					underButtonLableList=projectNameList
					reserved_items = ['預約' + item for item in projectNameList]

					underButtonSendMessageList=reserved_items
					memberBasicInformation=memberData(company,event.uid)
					memberRegistertemplate = line.flexTemplate('memberRegister')
					
					if memberBasicInformation:
						memberBasicInformation=memberBasicInformation[0]
						if memberBasicInformation['name']:
							memberRegistertemplate['hero']['contents'][1]['contents'][0]["contents"][0]["contents"][1]['text']=memberBasicInformation['name']
						if memberBasicInformation['phone']:
							memberRegistertemplate['hero']['contents'][1]['contents'][0]["contents"][1]["contents"][1]['text']=memberBasicInformation['phone']
						if memberBasicInformation['sex']:
							memberRegistertemplate['hero']['contents'][1]['contents'][0]["contents"][2]["contents"][1]['text']=memberBasicInformation['sex']


					if user_status=='nouser':
						template = line.flexTemplate('first')
						line.replyFlex(template)
					if user_status == 'phone':
						if member.isPhone(event.message) == False:
							line.replyText("電話號碼格式錯誤，請再輸入1次(Ex:0987654321)")
						else:
							histroyPhones=member.isPhoneRepeat(company)
							print('--histroyPhones--')
							print(histroyPhones)
							if (event.message in histroyPhones):
								line.doubleReplyMessageText(f'電話:{event.message} 已重複註冊','請嘗試重新輸入10碼電話號碼')
							else:
								member.memberDB.updateTwoSearchWhere("phone",event.message,"userId",event.uid,"company",company)
							# member.update(event.uid,{'phone': event.message})
							if member.isMember(event.uid,company)==True:
								line.replyText("電話號碼更新完成")
								
							elif member.isMember(event.uid,company)=='name':
								memberRegistertemplate['hero']['contents'][1]['contents'][0]["contents"][1]["contents"][1]['text']=event.message
								line.doubleReplyFlexMessageText('請於下方小鍵盤，輸入會員姓名',memberRegistertemplate,'會員姓名輸入')


					elif user_status == 'name' :
						if len(event.message) > 50:
							line.replyText("使用者名稱過長,請嘗試重新輸入")
						else:
							member.memberDB.updateTwoSearchWhere("name",event.message,"userId",event.uid,"company",company)
							# member.update(event.uid,{'name': event.message})
							user_status = member.isMember(event.uid,company)
							if user_status == 'phone':
								# memberRegistertemplate = line.flexTemplate('memberRegister')
								memberRegistertemplate['hero']['contents'][1]['contents'][0]["contents"][0]["contents"][1]['text']=event.message
								template=functionTemplate.buttonTemplate(["🙋🏻‍♂️男性","🙋🏻‍♀️女性"],['男','女'],"請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女")
								line.doubleReplyTwoFlex(memberRegistertemplate,template)
							elif user_status=='sex':
								memberRegistertemplate['hero']['contents'][1]['contents'][0]["contents"][0]["contents"][1]['text']=event.message

								template=functionTemplate.buttonTemplate(["🙋🏻‍♂️男性","🙋🏻‍♀️女性"],['男','女'],"🥰請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女")
								line.doubleReplyTwoFlex(memberRegistertemplate,template)
							else:
								print(user_status)
								line.replyText("會員資料更新完成")
					elif user_status == 'sex':
						if event.message=="男" or event.message=='女':
							memberRegistertemplate['hero']['contents'][1]['contents'][0]["contents"][2]["contents"][1]['text']=event.message

							member.memberDB.updateTwoSearchWhere("sex",event.message,"userId",event.uid,"company",company)
							reserve.reserveDB.Insert(("userId","company",),(event.uid,company,))
							user_status = member.isMember(event.uid,company)

							line.doubleReplyFlexMessageText('會員資料更新完成',memberRegistertemplate,'註冊完成')

							# line.replyText("會員資料更新完成")
						else:
							template=functionTemplate.buttonTemplate(["🙋🏻‍♂️男性","🙋🏻‍♀️女性"],['男','女'],"請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女")
							# templateTwo = line.flexTemplate('memberRegister')
							line.doubleReplyTwoFlex(memberRegistertemplate,template)
					elif user_status ==True:
						# before
						# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
						# before
						if event.message =='#個人狀況':
							template=copy.deepcopy(line.flexTemplate('carousel'))
							reserveList = copy.deepcopy(line.flexTemplate('reserveList'))
							templateAdd=copy.deepcopy(reserveList['contents'][0])
							print('---underButtonLableList---')
							projectlist=['球桿數據','揮桿數據']
							imageUrl=['https://i.imgur.com/nIByphE.png','https://i.imgur.com/3PgjXM1.png']
							print(len(projectlist))
							print(projectlist)
							i=0
							while i <len(projectlist):
								templateAdd['hero']['contents'][0]["url"]=imageUrl[i]
								templateAdd['hero']['contents'][1]["contents"][0]['text']='鴻運高爾夫工坊'
								templateAdd['hero']['contents'][2]["contents"][1]['contents'][0]['text']=f'點擊查看{projectlist[i]}'
								# templateAdd['hero']['action']['data']=f'ReserveProject:{projectlist[i]}'
								templateAdd['hero']['action']['data']=f'personalData:{projectlist[i]}'
								templateAdd['hero']['action']['displayText']=f'選擇預約{projectlist[i]}'
								template['contents'].append(copy.deepcopy(templateAdd))
								i+=1
							print("underButtonSendMessageList")
							# template=functionTemplate.buttonTemplate(underButtonLableList,underButtonSendMessageList)

							line.replyFlex(template)
							# line.replyMessage(template)

						elif event.message in underButtonSendMessageList and reserve.isReserveDBState(event.uid,company)=='noProject':
							reserve.reserveDB.updateThreeSearchWhere('project',event.message[2:],'userId',event.uid,'status','0',"company",company)
							print('=================print(')
							"""
							#時間轉UNIX
							def convert_to_timestamps(active_list):
								converted_active = []
								for time_range in active_list:
									converted_range = []
									for time_point in time_range:
										if time_point[0] is not None:
											start_time_str, end_time_str = time_point
											start_time = int(start_time_str.split(':')[0]) * 60 * 60 + int(start_time_str.split(':')[1])*60
											end_time = int(end_time_str.split(':')[0]) * 60 * 60 + int(end_time_str.split(':')[1])*60
											converted_range.append([int(start_time), int(end_time)] if time_range[0] is not None else [None, None])
										else:
											converted_range.append([None, None])
									converted_active.append(converted_range)
								return converted_active
							
							projectNameIdx = projectNameList.index(event.message)
							projectName=projectNameList[projectNameIdx]
							projectsActive=projectsActiveList[projectNameIdx]
							if(projectsActive[0][1][0]==None):
								print(projectsActive)
								a=convert_to_timestamps(projectsActive)
								print('測試')
								print(a)
							else:
								print('午休時段')
							"""
							projectNameIdx = projectNameList.index(event.message[2:])
							projectName=projectNameList[projectNameIdx]
							projectsDay=projectsDayList[projectNameIdx]
							projectsActive=projectsActiveList[projectNameIdx]
							projectsoffset=projectsoffsetList[projectNameIdx]
							projectsinterval=projectsintervalList[projectNameIdx]
							current_datetime = datetime.now()
							current = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

							nowtimestamp = current.timestamp()
							todayTimestamp=nowtimestamp+projectsDay+86400
							nextTimestamp=todayTimestamp+projectsoffset
							# print('---------------projectsoffset=====')
							# print(projectsDayList)
							# print(projectsDay)
							# print('---------------projectsoffset=====')

							# 打印結果


							dayList=[]

							# dayList.append(todayTimestamp)
							ranges = [(start, start + 86400 - 1) for start in publicBlackTimeList]
							while todayTimestamp < nextTimestamp:
								if not any(start <= todayTimestamp <= end for start, end in ranges):
									dayList.append(todayTimestamp)
								todayTimestamp += 86400


							template = copy.deepcopy(line.flexTemplate('appointmentNow'))
							template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
							template_page_item=copy.deepcopy(template['contents'][0])
							template['contents'][0]['body']['contents'] = []
							datapage = configs.appointment.datapage
							blackweekday=[]
							weekday_chinese = ['一', '二', '三', '四', '五', '六', '日']
							for i in range(7):
								if (projectsActive[i][0][0]=="00:00" and projectsActive[i][0][1]=="00:00"):
									blackweekday.append(weekday_chinese[i])
							idex=1
							for idx,ts in enumerate(dayList):
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

								if not weekday_chinese[dt.weekday()] in blackweekday:
									typePage = (idex / datapage) + 1 if idex % datapage > 0 else (idex / datapage)
									typePage = int(typePage)

									# print("==================pyage")
									# print(f"idx: {idx}  typepage: {typePage}  page:{datapage}")
									if len(template['contents'])<typePage:
										template['contents'].append(copy.deepcopy(template['contents'][0]))
										template['contents'][typePage-1]['body']['contents'] = []
									template_item[0]['contents'][0]['text'] = f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})"
									template_item[0]['contents'][1]['action']['data'] = f"appointment_choose_time:{int(ts)} project:{projectName}"
									template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[0]))
									template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[1]))
									idex+=1
									print(int(ts))
								else:
									print(weekday_chinese[dt.weekday()])
								# print(projectNameList[projectNameIdx])
								# activeTimes = configs.appointment.activeTimes

							"""
							activeTimesStr = configs.appointment.activeTimes(company)
							activeTimes=eval(activeTimesStr)
							num_dates = configs.appointment.num_dates
							deniedDates = configs.appointment.deniedDates
							offset = configs.appointment.offset
							datapage = configs.appointment.datapage
							# 
							def timeRange2Arr(timeRange):
								tmp = timeRange.replace('～','~').replace(' ','').replace('：',':').split('~')
								for idx, t in enumerate(tmp):
									tmp[idx] = t.split(':')
									tmp[idx][0] = int(tmp[idx][0])
									tmp[idx][1] = int(tmp[idx][1])
								return tmp
							# 
							ck_datetime = getDatetime()
							ck_datetime += timedelta(minutes=offset)
							dateList = []
							# 
							while len(dateList) < num_dates:
								ck_weekday = ck_datetime.isoweekday()
								ck_date = ck_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
								timeRanges = activeTimes[str(ck_weekday)]
								for idx, timeRange in enumerate(timeRanges):
									timeRange = timeRange2Arr(timeRange)
									ck_end_datetime = ck_date + timedelta(hours=timeRange[1][0], minutes=timeRange[1][1])
									if not ck_datetime.strftime("%m/%d") in deniedDates and activeTimes[str(ck_weekday)] and ck_datetime < ck_end_datetime:
										dateList.append(int(ck_datetime.timestamp()))
										break
								ck_datetime = ck_datetime.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
							# 
							# for d in dateList:
							# 	print(datetime.fromtimestamp(d, TZ))

							# render
							template = copy.deepcopy(line.flexTemplate('appointmentNow'))
							template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
							template_page_item=copy.deepcopy(template['contents'][0])
							template['contents'][0]['body']['contents'] = []
							# 
							items = []
							for idx,ts in enumerate(dateList):
								dt = datetime.fromtimestamp(ts, TZ)
								weekday_chinese = ['一', '二', '三', '四', '五', '六', '日']
								print(f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})")
								print(ts)
								idx+=1
								typePage = (idx / datapage) + 1 if idx % datapage > 0 else (idx / datapage)
								typePage = int(typePage)
								print("==================pyage")
								print(f"idx: {idx}  typepage: {typePage}  page:{datapage}")
								if len(template['contents'])<typePage:
									template['contents'].append(copy.deepcopy(template['contents'][0]))
									template['contents'][typePage-1]['body']['contents'] = []
								template_item[0]['contents'][0]['text'] = f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})"
								template_item[0]['contents'][1]['action']['data'] = f"appointment_choose_time:{int(ts)}"
								template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[0]))
								template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[1]))
							# print(template)
							"""
							line.replyFlex(template)
						elif event.message == '#會員查詢':
							template = copy.deepcopy(line.flexTemplate('mebersearch'))
							templateAdd=copy.deepcopy(line.flexTemplate('memberAddtemplates'))
							template['hero']['contents'][1]['contents'][0]['contents'][1]['contents'][1]['text']=member.memberDB.TableTwoSearch('userId',event.uid,'company',company)[0]['name']
							template['hero']['contents'][1]['contents'][0]['contents'][2]['contents'][1]['text']=member.memberDB.TableTwoSearch('userId',event.uid,'company',company)[0]['phone']
							# # isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
							# template = copy.deepcopy(line.flexTemplate('memberSearch'))
							# # template['body']['contents'][1]['contents'][1]['contents'][1]['text']=member.search(event.uid)[0]['name']
							# # template['body']['contents'][1]['contents'][2]['contents'][1]['text']=member.search(event.uid)[0]['phone']
							# template['body']['contents'][1]['contents'][1]['contents'][1]['text']=member.memberDB.TableTwoSearch('userId',event.uid,'company',company)[0]['name']
							# template['body']['contents'][1]['contents'][2]['contents'][1]['text']=member.memberDB.TableTwoSearch('userId',event.uid,'company',company)[0]['phone']
							# # historySearchStatusUserId=isReserveFunction.historyDBSearchStatusUserId()
							memberdate = member.memberDB.TableTwoSearch('userId',event.uid,'company',company)
							historySearchStatusUserId = reserve.reserveDB.TableThreeSearch('userId',event.uid,'company',company,'status',1)
							nowTimeUnix = datetime.timestamp(datetime.now())
			
							filtered_data = [item for item in historySearchStatusUserId if item['dataTime'] > nowTimeUnix]
							sortFilteredDataTime = sorted(filtered_data, key=lambda x: x['dataTime'])

							print('-----------會員查詢🙇‍♂️---------')
							print((sortFilteredDataTime))
							print('-----------會員查詢🙇‍♂️---------')
							if len(sortFilteredDataTime)>0:
								# reserveDateTimeformatYYYYMMDDhhmm=(datetime.fromtimestamp(int(sortFilteredDataTime[0]["dataTime"]),TZ)).strftime('20%y年%m月%d日%H:%M')

								# template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[0]))
								# template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[1]))
								# template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[2]))
								for correctData in sortFilteredDataTime:
									unixTime= correctData['dataTime']
									formattedYYYYMMDDhhmm = datetime.fromtimestamp(unixTime,tz=TZ).strftime('%Y年%m月%d日 %H:%M')
									templateAdd[0]["contents"][1]["text"]=correctData['project']
									templateAdd[1]["contents"][1]["text"]=formattedYYYYMMDDhhmm
									template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[0]))
									template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[1]))
									template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[2]))

								print('--------template=======')
								print(template)
							else:
								templateAdd[0]["contents"][1]["text"]='尚未預約'
								templateAdd[1]["contents"][1]["text"]="-"
								template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[0]))
								template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[1]))
								template["hero"]["contents"][1]["contents"][1]["contents"].append(copy.deepcopy(templateAdd[2]))

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
						elif event.message =='#商家資訊':
							line.replyTextAndImage("""地址:台南市東區裕文路376號
📍Google Map:https://maps.app.goo.gl/g3S5iD1Woo7a2SZF8
							  
📱電話：0919-102-803
							  
🌻周一至週六營業時間
      下午13:30 至 晚上21:00
							  
🌷週日和例假日公休
													""",
														"https://i.imgur.com/KTOITqS.png")

						elif event.message =='#聯絡我們':
							line.replyText('☎️請點此致電｜0919-102-803')
				# postback
				case 'postback':

					match event.postback:
							case data if data.startswith('appointment_confirm_reserve:'):
								# isReserveFunction=reserve.isReserveDBState(event.uid)
								# if isReserveFunction.isShortReserveDBState()==True:
								if len(data.split(":")) > 1:
									reserveTimeUnix = int(data.split(":")[1].strip())
									print(reserveTimeUnix)
								reserve.reserveDB.updateThreeSearchWhere('dataTime',reserveTimeUnix,'userId',event.uid,'status','0',"company",company)
								
								if reserve.isReserveDBState(event.uid,company) == True:
									memberSearchData=member.dbSearch(event.uid,company)
									template = copy.deepcopy(line.flexTemplate('appointment confirmation'))
									template['body']['contents'][2]['contents'][0]['contents'][1]['text']=memberSearchData['name']
									template['body']['contents'][2]['contents'][2]['contents'][1]['text']=memberSearchData['phone']

									# timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(isReserveFunction.shortDBSearch()[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")
									timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(reserve.reserveDB.TableThreeSearch('userId',event.uid,'status','0',"company",company)[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")

									print(timeFormatYYYYMMDDhhmm)
									# template['body']['contents'][2]['contents'][4]['contents'][1]['text']=isReserveFunction.shortDBSearch()[0]['project']
									reserveProjectName=reserve.reserveDB.TableThreeSearch('userId',event.uid,'status','0','company',company)[0]['project']
									template['body']['contents'][2]['contents'][4]['contents'][1]['text']=reserveProjectName

									template['body']['contents'][2]['contents'][6]['contents'][1]['text']=timeFormatYYYYMMDDhhmm
									line.replyFlex(template)

									# template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
									# template['contents'][0]['header']['contents'][0]['text']=dateFormatYYYYMMDD
									# template['contents'][0]['body']['contents'] = []

							case 'ConfirmReservation':
								reserveCount= configs.appointment.reserveCount
								# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
								NOTIFYTOKEN=configs.appointment.NOTIFYTOKEN
								# historySearchStatusUserId=isReserveFunction.historyDBSearchStatusUserId()
								historySearchStatusUserId = reserve.reserveDB.TableThreeSearch('userid',event.uid,'status','1','company',company)
								getReserveTimeList = [item['dataTime'] for item in historySearchStatusUserId]
								nowTime=getDatetime()
								nowTimeUinx=int(nowTime.timestamp())
								count = len({x for x in getReserveTimeList if x is not None and x > int(nowTimeUinx)})
								if not reserve.reserveDB.execute_query(f"SELECT * FROM reserve WHERE userId = '{event.uid}' AND (dataTime IS NULL OR project IS NULL) AND company = '{company}'"):
									if count< reserveCount:
										# userReservedate=isReserveFunction.historyDBAdd()
										userReservedate=reserve.reserveDB.rdbmsSearch(company,event.uid)[0]

										reserve.reserveDB.updateThreeSearchWhere('status','1','userId',event.uid,'status','0','company',company)
										reserve.reserveDB.Insert(("userId","company",),(event.uid,company,))

										print(userReservedate)
										notifyFunction=notify(NOTIFYTOKEN)
										print('-datetime.fromtimestamp(userReservedate["dataTime"]))----')
										# print((userReservedate))
										# print(reserve.reser)
										notifyTime=(datetime.fromtimestamp(userReservedate["dataTime"])).strftime('%Y年%m月%d日 %H:%M')
										notifyFunction.SendMessage(f'\n姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}\n點擊預約時間\n{userReservedate["auto_updae_time"]}\n')
										line.replyText(f'姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n項目:{userReservedate["project"]}\n預約時間:{notifyTime}\n')
									else:
										line.replyText('系統自動判斷目前您以有預約時段,請點擊會員查詢確認時段是否預約,若無預約煩請致電～')
									# isReserveFunction.historyDBUpdate(memberDate)

									# isReserveFunction.shortDBDelete()
									# print("確認預約")
								else:
									line.replyText('目前系統尚無預約資料，請從新預約！！！')

							case 'CancelReservation':
								# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
								try:
									if (reserve.reserveDB.TableThreeSearch('userId',event.uid,'status','0','company',company)):
										reserve.reserveDB.updateThreeSearchWhere("dataTime",None,"userId",event.uid,"status","0","company",company)
										reserve.reserveDB.updateThreeSearchWhere("project",None,"userId",event.uid,"status","0","company",company)
								# if isReserveFunction.shortDBcontains():
								# 	isReserveFunction.shortDBDelete()
								# 	reserve.add(event.uid)
								except:print()
								pass
							case 'updateuserId':
								memberDB= MYSQLDB('member')

								memberDB.updateTwoSearchWhere('name',None,'company',company,'userId',event.uid)
								# member.update(event.uid,{'name':None})
								line.replyText("請輸入使用者暱稱")
							case 'updateUserPhone':
								memberDB= MYSQLDB('member')

								# memberDB.updateTwoSearchWhere('phone',None,'company',company,'userId',event.uid)
								line.replyText("若要更動電話號碼請聯繫店家")
							case data if data.startswith('ReserveProject') :
								print(data)
							case 'firstviewTutoril':
								template=functionTemplate.videoTemplate('https://imgur.com/XVmZmIE','https://img.ttshow.tw/images/media/frontcover/2020/08/06/6.jpg')
								line.replyMessage(template)
							case 'registerNow':
								user_status = member.isMember(event.uid,company)
								if user_status == 'nouser':
									member.memberDB.Insert(('userId','company'),(event.uid,company))
									line.replyText("請輸入使用者名稱")
								elif user_status == 'name':
									line.replyText("請先輸入使用者名稱")
								elif user_status == 'phone':
									line.replyText("請先輸入電話號碼")
							case 'register':
								memberDB= MYSQLDB('member')
								if not memberDB.TableOneSearchAddField("userId","userId",event.uid,"company",company):
									memberDB.insertMember(event.uid,company)
									template = line.flexTemplate('memberRegister')

									line.doubleReplyFlexMessageText('請於下方小鍵盤，輸入會員電話',template,'使用者電話輸入')

								else:
									user_status=member.isMember(event.uid,company)
									if user_status == 'name':
										line.replyText("請先輸入使用者名稱")
									elif user_status == 'phone':
										line.replyText("請先輸入電話號碼")
									elif user_status == 'sex':
										line.replyText("請輸入性別\n🙋🏻‍♂️男性請輸入男\n🙋🏻‍♀️女性請輸入女")
							case data if data.startswith('personalData:'):
								personalData = (data.split(":"))[1]

								if personalData=='揮桿數據':
									clubDataDB=MYSQLDB('clubData')
									print(event.uid)
									clubDataSearch=(clubDataDB.clubTableSearch('clubData.ballHead,clubData.clubHead,clubData.shaftWeightStiffness,clubData.gripWeight,clubData.swingWeight,clubData.clubfaceAngle,clubData.lieAngle,clubData.remark','clubData',event.uid))
									print(clubDataSearch)
									template=copy.deepcopy(line.flexTemplate('carousel'))
									templateAdd = copy.deepcopy(line.flexTemplate('clubInformation'))
									#球桿名稱
									for index, value in enumerate(clubDataSearch):
										templateAdd['body']['contents'][0]['contents'][1]['contents'][1]['contents'][0]['contents'][1]['text']=value['ballHead']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][1]['contents'][1]['contents'][1]['text']=value['clubHead']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][2]['contents'][0]['contents'][1]['text']=value['shaftWeightStiffness']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][2]['contents'][1]['contents'][1]['text']=value['gripWeight']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][3]['contents'][0]['contents'][1]['text']=value['swingWeight']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][3]['contents'][1]['contents'][1]['text']=value['clubfaceAngle']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][4]['contents'][0]['contents'][1]['text']=value['lieAngle']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][5]['contents'][0]['contents'][1]['text']=value['remark']
										template['contents'].append(copy.deepcopy(templateAdd))

								if personalData=='球桿數據':
									playclubDB=MYSQLDB('playclubData')
									playclubSearch=(playclubDB.clubTableSearch('playclubData.name,playclubData.speed,playclubData.averageToTalDistance,playclubData.averageFlightDistance,playclubData.takeoffAngle,playclubData.ballSpeed,playclubData.remark','playclubData',event.uid))
									print(playclubSearch)
									template=copy.deepcopy(line.flexTemplate('carousel'))
									templateAdd = copy.deepcopy(line.flexTemplate('playclubInformation'))
									for index, value in enumerate(playclubSearch):
										templateAdd['body']['contents'][0]['contents'][0]['text']=value['name']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][1]['contents'][0]['contents'][1]['text']=value['speed']
										templateAdd['body']['contents'][0]['contents'][1]['contents'][1]['contents'][1]['contents'][1]['text']=f"{value['averageToTalDistance']}y"
										templateAdd['body']['contents'][0]['contents'][1]['contents'][2]['contents'][0]['contents'][1]['text']=f"{value['averageFlightDistance']}y"
										templateAdd['body']['contents'][0]['contents'][1]['contents'][2]['contents'][1]['contents'][1]['text']=f"{value['takeoffAngle']}°"
										templateAdd['body']['contents'][0]['contents'][1]['contents'][3]['contents'][0]['contents'][1]['text']=f"{value['ballSpeed']}"
										templateAdd['body']['contents'][0]['contents'][1]['contents'][4]['contents'][0]['contents'][1]['text']=value['remark']
										template['contents'].append(copy.deepcopy(templateAdd))

								line.replyFlex(template)					

							case data if data.startswith('postReserveProject:') and (user_status==True):
								reserveProjectName = (data.split(":"))[1]
								reserve.reserveDB.updateThreeSearchWhere('project',reserveProjectName,'userId',event.uid,'status','0',"company",company)
								reserve.reserveDB.updateThreeSearchWhere("dataTime",None,"userId",event.uid,"status","0","company",company)
								reserve.reserveDB.updateThreeSearchWhere("project",None,"userId",event.uid,"status","0","company",company)
								print(f"projectNameList$$${projectNameList}")
								if reserveProjectName in projectNameList:
									projectNameIdx = projectNameList.index(reserveProjectName)
									projectName=projectNameList[projectNameIdx]
									projectsDay=projectsDayList[projectNameIdx]
									projectsActive=projectsActiveList[projectNameIdx]
									projectsoffset=projectsoffsetList[projectNameIdx]
									projectsinterval=projectsintervalList[projectNameIdx]
									current_datetime = datetime.now()
									current = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
									nowtimestamp = current.timestamp()
									todayTimestamp=nowtimestamp+projectsDay+86400
									projectNameIdx = projectNameList.index(reserveProjectName)

									projectName=projectNameList[projectNameIdx]
									projectsDay=projectsDayList[projectNameIdx]
									projectsActive=projectsActiveList[projectNameIdx]
									projectsoffset=projectsoffsetList[projectNameIdx]
									projectsinterval=projectsintervalList[projectNameIdx]
									current_datetime = datetime.now()
									current = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
									nowtimestamp = current.timestamp()
									todayTimestamp=nowtimestamp+projectsDay+86400
									projectNameIdx = projectNameList.index(reserveProjectName)

									projectName=projectNameList[projectNameIdx]
									projectsDay=projectsDayList[projectNameIdx]
									projectsActive=projectsActiveList[projectNameIdx]
									projectsoffset=projectsoffsetList[projectNameIdx]
									projectsinterval=projectsintervalList[projectNameIdx]
									current_datetime = datetime.now()
									current = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
									nowtimestamp = current.timestamp()
									todayTimestamp=nowtimestamp+projectsDay+86400
									projectNameIdx = projectNameList.index(reserveProjectName)
									print('---------------projectNameIDx--------')
									print(projectNameIdx)
									print('---------------projectNameIDx--------')

									projectName=projectNameList[projectNameIdx]
									projectsDay=projectsDayList[projectNameIdx]
									projectsActive=projectsActiveList[projectNameIdx]
									projectsoffset=projectsoffsetList[projectNameIdx]
									projectsinterval=projectsintervalList[projectNameIdx]
									current_datetime = datetime.now()
									current = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
									nowtimestamp = current.timestamp()
									todayTimestamp=nowtimestamp+projectsDay+86400
									projectNameIdx = projectNameList.index(reserveProjectName)
									print('---------------projectNameIDx--------')
									print(projectNameIdx)
									print('---------------projectNameIDx--------')

									projectName=projectNameList[projectNameIdx]
									projectsDay=projectsDayList[projectNameIdx]
									projectsActive=projectsActiveList[projectNameIdx]
									projectsoffset=projectsoffsetList[projectNameIdx]
									projectsinterval=projectsintervalList[projectNameIdx]
									current_datetime = datetime.now()
									current = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
									nowtimestamp = current.timestamp()
									todayTimestamp=nowtimestamp+projectsDay+86400
									nextTimestamp=todayTimestamp+projectsoffset

									dayList=[]
									ranges = [(start, start + 86400 - 1) for start in publicBlackTimeList]

									while todayTimestamp < nextTimestamp:
										if not any(start <= todayTimestamp <= end for start, end in ranges):
											dayList.append(todayTimestamp)
										todayTimestamp += 86400
									template = copy.deepcopy(line.flexTemplate('appointmentNow'))
									template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
									template_page_item=copy.deepcopy(template['contents'][0])
									template['contents'][0]['body']['contents'] = []
									datapage = configs.appointment.datapage
									blackweekday=[]
									weekday_chinese = ['一', '二', '三', '四', '五', '六', '日']
									template['contents'][0]['header']['contents'][0]['text']=f'{reserveProjectName}-請選擇日期'
									for i in range(7):
										if (projectsActive[i][0][0]=="00:00" and projectsActive[i][0][1]=="00:00"):
											blackweekday.append(weekday_chinese[i])
									idex=1
									for idx,ts in enumerate(dayList):
										dt = datetime.fromtimestamp(ts)
										year = dt.year
										month = dt.month
										day = dt.day
										if not weekday_chinese[dt.weekday()] in blackweekday:
											typePage = (idex / datapage) + 1 if idex % datapage > 0 else (idex / datapage)
											typePage = int(typePage)
											if len(template['contents'])<typePage:
												template['contents'].append(copy.deepcopy(template['contents'][0]))
												template['contents'][typePage-1]['body']['contents'] = []
											template_item[0]['contents'][0]['text'] = f"{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})"
											template_item[0]['contents'][1]['action']['data'] = f"appointment_choose_time:{int(ts)}:project:{projectName}"
											template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[0]))
											template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[1]))
											idex+=1
											print(int(ts))
										else:
											print(weekday_chinese[dt.weekday()])
									line.replyFlex(template)
								else:
									line.doubleReplyMessageText(f'👨‍💻{reserveProjectName}尚未開放','☎️如有疑問請致電｜0919-102-803')				
							case data if data.startswith('appointment_choose_time:') and 'project:'in data:
								parts = data.split(":")
								timeUnix=parts[1]
								projectName=parts[3]
								reserve.reserveDB.updateThreeSearchWhere("project",projectName,"userId",event.uid,"status","0","company",company)

								if reserve.isReserveDBState(event.uid,company)=='noDataTime':
									projectNameIdx = projectNameList.index(projectName)
									projectName=projectNameList[projectNameIdx]
									projectsDay=projectsDayList[projectNameIdx]
									projectsActive=projectsActiveList[projectNameIdx]
									projectsoffset=projectsoffsetList[projectNameIdx]
									projectsinterval=projectsintervalList[projectNameIdx]
									projectSumberOfAppointments=projectSnumberOfAppointmentsList[projectNameIdx]
									projectGroupReserveStatus=projectGroupReserveStatusList[projectNameIdx]
									ALLprojectList = configsSearchDBProjectList[1:-1].split(',')

									AllProjectIndex=ALLprojectList.index(projectName)
									filterTimeUnix=[]
									element_count = {}

									# if projectsblockTimeList[projectNameIdx]:

									projectsblockTime=projectsblockTimeList[AllProjectIndex]
									def convert_to_timestamps(active_list):
										converted_active = []
										for time_range in active_list:
											converted_range = []
											for time_point in time_range:
												if time_point[0] is not None:
													start_time_str, end_time_str = time_point
													start_time = int(start_time_str.split(':')[0]) * 60 * 60 + int(start_time_str.split(':')[1])*60
													end_time = int(end_time_str.split(':')[0]) * 60 * 60 + int(end_time_str.split(':')[1])*60
													converted_range.append([int(start_time), int(end_time)] if time_range[0] is not None else [None, None])
												else:
													converted_range.append([None, None])
											converted_active.append(converted_range)
										return converted_active
									weekday_chinese = ['一', '二', '三', '四', '五', '六', '日']
									dt = datetime.fromtimestamp(int(timeUnix))
									print(f"{dt.year}/{dt.month}/{dt.day} ({weekday_chinese[dt.weekday()]})")
									unixActive=convert_to_timestamps(projectsActive)
									unixTimeActive=[]
									if((unixActive[dt.weekday()])[1][0]==None):
										while (unixActive[dt.weekday()][0][0])<(unixActive[dt.weekday()][0][1]):
											print('----unixActive[dt.weekday()][0][0]----')
											print(unixActive[dt.weekday()][0][0])
											print(unixActive[dt.weekday()][0][1])
											print(projectsActive)
											print(unixActive)
											print(f'dt.weekday():{dt.weekday()}')
											print('----unixActive[dt.weekday()][0][0]----')
											unixTimeActive.append((unixActive[dt.weekday()][0][0])+(int(dt.timestamp())))
											unixActive[dt.weekday()][0][0]+=projectsinterval
										print(int(dt.timestamp()))
										# timestamp = datetime.strptime(date_string, date_format).timestamp()
									else:
										while (unixActive[dt.weekday()][0][0])<(unixActive[dt.weekday()][0][1]):
											unixTimeActive.append((unixActive[dt.weekday()][0][0])+(int(dt.timestamp())))
											unixActive[dt.weekday()][0][0]+=projectsinterval
										while(unixActive[dt.weekday()][1][0])<(unixActive[dt.weekday()][1][1]):
											unixTimeActive.append((unixActive[dt.weekday()][1][0])+(int(dt.timestamp())))
											unixActive[dt.weekday()][1][0]+=projectsinterval
									uniqueUnixTimeActive = list(set(unixTimeActive))
									sortedUnixTimeActive = sorted(uniqueUnixTimeActive)

									print(f'sortedUnixTimeActive${sortedUnixTimeActive}')
									print(f'projectsblockTime{projectsblockTime}')

									filterBlackTimeUnix = [timestamp for timestamp in sortedUnixTimeActive if not any(range_item[0] <= timestamp <= range_item[1] for range_item in projectsblockTime)]
									if (projectGroupReserveStatus=='own'):
										historydate = reserve.reserveDB.TableThreeSearch('project',projectName,'status','1','company',company)
										historyDataTime = [item['dataTime'] for item in historydate]
										# historyDataTimeFormatYYYYMMDD=(datetime.fromtimestamp(int(historyDataTime),TZ)).strftime('20%y年%m月%d日')
										# if 
										print('-----x-x--xx--x-x')
										print(historyDataTime)
										for x in historyDataTime:
											element_count[x] = element_count.get(x, 0) + 1
										print(element_count)
										filterTimeUnix = [x for x in filterBlackTimeUnix if element_count.get(x, 0) < projectSumberOfAppointments]
									if (projectGroupReserveStatus=='groupReserve'):
										groupProjectList = []
										# numberAppointments=''
										for group, details in projectGroupNameList.items():
											print('test--------')
											print(AllProjectIndex)
											print(f'project{projectNameIdx+1}')
											print(details)
											print('test--------')
											if f'project{AllProjectIndex+1}' in details['projectList']:
												for item in details['projectList']:
													print('======item=====')
													groupProjectList.append(item)
													print('======item=====')
												print(f"project{projectNameIdx+1} is in group {group}")
												numberAppointments=details['numberAppointments']
										print(f'groupProjectList:{groupProjectList}')
										print('projectDetails------')
										# print(projectDetails)
										# print(projectDetails[groupProjectList[0]])
										groupProjectName=[]

										for projectNumber in groupProjectList:
											groupProjectName.append({projectDetails[projectNumber]['name']:projectDetails[projectNumber]['numberOfAppointments']})
										print(groupProjectName)
										# groupProjectUnixNumber={}
										for item in groupProjectName:
											for projectOneName , number in item.items():
												print('=-----------projectOneName-----')
												print(projectOneName)
												searchGroupHistoryUnixTime=reserve.reserveDB.TableThreeSearch('project',projectOneName,'status','1','company',company)
												if searchGroupHistoryUnixTime:
													for data in searchGroupHistoryUnixTime:
														found = False
														print("測試")
														for entryTime,entryNummber in element_count.items():
															print('---entry')
															print(entryTime, entryNummber)
															print(data['dataTime'])
															if data['dataTime'] == entryTime:
																element_count[data['dataTime']] += number
																found = True

																break
														if not found:
															element_count[data['dataTime']]=number

														# for key,value in groupProjectUnixNumber.items():
															# if key in 
														
												print('=-----------projectOneName-----')
										print(element_count)
										print(f'numberAppointments:{numberAppointments}')
										print(f'element_count:{element_count}')
										print(f'filterBlackTimeUnix:{filterBlackTimeUnix}')
										print(f'projectSumberOfAppointments:{projectSumberOfAppointments}')
										print(type(numberAppointments))
										print(int(projectSumberOfAppointments))
										print(type(projectSumberOfAppointments))
										print(numberAppointments-projectSumberOfAppointments)
										filterTimeUnix = [x for x in filterBlackTimeUnix if element_count.get(x, 0) <= int(numberAppointments)-int(projectSumberOfAppointments)]
										print(filterTimeUnix)
									# filterTimeUnix = [x for x in filterBlackTimeUnix if x not in historyDataTime]
									filterTimeYYYYDDList=[]
									print(f'filterTimeUnix:{filterTimeUnix}')
									dateFormatYYYYMMDD=(datetime.fromtimestamp(int(filterTimeUnix[0]),TZ)).strftime('20%y年%m月%d日')
									for filterTimeYYYYDD in filterTimeUnix:
										dt = datetime.fromtimestamp(filterTimeYYYYDD,TZ).strftime('%H:%M')
										filterTimeYYYYDDList.append(dt)

									# if len(filterTimeYYYYDDList)<1:
										# line.replyText(f'({})當日預約已滿請上方從選擇日期')
									# else:
									template = copy.deepcopy(line.flexTemplate('appointmentNow'))
									template_item = copy.deepcopy(template["contents"][0]['body']['contents'])
									template['contents'][0]['header']['contents'][0]['text']=dateFormatYYYYMMDD
									template['contents'][0]['body']['contents'] = []
									timepage= configs.appointment.timepage
									for idx,ts in enumerate(filterTimeYYYYDDList):
										idx+=1
										typePage = (idx / timepage) + 1 if idx % timepage > 0 else (idx / timepage)
										typePage = int(typePage)
										if len(template['contents'])<typePage:
											template['contents'].append(copy.deepcopy(template['contents'][0]))
											template['contents'][typePage-1]['body']['contents'] = []
										template_item[0]['contents'][0]['text'] = ts
										template_item[0]['contents'][1]['action']['data'] = f"appointment_confirm_reserve:{filterTimeUnix[idx-1]}"
										template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[0]))
										template["contents"][typePage-1]['body']['contents'].append(copy.deepcopy(template_item[1]))
									# print(template)
									line.replyFlex(template)

							case data if data.startswith('buyBallRoll:') and (user_status==True):
								reserve.reserveDB.updateThreeSearchWhere("dataTime",None,"userId",event.uid,"status","0","company",company)
								reserve.reserveDB.updateThreeSearchWhere("project",None,"userId",event.uid,"status","0","company",company)
								urlList=["https://i.imgur.com/HD83R4p.png","https://i.imgur.com/ekSGB7U.png","https://i.imgur.com/HYbdtoZ.png"]
								template=copy.deepcopy(line.flexTemplate('carousel'))
								ballRoll = copy.deepcopy(line.flexTemplate('ballRoll'))
								i=0
								if searchBallRollfillterTrue:
									for key,value in searchBallRollfillterTrue.items():
										k=i%3
										ballRoll['hero']['contents'][0]['contents'][0]['url']=urlList[k]
										ballRoll['hero']['contents'][0]['contents'][1]['text']=value['courtName']
										ballRoll['hero']['contents'][1]['contents'][0]['action']['data']=f"chooseBallRoll:{value['courtName']}"

										template['contents'].append(copy.deepcopy(ballRoll))
										i+=1
									line.replyFlex(template)
								else:
									line.doubleReplyMessageText(f'👨‍💻球卷尚未開放','☎️如有疑問請致電｜0919-102-803')				

							case data if data.startswith('chooseBallRoll:'):
								currentDate=datetime.now()
								first_day_of_month = currentDate.replace(day=1, hour=0, minute=0, second=0 ,microsecond=0)
								unix_timestamp = int(first_day_of_month.timestamp())

								parts = data.split(":")
								ballRollName = parts[1] if len(parts)>1 else None
								for key, value in searchBallRollfillterTrue.items():
									if value.get('courtName') == ballRollName:
										monthNumber = value.get('monthNumber', {})
								filtered_month_number = {key: value for key, value in monthNumber.items() if int(key) >= unix_timestamp}
								yearMonthDict = [datetime.utcfromtimestamp((int(timestamp)+86400)).strftime('%Y/%m') for timestamp in filtered_month_number.keys()]
								yearMonthValueDict=[]
								underButtonTextList=[]
								underButtonData=[]
								for key ,value in filtered_month_number.items():
									yearMonthValueDict.append(value)
								for i in range(ballRollNumber):
									underButtonTextList.append(yearMonthDict[i])
									underButtonData.append(f'ballRollunixTime:{yearMonthDict[i]}:ballRollnumber:{yearMonthValueDict[i]}:ballRollName:{ballRollName}')
								print('-----underButtonTextList----')
								print(underButtonTextList)
								print(type(underButtonData))
								template=functionTemplate.postUnderTemplate(underButtonTextList,underButtonData,f"目前已選擇{ballRollName}\n請於下方選擇月份")
								line.replyMessage(template)

								# reserve.reserveDB.updateThreeSearchWhere("project",ballRollName,"userId",event.uid,"status","0","company",company)
							case data if data.startswith('ballRollunixTime:') and ('ballRollnumber:' in data) and ('ballRollName:' in data):
								parts = data.split(":")
								unixTime=parts[1]
								number=parts[3]
								name=parts[5]
								input_date = datetime.strptime(unixTime, '%Y/%m')
								first_day_of_month = input_date.replace(day=1, hour=0, minute=0, second=0)
								unix_timestamp = int(first_day_of_month.timestamp())


								underButtonTextList=['1張','2張','3張','4張']
								underButtonData=[f'ballRollunixTime:{unixTime}:number:{1}:ballRollName:{name}',f'ballRollunixTime:{unixTime}:number:{2}:ballRollName:{name}',f'ballRollunixTime:{unixTime}:number:{3}:ballRollName:{name}',f'ballRollunixTime:{unixTime}:number:{4}:ballRollName:{name}']
								template=functionTemplate.postUnderTemplate(underButtonTextList,underButtonData,f"請選擇數量")

								print(template)

								line.replyMessage(template)
							case data if data.startswith('ballRollunixTime:') and ('number:' in data) and ('ballRollName:' in data):
								parts = data.split(":")
								unixTime=parts[1]
								number=parts[3]
								name=parts[5]
								date_object = datetime.strptime(unixTime, "%Y/%m")
								first_day_of_month = date_object.replace(day=1, hour=0, minute=0, second=0)
								unix_timestamp = int(first_day_of_month.timestamp())

								memberSearchData=member.dbSearch(event.uid,company)
								template = copy.deepcopy(line.flexTemplate('appointment confirmation'))
								template['body']['contents'][2]['contents'][0]['contents'][1]['text']=memberSearchData['name']
								template['body']['contents'][2]['contents'][2]['contents'][1]['text']=memberSearchData['phone']
								template['body']['contents'][3]['contents'][0]['action']['data']=f'ballRollConfirmf:ballRollunixTime:{unixTime}:number:{number}:ballRollName:{name}'
								# timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(isReserveFunction.shortDBSearch()[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")
								# timeFormatYYYYMMDDhhmm=(datetime.fromtimestamp(reserve.reserveDB.TableThreeSearch('userId',event.uid,'status','0',"company",company)[0]['dataTime'],TZ)).strftime("%Y年%m月%d日 %H:%M")
								reserveProjectName=reserve.reserveDB.TableThreeSearch('userId',event.uid,'status','0','company',company)[0]['project']
								template['body']['contents'][2]['contents'][4]['contents'][1]['text']=name

								template['body']['contents'][2]['contents'][6]['contents'][1]['text']=unixTime
								template['body']['contents'][1]['text']='球卷確認單'
								line.replyFlex(template)

							case data if data.startswith('ballRollConfirmf:ballRollunixTime:') and ('number:' in data) and ('ballRollName:' in data):
								reserveCount= configs.appointment.reserveCount
								# isReserveFunction=reserve.ShortAndHistoryReserveFunction(event.uid)
								NOTIFYTOKEN=configs.appointment.NOTIFYTOKEN
								# historySearchStatusUserId=isReserveFunction.historyDBSearchStatusUserId()
								parts = data.split(":")
								unixTime=parts[2]
								number=parts[4]
								name=parts[6]
								
								date_object = datetime.strptime(unixTime, "%Y/%m")
								first_day_of_month = date_object.replace(day=1, hour=0, minute=0, second=0)
								unix_timestamp = int(first_day_of_month.timestamp())
								# for i in number:
								# 	reserve.reserveDB.updateThreeSearchWhere("project",name,"userId",event.uid,"status","0","company",company)
								# 	reserve.reserveDB.updateThreeSearchWhere("dataTime",unix_timestamp,"userId",event.uid,"status","0","company",company)
								# 	reserve.reserveDB.TableThreeSearch('userid',event.uid,'status','ballRoll','company',company)
								historySearchStatusUserId = reserve.reserveDB.TableThreeSearch('userid',event.uid,'status','ballRoll','company',company)
								getReserveTimeList = [item['dataTime'] for item in historySearchStatusUserId]
								nowTime=getDatetime()
								nowTimeUinx=int(nowTime.timestamp())
								print(f'getReserveTimeList:{getReserveTimeList}')
								print(f'historySearchStatusUserId:{historySearchStatusUserId}')

								count = len({x for x in getReserveTimeList if x is not None and x > int(nowTimeUinx)})
								print(f'count{count}')
								print(reserveCount)
								if not reserve.reserveDB.execute_query(f"SELECT * FROM reserve WHERE userId = '{event.uid}' AND (dataTime IS NULL OR project IS NULL) AND company = '{company}'"):
									if count< reserveCount:
										print('------------')
										# userReservedate=isReserveFunction.historyDBAdd()
										userReservedate=reserve.reserveDB.rdbmsSearch(company,event.uid)[0]
										for i in number:
											reserve.reserveDB.Insert(("userId","company","project","dataTime","status",),(event.uid,company,name,unix_timestamp,"ballRoll",))

										print(userReservedate)
										notifyFunction=notify(NOTIFYTOKEN)
										# print((userReservedate))
										# print(reserve.reser)
										unixTime=userReservedate['dataTime']
										date_object = datetime.utcfromtimestamp(unixTime)
										year_month_str = date_object.strftime('%Y/%m')

										print(userReservedate['dataTime'])
										notifyTime=(datetime.fromtimestamp(userReservedate["dataTime"])).strftime('%Y年%m月%d日 %H:%M')
										notifyFunction.SendMessage(f'\n姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n球場:{userReservedate["project"]}\n球卷月份:{year_month_str}\n點擊預約時間\n{userReservedate["auto_updae_time"]}\n')
										line.replyText(f'姓名:{userReservedate["name"]}\n電話:{userReservedate["phone"]}\n球場:{userReservedate["project"]}\n球卷月份:{year_month_str}')
									else:
										line.replyText('系統自動判斷目前您以有預約時段,請點擊會員查詢確認時段是否預約,若無預約煩請致電～')
									# isReserveFunction.historyDBUpdate(memberDate)

									# isReserveFunction.shortDBDelete()
									# print("確認預約")
								else:
									line.replyText('目前系統尚無預約資料，請從新預約！！！')
							case data if (user_status!=True) and (data.startswith('postReserveProject:') or data.startswith('buyBallRoll:')):
								template = line.flexTemplate('first')
								line.doubleReplyFlexMessageText('您尚未註冊會員下方功能無法使用',template,'註冊訊息')
		# when error
		# except Exception as error:
		# 	print("Error [main]: ", type(error).__name__, " - ", error)
		# 	return jsonify({'status': 500})
		# end
		return jsonify({"status": "OK"})
	else:return print('無此公司')
print('test================')
def getIsProject(phone):
	testDb = MYSQLDB('bot_configs')
	LineToken = (testDb.TableOneSearch("companyphone",phone))[0]['lineConfig']
	if (LineToken):
		LineToken_dict = json.loads(LineToken)
	else:
		print('LINETOKEN iS NO EXSIT')
	print(f'LineToken{LineToken}')


	publicData = (testDb.TableOneSearch("companyphone",phone))[0]['deniedDates']
	print('----publicData----')
	print(publicData)
	publicBlackTimeList = []
	if publicData is not None:
		publicData_dict = json.loads(publicData)
		publicBlackTimeList = [item["deniedDates"] for item in publicData_dict if item["status"] == 0]

	searchBallRoll = (testDb.TableOneSearch("companyphone",phone))[0]['ballRoll']

	if (searchBallRoll):

		searchBallRoll_dict = json.loads(searchBallRoll)
		searchBallRollfillterTrue = {key: value for key, value in searchBallRoll_dict.items() if value.get("status") == "True"}
	else:
		searchBallRollfillterTrue=''
	ballRollNumber = (testDb.TableOneSearch("companyphone",phone))[0]['ballRollTime']


	rusult = (testDb.TableOneSearch("companyphone",phone))[0]['projectactivetimesblacktime']
	result_dict = json.loads(rusult)

	projects_with_status_1 = [project for project, details in result_dict.items() if details.get("status") == 1 and details.get("name") is not None and len(details.get("name")) > 0]
	print("Status 为 1 的项目有：", projects_with_status_1)
	projectsName = [details.get('name') for project, details in result_dict.items() if details.get('status') == 1 and details.get('name')]

	projectsShowText = [details.get('showText') for project, details in result_dict.items() if details.get('status') == 1 and details.get('showText')]
	# print('===projectsShowText====')
	# print(projectsShowText)
	projectsActive = [details.get('active') for project, details in result_dict.items() if details.get('status') == 1 and details.get('active')]
	# print('===projectsactive====') [0]星期一 [1]星期二 [2]星期三
	# print(projectsActive)
	#專案往後日期
	projectsDay = [details.get('day') for project, details in result_dict.items() if details.get('status') == 1]
	print('-----projectsDay-----')
	print(projectsDay)
	print('-----projectsDay-----')

	#專案預約時間
	projectsinterval = [details.get('interval') for project, details in result_dict.items() if details.get('status') == 1 and details.get('interval')]
	print('測試中')
	print(projectsinterval)
	projectsoffset = [details.get('offset') for project, details in result_dict.items() if details.get('status') == 1 and details.get('offset')]
	# print('=======result_dict======')
	# print(result_dict)
	# print('=======result_dict======')
	reserveProjectListStr = ((testDb.TableOneSearch("companyphone",phone))[0]['projectList'])
	if reserveProjectListStr:
		list(reserveProjectListStr)
	else:
		print('CONFIG_BOT設定檔案ProjectList欄位為必填')
	# projectsblockTime = [details.get('blockTime') for project, details in result_dict.items() if details.get('status') == 1 and details.get('blockTime') else []]
	
	projectsblockTime=[]
	for project ,details in result_dict.items():
		if details.get('status') == 1 and details.get('blockTime'):
			projectsblockTime.append(details.get('blockTime'))
		else:
			projectsblockTime.append([])

	projectSnumberOfAppointments=[]
	for project ,details in result_dict.items():
		if details.get('status') == 1 and details.get('numberOfAppointments'):
			projectSnumberOfAppointments.append(details.get('numberOfAppointments'))
		# else:
			# projectSnumberOfAppointments.append([])

	projectGroupReserveStatus=[]
	for project ,details in result_dict.items():
		if details.get('status') == 1 and details.get('groupReserveStatus'):
			projectGroupReserveStatus.append(details.get('groupReserveStatus'))

	projectGroupNameList=result_dict['projectGroupName']

	return reserveProjectListStr,LineToken_dict,ballRollNumber,searchBallRollfillterTrue,result_dict,projects_with_status_1,projectsName,projectsActive,projectsDay,projectsinterval,publicBlackTimeList,projectsoffset,projectsblockTime,projectSnumberOfAppointments,projectGroupReserveStatus,projectGroupNameList

def posDB():
	posOrderDb = MYSQLDB(
		table='customers',
		host = "pos-db.alpaca.tw",
		port=3316,
		user="root",
		password="=?michi_pos/=!",
		database="hongyun_pos"
	)
posDB()
def memberData(phone,userId):
	memberDB=MYSQLDB('member')
	memberData=memberDB.TableTwoSearch('company',phone,'userId',userId)
	if memberData:
		memberData[0]
	return memberData
# print((result_dict))
print('test================')
def pushRemindMessage():
	today = datetime.now()
	tomorrow = today + timedelta(days=1)
	start_of_day = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
	end_of_day = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59)
	start_unix_timestamp = int(start_of_day.timestamp())
	end_unix_timestamp = int(end_of_day.timestamp())
	current_unix_time = int(time.time())
	template = copy.deepcopy(line.flexTemplate('reserveRemind'))
	# if reserve.reserveDB.TableTwoSearch('dataTime',current_unix_time,'status','1'):
	reserveList=reserve.reserveDB.TableOneSearch('status','1')
	print(start_unix_timestamp)
	print(end_unix_timestamp)
	for index,item in enumerate(reserveList):
		if (item['dataTime']<end_unix_timestamp and item['dataTime']>start_unix_timestamp):
			datetime_object=(datetime.fromtimestamp(item['dataTime'], TZ))
			formattedDate=datetime_object.strftime('%Y/%m/%d %H:%M')
			template['body']['contents'][1]['contents'][0]['text']=item['project']
			template['body']['contents'][2]['contents'][0]['text']=formattedDate
			line.pushFlexMessage(item['userId'],template)

	# reserve.reserveDB.TableOneSearch('dataTime')


# while True:
#     schedule.run_pending()
#     time.sleep(1)

if __name__ == '__main__':
	app.debug =True
	app.run(host='0.0.0.0', port=85)
