from classes.db import *
from functions import member
import datetime
import copy

# reserveDB = DB('reserve')


    # else

# def add(userId, dataTime=None,project=None,status='0',):
# 	new_item = {"userId": userId,'dataTime':dataTime ,"project":project,"status":status}
# 	reserveDB.insert(new_item)
# def update(userId, data):
# 	reserveDB.update(data,Query().userId == userId)
# def delete(userId):
# 	reserveDB.delete(Query().userId == userId)
# def contains(userId):
# 	return reserveDB.contains(Query().userId == userId)
# def getdata(userId):
# 	return reserveDB.getdata(Query().userId == userId)
# def search(userId):
# 	return reserveDB.search(Query().userId==userId)
# def all():
# 	return reserveDB.all()
	
# #兩個以上
# class ShortAndHistoryReserveFunction:
# 	def __init__(self,userId):
# 			self.uid=userId
# 			self.shortdata=(Query().status== '0') &(Query().userId==userId)
# 			self.historydata=(Query().status== '1') 
# 			print(self.shortdata)
# 		#short 查詢刪除更新

# 	def shortDBSearch(self):
# 		return reserveDB.search(self.shortdata)
# 	def shortDBDelete(self):
# 		reserveDB.delete(self.shortdata)
# 	def shortDBUpdate(self,data):
# 		reserveDB.update(data,self.shortdata)
# 	def shortDBcontains(self):
# 		return reserveDB.contains((Query().status== '0') &(Query().userId==self.uid))
# 		#history 添加查詢
# 	def historyDBAdd(self):
# 		memberDate=(member.search(self.uid)[0])
# 		shortReserveDate=reserveDB.search(self.shortdata)[0]
# 		reserveList=copy.deepcopy({})
# 		reserveList.update(memberDate)
# 		reserveList.update(shortReserveDate)
# 		reserveList['status']='1'
# 		reserveTimeNow=datetime.datetime.now()
# 		reserveTimeNowUnix=reserveTimeNow.timestamp()
# 		reserveList.update({"reserveNowTime": str(reserveTimeNow)})
# 		reserveDB.insert(reserveList)
# 		reserveDB.update({'dataTime':None,'project':None},self.shortdata)
# 		return(reserveList)

# 	def historyDBSearch(self):
# 		return reserveDB.search(self.historydata)
# 	def historyDBSearchStatusUserId(self):
# 		return reserveDB.search((Query().status== '1') &(Query().userId==self.uid))
# 	def historyDBUpdate(self,data):
# 		reserveDB.update(data,self.historydata)
# 		print("historyDbup")

# def isShortReserveDBState(userid):
# 	shortReserveDBState = reserveDB.search(self.shortdata)
# 	shortReserveDBState = shortReserveDBState[0]
# 	if shortReserveDBState['project'] == None : return 'noProject'
# 	if shortReserveDBState['dataTime']==None  : return 'noDataTime'
# 	return True

reserveDB=MYSQLDB('reserve')

def isReserveDBState(userid,company):

	isReserveDBState=reserveDB.TableThreeSearch('userId',userid,'status','0','company',company)
	if (isReserveDBState):
		isReserveDBState=isReserveDBState[0]
	# isReserveDBState = isReserveDBState[0]
	if isReserveDBState['project'] == None : return 'noProject'
	if isReserveDBState['dataTime']==None  : return 'noDataTime'
	return True
