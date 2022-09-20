#!/usr/bin/env python3

import logging
import confighelper, chronosdb, chronossrv, chronostimer

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':

    config = confighelper.read_config()
    serverIP = config["Server"]["IP"]
    serverMac = config["Server"]["Mac"]
    serverAcc = config["Server"]["username"]
    rsaCertificate = config["Server"]["rsaCertificate"]

    server = chronossrv.Server(serverIP, serverMac, serverAcc, rsaCertificate)
    db = chronosdb.DBAction()
    timer = chronostimer.Timer()

    if server.Ping():
        if db.CheckPresence():
            if timer.SurpressPoweron():
                logging.info("Calling shutdown sequence based on SurpressPoweron")
                server.Poweroff()
                db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by SURPRESS")
            else:
                logging.debug("No PWR change based on PowerState, PresenceState, !SurpressPoweron")
        else:
            logging.info("Calling shutdown sequence based on PresenceState")
            server.Poweroff()
            db.InsertSrvState(False, "Chronos: SHUTDOWN CALL by PRESENCE")
    else:
        if db.CheckPresence():
            if not timer.SurpressPoweron():
                logging.info("Calling startup sequence based on PresenceState and !SurpressPoweron")
                server.Wake()
                db.InsertSrvState(True, "Chronos: WAKE CALL by PRESENCE")
            else:
                logging.debug("No PWR change based on !PowerState, PresenceState, SurpressPoweron")
        else:
            logging.debug("No PWR change based on !PowerState, !PresenceState")
    db.Close()
