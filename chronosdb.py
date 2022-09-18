#!/usr/bin/env python3

import mariadb, sys
import confighelper

class DBAction:
    def __init__(self):
        try:
            config = confighelper.read_config()
            self.mydb = mariadb.connect(
            host=config["DB"]["host"],
            user=config["DB"]["user"],
            password=config["DB"]["password"],
            database=config["DB"]["database"]
            )
            #return mydb
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
            #return False

    def Close(self):
        self.mydb.close()

    def CheckDatabases(self):
        cur = self.mydb.cursor()
        cur.execute('SHOW TABLES')
        sql = cur.fetchall()
        print(f"sql")

    def InitDatabase(self):
        cur = self.mydb.cursor()
        try:
            tableName = config["DB"]["presencetable"]
            cur.execute("CREATE TABLE IF NOT EXISTS {tableName} ( `timestamp` TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `state` TINYINT(1) NOT NULL , UNIQUE (`timestamp`)) ")
        except mydb.Error as e:
            print(f"Error creating table: {e}")
        try:
            tableName = config["DB"]["servertable"]
            cur.execute("CREATE TABLE IF NOT EXISTS {tableName} ( `timestamp` TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `status` TINYTEXT NOT NULL , `event` TEXT NOT NULL , UNIQUE (`timestamp`))")
        except mydb.Error as e:
            print(f"Error creating table: {e}")

    def CheckPresence(self):
        tableName = config["DB"]["presencetable"]
        data = tuple()
        result = 0
        cur = self.mydb.cursor()
        cur.execute('SELECT state FROM {tableName} ORDER BY timestamp DESC LIMIT 4')
        sql = cur.fetchall()
        print(sql)
        for row in sql:
            data = data + row
            print(data)
        for i in data:
            result += i
        print(result)
        #else: return False
        if result == 0: return False
        else: return True

    def InsertPresence(self, presence):
        tableName = config["DB"]["presencetable"]
        cur = self.mydb.cursor()
        try:
            cur.execute("INSERT INTO {tableName} (state) VALUES (?)", (presence))
            self.mydb.commit()
            print(cur.rowcount, "record inserted.")
        except mariadb.Error as e:
            print(f"InsertPresence error: {e}")

if __name__ == '__main__':
    db = DBAction()
    print("[I]nitDatabase")
    print("[C]heck presence")
    print("Insert [P]resence")
    action = input("Your choice? ").upper()
    if action == "I":
        db.InitDatabase()
        print("done")
    elif action == "C":
        print("DB: presence state : ")
        db.CheckPresence()
    elif action == "P":
        db.InsertPresence(1)
        print("done")
    db.Close()
    #print("Presence DB returns {", db.CheckPresence(), "}")