from bs4 import BeautifulSoup
import requests 
import pandas as pd
from geopy.geocoders import Nominatim
from urllib import parse
from geopy.geocoders import Nominatim
import re
import glob

filename = 'MEMORIALS/WESTERN_ISLES.csv'

data = pd.read_csv(filename, header = 0, sep=';')

new_data = data
new_data['UKNIWM_WEB'] = None
new_data['COMMEMORATION'] = None
new_data['LATITUDE'] = None
new_data['LONGITUDE'] = None
new_data['MAP'] = None

url = 'https://www.iwm.org.uk/memorials/item/memorial/'

def get_lat_long(location, country):
	geolocator = Nominatim(user_agent="location_finder")
	location_string = f"{location}, {country}"

	try:
		location_info = geolocator.geocode(location_string)

		if location_info:
			latitude = location_info.latitude
			longitude = location_info.longitude
			return latitude, longitude
		else:
			print(f"Location information not found for {location}, {country}")
			return None
	except Exception as e:
		print(f"An error occurred: {e}")
		return None

def generate_google_maps_url(latitude, longitude):
	return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}&query_place_id="

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

for index, row in data.iterrows():
	print(str(index))

	memorial_id = row[3]
	if memorial_id != 'NOT LISTED':
		UKNIWM_url = str(url) + str(memorial_id)
		new_data.at[index, 'UKNIWM_WEB'] = UKNIWM_url

		page = requests.get(UKNIWM_url) 

		if page.ok:
			soup = BeautifulSoup(page.content , 'html.parser') 

			def string_search(text) : 
				pattern = r'{}'.format(text)
				return [''.join([i if ord(i) < 128 else ' ' for i in text.get_text().replace("::before", "").replace("::after", "")]).strip()  for text in soup.find('dt', string=pattern).find_next_siblings('dd')][0:2]

			new_data.at[index, 'COMMEMORATION'] = string_search('Commemoration')[0]

			l = None
			for d in soup.find_all('div', class_='memorial-map__address'):
				for a in d.find_all('a'):
					l = a.get('href') 

			if l is not None:
				new_data.at[index, 'MAP'] = l
				_, query_string = parse.splitquery(new_data.at[index, 'MAP'])
				query = parse.parse_qs(query_string)
				latlng = query["query"]
				latitude, longitude = latlng[0].split(",")
				new_data.at[index, 'LATITUDE'] = latitude
				new_data.at[index, 'LONGITUDE'] = longitude
				new_data.at[index, 'MAP'] = l
	else:
		new_data.at[index, 'UKNIWM_WEB'] = 'NONE'
		new_data.at[index, 'COMMEMORATION'] = 'UNKNOWN'

	if new_data.at[index, 'LATITUDE'] is None:
		result = get_lat_long(new_data.at[index, 'COUNTY'], new_data.at[index, 'COUNTRY'])

		if result:
			latitude, longitude = result
			new_data.at[index, 'LATITUDE'] = latitude
			new_data.at[index, 'LONGITUDE'] = longitude
			new_data.at[index, 'MAP'] = generate_google_maps_url(latitude, longitude)
		else:
			new_data.at[index, 'LATITUDE'] = 'NONE'
			new_data.at[index, 'LONGITUDE'] = 'NONE'
			new_data.at[index, 'MAP'] = 'NONE'

	if new_data.at[index, 'COMMEMORATION'] == None or new_data.at[index, 'COMMEMORATION'] == 'UNKNOWN':
		new_data.at[index, 'COMMEMORATION'] = 'UNKNOWN'

	if new_data.at[index, 'UKNIWM_WEB'] == None or new_data.at[index, 'UKNIWM_WEB'] == 'NONE':
		new_data.at[index, 'UKNIWM_WEB'] = 'NONE'

	#print(new_data.at[index, 'LATITUDE'] + " : " + new_data.at[index, 'LONGITUDE'])


new_data.to_csv('_WESTERN_ISLES.csv', sep=';', index=False)