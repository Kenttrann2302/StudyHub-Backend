# this function will create and send a Geocoding Google Map API to the google maps database to check if the user entered an acceptable address, city, country and postal code

# _*_ coding: utf-8 _*_
# pylint: disable=unused-import
import json
import os
import pdb

import requests

# load in the sensitive data from .env
from dotenv import load_dotenv
from flask import Flask, request

from get_env import google_api_secret_key


class checkAddress:
    def __init__(
        self,
        errors,
        **kwargs,
        # first_address=None,
        # second_address=None,
        # city=None,
        # province=None,
        # country=None,
        # postal_code=None,
    ) -> None:
        self.errors = errors
        self.address_line_1 = kwargs.get("first_address", None)
        self.address_line_2 = kwargs.get("second_address", None)
        self.city = kwargs.get("city", None)
        self.province = kwargs.get("province", None)
        self.country = kwargs.get("country", None)
        self.postalCode = kwargs.get("postal_code", None)

    def is_valid_address(self) -> bool:
        # construct the address string to be used for the API request
        address_string = f"{self.address_line_1}"
        # if there is a secondary address, then add it to the string
        if self.address_line_2:
            address_string += f", {self.address_line_2}"
        address_string += f", {self.city}, {self.province}, {self.country}"

        # construct the URL for the Geocoding API request
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        # need to implement the api key
        params = {"address": address_string, "key": google_api_secret_key}
        response = requests.get(url, params=params)

        # check if the Geocoding API returned any results
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "OK" and len(result["results"]) > 0:
                # check if the Geocoding API returned a valid address
                location = result["results"][0]["geometry"]["location"]
                if location["lat"] != 0 and location["lng"] != 0:
                    print(f"Latitude: {location['lat']}, Longtitude: {location['lng']}")
                    return True
            else:
                print("Sorry! No results found!")
                self.errors["address1"] = f"Please enter a valid address!"
                return False

        # if the Geocoding API didn't return any results or returned an invalid address, return False
        print(f"Request failed with status code {response.status_code}.")
        return False
