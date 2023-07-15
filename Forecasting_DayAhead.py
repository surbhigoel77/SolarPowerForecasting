########################################################
####### Day-Ahead forecast for solar power plant #######
########################################################


#--------------------------
# Import modules
#--------------------------
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
from ffnet import ffnet, mlgraph, savenet, loadnet


#--------------------------
# Read the data from excel
#--------------------------
file = ('/home/surbhi/Downloads/assignment_surbhi/solar_data.xlsx')
power = pd.read_excel(file, sheet_name=0, index_col=0)
weather = pd.read_excel(file, sheet_name=1, index_col=0)


#-----------------------------------------------------
# Restructure the data to extract only requisite data
#-----------------------------------------------------
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
# actual = data[data.index>='2020-06-13 00:00:00']
# actual.to_csv('/home/surbhi/Desktop/actual.csv')


# #---------------------------------------------------------------
# # Data Smoothening
# #---------------------------------------------------------------
data = data.interpolate(method='linear',limit_direction='forward',limit=40)  #limit=40 for 10 hours missing data
data = data.rolling(4, win_type='gaussian').mean(std=10420)
data = data.shift(-2)


#---------------------------------------------------------------
# Forecasting for the given time interval
#--------------------------------------------------------------
fc_interval = pd.date_range(start='2020-06-13 00:00:00', end='2020-06-17 23:45:00', freq='1D')
forecast=[]

for fcdate in fc_interval:

	fc_start=fcdate

  #--------------------------------------------------------------
	# Features Engineering
	#---------------------------------------------------------------
	start = fc_start #dt.datetime.strptime(fc_start,'%Y-%m-%d %H:%M:%S')
	end = start + dt.timedelta(hours=23,minutes=59,seconds=00)
	date_rnge = pd.date_range(start=start, end=end, freq='15Min')

	InData=[]  #List to hold the input features

	while start<=end:
		features=[]
		p=[]
		
		indx = start.strftime('%Y-%m-%d %H:%M:%S')
		day1     = 	(start - dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
		day2     = 	(start - dt.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
		day3     = 	(start - dt.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
			
		features.append((data['AC_POWER'].loc[day1])/2000)
		features.append((data['AC_POWER'].loc[day2])/2000)  # 1-day before's data
		features.append((data['AC_POWER'].loc[day3])/2000)  # 1-day before's data
		features.append(data['IRRADIATION'].loc[indx])
		features.append(data['MODULE_TEMPERATURE'].loc[indx])
		features.append(start.hour)

		InData.append(features)   #Input to the model
		
		start= start + dt.timedelta(minutes=15)    #Interate the start timeblock

	#------------------------------
	# Load the trained Model
	#------------------------------
	fc_model = loadnet('Pres.net')
	prediction = fc_model(InData)


	#-------------------------------------------
	# Remove outliers from non-generation hours
	#------------------------------------------
	p=[]

	for i in range(len(prediction))	:
		if ((date_rnge[i].strftime('%H:%M:%S') >='06:00:00') & (date_rnge[i].strftime('%H:%M:%S') <='19:00:00')):  #Sunrise and Sunset time
			p.append((prediction[i][0])*2000)
		else:
			p.append(0)

	forecast.append(p)
	
	print("Successful Day-ahead forecasting for : " + date_rnge[i].strftime('%Y-%m-%d'))



#--------------------------------------------------------
# Convert the forecast list to dataframe for smoothening
#--------------------------------------------------------
forecast=np.array(forecast).ravel()
fc_interval2 = pd.date_range(start='2020-06-13 00:00:00', end='2020-06-17 23:45:00', freq='15Min')
forecast_df = pd.DataFrame(forecast, columns=['Ac_power'],index=fc_interval2)
forecast_df = forecast_df.rolling(4, win_type='gaussian').mean(std=10420)
forecast_df = forecast_df.shift(-2)

forecast_df.to_csv('/home/surbhi/Desktop/DA_prediction.csv')  #Saved the forecast to csv file for analysis












