import os
import requests
import datetime
import discord


WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
WEATHER_URI = "http://api.openweathermap.org/data/2.5/weather"
WEATHER_ENDPOINT = "{}?appid={}".format(WEATHER_URI, WEATHER_API_KEY)


def get_weather_response(zip_code):
    uri = "{}&q={},us".format(WEATHER_ENDPOINT, zip_code)
    resp = requests.get(uri)
    return resp.json()


def k_to_f(kelvin):
    # convert kelvin to farenheit
    return round(kelvin * 9 / 5 - 459.67)


def parse_weather_response(json_dict):
    place_name = json_dict["name"]
    place_id = json_dict["id"]
    weather_objs = json_dict["weather"]
    descriptions = [wo["description"] for wo in weather_objs]
    description_string = ", ".join(descriptions)
    current_temp = json_dict["main"]["temp"]
    high_temp = json_dict["main"]["temp_max"]
    low_temp = json_dict["main"]["temp_min"]
    feels_like = json_dict["main"]["feels_like"]
    humidity = json_dict["main"]["humidity"]
    icon_id = json_dict["weather"][0]["icon"]
    icon_url = "http://openweathermap.org/img/wn/{icon_id}@2x.png".format(
        icon_id=icon_id
    )
    parsed_data = {
        "name": place_name,
        "description": description_string,
        "current_temp": k_to_f(current_temp),
        "high_temp": k_to_f(high_temp),
        "low_temp": k_to_f(low_temp),
    }
    embed_data = {
        title: "Current Weather Data",
        embed_type: "rich",
        description: "https://openweathermap.org/city/{place_id}".format(
            place_id=place_id
        ),
        url: "https://openweathermap.org/city/{place_id}".format(place_id=place_id),
        timestamp: datetime.datetime.now().isoformat(),
        color: 0xEB6E4B,
        provider: {name: "Open Weather", url: "https://openweathermap.org"},
        image: {
            url: "https://openweathermap.org/img/wn/{icon_id}@2x.png".format(
                icon_id=icon_id
            ),
            height: 100,
            width: 100,
        },
        fields: [
            {"name": "Conditions", "value": description_string},
            {"name": "Temperature", "value": current_temp},
            {"name": "High", "value": high_temp},
            {"name": "Low", "value": low_temp},
            {"name": "Feels Like", "value": feels_like},
        ],
    }
    embed = discord.Embed.from_dict(embed_data)
    logger.info("Sending embed {embed}".format(embed))
    return embed
