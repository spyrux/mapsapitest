from flask import Flask
from dotenv import load_dotenv
import os
import googlemaps
import urllib.error
import urllib.request
import urllib.response
import urllib.parse
import json
import time


app = Flask(__name__)
load_dotenv()
api_key = os.getenv("API")
gmaps = googlemaps.Client(key = api_key)
geolocate_url = "https://www.googleapis.com/geolocation/v1/geolocate"
places_json_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"



class Restaurant:

   def __init__(self, name, rating, price, location):
      self.name = name
      self.rating = rating
      self.price = price
      self.location = location
   
   def create_restaurant(name, rating, price, location):
      if name is None:
        name = "Unknown"
      if price is None:
         price = "Unkown"
      if location is None:
         location = "Unkown"
      if rating is None:
         rating = "Unkown"

      restaurant = Restaurant(name, rating, price, location)
      return restaurant
   
   def toJSON(self):
      return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
   


@app.route('/')
def hello_world():
   location = get_current_location()
   params = urllib.parse.urlencode({"query": "restaurants near","location":f"{location['lat']},{location['lng']}","radius":"1000", "key": f"{api_key}"})
   url = f"{places_json_url}?{params}"
   response = urllib.request.urlopen(url)
   content = json.loads(response.read().decode('utf-8'))
   
   restaurants = []

   for result in content["results"]:
      rest = Restaurant.create_restaurant(result.get("name", None) , result.get("rating", None), result.get("price_level", None) , result.get("formatted_address", None))
      restaurants.append(rest)

   restaurants.sort(key = lambda x : x.rating, reverse= True)
   return json.dumps([ob.__dict__ for ob in restaurants])
   


@app.route('/current')
def get_current_location():

   # with exponential back off time to reduce calls and introduce failure

   params = urllib.parse.urlencode({"key": f"{api_key}"})
   url = f"{geolocate_url}?{params}"
   current_delay = 0.1
   max_delay = 5

   while True:
      try:
         request = urllib.request.Request(url, method = 'POST')

      except urllib.error.URLError:
         pass
      else:
         result = urllib.request.urlopen(request)
         response = json.load(result)
         return response['location']
    
         

      if current_delay > max_delay:
         raise Exception("timing out")
      print("Waiting", current_delay, "seconds before retrying.")

      time.sleep(current_delay)
      current_delay *= 2


   


if __name__ == '__main__':
   app.run()