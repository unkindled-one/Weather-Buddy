from meteostat import Stations, Hourly, Daily
from datetime import datetime, timedelta, timezone
import numpy as np
import location
from zoneinfo import ZoneInfo

default_zipcode = 22030

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


def current_temp(lat: float, long: float) -> float:
    """
    Gets the temperature at the location from the most recent hour
    """
    station = Stations().nearby(lat, long).fetch(1)
    now = datetime.now(ZoneInfo("America/New_York"))
    now = now.replace(tzinfo=None)
    hour_ago = now - timedelta(hours=1)
    frame = Hourly(station, start=hour_ago, end=now, timezone="EST").fetch()

    return (
        c_to_f(float(frame.get("temp")[0])),
        conditions.get(float(frame.get("coco")[0])),
    )


def detailed_weather(lat: float, long: float) -> tuple[float, str, float]:
    """
    Returns more detailed information about the conditions at lat,long
    """
    station = Stations().nearby(lat, long).fetch(1)
    now = datetime.now(ZoneInfo("America/New_York"))
    now = now.replace(tzinfo=None)
    hour_ago = now - timedelta(hours=1)
    df = Hourly(station, start=hour_ago, end=now, timezone="EST").fetch()

    temp = c_to_f(float(df.get("temp")[0]))
    cond = conditions.get(float(df.get("coco")[0]))
    wind_speed = kmph_to_mph(float(df.get("wspd")[0]))
    # return tuple/list so we can add emojis
    return (temp, cond, wind_speed)


def get_precip(lat: float, long: float) -> str:
    """
    Returns precipitation info
    """
    station = Stations().nearby(lat, long).fetch(1)
    now = datetime.now(ZoneInfo("America/New_York"))
    now = now.replace(tzinfo=None)
    hour_ago = now - timedelta(hours=1)
    df = Hourly(station, start=hour_ago, end=now, timezone="EST").fetch()
    # convert to inches
    prcp = mm_to_in(df.get("prcp"))
    snow = mm_to_in(df.get("snow"))
    # get value from pandas Series
    prcp = str(prcp).split()[3]
    snow = str(snow).split()[3]
    # if 'NaN set equal to 0
    if prcp == "NaN":
        prcp = 0.0
    if snow == "NaN":
        snow = 0.0
    # get condition name from condition code
    cond = conditions.get(float(df.get("coco")[0]))
    return (prcp, snow, cond)


def forecast_weather(
    lat: float, long: float, num_hours: int
) -> list[list[datetime.time, float, float, float, str]]:
    """
    Gets the forecast for the next num_hours hours at lat, long
    """
    # set hard limit for maximum number of hours in the future
    if num_hours > 60:
        num_hours = 60

    now = datetime.now(ZoneInfo("America/New_York"))
    now = now.replace(tzinfo=None)

    station = Stations().nearby(lat, long).fetch(1)
    end = now + timedelta(hours=num_hours)

    if now.minute < 30:
        now = now - timedelta(hours=1)

    frame = Hourly(station, start=now, end=end, timezone="EST").fetch()
    forecast = []

    # get info from each row in DF
    for idx, row in frame.iterrows():
        time = idx.to_pydatetime()
        temp = c_to_f(row["temp"])
        cond = conditions.get(float(row["coco"]))
        wind = kmph_to_mph(float(row["wspd"]))
        forecast.append([time, temp, wind, cond])

    return forecast


def daily_high_low(lat: float, long: float, zipcode: int):
    """
    Returns the daily high and low value for (lat,long)
    """
    date = datetime.today().date()
    date = np.datetime64(date)

    station = Stations().nearby(lat, long).fetch(1)
    data = Daily(station, date, date)
    data = data.fetch()

    low = data["tmin"][0]
    high = data["tmax"][0]

    return (c_to_f(low), c_to_f(high))


def historical_rain(lat: float, long: float):
    date = datetime.today().date()
    date = np.datetime64(date)
    station = Stations().nearby(lat, long).fetch(1)
    data = Daily(station, end=date)
    data = data.fetch()
    rain = data["prcp"]
    # summ = np.sum(rain)
    # num_NaNs = 0

    rain2 = np.zeros((len(rain), 1))

    i = 0
    for amt in rain:
        if not np.isnan(amt):
            rain2[i] = mm_to_in(amt)
            i += 1
    rain = rain2[:i]

    avg = np.average(rain)
    return np.round(avg, 3)


def c_to_f(temp: float) -> float:
    """
    Converts the specified Celsius temperature to Fahrenheit rounded to 2 digits.
    """
    return round((temp * 1.8) + 32, 2)


def mm_to_in(depth: float) -> float:
    """
    Converts MM to inches, rounded to 2 digits.
    """
    return round((depth / 25.4), 2)


def kmph_to_mph(speed: float) -> float:
    """
    Converts wind speed from kmph to mph, rounded to 2 digits
    """
    return round((speed / 1.609), 2)


def avg_next(lat: float, long: float, num_hours: int) -> float:
    """
    Gets the average temperature for the next X hours
    """
    now = datetime.now(ZoneInfo("America/New_York"))
    now = now.replace(tzinfo=None)

    station = Stations().nearby(lat, long).fetch(1)
    frame = Hourly(
        station,
        start=now - timedelta(hours=1),
        end=now + timedelta(hours=num_hours),
        timezone="EST",
    ).fetch()
    forecast = []
    avg = 0
    for i, temp in enumerate(frame.get("temp")):
        hour_of_forecast = (
            (now + timedelta(hours=i)).replace(microsecond=0, second=0, minute=0).time()
        )
        # forecast.append([hour_of_forecast, c_to_f(float(temp))])
        avg = avg + c_to_f(float(temp))

    avg = avg / num_hours

    return avg


if __name__ == "__main__":
    # print(detailed_weather(38.8315, -77.3117))
    lat, long = location.get_coord_from_zip(22030)
    historical_rain(lat, long)
    # print(forecast_weather(38.8315, -77.3117, 3))
    print(detailed_weather(lat, long))
