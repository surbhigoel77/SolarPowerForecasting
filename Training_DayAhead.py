########################################################
####### Day-Ahead Training for solar power plant #######
########################################################

import numpy as np
import pandas as pd
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


#--------------------------
# Restructure the data
#--------------------------
power = power.drop(['PLANT_ID'],axis=1)
weather = weather.drop(['PLANT_ID'],axis=1)
#power["UNIQUE_ID"] = power["PLANT_ID"].astype(str) + '_' + power["INVERTER_ID"].astype(str) ---alternative
power = power.groupby(by=["DATE_TIME"]).sum()   #Multiple records for same timestamp are for different inverters. So summed up power for all inverters
data = pd.merge(weather,power, on='DATE_TIME', how="outer")
data = data.drop(['DAILY_YIELD'],axis=1)
data = data.drop(['TOTAL_YIELD'],axis=1)
data = data.resample('15Min').mean()
data = data[(data.index>='2020-05-15 00:00:00') & (data.index<='2020-06-09 23:45:00')]
orig = data



#---------------------------------------------------------------
# Data Smoothening
#---------------------------------------------------------------
data = data.interpolate(method='linear',limit_direction='forward',limit=40)  #limit=40 for 10 hours missing data
data2 = data.rolling(4, win_type='gaussian').mean(std=10420)  #std dev calculated using one clear day's data, 10420 = std dev for 25-05-2020
data2 = data2.shift(-2)


#----------------------------------
# Correlation
#----------------------------------
corr = data.corr()
print ("\nThe correlation between variables as follow:")
print (corr)


train_start = '2020-05-19 00:00:00'
train_end   = '2020-06-09 23:45:00'
# #---------------------------------------------------------------
# # Features Engineering
# #---------------------------------------------------------------
start = dt.datetime.strptime(train_start,'%Y-%m-%d %H:%M:%S')
end = dt.datetime.strptime(train_end,'%Y-%m-%d %H:%M:%S')   #split the data manually

InData=[]
OutData=[]
op = data['AC_POWER']

while start<=end:
	features=[]
	
	indx = start.strftime('%Y-%m-%d %H:%M:%S')
	day1     = 	(start - dt.timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
	day2     = 	(start - dt.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
	day3     = 	(start - dt.timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
	hour1    =  (start - dt.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
		
	features.append((data2['AC_POWER'].loc[day1]))  # 1-day before's data
	features.append((data2['AC_POWER'].loc[day2]))  # 1-day before's data
	features.append((data2['AC_POWER'].loc[day3]))  # 1-day before's data
	features.append(data2['IRRADIATION'].loc[indx])  #Irradiation of the same day
	features.append(data2['MODULE_TEMPERATURE'].loc[indx]) #Mod Temp of the same day 
	features.append(start.hour)

	InData.append(features)          #Input to the model
	OutData.append((op.loc[indx]))   #Output to the model

	start= start + dt.timedelta(minutes=15)



#---------------------------------------------------------------
# Model
#---------------------------------------------------------------
conec = mlgraph((6,20,1))
net = ffnet(conec)
net.train_tnc(InData, OutData, maxfun = 1000)
savenet(net,'Pres.net')  #If the trained model is to be stored at other location, please specify the path here. 

print("\n *********Model Training Successful*********" )








