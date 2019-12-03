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
    df['month'] = df['date'].apply(lambda x: x[-5:-3])
    df['season'] = df['month'].apply(func)
    one_hot = pd.get_dummies(df['season'])
    df = df.join(one_hot)
    df = df.drop('season', axis = 1)

    return df

def holiday(df):
	holidays = ['01-01','01-15','02-19','05-28','07-04','09-03','11-11','11-12','11-22','11-23','12-25']

	df['holiday'] = df['date'].apply(lambda x : 1 if x[5:10] in holidays else 0)
	return df

def date_feature(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].apply(lambda x: str(x.month))
    df['day'] = df['date'].apply(lambda x: str(x.day))
    df['weekday'] = df['date'].apply(lambda x:x.weekday())
    df = df.drop(['date'], axis = 1)
    return df

def top_i_station_onehot(df, in_or_out = 'sum_ins_outs', top = 20):
    df['sum_ins_outs'] = df['total_out'] + df['total_in']
    a =  df.groupby(['station'], as_index = False)[in_or_out].agg('sum').sort_values(by = in_or_out, ascending=False).reset_index()
    top_stations = a.station[:top].tolist()
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
    df['weather_description'] = df['weather_description'].apply(lambda x: x.lower())
    df['thunderstorm'] = df['weather_description'].apply(lambda x: 1 if 'storm' in x else 0)
    df['cloudy'] = df['weather_description'].apply(lambda x: 1 if 'cloudy' in x else 0)
    df['drizzle'] = df['weather_description'].apply(lambda x: 1 if 'drizzle' in x else 0)
    df['fog'] = df['weather_description'].apply(lambda x: 1 if 'fog' in x else 0)
    df['haze'] = df['weather_description'].apply(lambda x: 1 if 'haz' in x else 0)
    df['rain'] = df['weather_description'].apply(lambda x: 1 if 'rain' in x else 0)
    df['snow'] = df['weather_description'].apply(lambda x: 1 if 'snow' in x or 'wintry' in x else 0)
    df['clear'] = df['weather_description'].apply(lambda x: 1 if 'clear' in x  else 0)

    df = df.drop('weather_description', axis = 1)
    return df

def wind_direction(df):
    df['N'] = df['wind_direction'].apply(lambda x: 1 if 'N' in x else 0)
    df['E'] = df['wind_direction'].apply(lambda x: 1 if 'E' in x else 0)
    df['W'] = df['wind_direction'].apply(lambda x: 1 if 'W' in x else 0)
    df['S'] = df['wind_direction'].apply(lambda x: 1 if 'S' in x else 0)

    df = df.drop('wind_direction', axis = 1)
    return df

#  Create 4 buckets for time and 2 for day
def hour_flag(df):
    if (5 <= df['hour'] < 10):
        return 'morning_peak'
    elif(10 <= df['hour'] < 15):
        return 'day_time'
    elif(15 <= df['hour'] < 21):
        return 'evening_peak'
    else:
        return 'night_time'
    
def hour_features(df):
    df['hour'] = df['time'].apply(lambda x: int(x.split(':')[0]))
    df['hour_flag'] = df.apply(hour_flag, axis = 1)

    # do one hot encoding 
    one_hot = pd.get_dummies(df['hour_flag'])
    df = df.join(one_hot)

    df = df.drop(['hour_flag', 'hour'], axis = 1)
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
    return df 


def heatindex(vTemperature, vRelativeHumidity):
    heatindex = -42.379 + 2.04901523*vTemperature + 10.14333127*vRelativeHumidity - .22475541*vTemperature*vRelativeHumidity - .00683783*vTemperature*vTemperature - .05481717*vRelativeHumidity*vRelativeHumidity + .00122874*vTemperature*vTemperature*vRelativeHumidity + .00085282*vTemperature*vRelativeHumidity*vRelativeHumidity - .00000199*vTemperature*vTemperature*vRelativeHumidity*vRelativeHumidity
    return heatindex

def heat_index(df):
    df['heat_index'] = heatindex(df.temp_in_f, df['humidity_in_%'])
    df.loc[(df['humidity_in_%'] <40 ) | (df.temp_in_f < 80), ['heat_index']] = df.temp_in_f
    return df  
    

def humidity_feature(df):
    df['very_humid'] = df['humidity_in_%'].apply(lambda x: 1 if x >= 75 else 0)
    df['humid'] = df['humidity_in_%'].apply(lambda x: 1 if  75 > x >= 50 else 0) 
    df['not_humid'] = df['humidity_in_%'].apply(lambda x: 1 if 50 > x >= 15 else 0)
    df['not_humid'] = df['humidity_in_%'].apply(lambda x: 1 if 15 > x  else 0)

    df = df.drop(['humidity_in_%'], axis=1)
    return df 

def visibility_feature(df):
    df['visible'] = df['visibility_in_miles'].apply(lambda x : 1 if x == 10 else 0)

    df = df.drop(['visibility_in_miles'], axis=1)
    return df 