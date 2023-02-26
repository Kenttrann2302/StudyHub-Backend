# this function will create and send a Geocoding Google Map API to the google maps database to check if the user entered an acceptable address, city, country and postal code

# _*_ coding: utf-8 _*_
# pylint: disable=unused-import
from flask import Flask, request
import requests
import json
import pdb

class checkAddress:
 def __init__(self, address_line_1, city, province, country, postalCode, address_line_2 = None) -> None:
  self.address_line_1 = address_line_1
  self.address_line_2 = address_line_2
  self.city = city
  self.province = province
  self.country = country
  self.postalCode = postalCode
 
 def is_valid_address(self) -> bool:
  # construct the address string to be used for the API request
  address_string = f'{self.address_line_1}'
  # if there is a secondary address, then add it to the string
  if self.address_line_2:
   address_string += f', {self.address_line_2}'
  address_string += f', {self.city}, {self.province}, {self.country}'


  # construct the URL for the Geocoding API request
  url = 'https://maps.googleapis.com/maps/api/geocode/json'
  # need to implement the api key
  params = {'address': address_string, 'key': 'AIzaSyDEDVXK_Xadoj4tr3qx6GNxGRF8n35R51E'}
  response = requests.get(url, params=params)

  # check if the Geocoding API returned any results
  if response.status_code == 200:
   result = response.json()
   if result['status'] == 'OK' and len(result['results']) > 0:
    # check if the Geocoding API returned a valid address
    location = result['results'][0]['geometry']['location']
    if location['lat'] != 0 and location['lng'] != 0:
     print(f"Latitude: {location['lat']}, Longtitude: {location['lng']}")
     return True
   else:
     print("Sorry! No results found!")
     raise ValueError("This address is invalid")
     
  # if the Geocoding API didn't return any results or returned an invalid address, return False
  print(f"Request failed with status code {response.status_code}.")
  return False
  