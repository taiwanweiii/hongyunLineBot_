from classes.db import *
import re

def dbSearch(userId,client):
    memberDB= MYSQLDB('member')
    user = memberDB.dynamicTableSearch({"userId":userId,"company":client})
    if user:
          user=user[0]
    return user

def isMember(userId,client):
    global memberDB 
    posCustomerDb = MYSQLDB(
		table='customers',
		# host = "pos-db.alpaca.tw",
        # host="172.19.0.4",
        host="127.0.0.1",
		# port=3316,
		user="root",
		# password="=?michi_pos/=!",
        password="root",
		database="hongyun_pos"
	)

    memberDB= MYSQLDB('member')
    user = memberDB.dynamicTableSearch({"userId":userId,"company":client})

    if len(user) < 1 : return 'nouser'
    user = user[0]
    if user['phone'] == None : return 'phone'
    if user['name'] == None : return 'name'
    if user['sex']==None:return 'sex'
    if not posCustomerDb.TableOneSearch('phone',user['phone']):
        sex_mapping = {"男": 1, "女": 0}
        sex_value = sex_mapping.get(user['sex'], None)

        posCustomerDb.Insert(('line_id','name','phone','sex'),(user['userId'],user['name'],user['phone'],sex_value))

    return True
def isPhoneRepeat(client):
    memberDB= MYSQLDB('member')

    phoneData=memberDB.dynamicTableSearch({"company":client})
    phones = [entry['phone'] for entry in phoneData if entry['phone'] is not None]
    return phones
# memberDB = DB('members')

# def isMember(userId):
#     user = memberDB.search(Query().userId == userId)
#     if len(user) < 1 : return 'nouser'
#     user = user[0]
#     if user['name'] == None : return 'name'
#     if user['phone'] == None : return 'phone'
#     return True
    # else
def isPhone(phone):
	if re.match(r'^0[1-9][0-9]{8}$', phone):
		return True
	else:
		return False


# def add(userId, name=None, phone=None,):
# 	new_item = {"userId": userId,'name':name ,"phone": phone,}
# 	memberDB.insert(new_item)

# def update(userId, data):
# 	memberDB.update(data,Query().userId == userId)

# def search(userId):
# 	return memberDB.search(Query().userId == userId)

