######################################
# Intra-Day forecast
######################################


#--------------------------
# Import required modules
#--------------------------
import numpy as np
import pandas as pd
import datetime as dt
from sys import exit
from datetime import timedelta
import matplotlib.pyplot as plt


#--------------------------
# Read the data from excel
#--------------------------
file = ('/home/surbhi/Downloads/assignment_surbhi/solar_data.xlsx')
power = pd.read_excel(file, sheet_name=0, index_col=0)
weather = pd.read_excel(file, sheet_name=1, index_col=0)


#--------------------------
# Restructure the data
#--------------------------
power = power.drop(['PLANT_ID'],axis=1)
weather = weather.drop(['PLANT_ID'],axis=1)
#power["UNIQUE_ID"] = power["PLANT_ID"].astype(str) + '_' + power["INVERTER_ID"].astype(str) ---alternative
power = power.groupby(by=["DATE_TIME"]).sum()   #Multiple records for same timestamp are for different inverters. So summed up power for all inverters
data = pd.merge(weather,power, on='DATE_TIME', how="outer")
data = data.resample('15Min').mean()
data = data.drop(['DAILY_YIELD'],axis=1)
data = data.drop(['TOTAL_YIELD'],axis=1)
data = data.drop(['AMBIENT_TEMPERATURE'],axis=1)
data = data[data.index>='2020-06-10 00:00:00']
	

# #---------------------------------------------------------------
# # Data Smoothening
# #---------------------------------------------------------------
data = data.interpolate(method='linear',limit_direction='forward',limit=40)  #limit=40 for 10 hours missing data
data = data.rolling(4, win_type='gaussian').mean(std=10420)
data = data.shift(-2)



#---------------------------------------------------------
# Check for the validity of forecast start date
#---------------------------------------------------------
fc_start_date = '2020-06-11 00:00:00'                                     #Enter you Forecast start date here

if (fc_start_date.split()[1]!='00:00:00'):
	start = fc_start_date
	print ("\n You have initiated an INTRA-day Forecast for: " + fc_start_date + " \n \n ")
else:
	print ("\n This is an Intraday forecast.\n Please put a date that does not end with 00:00:00 \n")
	exit()



#---------------------------------------------------------------
# Features Engineering
#---------------------------------------------------------------
start = dt.datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
end = start.replace(hour=23, minute=45, second=00) 
date_rnge = pd.date_range(start=start, end=end, freq='15Min')

pred=[]

while start<=end:
		
	indx = start.strftime('%Y-%m-%d %H:%M:%S')
	
	min15    =  (start - dt.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
	min30    =  (start - dt.timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
	min45    =  (start - dt.timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S')
	min60    =  (start - dt.timedelta(minutes=60)).strftime('%Y-%m-%d %H:%M:%S')

	G   = data['IRRADIATION'].loc[indx]  #Current timeblock's irradiation value
	G15 = data['IRRADIATION'].loc[min15]  
	G30 = data['IRRADIATION'].loc[min30]
	G45 = data['IRRADIATION'].loc[min45]  
	G60 = data['IRRADIATION'].loc[min60]   
	
	P15 = data['AC_POWER'].loc[min15]
	P30 = data['AC_POWER'].loc[min30]
	P45 = data['AC_POWER'].loc[min45]
	P60 = data['AC_POWER'].loc[min60]
	
	P = (((G/G15)*P15) + ((G/G30)*P30) + ((G/G45)*P45) + ((G/G60)*P60))/4

	pred.append(P)

	start= start + dt.timedelta(minutes=15)

#--------------------------------------------------------
# Convert the forecast list to dataframe for smoothening
#--------------------------------------------------------
pred1=pd.DataFrame(pred, index=date_rnge)
newpred = pred1.rolling(4, win_type='gaussian').mean(std=10420)
newpred = newpred.shift(-2)
newpred = newpred.fillna(0)
newpred.columns = ['AC_POWER_FC']

print("\n")
print (newpred)
newpred.to_csv('/home/surbhi/Desktop/newFC.csv')




