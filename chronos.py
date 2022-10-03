#!/usr/bin/env python3

import logging
import confighelper, chronosdb, chronossrv, chronostimer, chronosscan

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

config = confighelper.read_config()

def VerifyPresence(db):
    scanner = chronosscan.Scanner()
    result = scanner.Scan()
    db.InsertPresence(result)
    result = db.CheckPresence()
    return result

if __name__ == '__main__':

    serverIP = config["Server"]["IP"]
    serverMac = config["Server"]["Mac"]
    serverAcc = config["Server"]["username"]
    rsaCertificate = config["Server"]["rsaCertificate"]

    server = chronossrv.Server(serverIP, serverMac, serverAcc, rsaCertificate)
    db = chronosdb.Databaser()
    timer = chronostimer.Timer()

    if timer.PresenceCheckBeforePoweron():
        VerifyPresence(db)

    if server.Ping():
        if timer.SurpressPoweron():
            logging.info("Calling shutdown sequence based on SurpressPoweron")
            server.Poweroff()
            db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by SURPRESS")
        elif not VerifyPresence(db):
            server.Poweroff()
            db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by PRESENCE")
            logging.info("Calling shutdown sequence based on PresenceState")
        else:
            logging.debug("No PWR change based on PowerState, PresenceState, !SurpressPoweron")
    else:
        if not timer.SurpressPoweron():
            if VerifyPresence(db):
                logging.info("Calling startup sequence based on PresenceState and !SurpressPoweron")
                server.Wake()
                db.InsertSrvState(True, "Chronos: WAKE CALL by PRESENCE")
            else:
                logging.debug("No PWR change based on !PowerState, !PresenceState, !SurpressPoweron")
        else:
            logging.debug("No PWR change based on !SurpressPoweron")
    db.Close()
