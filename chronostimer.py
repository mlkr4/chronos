#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

import confighelper

config = confighelper.read_config()

from datetime import datetime

quiesceStartTime = int(config["Timer"]["quiesceStartTime"])
logging.debug("SurpressPoweronByDate: quiesceStartTime read from config as {a}".format(a = quiesceStartTime))
quiesceEndTime = int(config["Timer"]["quiesceEndTime"])
logging.debug("SurpressPoweronByDate: quiesceEndTime read from config as {a}".format(a = quiesceEndTime))
noPoweroffDay = config["Timer"]["quiesceDays"].split(",")
noPoweroffDay = [int(s) for s in noPoweroffDay]
logging.debug("SurpressPoweronByDate: noPoweroffDay read from config as {a}".format(a = noPoweroffDay))

class Timer():
    # TBD Holidays - build into init prolly?
    def SurpressPoweronByDate(self):
        now = datetime.now()
        currentTime = 100*now.hour + now.minute
        currentDay = now.weekday()                    # [0-6] - TBD: CurrentDayEval() - evaluate against holidays
        if not currentDay in noPoweroffDay:
            logging.debug("SurpressPoweronByDate: Current day ({a}) evaluated as outside of noPoweroffDay ({b})".format(a = currentDay, b = noPoweroffDay))
            if ((currentDay + 1) in noPoweroffDay) or ((currentDay - 6) in noPoweroffDay):
                logging.debug("SurpressPoweronByDate: Current day ({a}) evaluated as day before of noPoweroffDay ({b})".format(a = currentDay, b = noPoweroffDay))
                if (currentTime <= quiesceEndTime):
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")            
                    return True
                else:
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
                    return False
            else:
                logging.debug("SurpressPoweronByDate: Current day evaluated as not before noPoweroffDay")
                if ((currentTime <= quiesceEndTime) or (currentTime >= quiesceStartTime)):
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as true")            
                    return True
                else: 
                    logging.debug("SurpressPoweronByDate: Quiesce time evaluated as false")
                    return False
        else:
            logging.debug("SurpressPoweronByDate: Current day ({a}) evaluated as inside of noPoweroffDay ({b})".format(a = currentDay, b = noPoweroffDay))
            if ((currentDay + 1) in noPoweroffDay) or (currentDay - 6) in noPoweroffDay:
                logging.debug("SurpressPoweronByDate: Current day evaluated as inside of noPoweroffDay, quiesce time evaluated as false")
                return False
            else:
                logging.debug("SurpressPoweronByDate: Current day evaluated as in the end of noPoweroffDay")
                if (currentTime >= quiesceStartTime):
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

if __name__ == '__main__':

    now = datetime.now()
    query = Timer()
    print("Time now: {a} on day {b}".format(a = 100*now.hour + now.minute, b = now.weekday()))
    print("quiesceStartTime - quiesceEndTime set to: {a} - {b}".format(a = quiesceStartTime, b = quiesceEndTime))
    print("SurpressPoweron returns: {a}.".format(a = query.SurpressPoweron()))