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

