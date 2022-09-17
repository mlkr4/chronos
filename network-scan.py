#!/usr/bin/env python3

import nmap
import chronosdb, confighelper

config = confighelper.read_config()

danMac = config.["Scanner"]["mac1"].upper()
misMac = config.["Scanner"]["mac2"].upper()
danQuery = 0
misQuery = 0
for x in range(45):
    nm = nmap.PortScanner()
    nm.scan(hosts=config.["Scanner"]["subnet"], arguments='-sP')
    host_list = nm.all_hosts()
    for host in host_list:
        if  'mac' in nm[host]['addresses']:
            #print(host+' : '+nm[host]['addresses']['mac'])
            if danMac == nm[host]['addresses']['mac']:
                danQuery = 1
            if misMac == nm[host]['addresses']['mac']:
                misQuery = 1

print("INSERT INTO dev_connectiontest (dan, mis) VALUES (", danQuery,", ", misQuery,")")

#if DanQuery or MisaQuery:

db = chronosdb.DBAction()
db.InsertPresence(danQuery, misQuery)
db.Close()
