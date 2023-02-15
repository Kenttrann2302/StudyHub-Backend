# this function will create and send a Geocoding Google Map API to the google maps database to check if the user entered an acceptable address, city, country and postal code

class checkAddress:
 def __init__(self, address_line_1, address_line_2, city, country, postalCode) -> None:
  self.address_line_1 = address_line_1
  self.address_line_2 = address_line_2
  self.city = city
  self.country = country
  self.postalCode = postalCode
 
 def is_valid_address(self):
  # construct the URL for the Geocoding API request
  url = 'https://maps.googleapis.com/maps/api/geocode/json?'