import pandas as pd 
import numpy as np
import requests 
from bs4 import BeautifulSoup
import datetime
from datetime import date, timedelta
import sys
out_dir = './data/'

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

url_base = 'https://www.weatherforyou.com/reports/index.php?forecast=pass&pass=archivenws&zipcode=22747&pands=&place=washington&state=va&icao=KDCA&country=us&month=%s&day=%s&year=2018&dosubmit=Go'

#'https://www.weatherforyou.com/reports/index.php?forecast=pass&pass=archive&zipcode=22747&pands=&place=washington&state=va&icao=KDCA&country=us&month=%s&day=%s&year=2018&dosubmit=Go'

# dates generation
start_dt = date(2017, 12, 31)
end_dt = date(2018,12,31)
dates = [dt.strftime('%Y-%m-%d') for dt in daterange(start_dt, end_dt)]
	
col_names = ['date', 'time', 'weather_description', 'temp_in_f', 'dewpt_in_f', 'humidity_in_%', 'pressure', 'precipitation_in_inches', 'visibility_in_miles', 'wind_direction', 'wind_speed_in_mph']		

col_names2 =  ['date', 'time', 'weather_description', 'temp_in_f', 'humidity_in_%', 'pressure', 'precipitation_in_inches', 
			'visibility_in_miles', 'wind_direction', 'wind_speed_in_mph', 'temp_in_f_delta', 'pressure_delta', 'humidity_delta', 
			'visibility_delta', 'precipitation_delta', 'wind_speed_delta']
final_df = pd.DataFrame(columns = col_names2)


saved_previous_year = None
#dates = ['2017-12-31'] + dates 
dates.remove('2018-11-16')
print(dates)
#dates = ['2017-12-31', '2018-11-15', '2018-11-16']
for i, date in enumerate(dates):
	month = date.split('-')[1]
	day = date.split('-')[2]

	# open url for the corresponding date
	r = requests.get(url_base % (month, day)) # check the format 
	print(url_base % (month,day))


	if r.status_code == 200 : # everything is ok 
		# get the data from beautiful soup 
		soup = BeautifulSoup(r.text, 'html.parser')
		table = soup.find('table', {'width':'660', 'cellspacing':'1', 'cellpadding':'2', 'border':'0'})
		table_body = table.find_all('tbody')
	
		# column names
		rows = table.find_all('tr')[1:]
		
		columns = list()
		for row in rows:
		 	cols = row.find_all('td')
		 	cols = [ele.text.strip() for ele in cols]
		 	wind_elements = cols[6].replace('\xa0', ' ').split(' ')
		 	cols.pop(6)
		 	cols = [date] + cols + wind_elements[:2]
		 	columns.append(cols)

		#close request very important
		r.close()

		# create a dataframe 
		df = pd.DataFrame(columns, columns = col_names)
		df['temp_in_f'] =  pd.to_numeric(df['temp_in_f'].str.extract('(\d+)', expand=False))
		df['pressure'] =  pd.to_numeric(df['pressure'].str.extract('(\d+)', expand=False))
		df['wind_speed_in_mph'] =  pd.to_numeric(df['wind_speed_in_mph'].str.extract('(\d+)', expand=False))
		df['dewpt_in_f'] = df['dewpt_in_f'].str.extract('(\d+)', expand=False)
		df['humidity_in_%'] = pd.to_numeric(df['humidity_in_%'].str.extract('(\d+)', expand=False))
		df['visibility_in_miles'] = pd.to_numeric(df['visibility_in_miles'].str.extract('(\d+)', expand=False))
		df['precipitation_in_inches'] = pd.to_numeric(df['precipitation_in_inches'].str.extract('(\d+)', expand=False))


		# create a final data frame 
		interim_df = pd.DataFrame(columns = col_names)

		data_to_drop = list()
		hours = list()
		number_of_hours = range(0,23)
		
		# reformat timings 		
		for index, row in df.iterrows():
			hour, rest = row[1].split(':')
			mod_hour = int(hour) % 12 
	
			# define morning and afternoon
			if rest[-2:] == 'AM':
				if mod_hour < 10 : 
					hour = '0' + str(mod_hour) 
				else:
					hour = mod_hour
			elif rest[-2:] == 'PM':
				hour = mod_hour + 12

			# string for time
			hour = str(hour) + ':00:00'
			hours.append(hour) 
			df['time'][index] = hour

		# combine the data together 
		#final_df['date'] = 
		#final_df['time'] = 
		interim_df['time'] = list(set(hours))
		interim_df =  interim_df.sort_values(by=['time'])
		interim_df['temp_in_f'] = 0
		interim_df = interim_df.drop(['dewpt_in_f'], axis = 1)
		interim_df['date'] = date

		if date == '2018-11-15':
			last = len(interim_df)
			interim_df.loc[last, 'weather_description'] = 'Cloudy'
			interim_df.loc[last, 'temp_in_f'] = 32.0	
			interim_df.loc[last, 'humidity_in_%'] = 100.0	
			interim_df.loc[last, 'precipitation_in_inches'] = 0		
			interim_df.loc[last, 'visibility_in_miles'] = 2.0
			interim_df.loc[last, 'wind_direction'] = 'N'
			interim_df.loc[67, 'wind_direction'] = 'N'
			interim_df.loc[last, 'wind_speed_in_mph'] = 0.0

		#print(interim_df)

		for hour in hours: 
			interim_df['temp_in_f'] = np.where(interim_df['time'] == hour, round(df.loc[df['time'] == hour, 'temp_in_f'].mean()), interim_df['temp_in_f'])
			interim_df['pressure'] = np.where(interim_df['time'] == hour, round(df.loc[df['time'] == hour, 'pressure'].mean()), interim_df['pressure'])
			interim_df['humidity_in_%'] = np.where(interim_df['time'] == hour, round(df.loc[df['time'] == hour, 'humidity_in_%'].mean()), interim_df['humidity_in_%'])
			interim_df['visibility_in_miles'] = np.where(interim_df['time'] == hour, round(df.loc[df['time'] == hour, 'visibility_in_miles'].mean(), 1), interim_df['visibility_in_miles'])
			interim_df['precipitation_in_inches'] = np.where(interim_df['time'] == hour, df.loc[df['time'] == hour, 'precipitation_in_inches'].sum(), interim_df['precipitation_in_inches'])
			interim_df['wind_speed_in_mph'] = np.where(interim_df['time'] == hour, round(df.loc[df['time'] == hour, 'wind_speed_in_mph'].mean(), 1), interim_df['wind_speed_in_mph'])
			
			# get modes
			interim_df['weather_description'] = np.where(interim_df['time'] == hour, max(set(list(df.loc[df['time'] == hour, 'weather_description'])), key= list(df.loc[df['time'] == hour, 'weather_description']).count), interim_df['weather_description'])
			interim_df['wind_direction'] = np.where(interim_df['time'] == hour, max(set(list(df.loc[df['time'] == hour, 'wind_direction'])), key= list(df.loc[df['time'] == hour, 'wind_direction']).count), interim_df['wind_direction'])
			
		
		interim_df.reset_index(inplace = True)
		

		

		print(df[-10:])

		
		previous_row = None
		if date == '2017-12-31':
			for index, row in interim_df.iterrows():
				if index == 0 :
					previous_row = row
				else:
					interim_df.loc[index, 'temp_in_f_delta'] = row['temp_in_f'] - previous_row['temp_in_f'] 
					interim_df.loc[index,'pressure_delta'] = row['pressure'] - previous_row['pressure'] 
					interim_df.loc[index,'humidity_delta'] = row['humidity_in_%'] - previous_row['humidity_in_%'] 
					interim_df.loc[index,'visibility_delta'] = row['visibility_in_miles'] - previous_row['visibility_in_miles'] 
					interim_df.loc[index,'precipitation_delta'] = row['precipitation_in_inches'] - previous_row['precipitation_in_inches'] 
					interim_df.loc[index,'wind_speed_delta'] = row['wind_speed_in_mph'] - previous_row['wind_speed_in_mph'] 
				saved_previous_year = row
			final_df = final_df.append(interim_df)	
		else: 
			for index, row in interim_df.iterrows():
				# compute differences with previous hour
				if index == 0:
					if date == '2018-01-01':
						previous_row = saved_previous_year
					else:
						previous_row = final_df.iloc[-1,:] 
				
				interim_df.loc[index, 'temp_in_f_delta'] = row['temp_in_f'] - previous_row['temp_in_f'] 
				interim_df.loc[index,'pressure_delta'] = row['pressure'] - previous_row['pressure'] 
				interim_df.loc[index,'humidity_delta'] = row['humidity_in_%'] - previous_row['humidity_in_%'] 
				interim_df.loc[index,'visibility_delta'] = row['visibility_in_miles'] - previous_row['visibility_in_miles'] 
				interim_df.loc[index,'precipitation_delta'] = row['precipitation_in_inches'] - previous_row['precipitation_in_inches'] 
				interim_df.loc[index,'wind_speed_delta'] = row['wind_speed_in_mph'] - previous_row['wind_speed_in_mph'] 							
				previous_row = row

			#print(interim_df)

			# get the final row of data to compute the evolution in data

			final_df = final_df.append(interim_df)

			print('\n')
			

# write out 
#
final_df.drop(['index'], axis=1)
final_df = final_df[col_names2]
print('WRITING_FILE....')
final_df.to_csv(out_dir + 'weather_data4.csv', index = None, header=True) 
print('SUCCESS ')