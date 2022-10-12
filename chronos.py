#!/usr/bin/env python3

import logging
import confighelper, chronosdb, chronossrv, chronostimer, chronosscan

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

def verify_presence(db):
    logging.debug("Chronos: verify_presence> calling Scanner.is_mac_addr_present")
    scanner = chronosscan.Scanner()
    result = scanner.is_mac_addr_present()
    logging.debug("Chronos: verify_presence> scan returned {a}".format(a = result))
    logging.debug("Chronos: verify_presence> calling Databaser.record_presence_state({a})".format(a = result))
    db.record_presence_state(result)
    logging.debug("Chronos: verify_presence> calling Databaser.get_presence_state()")
    result = db.get_presence_state()
    logging.debug("Chronos: verify_presence> returning Databaser.get_presence_state() result = {a}".format(a = result))
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

    logging.debug("Chronos> calling timer.should_presence_be_got_before_poweron()")
    if timer.should_presence_be_got_before_poweron():
        logging.debug("Chronos> timer.should_presence_be_got_before_poweron() returned {a}, calling VerifyPresnece()".format(a = True))
        verify_presence(db)

    logging.debug("Chronos> Calling server.is_server_up()")
    if server.is_server_up():
        logging.debug("Chronos> Server.is_server_up() returned True")
        logging.debug("Chronos> Calling timer.SurpressPoweron() elif verify_presence()")
        if timer.should_server_be_down():
            logging.info("Chronos> Calling shutdown sequence based on should_server_be_down")
            server.shutdown_server()
            db.record_server_state(False, "Chronos: SHUTDOWN CALL by SURPRESS")
        elif not verify_presence(db):
            server.shutdown_server()
            db.record_server_state(False, "Chronos: SHUTDOWN CALL by PRESENCE")
            logging.info("Chronos> Called shutdown sequence based on verify_presence")
        else:
            logging.debug("Chronos> No PWR change based on is_server_up, !should_server_be_down, verify_presence()")
    else:
        logging.debug("Chronos> Server.is_server_up() returned False")
        if not timer.should_server_be_down():
            if verify_presence(db):
                logging.info("Chronos> Calling startup sequence based on !is_server_up, !should_server_be_down and verify_presence")
                server.wake_server()
                db.record_server_state(True, "Chronos: WAKE CALL by PRESENCE")
            else:
                logging.debug("Chronos> No PWR change based on !is_server_up, !should_server_be_down and !verify_presence")
        else:
            logging.debug("Chronos> No PWR change based on !should_server_be_down")
    logging.debug("Chronos> calling Databaser.close_db()")
    db.close_db()
    logging.debug("Chronos> Fin.")
