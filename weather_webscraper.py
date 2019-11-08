import pandas as pd 
import requests 
from bs4 import BeautifulSoup

out_dir = './weather_data/'

#url_base = 'https://www.wunderground.com/history/daily/us/va/arlington-county/KDCA/date/'
#https://www.weatherforyou.com/reports/index.php?forecast=pass&pass=archive&zipcode=22747&pands=&place=washington&state=va&icao=KDCA&country=us&month=11&day=08&year=2018&dosubmit=Go

url_base = 'https://www.weatherforyou.com/reports/index.php?forecast=pass&pass=archive&zipcode=22747&pands=&place=washington&state=va&icao=KDCA&country=us&month=%s&day=%s&year=2018&dosubmit=Go'
with open(out_dir + 'log_year.txt', 'w+') as f:
	f.write('LOGFILE: Scraping data for year: \n')
	f.write(url_base)

# list of tables 
year = 2018 
# dates should be in american format 
dates = ['2018-01-01']
month = '01'
day = '01'

for i, date in enumerate(dates):
	# open url for the corresponding date
	r = requests.get(url_base % (month, day)) # check the format 
	print(url_base % (month,day))

	with open(out_dir + 'log_year.txt', 'w') as file:
		file.write('Date: {} || Status: {}\n'.format(date, r.status_code))

	if r.status_code == 200 : # everything is ok 
		# get the data from beautiful soup 
		soup = BeautifulSoup(r.text, 'html.parser')
		table = soup.find('table', {'width':'660', 'cellspacing':'1', 'cellpadding':'2', 'border':'0'})
		table_body = table.find_all('tbody')
	
		# column names
		rows = table.find_all('tr')[1:]
		col_names = ['date', 'time', 'weather_description', 'temp_in_f', 'dewpt_in_f', 'humidity_in_%', 'pressure', 'precipitation_in_inches', 'wind_direction', 'wind_speed_in_mph']
		
		columns = list()
		for row in rows:
		 	cols = row.find_all('td')
		 	cols = [ele.text.strip() for ele in cols]
		 	wind_elements = cols[6].replace('\xa0', ' ').split(' ')
		 	cols.pop(6)
		 	cols = [date] + cols + wind_elements[:2]
		 	columns.append(cols)
		 	print(cols)

		df = pd.DataFrame(columns, columns = col_names)

		print(df.head())



		# row iteration 