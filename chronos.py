#!/usr/bin/env python3

import logging
import confighelper, chronosdb, chronossrv, chronostimer, chronosscan

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

def verify_presence(db):
    logging.debug("Chronos: verify_presence> calling Scanner.Scan")
    scanner = chronosscan.Scanner()
    result = scanner.Scan()
    logging.debug("Chronos: verify_presence> scan returned {a}".format(a = result))
    logging.debug("Chronos: verify_presence> calling Databaser.InsertPresence({a})".format(a = result))
    db.InsertPresence(result)
    logging.debug("Chronos: verify_presence> calling Databaser.CheckPresence()")
    result = db.CheckPresence()
    logging.debug("Chronos: verify_presence> returning Databaser.CheckPresence() result = {a}".format(a = result))
    return result

if __name__ == '__main__':

    logging.debug("Chronos> Reading config from confighelper")
    config = confighelper.read_config()

    serverIP = config["Server"]["IP"]
    serverMac = config["Server"]["Mac"]
    serverAcc = config["Server"]["username"]
    rsaCertificate = config["Server"]["rsaCertificate"]

    logging.debug("Chronos> Initializing chronossrv.Server")
    server = chronossrv.Server(serverIP, serverMac, serverAcc, rsaCertificate)
    logging.debug("Chronos> Initializing chronosdb.Databaser")
    db = chronosdb.Databaser()
    logging.debug("Chronos> Initializing chronostimer.Timer")
    timer = chronostimer.Timer()

    logging.debug("Chronos> calling timer.PresenceCheckBeforePoweron()")
    if timer.PresenceCheckBeforePoweron():
        logging.debug("Chronos> timer.PresenceCheckBeforePoweron() returned {a}, calling VerifyPresnece()".format(a = True))
        verify_presence(db)

    logging.debug("Chronos> Calling server.IsServerUp()")
    if server.IsServerUp():
        logging.debug("Chronos> Server.IsServerUp() returned True")
        logging.debug("Chronos> Calling timer.SurpressPoweron() elif verify_presence()")
        if timer.should_server_be_down():
            logging.info("Chronos> Calling shutdown sequence based on should_server_be_down")
            server.Poweroff()
            db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by SURPRESS")
        elif not verify_presence(db):
            server.Poweroff()
            db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by PRESENCE")
            logging.info("Chronos> Called shutdown sequence based on verify_presence")
        else:
            logging.debug("Chronos> No PWR change based on IsServerUp, !should_server_be_down, verify_presence()")
    else:
        logging.debug("Chronos> Server.IsServerUp() returned False")
        if not timer.should_server_be_down():
            if verify_presence(db):
                logging.info("Chronos> Calling startup sequence based on !IsServerUp, !should_server_be_down and verify_presence")
                server.Wake()
                db.InsertSrvState(True, "Chronos: WAKE CALL by PRESENCE")
            else:
                logging.debug("Chronos> No PWR change based on !IsServerUp, !should_server_be_down and !verify_presence")
        else:
            logging.debug("Chronos> No PWR change based on !should_server_be_down")
    logging.debug("Chronos> calling Databaser.close_db()")
    db.close_db()
    logging.debug("Chronos> Fin.")
