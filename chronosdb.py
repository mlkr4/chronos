#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

import mariadb, sys
import confighelper

class DBAction:
    def __init__(self):
        logging.debug("chronosdb init: Init started")
        self.config = confighelper.read_config()
        self.presenceRowSum = 0
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
        self.presenceRowSum = 0
        tableName = self.config["DB"]["presencetable"]
        result = False
        cur = self.mydb.cursor()
        query = "SELECT state FROM " + tableName + " ORDER BY timestamp DESC LIMIT 4"
        logging.debug("chronosdb CheckPresence: built query: " + query)
        cur.execute(query)
        response = cur.fetchall()
        logging.debug("chronosdb CheckPresence: query response caught: {a}".format(a = response))
        for row in response:
            self.presenceRowSum += row[0]
            logging.debug("chronosdb CheckPresence: self.presenceRowSum == {a}".format(a = self.presenceRowSum))
            if row[0] == 1: 
                logging.debug("chronosdb CheckPresence: found active presence, setting result = true")
                result = True
        logging.info("chronosdb CheckPresence: returning {a}".format(a = result))
        return result

    def InsertPresence(self, state):
        tableName = self.config["DB"]["presencetable"]
        logging.debug("chronosdb InsertPresence: calling self.CheckPresence, self.presenceRowSum == {a}".format(a = self.presenceRowSum))
        presenceState = self.CheckPresence()
        logging.debug("chronosdb InsertPresence: self.presenceRowSum == {a}".format(a = self.presenceRowSum))
        if (self.presenceRowSum in range(1,4)) or (state =! presenceState):
            logging.debug("chronosdb InsertPresence: (self.presenceRowSum [{a}] in range(1,4)) or (state [{b}] =! presenceState [{c}]) evaluated as TRUE".format(a = self.presenceRowSum, b = state, c = presenceState))
            cur = self.mydb.cursor()
            try:
                logging.debug("chronosdb InsertPresence: built query INSERT INTO {a} (state) VALUE ({b})".format(a = tableName, b = state))
                cur.execute("INSERT INTO {a} (state) VALUE (?)".format(a = tableName), (state, ))
                self.mydb.commit()
                logging.info("chronosdb InsertPresence: {a} record inserted.".format(a = cur.rowcount))
            except mariadb.Error as e:
                logging.error("chronosdb InsertPresence: error: {e}".format())
        else:
            logging.debug("chronosdb InsertPresence: (self.presenceRowSum [{a}] in range(1,4)) or (state [{b}] =! presenceState [{c}]) evaluated as FALSE".format(a = self.presenceRowSum, b = state, c = presenceState))
            logging.debug("chronosdb InsertPresence: nothing to do.")

    def CheckSrvState(self):
        tableName = self.config["DB"]["servertable"]
        result = False
        cur = self.mydb.cursor()
        logging.debug("chronosdb CheckState: built query: SELECT status FROM {a} ORDER BY timestamp DESC LIMIT 1".format(a = tableName))
        cur.execute("SELECT status FROM {a} ORDER BY timestamp DESC LIMIT 1".format(a = tableName))
        response = cur.fetchall()
        logging.debug("chronosdb CheckState: query response caught: {a}".format(a = response))
        for row in response:
            if row[0] == 1:
                logging.debug("chronosdb CheckState: found active state, setting result = true")
                result = True
            elif row[0] == 0:
                logging.debug("chronosdb CheckState: found active state, setting result = false")
                result = False
        logging.info("chronosdb CheckState: returning {a}".format(a = result))
        return result

    def InsertSrvState(self, status, event):
        logging.debug("chronosdb InsertSrvState: input parameters status = {a}, event = {b}".format(a = status, b = event))
        tableName = self.config["DB"]["servertable"]
        cur = self.mydb.cursor()
        try:
            logging.debug("chronosdb InsertSrvState: built query: INSERT INTO {a} (status, event) VALUES ({b}, {c})".format(a = tableName, b = status, c = event))
            cur.execute("INSERT INTO {a} (status, event) VALUES (?, ?)".format(a = tableName), (status, event))
            self.mydb.commit()
            logging.info("chronosdb InsertSrvState: {a} record inserted.".format(a = cur.rowcount))
        except mariadb.Error as e:
            logging.error("chronosdb InsertSrvState: error: {e}")


if __name__ == '__main__':
    logging.info("chronosdb started")
    db = DBAction()
    print("[I]nitDatabase")
    print("[C]heck presence")
    print("Insert [P]resence")
    print("C[H]eck server state")
    print("I[N]sert server state")
    action = input("Your choice? ").upper()
    if action == "I":
        db.InitDatabase()
        print("done")
    elif action == "C":
        print("DB: presence state : ")
        db.CheckPresence()
    elif action == "P":
        db.InsertPresence(False)
        print("done")
    elif action == "H":
        db.CheckSrvState()
        print("done")
    elif action == "N":
        db.InsertSrvState(False, "chronosdb dry run")
    db.Close()
    logging.info("chronosdb finished")