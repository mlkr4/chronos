#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')
logging.info("network-scan started")

import nmap
import chronosdb, confighelper

class Scanner():
    def __init__(self):
        logging.debug("chronosscan: Scanner.init started")
        self.config = confighelper.read_config()
        self.macs = (config["Scanner"]["mac"]).upper().split(",")
        logging.debug("chronosscan: Scanner.init: Querried macs: {a}".format(a = macs))

    def Scan(self):
        logging.debug("chronosscan: Scanner.Scan() started")
        result = False
        logging.debug("chronosscan: Scanner.Scan() result set to {a}".format(a = result))
        for x in range(45):
            nm = nmap.PortScanner()
            nm.scan(hosts=self.config["Scanner"]["subnet"], arguments='-sP')
            host_list = nm.all_hosts()
            for host in host_list:
                if 'mac' in nm[host]['addresses']:
                    for mac in macs:
                        # print(mac)
                        # print(host+' : '+nm[host]['addresses']['mac'])
                        if mac == nm[host]['addresses']['mac']:
                            result = True
                            logging.debug("chronosscan: Scanner.Scan() Loop {a}: {b} : found in {c}, result set to {d}".format(a = x, b = mac, c = nm[host]['addresses']['mac'], d = result))
    logging.info("chronosscan: Scanner.Scan() finished, returning {a}.".format(a = result))
    return result

    def UpdateDatabase(self):
        logging.debug("chronosscan: Scanner.UpdateDatabase() started")
        presence = self.Scan()
        db = chronosdb.DBAction()
        logging.info("network-scan: Scanner.UpdateDatabase() calling : db.InsertPresence({a})".format(a = presence))
        db.InsertPresence(presence)
        db.Close()

if __name__ == '__main__':
    result = Scanner()
    print("Found presence: {a}".format(a = result.Scan()))
