#!/usr/bin/env python3

import socket, struct, subprocess
import confighelper

config = confighelper.read_config()

class Waker():
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
        self.MakeMagicPacket(macAddress)
        self.SendPacket(self.packet, destIP, destPort)
        print('Packet successfully sent to', macAddress)

class Worker():
    def Poweroff(self, serverAcc, serverIP, rsaCertificate):
            if subprocess.Popen(f"ssh -i{rsaCertificate} {serverAcc}@{serverIP} sudo poweroff", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate():
                print('Poweroff sent.')
            else:
                print('Poweroff fucked')

if __name__ == '__main__':
    serverIP = config["Server"]["IP"]
    serverMac = config["Server"]["Mac"]
    serverAcc = config["Server"]["username"]
    rsaCertificate = config["Server"]["rsaCertificate"]
    print('[W]ake on lan')
    print('[P]oweroff')
    action = input('Your choice? ').upper()
    if action == 'W':
        srvState = Waker()
        srvState.Wake(serverMac, serverIP)
    elif action == 'P':
        srvState = Worker()
        srvState.Poweroff(serverAcc, serverIP, rsaCertificate)
    else:
        print('wrong input')
