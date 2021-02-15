import os
import requests
import datetime
import discord

WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
WEATHER_URI = "http://api.openweathermap.org/data/2.5/weather"
WEATHER_ENDPOINT = "{}?appid={}".format(WEATHER_URI, WEATHER_API_KEY)


def get_weather_response(zip_code):
    uri = "{}&q={},us&units={}".format(WEATHER_ENDPOINT, zip_code, "imperial")
    resp = requests.get(uri)
    return resp.json()


# stolen from: https://stackoverflow.com/a/7490772
def degToCompass(num):
    val = int((num / 22.5) + 0.5)
    arr = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    return arr[(val % 16)]


def parse_weather_response(json_dict):
    place_name = json_dict["name"]
    country_code = json_dict["sys"]["country"]
    place_id = json_dict["id"]
    weather_objs = json_dict["weather"]
    descriptions = [wo["description"].capitalize() for wo in weather_objs]
    description_string = ", ".join(descriptions)
    current_temp = json_dict["main"]["temp"]
    high_temp = json_dict["main"]["temp_max"]
    low_temp = json_dict["main"]["temp_min"]
    feels_like = json_dict["main"]["feels_like"]
    humidity = json_dict["main"]["humidity"]
    wind_speed = json_dict["wind"]["speed"]
    wind_dir = str(degToCompass(json_dict["wind"]["deg"]))
    icon_id = json_dict["weather"][0]["icon"]
    icon_url = "http://openweathermap.org/img/wn/{icon_id}@2x.png".format(
        icon_id=icon_id
    )
    time_of_calc = json_dict["dt"]
    time_stamp = datetime.datetime.fromtimestamp(time_of_calc).isoformat()
    embed_data = {
        "title": "Current Weather Data",
        "type": "rich",
        "description": "{p}, {c}".format(p=place_name, c=country_code),
        "url": "https://openweathermap.org/city/{place_id}".format(place_id=place_id),
        "color": 0xEB6E4B,
        "thumbnail": {
            "url": "https://openweathermap.org/img/wn/{icon_id}@2x.png".format(
                icon_id=icon_id
            ),
            "height": 100,
            "width": 100,
        },
        "timestamp": time_stamp,
        "provider": {"name": "Open Weather", "url": "https://openweathermap.org"},
        "fields": [
            {"name": "Conditions", "value": description_string},
            {
                "name": "Currently",
                "value": str(current_temp) + "°F",
                "inline": True,
            },
            {"name": "High", "value": str(high_temp) + "°F", "inline": True},
            {"name": "Low", "value": str(low_temp) + "°F", "inline": True},
            {
                "name": "Feels Like",
                "value": str(feels_like) + "°F",
                "inline": True,
            },
            {"name": "Humidity", "value": str(humidity) + "%", "inline": True},
            {
                "name": "Wind",
                "value": "{s}mph {d}".format(s=wind_speed, d=wind_dir),
                "inline": True,
            },
        ],
        "author": {
            "name": "Open Weather API",
            "url": "https://openweathermap.org",
            "icon_url": "https://pbs.twimg.com/profile_images/1173919481082580992/f95OeyEW_400x400.jpg",
        },
    }
    embed = discord.Embed.from_dict(embed_data)
    return embed
