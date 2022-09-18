#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.info("network-scan started")

import nmap
import chronosdb, confighelper

config = confighelper.read_config()

macs = (config["Scanner"]["mac"]).upper().split(",")
print(macs)
macQuery = 0
for x in range(45):
    nm = nmap.PortScanner()
    nm.scan(hosts=config["Scanner"]["subnet"], arguments='-sP')
    host_list = nm.all_hosts()
    for host in host_list:
        if 'mac' in nm[host]['addresses']:
            for mac in macs:
                # print(mac)
                # print(host+' : '+nm[host]['addresses']['mac'])
                if mac == nm[host]['addresses']['mac']:
                    macQuery = 1
                    logging.debug("Loop "+ str(x) +": "+ mac + " : found in " + nm[host]['addresses']['mac'] + ", macQuery = " + str(macQuery))

logging.info("network-scan: final macQuery: " + str(macQuery))
db = chronosdb.DBAction()
db.InsertPresence(macQuery)
db.Close()
logging.info("network-scan finished")
