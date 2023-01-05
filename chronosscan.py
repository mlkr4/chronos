#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')
logging.info("network-scan started")

import nmap
import chronosdb, confighelper

class Scanner():
    def __init__(self):
        logging.debug("chronosscan: Scanner> init")
        self.config = confighelper.read_config()
        self.macs = (self.config["Scanner"]["mac"]).upper().split(",")
        self.ips = (self.config["Scanner"]["ip"]).upper().split(",")
        logging.debug("chronosscan: Scanner.init> Querried macs: {a}".format(a = self.macs))

    def is_mac_addr_present(self):
        logging.debug("chronosscan: Scanner.is_mac_addr_present> started")
        result = False
        logging.debug("chronosscan: Scanner.is_mac_addr_present> result set to {a}".format(a = result))
        for x in range(45):
            nm = nmap.PortScanner()
            nm.scan(hosts=self.config["Scanner"]["subnet"], arguments='-sP')
            host_list = nm.all_hosts()
            for host in host_list:
                if 'mac' in nm[host]['addresses']:
                    for mac in self.macs:
                        # print(mac)
                        # print(host+' : '+nm[host]['addresses']['mac'])
                        if mac == nm[host]['addresses']['mac']:
                            result = True
                            logging.debug("chronosscan: Scanner.is_mac_addr_present> Loop {a}: {b} : found in {c}, result set to {d}".format(a = x, b = mac, c = nm[host]['addresses']['mac'], d = result))
            if result: break
        logging.info("chronosscan: Scanner.is_mac_addr_present> finished, returning {a}.".format(a = result))
        return result

    def is_ip_addr_present(self):
        logging.debug("chronosscan: Scanner.is_ip_addr_present> started")
        result = False
        for ip in self.ips:
            logging.debug("chronosscan: Scanner.is_ip_addr_present> scanning for {ip}.")
            if self.is_ip_addr_up(ip):
                result = True
            if result: break
        logging.debug("chronosscan: Scanner.is_ip_addr_present> returning {result}.")
        return result


    def is_ip_addr_up(self, hostIP):
        logging.debug("chronosscan: Scanner.is_ip_addr_up> init")
        hostUp = True if os.system("ping -c 1 " + hostIP) == 0 else False
        logging.debug("chronosscan: Scanner.is_ip_addr_up> sent ping -c 1 {serverIP}, evaluated as {hostUP}.")
        if hostUp:
            logging.info("chronossrv: Scanner.is_ip_addr_up> host is up, returning True")
            return True
        else:
            logging.info("chronossrv: Scanner.is_ip_addr_up> host is down, returning False")
            return False

if __name__ == '__main__':
    result = Scanner()
    print("Running scanner, this may take a while. Works only with sudo privileges btw.")
    print("Found IP presence: {a}".format(a = result.is_ip_addr_present()))
    print("Found mac presence: {a}".format(a = result.is_mac_addr_present()))
