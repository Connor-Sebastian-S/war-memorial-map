from bs4 import BeautifulSoup
import requests 
import pandas as pd
from geopy.geocoders import Nominatim
from urllib import parse
from geopy.geocoders import Nominatim
import re

def get_country_from_coordinates(latitude, longitude, county):
	geolocator = Nominatim(user_agent="country_locator")
	location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)

	if location and 'address' in location.raw:
		address = location.raw['address']
		if 'country' in address:
			country = address['country']
			if country == 'United Kingdom':
				if 'state' in address:
					return address['state']
				if county == True:
					if 'county' in address:
						return address['county']
			elif 'state' in address:
				return address['state']

	return "Country not found"

filename = 'castles.csv'

data = pd.read_csv(filename)

data['name'] = None #
data['latitude'] = None #
data['longitude'] = None #
data['map'] = None #
data['country'] = None #
data['date'] = None

for index, row in data.iterrows():
	memorial_html = row[0]
	print(str(index) + " - " + memorial_html)

	page = requests.get(memorial_html) 

	# parse html content 
	soup = BeautifulSoup(page.content , 'html.parser') 

	#memorial_type = soup.find(class_='md-group type').text.replace('Type:', '').strip()

	l = soup.find("memorial-map__address",href=re.compile('^http://maps.google.com/maps?'))

	if l is not None:
		data.at[index, 'map'] = l.get("href")
		_, query_string = parse.splitquery(data.at[index, 'map'])
		#https://www.google.com/maps?ll=55.599018,-2.719393&hl=en&t=h&z=18
		query = parse.parse_qs(query_string)
		latlng = query["ll"]
		latitude, longitude = latlng[0].split(",")
		data.at[index, 'latitude'] = latitude.replace("loc:", '')
		data.at[index, 'longitude'] = longitude.replace("loc:", '')

		data.at[index, 'country'] = get_country_from_coordinates(
			data.at[index, 'latitude'], 
			data.at[index, 'longitude'],
			county = False
			).replace('Alba / ', '')
	else:
		data.at[index, 'latitude'] = 0
		data.at[index, 'longitude'] = 0
		data.at[index, 'country'] = 'Scotland'
		data.at[index, 'map'] = '0'

	container = soup.find('div', attrs={'class':'c8'})
	if container != None:
		para = '\n'.join([x.text for x in container.find_all('p') if x.text != "" and "Lat / long:" not in x.text and "Grid reference:" not in x.text])
		all_dates = re.findall(r'\d+', para)
		all_dates = [int(number) - 1 for number in all_dates if len(str(number)) == 2]
		all_dates = [int('{:<04}'.format(number)) for number in all_dates]
		if len(all_dates) == 0:
			all_dates.append(0000)
		all_dates = [int('{:<04}'.format(number)) for number in all_dates]
		all_dates.sort()
		earliest_date = all_dates[0]

		data.at[index, 'date'] = earliest_date

	else:
		data.at[index, 'date'] = 0
	

	title = soup.h1
	data.at[index, 'name'] = title.text.strip()

# Save the updated DataFrame back to the CSV file
data.to_csv('c_test.csv', sep=';', index=False)

