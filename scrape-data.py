from bs4 import BeautifulSoup
import requests 
import pandas as pd
from geopy.geocoders import Nominatim
from urllib import parse
from geopy.geocoders import Nominatim


def get_country_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="country_locator")
    location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
    
    if location and 'address' in location.raw:
        address = location.raw['address']
        if 'country' in address:
            country = address['country']
            if country == 'United Kingdom':
                # Check for administrative divisions within the UK
                if 'state' in address:
                    return address['state']
                else:
                    return "United Kingdom"
            else:
                return country
    
    return "Country not found"

filename = 'jr_war_memorials.csv'

data = pd.read_csv(filename)

data['name'] = None
data['type'] = None
data['latitude'] = None
data['longitude'] = None
data['conflicts'] = None
#data['description'] = None
data['map'] = None
data['country'] = None

for index, row in data.iterrows():
	memorial_html = row[0]
	print(str(index) + " - " + memorial_html)

	page = requests.get(memorial_html) 

	# parse html content 
	soup = BeautifulSoup(page.content , 'html.parser') 

	memorial_type = soup.find(class_='md-group type').text.replace('Type:', '').strip()
	memorial_title = soup.find(class_='pull-left').text.strip()
	memorial_conflicts = soup.find(class_='md-group conflicts').text.replace('Conflicts:', '').strip().replace("\r", "; ").replace("\n", "; ")
	data.at[index, 'name'] = memorial_title
	data.at[index, 'type'] = memorial_type
	data.at[index, 'conflicts'] = memorial_conflicts
	memorial_location = [link['href'] for link in soup.findAll("a", {"class": "open-large-map"})]
	
	_, query_string = parse.splitquery(memorial_location[0])
	query = parse.parse_qs(query_string)
	latlng = query["q"]
	latitude, longitude = latlng[0].split(",")

	data.at[index, 'latitude'] = latitude.replace("loc:", '')
	data.at[index, 'longitude'] = longitude.replace("loc:", '')
	data.at[index, 'map'] = memorial_location[0].strip()
	data.at[index, 'country'] = get_country_from_coordinates(latitude, longitude)

# Save the updated DataFrame back to the CSV file
data.to_csv('updated.csv', sep=',', index=False)

