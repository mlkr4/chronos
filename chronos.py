#!/usr/bin/env python3

import logging
import confighelper, chronosdb, chronossrv, chronostimer, chronosscan

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

def VerifyPresence(db):
    logging.debug("Chronos: VerifyPresence> calling Scanner.Scan")
    scanner = chronosscan.Scanner()
    result = scanner.Scan()
    logging.debug("Chronos: VerifyPresence> scan returned {a}".format(a = result))
    logging.debug("Chronos: VerifyPresence> calling Databaser.InsertPresence({a})".format(a = result))
    db.InsertPresence(result)
    logging.debug("Chronos: VerifyPresence> calling Databaser.CheckPresence()")
    result = db.CheckPresence()
    logging.debug("Chronos: VerifyPresence> returning Databaser.CheckPresence() result = {a}".format(a = result))
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
        VerifyPresence(db)

    logging.debug("Chronos> Calling server.Ping()")
    if server.Ping():
        logging.debug("Chronos> Server.Ping() returned True")
        logging.debug("Chronos> Calling timer.SurpressPoweron() elif VerifyPresence()")
        if timer.SurpressPoweron():
            logging.info("Chronos> Calling shutdown sequence based on SurpressPoweron")
            server.Poweroff()
            db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by SURPRESS")
        elif not VerifyPresence(db):
            server.Poweroff()
            db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by PRESENCE")
            logging.info("Chronos> Called shutdown sequence based on VerifyPresence")
        else:
            logging.debug("Chronos> No PWR change based on Ping, !SurpressPoweron, VerifyPresence()")
    else:
        logging.debug("Chronos> Server.Ping() returned False")
        if not timer.SurpressPoweron():
            if VerifyPresence(db):
                logging.info("Chronos> Calling startup sequence based on !Ping, !SurpressPoweron and VerifyPresence")
                server.Wake()
                db.InsertSrvState(True, "Chronos: WAKE CALL by PRESENCE")
            else:
                logging.debug("Chronos> No PWR change based on !Ping, !SurpressPoweron and !VerifyPresence")
        else:
            logging.debug("Chronos> No PWR change based on !SurpressPoweron")
    logging.debug("Chronos> calling Databaser.Close()")
    db.Close()
    logging.debug("Chronos> Fin.")
