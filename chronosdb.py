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
        self.foundPresenceState = 0
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

    def init_database(self):
        logging.debug("chronosdb: Databaser.init_database> init")
        cur = self.mydb.cursor()
        try:
            tableName = self.config["DB"]["presencetable"]
            query = "CREATE TABLE IF NOT EXISTS " + tableName + " (timestamp TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , state TINYINT(1) NOT NULL , UNIQUE (timestamp))"
            logging.debug("chronosdb: Databaser.init_database> built query: " + query)
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb: Databaser.init_database> presencetable commited.")
        except mariadb.Error as e:
            logging.error("chronosdb: Databaser.init_database> Error creating table: {e}")
        try:
            tableName = self.config["DB"]["servertable"]
            query = "CREATE TABLE IF NOT EXISTS " + tableName + " (timestamp TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , status TINYTEXT NOT NULL , event TEXT NOT NULL , UNIQUE (timestamp))"
            logging.debug("chronosdb: Databaser.init_database> built query: " + query)
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb: Databaser.init_database> servertable commited.")
        except mariadb.Error as e:
            logging.error("chronosdb Databaser.init_database> Error creating table: {e}")
        try:
            tableName = self.config["DB"]["holidaytable"]
            query = "CREATE TABLE IF NOT EXISTS " + tableName + " (timestamp TIMESTAMP on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , status TINYTEXT NOT NULL , event TEXT NOT NULL , UNIQUE (timestamp))"
            logging.debug("chronosdb: Databaser.init_database> built query: " + query)
            cur.execute(query)
            self.mydb.commit()
            logging.info("chronosdb: Databaser.init_database> servertable commited.")
        except mariadb.Error as e:
            logging.error("chronosdb Databaser.init_database> Error creating table: {e}")

    def get_presence_state(self):
        logging.debug("chronosdb: Databaser.get_presence_state> init")
        self.foundPresenceState = 0
        tableName = self.config["DB"]["presencetable"]
        cur = self.mydb.cursor()
        query = "SELECT state FROM " + tableName + " ORDER BY timestamp DESC LIMIT 4"
        logging.debug("chronosdb: Databaser.get_presence_state> built query: " + query)
        cur.execute(query)
        response = cur.fetchall()
        logging.debug("chronosdb: Databaser.get_presence_state> query response caught: {a}".format(a = response))
        self.foundPresenceState = sum(list(sum(response,())))
        result = True if self.foundPresenceState >= 1 else False
        logging.info("chronosdb: Databaser.get_presence_state> returning {a}".format(a = result))
        return result

    def record_presence_state(self, state):
        logging.debug("chronosdb: Databaser.record_presence_state> init")
        tableName = self.config["DB"]["presencetable"]
        logging.debug("chronosdb Databaser.record_presence_state> calling self.get_presence_state, self.foundPresenceState == {a}".format(a = self.foundPresenceState))
        presenceState = self.get_presence_state()
        logging.debug("chronosdb: Databaser.record_presence_state> self.foundPresenceState == {a}".format(a = self.foundPresenceState))
        if (self.foundPresenceState >= 1) or (state is not presenceState):
            logging.debug("chronosdb: Databaser.record_presence_state> (self.foundPresenceState [{a}] >= 1 or (state [{b}] =! presenceState [{c}]) evaluated as TRUE".format(a = self.foundPresenceState, b = state, c = presenceState))
            cur = self.mydb.cursor()
            try:
                query = "INSERT INTO {a} (state) VALUE (?)".format(a = tableName)
                logging.debug("chronosdb: Databaser.record_presence_state> built query: {a}".format(a = query))
                cur.execute(query, (state, ))
                self.mydb.commit()
                logging.info("chronosdb: Databaser.record_presence_state> {a} record inserted.".format(a = cur.rowcount))
            except mariadb.Error as e:
                logging.error("chronosdb: Databaser.record_presence_state> error: {e}".format())
        else:
            logging.debug("chronosdb: Databaser.record_presence_state> (self.foundPresenceState [{a}] in range(1,4)) or (state [{b}] =! presenceState [{c}]) evaluated as FALSE".format(a = self.foundPresenceState, b = state, c = presenceState))
            logging.debug("chronosdb: Databaser.record_presence_state> nothing to do.")

    def get_server_state(self):
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

    def record_server_state(self, status, event):
        logging.debug("chronosdb: Databaser.record_server_state> input parameters status = {a}, event = {b}".format(a = status, b = event))
        tableName = self.config["DB"]["servertable"]
        cur = self.mydb.cursor()
        try:
            query = "INSERT INTO {a} (status, event) VALUES (?, ?)".format(a = tableName)
            logging.debug("chronosdb: Databaser.record_server_state> built query: {a}".format(a = query))
            cur.execute(query, (status, event))
            self.mydb.commit()
            logging.info("chronosdb: Databaser.record_server_state> {a} record inserted.".format(a = cur.rowcount))
        except mariadb.Error as e:
            logging.error("chronosdb Databaser.record_server_state> error: {e}")


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
        db.init_database()
        print("done")
    elif action == "C":
        print("DB: presence state : ")
        db.get_presence_state()
    elif action == "P":
        db.record_presence_state(False)
        print("done")
    elif action == "H":
        db.get_server_state()
        print("done")
    elif action == "N":
        db.record_server_state(False, "chronosdb dry run")
    db.close_db()
    logging.info("chronosdb> fin.")