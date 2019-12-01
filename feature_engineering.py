import pandas as pd 
import numpy as np 
from dateutil import parser 
import bisect 
import re 
from datetime import datetime
from sklearn import metrics

pd.options.mode.chained_assignment = None  # default='warn'

def func(x): 
    spring = ['03','04','05']
    summer = ['06','07','08']
    autumn = ['09','10','11']
    winter = ['12','01','02']

    if x in spring:
        return "spring"
    elif x in summer:
        return "summer"
    elif x in autumn:
        return "autumn"
    return 'winter'

def season(df) :
    df['month'] = df['start_date'].apply(lambda x: x[-5:-3])
    df['season'] = df['month'].apply(func)
    one_hot = pd.get_dummies(df['season'])
    df = df.join(one_hot)
    df = df.drop('season', axis = 1)

    return df

def holiday(df):
	holidays = ['01-01','01-15','02-19','05-28','07-04','09-03','11-11','11-12','11-22','11-23','12-25']

	df['holiday'] = df['start_date'].apply(lambda x : 1 if x[5:10] in holidays else 0)
	return df

def date_feature(df):
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['month'] = df['start_date'].apply(lambda x: str(x.month))
    df['day'] = df['start_date'].apply(lambda x: str(x.day))
    df['weekday'] = df['start_date'].apply(lambda x:x.weekday())
    df = df.drop(['start_date'], axis = 1)
    return df

def top_i_station_onehot(df, top = 20):
    a = df.groupby('station')['in_count'].sum().sort_values(ascending=False)
    top_stations = a.index.tolist()[:top]
    df['station_popularity'] = df['station'].apply(lambda x: 'other' if x not in top_stations else x)
    one_hot = pd.get_dummies(df['station_popularity'])
    df = df.drop(['station_popularity'], axis = 1)
    df = df.join(one_hot)
    return df

def member_type(df):
    one_hot = pd.get_dummies(df['member_type'])
    df = df.join(one_hot)
    df = df.drop(['member_type'], axis = 1)
    return df

def weather(df):
    one_hot_2 = pd.get_dummies(df['weather_description'])
    df = df.drop('weather_description', axis = 1)
    df = df.join(one_hot_2)
    return df

def wind_direction(df):
    one_hot_2 = pd.get_dummies(df['wind_direction'])
    df = df.drop('wind_direction', axis = 1)
    df = df.join(one_hot_2)
    return df

#  Create 4 buckets for time and 2 for day
def hour_flag(df):
    if (5 <= df['start_hour'] < 10):
        return 'morning_peak'
    elif(10 <= df['start_hour'] < 15):
        return 'day_time'
    elif(15 <= df['start_hour'] < 21):
        return 'Evening_peak'
    else:
        return 'night_time'
    
def hour_features(df):
    df['hour_flag'] = df.apply(hour_flag, axis = 1)

    # do one hot encoding 
    one_hot = pd.get_dummies(df['hour_flag'])
    df = df.join(one_hot)

    df = df.drop(['hour_flag', 'start_hour'], axis = 1)
    return df 

def day_flag(df):
    if (df['weekday'] <= 5):
        return 0
    else:
        return 1
    
def day_features(df):
    df['weekday_flag'] = df.apply(day_flag, axis = 1)

    df = df.drop(['weekday'], axis=1)
    return df 

def wind_chill(df):
	df['wind_chill'] = 35.74 + (0.6215*df.temp_in_f) - 35.75*(df.wind_speed_in_mph**0.16) + ((0.4275*df.temp_in_f)*(df.wind_speed_in_mph**0.16))
	df.loc[(df.wind_speed_in_mph < 3) | (df.temp_in_f > 50), ['wind_chill']] = df.temp_in_f

def heatindex(vTemperature, vRelativeHumidity):
    heatindex = -42.379 + 2.04901523*vTemperature + 10.14333127*vRelativeHumidity - .22475541*vTemperature*vRelativeHumidity - .00683783*vTemperature*vTemperature - .05481717*vRelativeHumidity*vRelativeHumidity + .00122874*vTemperature*vTemperature*vRelativeHumidity + .00085282*vTemperature*vRelativeHumidity*vRelativeHumidity - .00000199*vTemperature*vTemperature*vRelativeHumidity*vRelativeHumidity
    return heatindex

def heat_index(df):
	df['heat_index'] = heatindex(df.temp_in_f, df['humidity_in_%'])
	df.loc[(df['humidity_in_%'] <40 ) | (df.temp_in_f < 80), ['heat_index']] = df.temp_in_f
    
