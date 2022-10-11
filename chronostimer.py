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
        self.quiesce_start_time = int(config["Timer"]["quiesceStartTime"])
        logging.debug("chronostimer: Timer.init> quiesceStartTime read from config as {a}".format(a = self.quiesce_start_time))
        self.quiesce_end_time = int(config["Timer"]["quiesceEndTime"])
        logging.debug("chronostimer: Timer.init> quiesceEndTime read from config as {a}".format(a = self.quiesce_end_time))
        self.no_quiesce_days = config["Timer"]["quiesceDays"].split(",")
        self.no_quiesce_days = [int(s) for s in self.no_quiesce_days]
        logging.debug("chronostimer: Timer.init> noPoweroffDay read from config as {a}".format(a = self.no_quiesce_days))
        self.current_time = 100*self.now.hour + self.now.minute
        self.current_day = self.now.weekday()                    # [0-6] - TBD: CurrentDayEval() - evaluate against holidays
        logging.debug("chronostimer: Timer.init> fin.")

    def report(self):
        logging.debug("chronostimer: Timer.report> init")
        print("Time now: {a} on day {b}".format(a = 100*self.now.hour + self.now.minute, b = self.now.weekday()))
        print("quiesceStartTime - quiesceEndTime set to: {a} - {b}".format(a = self.quiesce_start_time, b = self.quiesce_end_time))
        print("should_server_be_down returns: {a}.".format(a = self.should_server_be_down()))
        print("PresenceCheckBeforePoweron returns: {a}".format(a = self.PresenceCheckBeforePoweron()))
        logging.debug("chronostimer: Timer.report> fin.")

    # TBD Holidays - build into init prolly?
    # def is_poweron_surpressed_by_date_and_time(self):
    #     # TBD - atomizace jednotlivých fcí
    #     logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> init")
    #     logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Current day ({a}) evaluated as outside of noPoweroffDay ({b})".format(a = self.current_day, b = self.no_quiesce_days))
    #     if not self.current_day in self.no_quiesce_days:
    #         logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Current day ({a}) evaluated as outside of noPoweroffDay ({b})".format(a = self.current_day, b = self.no_quiesce_days))
    #         if ((self.current_day + 1) in self.no_quiesce_days) or ((self.current_day - 6) in self.no_quiesce_days):
    #             logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Current day ({a}) evaluated as day before of noPoweroffDay ({b})".format(a = self.current_day, b = self.no_quiesce_days))
    #             if (self.current_time < self.quiesce_end_time):
    #                 logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Quiesce time evaluated as true")            
    #                 return True
    #             else:
    #                 logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Quiesce time evaluated as false")
    #                 return False
    #         else:
    #             logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Current day evaluated as not before noPoweroffDay")
    #             if ((self.current_time < self.quiesce_end_time) or (self.current_time >= self.quiesce_start_time)):
    #                 logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Quiesce time evaluated as true")            
    #                 return True
    #             else: 
    #                 logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Quiesce time evaluated as false")
    #                 return False
    #     else:
    #         logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Current day ({a}) evaluated as inside of noPoweroffDay ({b})".format(a = self.current_day, b = self.no_quiesce_days))
    #         if ((self.current_day + 1) in self.no_quiesce_days) or (self.current_day - 6) in self.no_quiesce_days:
    #             logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Current day evaluated as inside of noPoweroffDay, quiesce time evaluated as false")
    #             return False
    #         else:
    #             logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Current day evaluated as in the end of noPoweroffDay")
    #             if (self.current_time >= self.quiesce_start_time):
    #                 logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Quiesce time evaluated as true")
    #                 return True
    #             else:
    #                 logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> Quiesce time evaluated as false")
    #                 return False
    #     logging.debug("chronostimer: Timer.is_poweron_surpressed_by_date_and_time> fin.")

    def is_poweron_surpressed_by_date_and_time(self):
        result = False
        if is_now_within_quiesce_time():
            if is_tomorrow_workday():
                if is_today_workday():
                    result = True
                elif not is_now_before_quiesce_end_time():
                    result = True
            elif is_today_workday() and is_now_before_quiesce_end_time():
                result = True
        return result

    def is_today_workday(self):
        return True if not self.current_day in self.no_quiesce_days else False

    def is_tomorrow_workday(self):
        result = False
        if self.is_today_holiday():
            if ((self.current_day + 1) not in self.no_quiesce_days) or (self.current_day - 6) not in self.no_quiesce_days:
                result = True
        return result

    def is_now_after_quiesce_start_time(self):
        return True if self.current_time >= self.quiesce_start_time else False

    def is_now_before_quiesce_end_time(self):
        return True if self.current_time <= self.quiesce_end_time else False

    def is_now_within_quiesce_time(self):
        result = False
        if self.quiesce_start_time > self.quiesce_end_time:
            result = True if is_now_after_quiesce_start_time() or is_now_before_quiesce_end_time()
        elif self.quiesce_start_time < self.quiesce_end_time:
            result = True if is_now_after_quiesce_start_time() and is_now_before_quiesce_end_time()
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
    
    def is_powertimer_surpressed(self):
        # cekni hardlocky proti DB
        logging.debug("chronostimer: Timer.is_powertimer_surpressed> defaulting to false")
        return False

    def PresenceCheckBeforePoweron(self):
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> init")
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> checking: is_poweron_surpressed_by_date_and_time")
        if self.is_poweron_surpressed_by_date_and_time():
            logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> is_poweron_surpressed_by_date_and_time returned True")
            logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> checking: quiesceEndTime({a}) - 100 <= currentTime({b})")
            if (self.quiesce_end_time - 100) <= self.current_time:
                logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> returning True")
                return True
            else:
                logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> returning False")
                return False
        else:
            logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> is_poweron_surpressed_by_date_and_time returned False, returning False")
            return False
        logging.debug("chronostimer: Timer.PresenceCheckBeforePoweron> fin.")

if __name__ == '__main__':

    now = datetime.now()
    query = Timer()
    query.report()