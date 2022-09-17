#!/usr/bin/env python3

from datetime import datetime
import socket, struct, os, logging, subprocess

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

now = datetime.now()

serverIP = "192.168.1.100"
serverMac = "e0:d5:5e:e7:20:3a"
rsaCertificate = "/home/dan/..."
quiesceStartTime = 2300
quiesceEndTime = 930

class Waker():
    def makeMagicPacket(self, macAddress):
        # Take the entered MAC address and format it to be sent via socket
        splitMac = str.split(macAddress,':')
    
        # Pack together the sections of the MAC address as binary hex
        hexMac = struct.pack('BBBBBB', int(splitMac[0], 16),
                             int(splitMac[1], 16),
                             int(splitMac[2], 16),
                             int(splitMac[3], 16),
                             int(splitMac[4], 16),
                             int(splitMac[5], 16))
    
        self.packet = '\xff' * 6 + hexMac * 16 #create the magic packet from MAC address
    
    def sendPacket(self, packet, destIP, destPort = 7):
        # Create the socket connection and send the packet
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(packet,(destIP,destPort))
        s.close()
        
    def wake(self, macAddress, destIP, destPort=7):
        self.makeMagicPacket(macAddress)
        self.sendPacket(self.packet, destIP, destPort)
        print('Packet successfully sent to', macAddress)

def SurpressPoweronByDate():
    currentTime = 100*now.hour + now.minute
    currentDay = now.weekday()                     # [0-6] - TBD: CurrentDayEval() - evaluate against holidays
    if (currentDay <= 3):                         # mon - thu
        logging.debug("SurpressPoweronByDate: Current day evaluated as MON-THU")
        if ((currentTime <= quiesceEndTime) or (currentTime >= quiesceStartTime)):
            logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")            
            return True
        else: 
            logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
            return False
    elif (currentDay == 4):                     # fri OR workday before holiday
        logging.debug("SurpressPoweronByDate: Current day evaluated as FRI")
        if (currentTime <= quiesceEndTime):
            logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")            
            return True
        else:
            logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
            return False
    elif (currentDay == 5):
        logging.debug("SurpressPoweronByDate: Current day evaluated as SAT, quiesce time evaluated as false")
        return False                             # sat OR holiday before holiday
    else:                                    # sun OR holiday before workday
        logging.debug("SurpressPoweronByDate: Current day evaluated as SUN")
        if (currentTime >= quiesceStartTime):
            logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")
            return True
        else:
            logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
            return False

def SurpressPoweron():
    if SurpressPoweroffByOverride():
        logging.debug("SurpressPoweron: SurpressPoweroffByOverride evaluated as true, returning false")
        return False
    elif SurpressPoweronByDate():
        logging.debug("SurpressPoweron: SurpressPoweronByDate evaluated as true, returning true")
        return True
    else:
        logging.debug("SurpressPoweron: defaulting to false")
        return False

def SurpressPoweroffByOverride():
    # cekni hardlocky proti DB
    logging.debug("SurpressPoweroffByOverride: defaulting to false")
    return False

def PresenceState():
    # cekni prezenci proti DB
    logging.debug("PresenceState: defaulting to true")
    return True

def PowerState():
    hostUp = True if os.system("ping -c 1 " + serverIP) is 0 else False
    if not CheckStateDB("hostUP", hostUp):
        logging.warning("PowerState: CheckStateDB returned unexpected state, fixing")
        UpdateStateDB("hostUP", hostUp)
    if hostUp:
        logging.debug("PowerState: host is up, returning true")
        return True
    else:
        logging.debug("PowerState: host is down, returning false")
        return False

def Startup():
    wol = Waker()
    wol.wake(serverMac)
    UpdateStateDB("hostUP", True)
    logging.event("Startup: WoL sequence complete")

def Shutdown():
    #send shutdown pres ssh, zapis do DB
    if subprocess.Popen(f"ssh -i{rsaCertificate} chronos@{serverIP} sudo poweroff", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate():
        UpdateStateDB("hostUP", False)
        logging.event("Shutdown: shutdown sequence complete")
    else
        logging.error("Shutdown: shutdown sequence failed")

def CheckStateDB(query, state):
    logging.debug("CheckStateDB defaulting to true")
    return True

def UpdateStateDB(query, state):
    logging.debug("UpdateStateDB defaulting to true")
    return True

if __name__ == '__main__':

    if PowerState():
        if PresenceState():
            if SurpressPoweron():
                logging.event("Calling shutdown sequence based on SurpressPoweron")
                Shutdown()
            else:
                logging.debug("No PWR change based on PowerState, PresenceState, !SurpressPoweron")
        else:
            logging.event("Calling shutdown sequence based on PresenceState")
            Shutdown()
    else:
        if PresenceState():
            if not SurpressPoweron():
                logging.event("Calling startup sequence based on PresenceState and !SurpressPoweron")
                Startup()
            else:
                logging.debug("No PWR change based on !PowerState, PresenceState, SurpressPoweron")
        else:
            logging.debug("No PWR change based on !PowerState, !PresenceState")
