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
<<<<<<< HEAD
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
=======
        self.quiesce_start_time = int(config["Timer"]["quiesceStartTime"])
        logging.debug("chronostimer: Timer.init> quiesceStartTime read from config as {a}".format(a = self.quiesce_start_time))
        self.quiesce_end_time = int(config["Timer"]["quiesceEndTime"])
        logging.debug("chronostimer: Timer.init> quiesceEndTime read from config as {a}".format(a = self.quiesce_end_time))
        self.no_quiesce_days = config["Timer"]["quiesceDays"].split(",")
        self.no_quiesce_days = [int(s) for s in self.no_quiesce_days]
        logging.debug("chronostimer: Timer.init> noshutdown_serverDay read from config as {a}".format(a = self.no_quiesce_days))
        self.current_time = 100*self.now.hour + self.now.minute
        self.current_day = self.now.weekday()                    # [0-6] - TBD: CurrentDayEval() - evaluate against holidays
        logging.debug("chronostimer: Timer.init> fin.")

    def report(self):
        logging.debug("chronostimer: Timer.report> init")
        print("Time now: {a} on day {b}".format(a = 100*self.now.hour + self.now.minute, b = self.now.weekday()))
        print("quiesceStartTime - quiesceEndTime set to: {a} - {b}".format(a = self.quiesce_start_time, b = self.quiesce_end_time))
        print("is_poweron_surpressed_by_date_and_time returns {a}".format(a = self.is_poweron_surpressed_by_date_and_time()))
        print("is_today_workday returns {a}".format(a = self.is_today_workday()))
        print("is_tomorrow_workday returns {a}".format(a = self.is_tomorrow_workday()))
        print("is_now_after_quiesce_start_time returns {a}".format(a = self.is_now_after_quiesce_start_time()))
        print("is_now_before_quiesce_end_time returns {a}".format(a = self.is_now_before_quiesce_end_time()))
        print("is_now_within_quiesce_time returns {a}".format(a = self.is_now_within_quiesce_time()))
        print("should_server_be_down returns: {a}.".format(a = self.should_server_be_down()))
        print("should_presence_be_got_before_poweron returns: {a}".format(a = self.should_presence_be_got_before_poweron()))
        logging.debug("chronostimer: Timer.report> fin.")

    def is_poweron_surpressed_by_date_and_time(self):
        logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> init")
        result = False
        if self.is_now_within_quiesce_time():
            logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> is_now_within_quiesce_time() == true")
            if self.is_tomorrow_workday():
                logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> is_tomorrow_workday() == true")
                if self.is_today_workday():
                    logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> is_today_workday() == true; result = True")
                    result = True
                elif not self.is_now_before_quiesce_end_time():
                    logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> !is_now_before_quiesce_end_time() == true; result = True")
                    result = True
            elif self.is_today_workday() and self.is_now_before_quiesce_end_time():
                logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> is_today_workday() == true and is_now_before_quiesce_end_time == true; result = True")
                result = True
        logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> returns {a}".format(a = result))
        return result

    def is_today_workday(self):
        result = True if not self.current_day in self.no_quiesce_days else False
        logging.debug("chronostimer: Timer.is_today_workday> returns {a}".format(a = result))
        return result

    def is_tomorrow_workday(self):
        result = True if ((self.current_day + 1) not in self.no_quiesce_days) and ((self.current_day - 6) not in self.no_quiesce_days) else False
        logging.debug("chronostimer: Timer.is_tomorrow_workday> returns {a}".format(a = result))
        return result

    def is_now_after_quiesce_start_time(self):
        result = True if self.current_time >= self.quiesce_start_time else False
        logging.debug("chronostimer: Timer.is_now_after_quiesce_start_time> returns {a}".format(a = result))
        return result

    def is_now_before_quiesce_end_time(self):
        result = True if self.current_time <= self.quiesce_end_time else False
        logging.debug("chronostimer: Timer.is_now_before_quiesce_end_time> returns {a}".format(a = result))
        return result

    def is_now_within_quiesce_time(self):
        logging.debug("chronostimer: Timer.is_now_within_quiesce_time> init")
        result = False
        if self.quiesce_start_time > self.quiesce_end_time:
            logging.debug("chronostimer: Timer.is_now_within_quiesce_time> quiesce_start_time > quiesce_end_time")
            result = True if (self.is_now_after_quiesce_start_time() or self.is_now_before_quiesce_end_time()) else False
        elif self.quiesce_start_time < self.quiesce_end_time:
            logging.debug("chronostimer: Timer.is_now_within_quiesce_time> quiesce_start_time < quiesce_end_time")
            result = True if (self.is_now_after_quiesce_start_time() and self.is_now_before_quiesce_end_time()) else False
        logging.debug("chronostimer: Timer.is_now_within_quiesce_time> result = {a}".format(a = result))
        return result

    def should_server_be_down(self):
        logging.debug("chronostimer: Timer.should_server_be_down> init")
        if self.is_powertimer_surpressed():
            logging.debug("chronostimer: Timer.should_server_be_down> is_powertimer_surpressed evaluated as true, returning false")
            return False
        elif self.is_poweron_surpressed_by_date_and_time():
            logging.debug("chronostimer: Timer.should_server_be_down> is_poweron_surpressed_by_date_and_time evaluated as true, returning true")
            return True
        else:
            logging.debug("chronostimer: Timer.should_server_be_down> defaulting to false")
            return False
        logging.debug("chronostimer: Timer.should_server_be_down> fin.")
>>>>>>> dev
    
    def is_powertimer_surpressed(self):
        # cekni hardlocky proti DB
<<<<<<< HEAD
        logging.debug("chronostimer: Timer.SurpressPoweroffByOverride> defaulting to false")
        return False

    def PresenceCheckBeforePoweron(self):
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> init")
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> checking: SurpressPoweronByDate")
        if self.SurpressPoweronByDate():
            logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> SurpressPoweronByDate returned True")
            logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> checking: quiesceEndTime({a}) - 100 <= currentTime({b})")
            if (self.quiesceEndTime - 100) <= self.currentTime:
                logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> returning True")
                return True
            else:
                logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> returning False")
                return False
        else:
            logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> SurpressPoweronByDate returned False, returning False")
            return False
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> fin.")
=======
        logging.debug("chronostimer: Timer.is_powertimer_surpressed> defaulting to false")
        return False

    def should_presence_be_got_before_poweron(self):
        logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> init")
        logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> checking: is_poweron_surpressed_by_date_and_time")
        if self.is_poweron_surpressed_by_date_and_time():
            logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> is_poweron_surpressed_by_date_and_time returned True")
            logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> checking: quiesceEndTime({a}) - 100 <= currentTime({b})")
            if (self.quiesce_end_time - 100) <= self.current_time:
                logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> returning True")
                return True
            else:
                logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> returning False")
                return False
        else:
            logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> is_poweron_surpressed_by_date_and_time returned False, returning False")
            return False
        logging.debug("chronostimer: Timer.should_presence_be_got_before_poweron> fin.")
>>>>>>> dev

if __name__ == '__main__':

    now = datetime.now()
    query = Timer()
<<<<<<< HEAD
    query.Report()
=======
    query.report()
>>>>>>> dev
