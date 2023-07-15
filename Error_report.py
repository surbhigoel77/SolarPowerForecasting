#Error_report

import math
#import xlwt
import datetime
import numpy as np
import pandas as pd
from ffnet import loadnet
import statsmodels.api as sm
from pandas import ExcelWriter
# from pdfrw import PdfReader, PdfWriter
# from xlsxwriter.utility import xl_range

forecast = pd.read_csv('/home/surbhi/Desktop/DA_prediction.csv')#,names=['Timestamp','AC_power'],index_col='Timestamp')

actual = pd.read_csv('/home/surbhi/Desktop/actual.csv')#,names=['Timestamp','AC_power'],index_col='Timestamp')

err = (actual['AC_POWER'].values-forecast['Ac_power'].values)#.abs()
mae = err.mean()
mape = round((((err/actual)*100).mean()),3)

# rmse_err = (err*err).mean()
# rmse = math.sqrt(rmse_err)
# nrmse = rmse/30000

err = ((actual['AC_POWER']-forecast['Ac_power'])/actual['AC_POWER'])*100