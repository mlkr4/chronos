#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

import mariadb, sys
import confighelper

class Databaser:
    def __init__(self):
        logging.debug("chronosdb: Databaser> init")
        self.config = confighelper.read_config()
        self.presenceRowSum = 0
        try:
            self.mydb = mariadb.connect(
            host=self.config["DB"]["host"],
            user=self.config["DB"]["user"],
            password=self.config["DB"]["password"],
            database=self.config["DB"]["database"]
            )
            logging.info("chronosdb: Databaser.init> MariaDB connect succesfull")
        except mariadb.Error as e:
            logging.error("chronosdb: Databaser.init> Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def close_db(self):
        self.mydb.close()
        logging.info("chronosdb: Databaser.close_db> Succesfully closed MariaDB platform.")

    def InitDatabase(self):
        logging.debug("chronosdb: Databaser.InitDatabase> init")
        cur = self.mydb.cursor()
        try:
            tableName = self.config["DB"]["presencetable"]
            query = "CREATE TABLE IF NOT EXISTS " + tableName + " (timestamp TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , state TINYINT(1) NOT NULL , UNIQUE (timestamp))"
            logging.debug("chronosdb: Databaser.InitDatabase> built query: " + query)
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb: Databaser.InitDatabase> presencetable commited.")
        except mariadb.Error as e:
            logging.error("chronosdb: Databaser.InitDatabase> Error creating table: {e}")
        try:
            tableName = self.config["DB"]["servertable"]
            query = "CREATE TABLE IF NOT EXISTS " + tableName + " (timestamp TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , status TINYTEXT NOT NULL , event TEXT NOT NULL , UNIQUE (timestamp))"
            logging.debug("chronosdb: Databaser.InitDatabase> built query: " + query)
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb: Databaser.InitDatabase> servertable commited.")
        except mariadb.Error as e:
            logging.error("chronosdb Databaser.InitDatabase> Error creating table: {e}")

    def CheckPresence(self):
        logging.debug("chronosdb: Databaser.CheckPresence> init")
        self.presenceRowSum = 0
        tableName = self.config["DB"]["presencetable"]
        result = False
        cur = self.mydb.cursor()
        query = "SELECT state FROM " + tableName + " ORDER BY timestamp DESC LIMIT 4"
        logging.debug("chronosdb: Databaser.CheckPresence> built query: " + query)
        cur.execute(query)
        response = cur.fetchall()
        logging.debug("chronosdb: Databaser.CheckPresence> query response caught: {a}".format(a = response))
        for row in response:
            self.presenceRowSum += row[0]
            logging.debug("chronosdb: Databaser.CheckPresence> self.presenceRowSum == {a}".format(a = self.presenceRowSum))
            if row[0] == 1: 
                logging.debug("chronosdb: Databaser.CheckPresence> found active presence, setting result = true")
                result = True
        logging.info("chronosdb: Databaser.CheckPresence> returning {a}".format(a = result))
        return result

    def InsertPresence(self, state):
        logging.debug("chronosdb: Databaser.InsertPresence> init")
        tableName = self.config["DB"]["presencetable"]
        logging.debug("chronosdb Databaser.InsertPresence> calling self.CheckPresence, self.presenceRowSum == {a}".format(a = self.presenceRowSum))
        presenceState = self.CheckPresence()
        logging.debug("chronosdb: Databaser.InsertPresence> self.presenceRowSum == {a}".format(a = self.presenceRowSum))
        if (self.presenceRowSum in range(1,4)) or (state is not presenceState):
            logging.debug("chronosdb: Databaser.InsertPresence> (self.presenceRowSum [{a}] in range(1,4)) or (state [{b}] =! presenceState [{c}]) evaluated as TRUE".format(a = self.presenceRowSum, b = state, c = presenceState))
            cur = self.mydb.cursor()
            try:
                query = "INSERT INTO {a} (state) VALUE (?)".format(a = tableName)
                logging.debug("chronosdb: Databaser.InsertPresence> built query: {a}".format(a = query))
                cur.execute(query, (state, ))
                self.mydb.commit()
                logging.info("chronosdb: Databaser.InsertPresence> {a} record inserted.".format(a = cur.rowcount))
            except mariadb.Error as e:
                logging.error("chronosdb: Databaser.InsertPresence> error: {e}".format())
        else:
            logging.debug("chronosdb: Databaser.InsertPresence> (self.presenceRowSum [{a}] in range(1,4)) or (state [{b}] =! presenceState [{c}]) evaluated as FALSE".format(a = self.presenceRowSum, b = state, c = presenceState))
            logging.debug("chronosdb: Databaser.InsertPresence> nothing to do.")

    def CheckSrvState(self):
        tableName = self.config["DB"]["servertable"]
        result = False
        cur = self.mydb.cursor()
        query = "SELECT status FROM {a} ORDER BY timestamp DESC LIMIT 1".format(a = tableName)
        logging.debug("chronosdb: Databaser.CheckState> built query: {a}".format(a = query))
        cur.execute(query)
        response = cur.fetchall()
        logging.debug("chronosdb: CheckState> query response caught: {a}".format(a = response))
        for row in response:
            if row[0] == 1:
                logging.debug("chronosdb: Databaser.CheckState> found active state, setting result = true")
                result = True
            elif row[0] == 0:
                logging.debug("chronosdb: Databaser.CheckState> found active state, setting result = false")
                result = False
        logging.info("chronosdb: Databaser.CheckState> returning {a}".format(a = result))
        return result

    def InsertSrvState(self, status, event):
        logging.debug("chronosdb: Databaser.InsertSrvState> input parameters status = {a}, event = {b}".format(a = status, b = event))
        tableName = self.config["DB"]["servertable"]
        cur = self.mydb.cursor()
        try:
            query = "INSERT INTO {a} (status, event) VALUES (?, ?)".format(a = tableName)
            logging.debug("chronosdb: Databaser.InsertSrvState> built query: {a}".format(a = query))
            cur.execute(query, (status, event))
            self.mydb.commit()
            logging.info("chronosdb: Databaser.InsertSrvState> {a} record inserted.".format(a = cur.rowcount))
        except mariadb.Error as e:
            logging.error("chronosdb Databaser.InsertSrvState> error: {e}")


if __name__ == '__main__':
    logging.info("chronosdb> main")
    db = Databaser()
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
    db.close_db()
    logging.info("chronosdb> fin.")