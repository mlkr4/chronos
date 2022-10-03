#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

import os, subprocess, socket, struct, argparse
import confighelper, chronosdb

from typing import List

class Server():
    def __init__(self, IP, mac, acc, cert):
        logging.debug("chronossrv: Server init")
        self.serverIP = IP
        self.serverMac = mac
        self.serverAcc = acc
        self.serverCert = cert

    def CreateMagicPacket(self, macaddress: str) -> bytes:
        if len(macaddress) == 17:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, "")
        elif len(macaddress) != 12:
            raise ValueError("Incorrect MAC address format")
        return bytes.fromhex("F" * 12 + macaddress * 16)

    def Wake(self):
        logging.debug('chronossrv: Server.Wake(): initializing.')
        ip_address = "255.255.255.255"
        port = 9
        interface = None
        packet = self.CreateMagicPacket(self.serverMac)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            if interface is not None:
                sock.bind((interface, 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.connect((ip_address, port))
            sock.send(packet)
            logging.info('chronossrv: Server.Wake(): Magic packet sent.')
            return True

    def Poweroff(self):
            logging.debug('chronossrv: Server.Poweroff(): initializing.')
            if subprocess.Popen(f"ssh -i{self.serverCert} {self.serverAcc}@{self.serverIP} sudo poweroff", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate():
                logging.debug("chronossrv: Server.Poweroff(): sent: ssh -i{rsaCertificate} {serverAcc}@{serverIP} sudo poweroff")
                logging.info('chronossrv: Server.Poweroff(): Poweroff sent.')
                logging.debug("chronossrv: Server.Poweroff(): Returning True")
                return True
            else:
                logging.error('chronossrv: Server.Poweroff(): Returning False')
                return False

    def Ping(self):
        logging.debug("chronossrv: Server.Ping(): initializing")
        hostUp = True if os.system("ping -c 1 " + self.serverIP) == 0 else False
        logging.debug("chronossrv: Ping: sent ping -c 1 {serverIP}, evaluated as {hostUP}.")
        if hostUp:
            logging.info("chronossrv: Server.Ping(): host is up, returning true")
            return True
        else:
            logging.info("chronossrv: Server.Ping(): host is down, returning false")
            return False

def main(argv: List[str] = None) -> None:
    logging.debug('chronossrv: main: initializing.')
    parser = argparse.ArgumentParser(description = "Control configured computer - WoL, shutdown, ping, verify.", formatter_class = argparse.ArgumentDefaultsHelpFormatter,)
    parser.add_argument(dest = "controlArg", choices=["ping", "shutdown", "verify", "wake"], help = "wake | shutdown | ping | verify")
    args = parser.parse_args()
    logging.debug('chronossrv: main: arguments parsed: {a}'.format(a = args))

    if args.controlArg:
        logging.debug("chronossrv: main: control argument passed.")

        config = confighelper.read_config()
        serverIP = config["Server"]["IP"]
        serverMac = config["Server"]["Mac"]
        serverAcc = config["Server"]["username"]
        rsaCertificate = config["Server"]["rsaCertificate"]
    
        logging.debug("chronossrv: main: initializing Computer object.")
        computer = Server(serverIP, serverMac, serverAcc, rsaCertificate)

        logging.debug("chronossrv: main: initializing DB object.")
        db = chronosdb.Databaser()

        if args.controlArg == "wake":
            if computer.Wake():
                print("WoL initiated.")
                db.InsertSrvState(True, "Chronossrv.main call")
            else:
                print("WoL error.")
        elif args.controlArg == "shutdown":
            if computer.Poweroff():
                print("Shutdown initiated.")
                db.InsertSrvState(False, "Chronossrv.main call")
            else:
                print("Shutdown failed.")
        elif args.controlArg == "ping":
            if computer.Ping():
                print("Server is alive.")
            else:
                print("Server unresponsive.")
        elif args.controlArg == "verify":
            if computer.Ping():
                if not db.CheckSrvState():
                    db.InsertSrvState(True, "Chronossrv.main verify fix")
                    print("Server is alive, DB state inconsistent, fixed")
                else:
                    print("Server is alive, DB state consistent")
            else:
                if db.CheckSrvState():
                    db.InsertSrvState(False, "Chronossrv.main verify fix")
                    print("Server is unresponsive, DB state inconsistent, fixed")
                else:
                    print("Server is unresponsive, DB state consistent")
        db.Close()
    else:
        print("Nothing to do.")

if __name__ == '__main__':
    main()
