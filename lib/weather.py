import os
import requests

def get_weather_response(zip_code):
    uri = '{}&q={},us'.format(WEATHER_ENDPOINT, zip_code)
    resp = requests.get(uri)
    return resp.json()

def k_to_f(kelvin):
    # convert kelvin to farenheit
    return round(kelvin * 9/5 - 459.67)

def parse_weather_response(json_dict):
    place_name = json_dict['name']
    weather_objs = json_dict['weather']
    descriptions = [wo['description'] for wo in weather_objs]
    description_string = ', '.join(descriptions)
    current_temp = json_dict['main']['temp']
    high_temp = json_dict['main']['temp_max']
    low_temp = json_dict['main']['temp_min']
    parsed_data = {
        "name": place_name,
        "description": description_string,
        "current_temp": k_to_f(current_temp),
        "high_temp": k_to_f(high_temp),
        "low_temp": k_to_f(low_temp)
    }
    weather_string = "**{name}**: {description}. *Currently* {current_temp} °F with *highs* of {high_temp} °F and *lows* of {low_temp} °F.".format(**parsed_data)
    return weather_string


WEATHER_API_KEY = os.environ['WEATHER_API_KEY']
WEATHER_URI = 'http://api.openweathermap.org/data/2.5/weather'
WEATHER_ENDPOINT = "{}?appid={}".format(WEATHER_URI, WEATHER_API_KEY)