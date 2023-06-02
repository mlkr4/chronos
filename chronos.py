#!/usr/bin/env python3

import logging
import confighelper, chronosdb, chronossrv, chronostimer, chronosscan

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

def verify_home_presence(db):
    logging.debug("Chronos: verify_home_presence> calling Scanner.is_mac_addr_present")
    scanner = chronosscan.Scanner()
    result = scanner.is_mac_addr_present()
    logging.debug("Chronos: verify_home_presence> scan returned {a}".format(a = result))
    logging.debug("Chronos: verify_home_presence> calling Databaser.record_presence_state({a})".format(a = result))
    db.record_presence_state(result)
    logging.debug("Chronos: verify_home_presence> calling Databaser.get_presence_state()")
    result = db.get_presence_state()
    logging.debug("Chronos: verify_home_presence> returning Databaser.get_presence_state() result = {a}".format(a = result))
    return result

def verify_remote_presence():
    logging.debug("Chronos: verify_remote_presence> calling Scanner.is_ip_addr_present")
    scanner = chronosscan.Scanner()
    result = scanner.is_ip_addr_present()
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

    ''' Not working nmap on debian causes errors in script and general chronos shenanigans. not worth it, has to be rewritten

    logging.debug("Chronos> calling timer.should_presence_be_got_before_poweron()")
    if timer.should_presence_be_got_before_poweron():
        logging.debug("Chronos> timer.should_presence_be_got_before_poweron() returned {a}, calling VerifyPresnece()".format(a = True))
        verify_home_presence(db)

    logging.debug("Chronos> Calling server.is_server_up()")
    if server.is_server_up():
        logging.debug("Chronos> Server.is_server_up() returned True")
        logging.debug("Chronos> Calling timer.SurpressPoweron() elif verify_home_presence()")
        if not server.is_server_locked():
            if timer.should_server_be_down() and not verify_remote_presence():
                logging.info("Chronos> Calling shutdown sequence based on should_server_be_down and not verify_remote_presence()")
                server.shutdown_server()
                db.record_server_state(False, "Chronos: SHUTDOWN CALL by TIME SURPRESS")
            elif not verify_home_presence(db) and not verify_remote_presence():
                server.shutdown_server()
                db.record_server_state(False, "Chronos: SHUTDOWN CALL by PRESENCE")
                logging.info("Chronos> Called shutdown sequence based on verify_home_presence and verify_remote_presence")
            else:
                logging.debug("Chronos> No PWR change based on is_server_up, !should_server_be_down, verify_home_presence(), verify_remote_presence()")
        else:
            logging.debug("Chronos> Server lockfile found, no changes")

    else:
        logging.debug("Chronos> Server.is_server_up() returned False")
        if verify_remote_presence():
            server.wake_server()
            db.record_server_state(True, "Chronos: WAKE CALL by REMOTE PRESENCE")
        elif not timer.should_server_be_down():
            if verify_home_presence(db):
                logging.info("Chronos> Calling startup sequence based on !is_server_up, !should_server_be_down and verify_home_presence")
                server.wake_server()
                db.record_server_state(True, "Chronos: WAKE CALL by PRESENCE")
            else:
                logging.debug("Chronos> No PWR change based on !is_server_up, !should_server_be_down and !verify_home_presence")
        else:
            logging.debug("Chronos> No PWR change based on !should_server_be_down")
    '''
    logging.debug("Chronos> Calling server.is_server_up()")

    if server.is_server_up():
        if timer.should_server_be_down():
            if not server.is_server_locked():
                logging.debug("Chronos> Server PWR down")
                server.shutdown_server()
                db.record_server_state(False, "Chronos: SHUTDOWN CALL by TIME")
            else:
                logging.debug("Chronos> Server lockfile found, no changes")
        else:
            logging.debug("Chronos> Server is UP, no change mandated")
    else:
        if not timer.should_server_be_down():
            logging.debug("Chronos> Server PWR up")
            server.wake_server()
            db.record_server_state(True, "Chronos: WAKE CALL by TIME")
        else:
            logging.debug("Chronos> Server is DOWN, no change mandated")

    logging.debug("Chronos> calling Databaser.close_db()")
    db.close_db()
    logging.debug("Chronos> Fin.")
