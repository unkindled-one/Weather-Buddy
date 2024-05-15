from meteostat import Stations, Hourly, Daily
from datetime import datetime, timedelta, timezone
import numpy as np
import location
from zoneinfo import ZoneInfo

import weather

conditions = {
    1.0: "Clear",
    2.0: "Fair",
    3.0: "Cloudy",
    4.0: "Overcast",
    5.0: "Fog",
    6.0: "Freezing Fog",
    7.0: "Light Rain",
    8.0: "Rain",
    9.0: "Heavy Rain",
    10.0: "Freezing Rain",
    11.0: "Heavy Freezing Rain",
    12.0: "Sleet",
    13.0: "Heavy Sleet",
    14.0: "Light Snowfall",
    15.0: "Snowfall",
    16.0: "Heavy Snowfall",
    17.0: "Rain Shower",
    18.0: "Heavy Rain Shower",
    19.0: "Sleet Shower",
    20.0: "Heavy Sleet Shower",
    21.0: "Snow Shower",
    22.0: "Heavy Snow Shower",
    23.0: "Lightning",
    24.0: "Hail",
    25.0: "Thunderstorm",
    26.0: "Heavy Thunderstorm",
    27.0: "Storm",
}

thermometer_emoji = " :thermometer: "
snowflake_emoji = ":snowflake"
sunny_emoji = ":sunny:"
partially_cloudy_emoji = ":white_sun_small_cloud:"
cloudy_emoji = ":cloud:"
rain_cloud_emoji = ":cloud_rain:"
cold_face_emoji = ":cold_face:"
umbrella_emoji = ":umbrella:"
thunder_cloud_rain_emoji = ":thunder_cloud_rain:"
sun_with_face_emoji = ":sun_with_face:"
snow_cloud_emoji = ":cloud_snow:"
hot_face_emoji = ":hot_face:"
fog = ":fog:"
jeans = ":jeans:"
shorts = ":shorts:"
# jacket = ':jacket:'
shirt = ":shirt:"
lightshirt = ":running_shirt_with_sash:"
briefs = ":briefs:"
bikini = ":bikini:"
flipflop = ":thong_sandal:"
umbrella_emoji2 = ":umbrella2:"
wind1 = ":wind_blowing_face:"
wind2 = ":dash:"
sunglasses = ":sunglasses:"
labcoat = ":lab_coat:"
coat = ":coat:"
snowman = ":snowman:"


def get_outfit(pref: int, temp: float, lat: int, long: int):

    # first calculate proprietary outfit score
    station = Stations().nearby(lat, long).fetch(1)
    now = datetime.now(ZoneInfo("America/New_York"))
    now = now.replace(tzinfo=None)
    hour_ago = now - timedelta(hours=1)
    df = Hourly(station, start=hour_ago, end=now, timezone="EST").fetch()

    length = 5
    temp = weather.c_to_f(float(df.get("temp")[0]))
    cond = weather.conditions.get(float(df.get("coco")[0]))
    wind_speed = weather.kmph_to_mph(float(df.get("wspd")[0]))

    otemp = temp
    temp = temp + 10 - 20.0 * (pref / 10.0)

    x = ""

    # conditions first
    if cond == conditions[1]:
        x += "Sky is clear! " + sunny_emoji

    if cond == conditions[3]:
        x += "Sky is Cloudy! " + partially_cloudy_emoji

    if cond == conditions[4]:
        x += "Sky is Cloudy! " + partially_cloudy_emoji

    if cond == conditions[5]:
        x += "Foggy out, be careful! " + fog

    if (
        cond == conditions[7]
        or cond == conditions[8]
        or cond == conditions[9]
        or cond == conditions[10]
        or cond == conditions[17]
        or cond == conditions[18]
    ):
        x += "Looks like rain, may want to bring an umbrella! " + rain_cloud_emoji

    # check for thunderstorms
    if cond == conditions[25] or cond == conditions[26] or cond == conditions[27]:
        x += "Careful, may be thunderstorms! " + thunder_cloud_rain_emoji

    x += (
        "\nAverage temp for next "
        + str(length)
        + " hours is "
        + str(otemp)
        + f"{chr(176)} F."
    )
    print(cond)

    if temp > 100:
        x += (
            "\nTemperature is scorching hot! Wear something light! And stay hydrated. "
            + lightshirt
            + shorts
            + hot_face_emoji
        )
    elif temp > 90:
        x += "\nTemperature is hot! Wear something light. " + lightshirt + shorts
    elif temp > 80:
        x += (
            "\nTemperature is getting pretty warm! Tee shirt and shorts weather! "
            + shirt
            + shorts
            + sunglasses
        )
    elif temp > 70:
        x += (
            "\nTemperature is nice! A tee shirt and shorts, or jeans. "
            + shirt
            + shorts
            + jeans
        )
    elif temp > 60:
        x += (
            "\nTemperature is a little on the colder side, may want jeans and a light jacket. "
            + jeans
            + labcoat
        )
    elif temp > 50:
        x += (
            "\nTemperature is getting colder, may want to grab a jacket! "
            + jeans
            + labcoat
        )
    elif temp > 40:
        x += "\nTemperature is pretty cold, wear a heavier jacket " + jeans + coat
    elif temp > 30:
        x += "\nBurr! Wear extra layers and a heavy jacket! " + coat
    elif temp > 20:
        x += (
            "\nIts freeezing out there, stay warm! Wear layers, warm jacket, and get some gloves and a hat! "
            + coat
        )
    else:
        x += (
            "\nAt this point you will be a snowman if you stay out for too long, so bring a carrot and sticks for arms "
            + snowman
        )

    if wind_speed > 30:
        x += "\nCareful super windy, speed is " + str(wind_speed) + "mph! " + wind1
    elif wind_speed > 22:
        x += (
            "\nIt's pretty windy out there, speed is "
            + str(wind_speed)
            + " mph, careful. "
            + wind1
        )
    elif wind_speed > 15:
        x += "\nIt's windy, speed is " + str(wind_speed) + " mph. " + wind2
    elif wind_speed > 7:
        x += "\nIt's a little windy, speed is " + str(wind_speed) + " mph. " + wind2

    return x
