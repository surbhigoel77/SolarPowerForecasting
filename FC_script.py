## Script to obtain solar forecast

import os
import imp
import datetime as dt
from datetime import timedelta

fc_start = dt.datetime.strptime('2020-06-13 00:00:00',"%Y-%m-%d %H:%M:%S")
fc_end = fc_start + dt.timedelta(hours=23, minutes=45,seconds=00)

path = imp.load_source('DayAhead','/home/surbhi/Desktop/DayAhead.py')
model_name = os.path.basename(path).split('.')[0]
DayHead = getattr(path,model_name, None)

# os.chdir('/home/surbhi/Desktop/FC.py')

# Forecast = DayAhead(fc_start,fc_end)