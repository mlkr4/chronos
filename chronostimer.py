#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='event.log', filemode='w', format='%(asctime)s: %(name)s - %(levelname)s - %(message)s')

from datetime import datetime

quiesceStartTime = 2300
quiesceEndTime = 930

class Timer():
	# TBD Holidays, config in conf.ini
	def SurpressPoweronByDate(self):
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

	def SurpressPoweron(self):
	    if SurpressPoweroffByOverride():
	        logging.debug("SurpressPoweron: SurpressPoweroffByOverride evaluated as true, returning false")
	        return False
	    elif SurpressPoweronByDate():
	        logging.debug("SurpressPoweron: SurpressPoweronByDate evaluated as true, returning true")
	        return True
	    else:
	        logging.debug("SurpressPoweron: defaulting to false")
	        return False
	
	def SurpressPoweroffByOverride(self):
	    # cekni hardlocky proti DB
	    logging.debug("SurpressPoweroffByOverride: defaulting to false")
	    return False
