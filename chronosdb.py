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

    def CheckPresence(self):
        data = tuple()
        result = 0
        cur = self.mydb.cursor()
        cur.execute('SELECT dan, mis FROM dev_connectiontest ORDER BY date DESC LIMIT 4')
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

    def InsertPresence(self, danPresence, misPresence):
        cur = self.mydb.cursor()
        try:
            cur.execute("INSERT INTO dev_connectiontest (dan, mis) VALUES (?, ?)", (danPresence, misPresence))
            self.mydb.commit()
            print(cur.rowcount, "record inserted.")
        except mariadb.Error as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    db = DBAction()
    #db.InsertPresence(1, 1)
    db.CheckPresence()
    db.Close()
    #print("Presence DB returns {", db.CheckPresence(), "}")