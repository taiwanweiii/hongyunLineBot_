from classes.db import *
def posDB(tableName):
	posOrderDb = MYSQLDB(
		table=tableName,
        # host="172.19.0.4",
    	host= '127.0.0.1',
		# host = "pos-db.alpaca.tw",
		# port=3316,
		user="root",
		# password="=?michi_pos/=!",
		password="root",
		database="hongyun_pos"
	)
	return posOrderDb