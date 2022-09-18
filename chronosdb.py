#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

import mariadb, sys
import confighelper

class DBAction:
    def __init__(self):
        logging.debug("chronosdb init: Init started")
        self.config = confighelper.read_config()
        try:
            self.mydb = mariadb.connect(
            host=self.config["DB"]["host"],
            user=self.config["DB"]["user"],
            password=self.config["DB"]["password"],
            database=self.config["DB"]["database"]
            )
            logging.info("chronosdb init: MariaDB connect succesfull")
        except mariadb.Error as e:
            logging.error("chronosdb init: Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def Close(self):
        self.mydb.close()
        logging.info("chronosdb Close: Succesfully closed MariaDB platform.")

    def InitDatabase(self):
        cur = self.mydb.cursor()
        try:
            tableName = self.config["DB"]["presencetable"]
            query = "CREATE TABLE IF NOT EXISTS " + tableName + " (timestamp TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , state TINYINT(1) NOT NULL , UNIQUE (timestamp))"
            logging.debug("chronosdb InitDatabase: built query: " + query)
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb InitDatabase: presencetable commited.")
        except mariadb.Error as e:
            logging.error("chronosdb InitDatabase: Error creating table: {e}")
        try:
            tableName = self.config["DB"]["servertable"]
            query = "CREATE TABLE IF NOT EXISTS " + tableName + " (timestamp TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , status TINYTEXT NOT NULL , event TEXT NOT NULL , UNIQUE (timestamp))"
            logging.debug("chronosdb InitDatabase: built query: " + query)
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb InitDatabase: servertable commited.")
        except mariadb.Error as e:
            logging.error("chronosdb InitDatabase: Error creating table: {e}")

    def CheckPresence(self):
        tableName = self.config["DB"]["presencetable"]
        result = False
        cur = self.mydb.cursor()
        query = "SELECT state FROM " + tableName + " ORDER BY timestamp DESC LIMIT 4"
        logging.debug("chronosdb CheckPresence: built query: " + query)
        cur.execute(query)
        response = cur.fetchall()
        logging.debug("chronosdb CheckPresence: query response caught: {a}".format(a = response))
        for row in response:
            if row[0] == 1: 
                logging.debug("chronosdb CheckPresence: found active presence, setting result = true")
                result = True
        logging.info("chronosdb CheckPresence: returning {a}".format(a = result))
        return result

    def InsertPresence(self, presence):
        tableName = self.config["DB"]["presencetable"]
        cur = self.mydb.cursor()
        try:
            query = "INSERT INTO " + tableName + " (state) VALUES (" + str(presence) + ")"
            logging.debug("chronosdb InsertPresence: built query {a}".format(a = query))
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb InsertPresence: {a} record inserted.".format(a = cur.rowcount))
        except mariadb.Error as e:
            logging.error("chronosdb InsertPresence: error: {e}")

if __name__ == '__main__':
    logging.info("chronosdb started")
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
        db.InsertPresence(0)
        print("done")
    db.Close()
    logging.info("chronosdb finished")