from tinydb import TinyDB, Query
import mysql.connector
from time import sleep

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
    # def __init__(self,table,host='172.19.0.2',user="root",password='root',database='line_bot_configs',port=3306):
    def __init__(self,table,host='127.0.0.1',user="root",password='root',database='line_bot_configs',port=3306):
        self.host =host
        self.user = user 
        self.password=password
        self.database=database
        self.port=port
        self.connection = self.openConnection()
        self.cursor = self.connection.cursor(dictionary=True)
        self.table= table
    #DB Search
    def allTableSearch(self):
        query = f"SELECT * FROM {self.table}"
        return self.executeQuery(query)

            # self.cursor.execute(f"SELECT * FROM {self.table}")
            # return self.cursor.fetchall()
        # except Exception as e:
            # print('class.db.allTableSearch is Error:'+e)
    def TableOneSearch(self,whereTable,whereValue):
        query = f"SELECT * FROM {self.table} WHERE {whereTable} = %s"
        return self.executeQuery(query, (whereValue,))
    def dynamicTableSearch(self, conditions):
        query = f"SELECT * FROM {self.table} WHERE "
        where_clause = " AND ".join([f"{key} = %s" for key in conditions.keys()])
        query += where_clause
        return self.executeQuery(query, tuple(conditions.values()))

        # try:
        #     self.cursor.execute(f"SELECT * FROM {self.table} WHERE {whereTable} = %s",(whereValue,))
        #     return self.cursor.fetchall()
        # except Exception as e:
        #     print('class.db.TableOneSearch is Error:'+e)
    # def TableTwoSearch(self,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue):
    #     try:
    #         self.cursor.execute(f"SELECT * FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s",(oneWhereValue,twoWhereValue))
    #         return self.cursor.fetchall()
    #     except Exception as e:
    #         print('class.db.TableTwoSearch is Error:'+e)
    # def TableThreeSearch(self,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue,threeWhereTable,threeWhereValue):
    #     try:
    #         self.cursor.execute(f"SELECT * FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s AND {threeWhereTable} = %s" ,(oneWhereValue,twoWhereValue,threeWhereValue))
    #         return self.cursor.fetchall()
    #     except Exception as e:
    #         print('class.db.TableTwoSearch is Error:'+str(e))
    # def TableFourSearch(self,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue,threeWhereTable,threeWhereValue,fourWhereTable,fourWhereValue):
    #     try:
    #         self.cursor.execute(f"SELECT * FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s AND {threeWhereTable} = %s AND {fourWhereTable}=%s" ,(oneWhereValue,twoWhereValue,threeWhereValue,fourWhereValue))
    #         return self.cursor.fetchall()
    #     except Exception as e:
    #         print('class.db.TableTwoSearch is Error:'+str(e))
    # def TableFiveSearch(self,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue,threeWhereTable,threeWhereValue,fourWhereTable,fourWhereValue,fiveWhereTable,fiveWhereValue):
    #     try:
    #         self.cursor.execute(f"SELECT * FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s AND {threeWhereTable} = %s AND {fourWhereTable}=%s AND {fiveWhereTable}=%s" ,(oneWhereValue,twoWhereValue,threeWhereValue,fourWhereValue,fiveWhereValue))
    #         return self.cursor.fetchall()
    #     except Exception as e:
    #         print('class.db.TableTwoSearch is Error:'+str(e))

    
    def rdbmsSearch(self,company,userId):
        try:
            query=f"""
                    SELECT member.name, member.phone, member.userId, reserve.dataTime, reserve.project, reserve.auto_updae_time  
                    FROM {self.table} 
                    JOIN member ON {self.table}.userId = member.userId AND reserve.company = member.company
                    WHERE status='0' AND reserve.company=%s AND member.userId=%s
                """
            params = (company, userId)
            result = self.executeQuery(query, params)

            return result
        except Exception as e:
            print('class.db.rdbmsSearch is Error:'+str(e))
    def ballRollrdbmsSearch(self,company,userId):
        try:
            query=f"""
                    SELECT member.name, member.phone, member.userId, reserve.dataTime, reserve.project, reserve.auto_updae_time 
                    FROM {self.table} 
                    JOIN member ON {self.table}.userId = member.userId AND reserve.company = member.company
                    Where status='ballRoll' AND reserve.company=%s and member.userId=%s
                    ORDER BY reserve.id DESC
                    LIMIT 1
                """
            params = (company, userId)
            result = self.executeQuery(query, params)

            return result
        except Exception as e:
            print('class.db.rdbmsSearch is Error:'+str(e))
    def TableOneSearchAddField(self,field,oneWhereTable,oneWhereValue,twoWhereTable,twoWhereValue):
        try:
            query = f"SELECT {field} FROM {self.table} WHERE {oneWhereTable} = %s AND {twoWhereTable} = %s"
            params=(oneWhereValue,twoWhereValue)
            result = self.executeQuery(query, params)
            return result
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
        return self.executeQuery(query, params)
    def memberPhone(self,oneWhereTable,oneWhereValue):
        try:
            self.cursor.execute(f"SELECT phone FROM {self.table} WHERE {oneWhereTable} = %s",(oneWhereValue,))
            return self.cursor.fetchall()
        except Exception as e:
            print('class.db.TableOneSearchAddField is Error:'+e)
    
    def clubTableSearch(self,filed,joinTable,userId):
        query = f"SELECT member.name, member.phone, {filed} FROM {self.table} INNER JOIN member ON member.phone = {joinTable}.memberphone WHERE member.userId = %s"
        params=(userId,)
        return self.executeQuery(query, params)

    #DB Search

    #DB Update   
    def updateOneSearchWhere(self,field,fieldValue,whereField,whereValue):
        query=(f"UPDATE {self.table} SET {field} = %s WHERE {whereField} = %s")
        params=(fieldValue,whereValue)
        return self.executeQuery(query, params)
    def updateTwoSearchWhere(self,field,fieldValue,whereField,whereValue,twoWhereField,twoWhereValue):
        query=(f"UPDATE {self.table} SET {field} = %s WHERE {whereField} = %s AND {twoWhereField}=%s")
        params=(fieldValue,whereValue,twoWhereValue)
        return self.executeQuery(query, params)
    def updateThreeSearchWhere(self,field,fieldValue,whereField,whereValue,twoWhereField,twoWhereValue,threeWhereField,threeWhereValue):
        query=(f"UPDATE {self.table} SET {field} = %s WHERE {whereField} = %s AND {twoWhereField}=%s AND {threeWhereField} = %s")
        params=(fieldValue,whereValue,twoWhereValue,threeWhereValue)
        return self.executeQuery(query, params)

    #DB Update

    #DB INSERT
    def Insert(self , addFieldName=None ,addFieldValue=None):
        print(f'addFieldName{addFieldName}')
        print(f'addFieldValue:{addFieldValue}')
        print(f"INSERT INTO {self.table} {addFieldName} VALUES {addFieldValue} ")
        field_names = ', '.join(addFieldName)
        placeholders = ', '.join(['%s' for _ in addFieldValue])
        sql_query = f"INSERT INTO {self.table} ({field_names}) VALUES ({placeholders})"
        print('Insert 成功新增')

        return self.executeQuery(sql_query, addFieldValue)
    def insertMember(self,userId,company):
        try:
            query = f"INSERT INTO {self.table} (userId, company) VALUES (%s, %s)"
            params=(userId, company)
            self.executeQuery(query, params)
            print('會員UserID成功新增')
        except Exception as e:
            print('class.db.TableOneSearchAddField is Error:',e)    #DB INSERT

    #DB DELETE
    def Delete(self,field,delValue):
        query = f"DELETE FROM {self.table} WHERE {field}=%s"
        params=(delValue,)
        self.executeQuery(query, params)

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
    def openConnection(self):
        while True:
            try:
                connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
                if connection.is_connected():
                    print("資料庫連線成功")
                    return connection
            except mysql.connector.Error as e:
                print(e)
                print("嘗試重新連線...")
                sleep(5)  # 等待5秒後重試

    def executeQuery(self, query, params=None):
        try:
            if not self.connection.is_connected():
                print("資料庫連線已斷開，嘗試重新連線...")
                self.connection = self.openConnection()
                self.cursor = self.connection.cursor(dictionary=True)
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            self.connection.commit()  # 確保將修改提交到資料庫
            return result
        except mysql.connector.Error as e:
            print(f"執行查詢時發生錯誤: {e}")
            print("試圖重新連線...")
            self.connection = self.openConnection()
            self.cursor = self.connection.cursor(dictionary=True)
            return None


    #DB Close Connection
    def closeConnection(self):
        self.cursor.close()
        self.connection.close()
