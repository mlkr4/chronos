#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

import os, subprocess, socket, struct
import confighelper, chronosdb

config = confighelper.read_config()

class Server():
    def __init__(self, IP, mac, acc, cert):
        logging.debug("chronossrv: Server init")
        self.serverIP = IP
        self.serverMac = mac
        self.serverAcc = acc
        self.serverCert = cert

    # def MakeMagicPacket(self, macAddress):
    #     # Take the entered MAC address and format it to be sent via socket
    #     splitMac = str.split(macAddress,':')
    #     # Pack together the sections of the MAC address as binary hex
    #     hexMac = struct.pack('BBBBBB', int(splitMac[0], 16),
    #                          int(splitMac[1], 16),
    #                          int(splitMac[2], 16),
    #                          int(splitMac[3], 16),
    #                          int(splitMac[4], 16),
    #                          int(splitMac[5], 16))
    #     self.packet = b'\xff' * 6 + hexMac * 16 #create the magic packet from MAC address

    # def SendPacket(self, packet, destIP, destPort = 7):
    #     # Create the socket connection and send the packet
    #     s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s.sendto(packet,(destIP,destPort))
    #     s.close()

    # def Wake(self, destPort = 7):
    #     logging.debug('chronossrv: Server.Wake(): initializing.')
    #     self.MakeMagicPacket(self.serverMac)
    #     self.SendPacket(self.packet, self.serverIP, destPort)
    #     logging.info("chronossrv: Server.Wake(): Packet successfully sent to " + self.serverMac)
    #     db = chronosdb.DBAction()
    #     db.InsertSrvState(True, "WoL packet sent")
    #     db.Close()
    #     logging.debug('chronossrv: Server.Wake(): Database updated.')
    def CreateMagicPacket(self, macaddress: str) -> bytes:
        """
        Create a magic packet.
        A magic packet is a packet that can be used with the for wake on lan
        protocol to wake up a computer. The packet is constructed from the
        mac address given as a parameter.
        Args:
            macaddress: the mac address that should be parsed into a magic packet.
        """
        if len(macaddress) == 17:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, "")
        elif len(macaddress) != 12:
            raise ValueError("Incorrect MAC address format")
    
        return bytes.fromhex("F" * 12 + macaddress * 16)
    
    
    def Wake(self) -> None:
        """
        Wake up computers having any of the given mac addresses.
        Wake on lan must be enabled on the host device.
        Args:
            macs: One or more macaddresses of machines to wake.
        Keyword Args:
            ip_address: the ip address of the host to send the magic packet to.
            port: the port of the host to send the magic packet to.
            interface: the ip address of the network adapter to route the magic packet through.
        """
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

    def Poweroff(self):
            logging.debug('chronossrv: Server.Poweroff(): initializing.')
            if subprocess.Popen(f"ssh -i{self.serverCert} {self.serverAcc}@{self.serverIP} sudo poweroff", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate():
                logging.debug("chronossrv: Server.Poweroff(): sent: ssh -i{rsaCertificate} {serverAcc}@{serverIP} sudo poweroff")
                logging.info('chronossrv: Server.Poweroff(): Poweroff sent.')
                # db = chronosdb.DBAction()
                # db.InsertSrvState(False, "Shutdown sent")
                # db.Close()
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

    def VerifyState(self):
        serverState = self.Ping()
        db = chronosdb.DBAction()
        if not (serverState == db.CheckSrvState()):
            logging.warning("chronossrv: Server init: inconsistency in server DB state, fixing")
            db.InsertSrvState(serverState, "Status fixed by server constructor")
        db.Close()
        logging.debug("chronossrv: Server init complete")

class ServerOld():
    def MakeMagicPacket(self, macAddress):
        # Take the entered MAC address and format it to be sent via socket
        splitMac = str.split(macAddress,':')

        # Pack together the sections of the MAC address as binary hex
        hexMac = struct.pack('BBBBBB', int(splitMac[0], 16),
                             int(splitMac[1], 16),
                             int(splitMac[2], 16),
                             int(splitMac[3], 16),
                             int(splitMac[4], 16),
                             int(splitMac[5], 16))

        self.packet = b'\xff' * 6 + hexMac * 16 #create the magic packet from MAC address

    def SendPacket(self, packet, destIP, destPort = 7):
        # Create the socket connection and send the packet
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(packet,(destIP,destPort))
        s.close()

    def Wake(self, macAddress, destIP, destPort=7):
        logging.debug('chronossrv: Server.Wake(): initializing.')
        self.MakeMagicPacket(macAddress)
        self.SendPacket(self.packet, destIP, destPort)
        logging.info("chronossrv: Server.Wake(): Packet successfully sent to " + macAddress)
        db = chronosdb.DBAction()
        db.InsertSrvState(True, "WoL packet sent")
        db.Close()
        logging.debug('chronossrv: Server.Wake(): Database updated.')

    def Poweroff(self, serverIP, serverAcc, rsaCertificate):
            logging.debug('chronossrv: Server.Poweroff(): initializing.')
            if subprocess.Popen(f"ssh -i{rsaCertificate} {serverAcc}@{serverIP} sudo poweroff", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate():
                logging.debug("chronossrv: Server.Poweroff(): sent: ssh -i{rsaCertificate} {serverAcc}@{serverIP} sudo poweroff")
                logging.info('chronossrv: Server.Poweroff(): Poweroff sent.')
                db = chronosdb.DBAction()
                db.InsertSrvState(False, "Shutdown sent")
                db.Close()
                logging.debug("chronossrv: Server.Poweroff(): Database updated")
            else:
                logging.error('chronossrv: Server.Poweroff(): Poweroff fucked')

    def Ping(self, serverIP):
        logging.debug("chronossrv: Ping: initializing")
        hostUp = True if os.system("ping -c 1 " + serverIP) == 0 else False
        logging.debug("chronossrv: Ping: sent ping -c 1 {serverIP}, evaluated as {hostUP}.")
        if hostUp:
            logging.info("chronossrv: Ping: host is up, returning true")
            return True
        else:
            logging.info("chronossrv: Ping: host is down, returning false")
            return False


if __name__ == '__main__':
    serverIP = config["Server"]["IP"]
    serverMac = config["Server"]["Mac"]
    serverAcc = config["Server"]["username"]
    rsaCertificate = config["Server"]["rsaCertificate"]
    rutherford = Server(serverIP, serverMac, serverAcc, rsaCertificate)
    print('[W]ake on lan')
    print('[P]oweroff')
    print("P[I]ng")
    action = input('Your choice? ').upper()
    if action == 'W':
        rutherford.Wake()
    elif action == 'P':
        rutherford.Poweroff()
    elif action == "I":
        rutherford.Ping()
    else:
        print('wrong input')
