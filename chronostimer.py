#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

import confighelper

from datetime import datetime

class Timer():
    def __init__(self):
        logging.debug("Timer innit commenced")
        config = confighelper.read_config()
        self.now = datetime.now()
        self.quiesceStartTime = int(config["Timer"]["quiesceStartTime"])
        logging.debug("Timer: init: quiesceStartTime read from config as {a}".format(a = self.quiesceStartTime))
        self.quiesceEndTime = int(config["Timer"]["quiesceEndTime"])
        logging.debug("Timer: init: quiesceEndTime read from config as {a}".format(a = self.quiesceEndTime))
        self.noPoweroffDay = config["Timer"]["quiesceDays"].split(",")
        self.noPoweroffDay = [int(s) for s in self.noPoweroffDay]
        logging.debug("Timer: init: noPoweroffDay read from config as {a}".format(a = self.noPoweroffDay))
        self.currentTime = 100*self.now.hour + self.now.minute
        self.currentDay = self.now.weekday()                    # [0-6] - TBD: CurrentDayEval() - evaluate against holidays

    def Report(self):
        print("Time now: {a} on day {b}".format(a = 100*self.now.hour + self.now.minute, b = self.now.weekday()))
        print("quiesceStartTime - quiesceEndTime set to: {a} - {b}".format(a = self.quiesceStartTime, b = self.quiesceEndTime))
        print("SurpressPoweron returns: {a}.".format(a = self.SurpressPoweron()))
        print("PresenceCheckBeforePoweron returns: {a}".format(a = self.PresenceCheckBeforePoweron()))

    # TBD Holidays - build into init prolly?
    def SurpressPoweronByDate(self):
        if not self.currentDay in self.noPoweroffDay:
            logging.debug("SurpressPoweronByDate: Current day ({a}) evaluated as outside of noPoweroffDay ({b})".format(a = self.currentDay, b = self.noPoweroffDay))
            if ((self.currentDay + 1) in self.noPoweroffDay) or ((self.currentDay - 6) in self.noPoweroffDay):
                logging.debug("SurpressPoweronByDate: Current day ({a}) evaluated as day before of noPoweroffDay ({b})".format(a = self.currentDay, b = self.noPoweroffDay))
                if (self.currentTime < self.quiesceEndTime):
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")            
                    return True
                else:
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
                    return False
            else:
                logging.debug("SurpressPoweronByDate: Current day evaluated as not before noPoweroffDay")
                if ((self.currentTime < self.quiesceEndTime) or (self.currentTime >= self.quiesceStartTime)):
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")            
                    return True
                else: 
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
                    return False
        else:
            logging.debug("SurpressPoweronByDate: Current day ({a}) evaluated as inside of noPoweroffDay ({b})".format(a = self.currentDay, b = self.noPoweroffDay))
            if ((self.currentDay + 1) in self.noPoweroffDay) or (self.currentDay - 6) in self.noPoweroffDay:
                logging.debug("SurpressPoweronByDate: Current day evaluated as inside of noPoweroffDay, quiesce time evaluated as false")
                return False
            else:
                logging.debug("SurpressPoweronByDate: Current day evaluated as in the end of noPoweroffDay")
                if (self.currentTime >= self.quiesceStartTime):
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")
                    return True
                else:
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
                    return False

    def SurpressPoweron(self):
        if self.SurpressPoweroffByOverride():
            logging.debug("SurpressPoweron: SurpressPoweroffByOverride evaluated as true, returning false")
            return False
        elif self.SurpressPoweronByDate():
            logging.debug("SurpressPoweron: SurpressPoweronByDate evaluated as true, returning true")
            return True
        else:
            logging.debug("SurpressPoweron: defaulting to false")
            return False
    
    def SurpressPoweroffByOverride(self):
        # cekni hardlocky proti DB
        logging.debug("SurpressPoweroffByOverride: defaulting to false")
        return False

    def PresenceCheckBeforePoweron(self):
        if self.SurpressPoweronByDate():
            if (self.quiesceEndTime - 100) <= self.currentTime:
                return True
            else:
                return False
        else:
            return False

if __name__ == '__main__':

    now = datetime.now()
    query = Timer()
    query.Report()