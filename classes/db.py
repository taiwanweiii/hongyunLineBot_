from tinydb import TinyDB, Query
import mysql.connector

class DB:
    def __init__(self, dbName=''):
        db = TinyDB(f"databases/{dbName}.json",encoding="utf-8")
        self.insertMult = db.insert_multiple
        self.search = db.search
        self.update = db.update
        self.insert = db.insert
        self.delete = db.remove
        self.contains=db.contains
        self.getdata=db.get
        self.all=db.all

class MYSQLDB:
    def __init__(self,table,host='localhost',user="root",password='',database='line_bot_configs',port=3306):
        self.connection = self.openConnection(host=host,user=user,password=password,database=database,port=port)
        self.cursor = self.connection.cursor(dictionary=True)
        self.table= table
    #DB Search
    def allTableSearch(self):
        try:
            self.cursor.execute(f"SELECT * FROM {self.table}")
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.allTableSearch is Error:'+e)
    def TableOneSearch(self,whereTable,whereValue):
        try:
            self.cursor.execute(f"SELECT * FROM {self.table} WHERE {whereTable} = %s",(whereValue,))
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableOneSearch is Error:'+e)
    def TableTwoSearch(self,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue):
        try:
            self.cursor.execute(f"SELECT * FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s",(oneWhereValue,twoWhereValue))
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableTwoSearch is Error:'+e)
    def TableThreeSearch(self,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue,threeWhereTable,threeWhereValue):
        try:
            self.cursor.execute(f"SELECT * FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s AND {threeWhereTable} = %s" ,(oneWhereValue,twoWhereValue,threeWhereValue))
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableTwoSearch is Error:'+str(e))
    
    def rdbmsSearch(self,company,userId):
        try:
            self.cursor.execute(f"""
                                    SELECT member.name, member.phone, member.userId, reserve.dataTime, reserve.project, reserve.auto_updae_time 
                                    FROM {self.table} 
                                    JOIN member ON {self.table}.userId = member.userId 
                                    Where status=0 AND reserve.company='{company}' and member.userId='{userId}'
                                """)
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.rdbmsSearch is Error:'+str(e))
    def TableOneSearchAddField(self,field,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue):
        try:
            self.cursor.execute(f"SELECT {field} FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s",(oneWhereValue,twoWhereValue))
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableOneSearchAddField is Error:'+e)
    def execute_query(self, query, params=None):
        """
        執行 SQL 查詢。

        Parameters:
        - query (str): SQL 查詢語句。
        - params (tuple): 查詢中的參數，如果有的話。

        Returns:
        - list: 查詢結果的列表。
        """
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        return result
    def memberPhone(self,oneWhereTable,oneWhereValue):
        try:
            self.cursor.execute(f"SELECT phone FROM {self.table} WHERE {oneWhereTable} = %s",(oneWhereValue,))
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableOneSearchAddField is Error:'+e)
    
    def clubTableSearch(self,filed,joinTable,userId):
        try:
            self.cursor.execute(f"SELECT member.name, member.phone,{filed} FROM {self.table} INNER JOIN member ON member.phone = {joinTable}.memberphone WHERE member.userId = %s",(userId,))
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableOneSearchAddField is Error:'+e)
    
    #DB Search

    #DB Update   
    def updateOneSearchWhere(self,field,fieldValue,whereField,whereValue):
        self.cursor.execute(f"UPDATE {self.table} SET {field} = %s WHERE {whereField} = %s",(f"{fieldValue}",f"{whereValue}"))
        self.connection.commit()
        print('updateOneSearchWhere 執行成功')
    def updateTwoSearchWhere(self,field,fieldValue,whereField,whereValue,twoWhereField,twoWhereValue):
        self.cursor.execute(f"UPDATE {self.table} SET {field} = %s WHERE {whereField} = %s AND {twoWhereField}=%s ",(fieldValue,whereValue,twoWhereValue))
        self.connection.commit()
        print('updateTwoSearchWhere 執行成功')
    def updateThreeSearchWhere(self,field,fieldValue,whereField,whereValue,twoWhereField,twoWhereValue,threeWhereField,threeWhereValue):
        self.cursor.execute(f"UPDATE {self.table} SET {field} = %s WHERE {whereField} = %s AND {twoWhereField}=%s AND {threeWhereField} = %s",(fieldValue,whereValue,twoWhereValue,threeWhereValue))
        self.connection.commit()
        print('updateTwoSearchWhere 執行成功')

    #DB Update

    #DB INSERT
    def Insert(self , addFieldName=None ,addFieldValue=None):
        print(f'addFieldName{addFieldName}')
        print(f'addFieldValue:{addFieldValue}')
        print(f"INSERT INTO {self.table} {addFieldName} VALUES {addFieldValue} ")
        field_names = ', '.join(addFieldName)
        placeholders = ', '.join(['%s' for _ in addFieldValue])
        sql_query = f"INSERT INTO {self.table} ({field_names}) VALUES ({placeholders})"
        self.cursor.execute(sql_query, addFieldValue)
        self.connection.commit()
        print('Insert 成功新增')
    def insertMember(self,userId,company):
        try:
            self.cursor.execute(f"INSERT INTO {self.table} (userId,company) VALUES (%s,%s)",(userId,company))
            self.connection.commit()
            print('會員UserID成功新增')

            # self.cursor.execute(f"INSERT INTO {self.table} (userId,company) VALUES (%s,%s)",(userId,company))

            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableOneSearchAddField is Error:'+e)    #DB INSERT

    #DB DELETE
    def Delete(self,table,field,delValue):
        self.cursor.execute(f"DELETE FROM {self.table} WHERE {field}=%s",(delValue))
    #DB DELETE

    #DB ROOT Update Dele Add
    def executeUpdate(self, query, params=None):
        """
        執行 SQL 更新操作。

        Parameters:
        - query (str): SQL 更新操作語句。
        - params (tuple): 更新操作中的參數，如果有的話。
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error executing update: {e}")
            self.connection.rollback()
            return 'Class.db.executeUpdate:ERROR!!!' 
    #DB ROOT

    #DB connection
    def openConnection(self, host='localhost',user="root",password='',database='line_bot_configs',port=3306):
        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
    #DB Close Connection
    def closeConnection(self):
        self.cursor.close()
        self.connection.close()
