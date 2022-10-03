#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

import confighelper

from datetime import datetime

class Timer():
    def __init__(self):
        logging.debug("chronostimer: Timer> init")
        config = confighelper.read_config()
        self.now = datetime.now()
        self.quiesceStartTime = int(config["Timer"]["quiesceStartTime"])
        logging.debug("chronostimer: Timer.init> quiesceStartTime read from config as {a}".format(a = self.quiesceStartTime))
        self.quiesceEndTime = int(config["Timer"]["quiesceEndTime"])
        logging.debug("chronostimer: Timer.init> quiesceEndTime read from config as {a}".format(a = self.quiesceEndTime))
        self.noPoweroffDay = config["Timer"]["quiesceDays"].split(",")
        self.noPoweroffDay = [int(s) for s in self.noPoweroffDay]
        logging.debug("chronostimer: Timer.init> noPoweroffDay read from config as {a}".format(a = self.noPoweroffDay))
        self.currentTime = 100*self.now.hour + self.now.minute
        self.currentDay = self.now.weekday()                    # [0-6] - TBD: CurrentDayEval() - evaluate against holidays
        logging.debug("chronostimer: Timer.init> fin.")

    def Report(self):
        logging.debug("chronostimer: Timer.Report> init")
        print("Time now: {a} on day {b}".format(a = 100*self.now.hour + self.now.minute, b = self.now.weekday()))
        print("quiesceStartTime - quiesceEndTime set to: {a} - {b}".format(a = self.quiesceStartTime, b = self.quiesceEndTime))
        print("SurpressPoweron returns: {a}.".format(a = self.SurpressPoweron()))
        print("PresenceCheckBeforePoweron returns: {a}".format(a = self.PresenceCheckBeforePoweron()))
        logging.debug("chronostimer: Timer.Report> fin.")

    # TBD Holidays - build into init prolly?
    def SurpressPoweronByDate(self):
        logging.debug("chronostimer: Timer.SurpressPoweronByDate> init")
        logging.debug("chronostimer: Timer.SurpressPoweronByDate> Current day ({a}) evaluated as outside of noPoweroffDay ({b})".format(a = self.currentDay, b = self.noPoweroffDay))
        if not self.currentDay in self.noPoweroffDay:
            logging.debug("chronostimer: Timer.SurpressPoweronByDate> Current day ({a}) evaluated as outside of noPoweroffDay ({b})".format(a = self.currentDay, b = self.noPoweroffDay))
            if ((self.currentDay + 1) in self.noPoweroffDay) or ((self.currentDay - 6) in self.noPoweroffDay):
                logging.debug("chronostimer: Timer.SurpressPoweronByDate> Current day ({a}) evaluated as day before of noPoweroffDay ({b})".format(a = self.currentDay, b = self.noPoweroffDay))
                if (self.currentTime < self.quiesceEndTime):
                    logging.debug("chronostimer: Timer.SurpressPoweronByDate> Quiesce time evaluated as true")            
                    return True
                else:
                    logging.debug("chronostimer: Timer.SurpressPoweronByDate> Quiesce time evaluated as false")
                    return False
            else:
                logging.debug("chronostimer: Timer.SurpressPoweronByDate> Current day evaluated as not before noPoweroffDay")
                if ((self.currentTime < self.quiesceEndTime) or (self.currentTime >= self.quiesceStartTime)):
                    logging.debug("chronostimer: Timer.SurpressPoweronByDate> Quiesce time evaluated as true")            
                    return True
                else: 
                    logging.debug("chronostimer: Timer.SurpressPoweronByDate> Quiesce time evaluated as false")
                    return False
        else:
            logging.debug("chronostimer: Timer.SurpressPoweronByDate> Current day ({a}) evaluated as inside of noPoweroffDay ({b})".format(a = self.currentDay, b = self.noPoweroffDay))
            if ((self.currentDay + 1) in self.noPoweroffDay) or (self.currentDay - 6) in self.noPoweroffDay:
                logging.debug("chronostimer: Timer.SurpressPoweronByDate> Current day evaluated as inside of noPoweroffDay, quiesce time evaluated as false")
                return False
            else:
                logging.debug("chronostimer: Timer.SurpressPoweronByDate> Current day evaluated as in the end of noPoweroffDay")
                if (self.currentTime >= self.quiesceStartTime):
                    logging.debug("chronostimer: Timer.SurpressPoweronByDate> Quiesce time evaluated as true")
                    return True
                else:
                    logging.debug("chronostimer: Timer.SurpressPoweronByDate> Quiesce time evaluated as false")
                    return False
        logging.debug("chronostimer: Timer.SurpressPoweronByDate> fin.")

    def SurpressPoweron(self):
        logging.debug("chronostimer: Timer.SurpressPoweron> init")
        if self.SurpressPoweroffByOverride():
            logging.debug("chronostimer: Timer.SurpressPoweron> SurpressPoweroffByOverride evaluated as true, returning false")
            return False
        elif self.SurpressPoweronByDate():
            logging.debug("chronostimer: Timer.SurpressPoweron> SurpressPoweronByDate evaluated as true, returning true")
            return True
        else:
            logging.debug("chronostimer: Timer.SurpressPoweron> defaulting to false")
            return False
        logging.debug("chronostimer: Timer.SurpressPoweron> fin.")
    
    def SurpressPoweroffByOverride(self):
        # cekni hardlocky proti DB
        logging.debug("chronostimer: Timer.SurpressPoweroffByOverride> defaulting to false")
        return False

    def PresenceCheckBeforePoweron(self):
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> init")
        if self.SurpressPoweronByDate():
            if (self.quiesceEndTime - 100) <= self.currentTime:
                return True
            else:
                return False
        else:
            return False
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> fin.")

if __name__ == '__main__':

    now = datetime.now()
    query = Timer()
    query.Report()