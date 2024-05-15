import discord
from discord import app_commands
import database
import weather as weather_
import location
import reminder
import weather_warnings
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import datetime
import userpreference
import whattowear
from zoneinfo import ZoneInfo

#  Get the dicord token from the .env file
load_dotenv()
token = os.getenv("TOKEN")

#  Set up preliminary bot settings
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="/", intents=intents, help_command=None)

#  Strings to help printing
not_enough_args = (
    "Using default location, set your location with /setzipcode [zipcode]\n"
)
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


@client.event
async def on_ready():
    print("bot is online!")
    send_reminders.start()
    send_warnings.start()
    try:
        synced = await client.tree.sync(guild=None)  # Add the commands to the bot
        print(synced)
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)


@tasks.loop(minutes=1)
async def send_reminders():
    now = datetime.datetime.now(ZoneInfo("America/New_York"))
    hour = str(now.hour)
    minute = str(now.minute)
    for entry in database.get_ids_from_time(hour, minute):
        if entry is None:
            return
        user_id, username = entry
        zipcode = database.get_zip(str(user_id))
        if zipcode == -1:
            # ctx.send(not_enough_args)
            zipcode = weather_.default_zipcode
        # embed = discord.Embed(title=f'{username}, here is your daily weather reminder')
        lat, long = location.get_coord_from_zip(zipcode)
        embed = discord.Embed(
            # title=f"{username}, here is your daily weather reminder for {zipcode}",
            title=f"Bob, here is your daily weather reminder for {zipcode}",
            color=discord.Color.blue(),
        )
        for time, temp, wind, cond in weather_.forecast_weather(lat, long, 3):
            ret = f"{temp}{chr(176)} F\n"
            if temp < 32.0:
                ret += cold_face_emoji + "\n"
            if temp > 99.0:
                ret += hot_face_emoji + "\n"
            ret += str(cond) + " "
            if cond == "Cloudy":
                ret += cloudy_emoji
            if cond == "Overcast":
                ret += partially_cloudy_emoji
            if "Snowfall" in cond:
                ret += snowflake_emoji
            if "Snow Shower" in cond:
                ret += snow_cloud_emoji
            if cond == "Clear" or cond == "Fair":
                ret += sun_with_face_emoji
            if "Rain" in cond:
                ret += rain_cloud_emoji
                ret += umbrella_emoji
            if "Thunderstorm" in cond:
                ret += thunder_cloud_rain_emoji
            ret += "\n"
            ret += str(wind) + " mph wind\n"
            embed.add_field(name=f'{time.strftime("%I %p").strip("0")}', value=ret)

        user_object = await client.fetch_user(int(user_id))
        await user_object.send(embed=embed)


@tasks.loop(minutes=30)
async def send_warnings():
    warn_emoji = ":warning:"
    for user in database.get_all_users():
        zipcode = weather_.default_zipcode
        if user[0] != -1:
            zipcode = user[0]
        lat, long = location.get_coord_from_zip(zipcode)
        warnings = weather_warnings.weather_warnings(lat, long)
        if warnings == "There are not current weather warnings in your area.":
            continue
        user_object = await client.fetch_user(int(user[2]))
        embed = discord.Embed(
            title=f"{warn_emoji} {user[1]}, there are weather warnings in your area {warn_emoji}",
            description=warnings,
            color=discord.Color.yellow(),
        )
        await user_object.send(embed=embed)


@client.tree.command(name="temp")
@app_commands.describe(zipcode="Zipcode")
async def temp(interaction: discord.Interaction, zipcode: int | None = None):
    """
    Returns the current temperature
    Optionally takes a zipcode, otherwise uses default location
    Usage: /temp (zipcode)
    """
    ret = ""
    if zipcode is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
            ret += not_enough_args
        valid_zipcode = True
    else:
        valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title=f"Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        lat, long = location.get_coord_from_zip(zipcode)

    temperature, condition = weather_.current_temp(lat, long)
    # color stuff
    if temperature < 30:
        color = discord.Color.dark_blue()
    elif temperature < 40:
        color = discord.Color.blue()
    elif temperature < 50:
        color = discord.Color.teal()
    elif temperature < 60:
        color = discord.Color.dark_teal()
    elif temperature < 70:
        color = discord.Color.green()
    elif temperature < 80:
        color = discord.Color.yellow()
    elif temperature < 90:
        color = discord.Color.orange()
    elif temperature < 100:
        color = discord.Color.dark_orange()
    elif temperature < 110:
        color = discord.Color.red()
    else:
        color = discord.Color.dark_red()

    embed = discord.Embed(
        title=f"Current Temperature",
        description=f"It is currently {temperature}{chr(176)} F {thermometer_emoji} in {zipcode}",
        color=color,
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="precip")
@app_commands.describe(zipcode="Zipcode")
async def precip(interaction: discord.Interaction, zipcode: int = None):
    """
    Returns the daily total precipitation in inches. Includes snowfall if applicable
    Usage: /precip [zipcode]
    """
    ret = ""
    if zipcode is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
            ret += not_enough_args
        lat, long = location.get_coord_from_zip(zipcode)
    valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title=f"Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        lat, long = location.get_coord_from_zip(zipcode)
    # call precip method from weatheralt
    prcp, snow, cond = weather_.get_precip(lat, long)
    ret = ""
    ret += f"{prcp} inches "
    if float(prcp) > 0:
        ret += ":droplet: "
    if cond == 14.0 or cond == 15.0 or cond == 16.0:
        ret += str(snow) + "in snowfall :snowflake: "
    ret += f" in {zipcode}"
    embed = discord.Embed(
        title=f"Current Precipitation", description=ret, color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="weather")
@app_commands.describe(zipcode="Zipcode")
async def weather(interaction: discord.Interaction, zipcode: int = None):
    """
    Returns current weather conditions
    Optionally takes a zipcode, otherwise uses default location
    Usage: /weather (zipcode)
    """
    ret = ""
    if zipcode is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
            ret += not_enough_args
        lat, long = location.get_coord_from_zip(zipcode)
    valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title=f"Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        lat, long = location.get_coord_from_zip(zipcode)

    # add weather.py function here
    temperature, condition, wspd = weather_.detailed_weather(lat, long)
    # color stuff
    if temperature < 30:
        color = discord.Color.dark_blue()
    elif temperature < 40:
        color = discord.Color.blue()
    elif temperature < 50:
        color = discord.Color.teal()
    elif temperature < 60:
        color = discord.Color.dark_teal()
    elif temperature < 70:
        color = discord.Color.green()
    elif temperature < 80:
        color = discord.Color.yellow()
    elif temperature < 90:
        color = discord.Color.orange()
    elif temperature < 100:
        color = discord.Color.dark_orange()
    elif temperature < 110:
        color = discord.Color.red()
    else:
        color = discord.Color.dark_red()

    # add emojis
    ret += str(temperature) + chr(176) + " F " + thermometer_emoji
    if temperature < 32.0:
        ret += cold_face_emoji + "\n"
    if temperature > 99.0:
        ret += hot_face_emoji + "\n"
    ret += "\n" + str(condition) + " "
    if condition == "Cloudy":
        ret += cloudy_emoji
    if condition == "Overcast":
        ret += partially_cloudy_emoji
    if "Snowfall" in condition:
        ret += snowflake_emoji
    if "Snow Shower" in condition:
        ret += snow_cloud_emoji
    if condition == "Clear" or condition == "Fair":
        ret += sun_with_face_emoji
    if "Rain" in condition:
        ret += rain_cloud_emoji
        ret += umbrella_emoji
    if "Thunderstorm" in condition:
        ret += thunder_cloud_rain_emoji
    ret += "\n"
    ret += str(wspd) + " mph wind"
    embed = discord.Embed(
        title=f"Current Weather for {zipcode}", description=ret, color=color
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="daily")
@app_commands.describe(zipcode="Zipcode")
async def daily(interaction: discord.Interaction, zipcode: int = None):
    """
    Returns the daily high and low for a location
    Optionally takes a zipcode, otherwise uses default location
    Usage: /daily (zipcode)
    """
    ret = ""
    if zipcode is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
            ret += not_enough_args
        lat, long = location.get_coord_from_zip(zipcode)
    valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title=f"Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        lat, long = location.get_coord_from_zip(zipcode)

    low, high = weather_.daily_high_low(lat, long, zipcode)
    embed = discord.Embed(
        title=f"Today's High/Low in {zipcode}",
        description=f"High: {high}{chr(176)} F {thermometer_emoji}\nLow: {low}{chr(176)} F {thermometer_emoji}",
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="warnings")
@app_commands.describe(zipcode="Zipcode")
async def warnings(interaction: discord.Interaction, zipcode: int = None):
    """
    Returns the current weather warnings for a location
    Optionally takes a zipcode, otherwise uses default location
    Usage /warnings (zipcode)
    """
    ret = ""
    if zipcode is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
            ret += not_enough_args
        lat, long = location.get_coord_from_zip(zipcode)
        valid_zipcode = True
    else:
        valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title=f"Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        lat, long = location.get_coord_from_zip(zipcode)

    ret += str(weather_warnings.weather_warnings(lat, long))
    if ret == "There are not current weather warnings in your area.":
        embed = discord.Embed(
            title=f"Weather Warnings for {zipcode}",
            description=ret,
            color=discord.Color.green(),
        )
    else:
        embed = discord.Embed(
            title=f"Weather Warnings for {zipcode}",
            description=ret,
            color=discord.Color.yellow(),
        )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="forecast")
@app_commands.describe(zipcode="Zipcode")
@app_commands.describe(hours="Hours")
async def forecast(
    interaction: discord.Interaction, zipcode: int = None, hours: int = None
):
    """
    Returns future temperature for a location
    Optionally takes a zipcode and number of hours,
    otherwise uses default location and 3 hour
    Usage: /forecast [zipcode] [hours]
    """
    ret = ""
    if zipcode is None and hours is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
        hours = 3
    if zipcode is None and hours is not None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
    if zipcode is not None and hours is None:
        hours = 3
    valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title="Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    lat, long = location.get_coord_from_zip(zipcode)
    embed = discord.Embed(
        title=f"Current Forecast for {zipcode}", color=discord.Color.blue()
    )
    for time, temp, wind, cond in weather_.forecast_weather(lat, long, hours):
        ret = f"{temp}{chr(176)} F\n"
        if temp < 32.0:
            ret += cold_face_emoji + "\n"
        if temp > 99.0:
            ret += hot_face_emoji + "\n"
        ret += str(cond) + " "
        if cond == "Cloudy":
            ret += cloudy_emoji
        if cond == "Overcast":
            ret += partially_cloudy_emoji
        if "Snowfall" in cond:
            ret += snowflake_emoji
        if "Snow Shower" in cond:
            ret += snow_cloud_emoji
        if cond == "Clear" or cond == "Fair":
            ret += sun_with_face_emoji
        if "Rain" in cond:
            ret += rain_cloud_emoji
            ret += umbrella_emoji
        if "Thunderstorm" in cond:
            ret += thunder_cloud_rain_emoji
        ret += "\n"
        ret += str(wind) + " mph wind\n"
        embed.add_field(name=f'{time.strftime("%I %p").strip("0")}', value=ret)
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="wear")
@app_commands.describe(zipcode="Zipcode")
async def wear(interaction: discord.Interaction, zipcode: int = None):
    """
    Returns a suggestion on what to wear based on preference and weather conditions
    Requires /setpref to have been called to set a user preference
    Usage: /wear [zipcode]
    """
    ret = ""
    skip = 0
    if zipcode is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1 or zipcode == "NoneType" or zipcode is None:
            zipcode = weather_.default_zipcode
            ret += "Please add a zipcode using /setzip XXXXX, or add zipcode after command /wear XXXXX"
            skip = 1
        else:
            lat, long = location.get_coord_from_zip(zipcode)
    valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title="Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        lat, long = location.get_coord_from_zip(zipcode)

    if skip == 0:
        x = userpreference.get_weather_pref(str(interaction.user.id))
        if x is None or x < 0 or x > 10:
            x = 5
        avg = weather_.avg_next(lat, long, 5)
        ret += whattowear.get_outfit(x, avg, lat, long)
    embed = discord.Embed(
        title=f"Clothing Recommendations for {zipcode}",
        description=ret,
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="setpref")
@app_commands.describe(pref="Preference")
async def setpref(interaction: discord.Interaction, pref: int):
    """
    Allows user to set their preference level from 0-10
    Needed before /wear will function correctly
    Usage: /setpref (preference)
    """
    if pref >= 0 or pref <= 10:
        x = userpreference.set_weather_pref(str(interaction.user.id), str(pref))
        embed = discord.Embed(
            title=f"Set your preference to {str(pref)}", color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="Please enter an int from 0-10", color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)


@client.tree.command(name="getpref")
async def getpref(interaction: discord.Interaction):
    """
    Returns set preference value
    Usage: /getpref
    """
    ret = ""

    x = userpreference.get_weather_pref(str(interaction.user.id))
    embed = discord.Embed(
        title=f"Your preference is currently set to {str(x)}",
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="setzip")
@app_commands.describe(zipcode="Zipcode")
async def setzip(interaction: discord.Interaction, zipcode: int):
    """
    Set default zipcode so the user doesn't have to pass it with every command
    Usage: /setzip (zipcode)
    """
    ret = ""
    if 501 <= zipcode <= 99950:
        x = location.set_zip(
            str(interaction.user.id),
            str(zipcode),
            str(await client.fetch_user(interaction.user.id)).split("#")[0],
        )
        embed = discord.Embed(
            title=f"Zipcode set to {str(zipcode)}", color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="Please enter a valid zipcode", color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)


@client.tree.command(name="getzip")
async def getzip(interaction: discord.Interaction):
    """
    Returns set zipcode
    Usage: /getzip
    """
    x = location.get_zip(str(interaction.user.id))
    embed = discord.Embed(
        title=f"Your zipcode is currently set to {str(x)}", color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="historicalrain")
@app_commands.describe(zipcode="Zipcode")
async def historicalrain(interaction: discord.Interaction, zipcode: int = None):
    """
    Returns the historical average rainfall
    Optionally takes a zipcode
    Usage: /historicalrain [zipcode
    """
    ret = ""
    if zipcode is None:
        zipcode = location.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
        lat, long = location.get_coord_from_zip(zipcode)
        valid_zipcode = True
    else:
        valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title=f"Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    else:
        lat, long = location.get_coord_from_zip(zipcode)
    hist_rain = weather_.historical_rain(lat, long)
    embed = discord.Embed(
        title=f"Historical Rainfall",
        description=f"Historically, there have been {hist_rain} inches of rain on this day in {zipcode}.",
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="outdoorplanning")
@app_commands.describe(zipcode="Zipcode")
@app_commands.describe(hours="Hours")
async def outdoorplanning(
    interaction: discord.Interaction, zipcode: int = None, hours: int = None
):
    """
    Finds the best time to go outside according to the user's preferences
    You must set your preferences with /setpref (preference [0-10]) to use this
    Optionally can provide the number of hours to search in the future
    Usage: /outdoorplanning [zipcode] [hour]
    """
    ret = ""
    pref = userpreference.get_weather_pref(str(interaction.user.id))
    # hours = 5
    # zipcode = database.get_zip(str(interaction.user.id))
    if pref == -1:
        await interaction.response.send_message(
            "You must set your preferences with /setpref to use this command."
        )
        return

    if zipcode is None and hours is None:

        valid_zipcode = True
    elif zipcode is None:
        pass
    elif hours is None:
        pass

    if zipcode is None and hours is None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
        hours = 5
    if zipcode is None and hours is not None:
        zipcode = database.get_zip(str(interaction.user.id))
        if zipcode == -1:
            zipcode = weather_.default_zipcode
    if zipcode is not None and hours is None:
        hours = 5
    if zipcode is not None:
        valid_zipcode = location.valid_zipcode_check(zipcode=zipcode)
    if not valid_zipcode:
        embed = discord.Embed(title=f"Invalid Zipcode", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    lat, long = location.get_coord_from_zip(zipcode)
    forecast_data = weather_.forecast_weather(lat, long, hours)
    # Assume that preferred weather is within 50-90, with each pref + 1 adding 4 degrees
    forecast_pref = [
        [i, abs(x[1] - (50 + 4 * pref))] for i, x in enumerate(forecast_data)
    ]
    forecast_pref.sort(key=lambda x: x[1])
    best_time = forecast_data[forecast_pref[0][0]]
    time, temperature, wspd, condition = best_time

    ret += f'The best time to go outside based on your preferences is {time.strftime("%I %p").strip("0")}.\n Where it will be:\n'
    # add emojis
    ret += str(temperature) + chr(176) + " F " + thermometer_emoji

    if temperature < 32.0:
        ret += cold_face_emoji + "\n"
    if temperature > 99.0:
        ret += hot_face_emoji + "\n"
    ret += "\n" + str(condition) + " "
    if condition == "Cloudy":
        ret += cloudy_emoji
    if condition == "Overcast":
        ret += partially_cloudy_emoji
    if "Snowfall" in condition:
        ret += snowflake_emoji
    if "Snow Shower" in condition:
        ret += snow_cloud_emoji
    if condition == "Clear" or condition == "Fair":
        ret += sun_with_face_emoji
    if "Rain" in condition:
        ret += rain_cloud_emoji
        ret += umbrella_emoji
    if "Thunderstorm" in condition:
        ret += thunder_cloud_rain_emoji
    ret += "\n"
    ret += str(wspd) + " mph wind"
    embed = discord.Embed(
        title="Outdoor Planning", description=ret, color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="getreminder")
async def getreminder(interaction: discord.Interaction):
    """
    Returns the time set to be reminded at
    Usage: /getreminder
    """
    ret = ""
    database_time = database.get_reminder(str(interaction.user.id))
    time = datetime.time(hour=database_time[0], minute=database_time[1])
    embed = discord.Embed(
        title=f'Your daily reminder is currently set for {time.strftime("%I:%M %p").strip("0")}',
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="setreminder")
@app_commands.describe(hour="Hour")
@app_commands.describe(_min="Minutes")
async def setreminder(interaction: discord.Interaction, hour: int, _min: int):
    """
    Sets a weather reminder for the specified time
    Optionally takes a zipcode, otherwise uses user's set location or default location
    Usage: /set_reminder (hour) (minute) [zipcode]
    """
    if int(hour) > 23 or int(hour) < 0 or int(_min) < 0 or int(_min) > 59:
        embed = discord.Embed(
            title="Please enter valid time in military time, ie 14 46",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)
    else:
        x = database.add_reminder(interaction.user.id, hour, _min)
        time = datetime.time(hour=int(hour), minute=int(_min))
        if x == 1:
            username = str(await client.fetch_user(interaction.user.id))
            username = username.split("#")[0] if username is not None else None
            embed = discord.Embed(
                title=f'Daily reminder set for {time.strftime("%I:%M %p").strip("0")}',
                color=discord.Color.blue(),
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Error saving time", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)


@client.tree.command(name="help")
@app_commands.describe(cmd="Command Name")
async def help(interaction: discord.Interaction, cmd: str = None):
    ret = ""
    if cmd is None:
        ret += """Available commands: (required arguments) [optional arguments]

__Main Commands__
/weather [zipcode]
/forecast [zipcode] [hours]
/wear [zipcode]
/warnings [zipcode]
/outdoorplanning [zipcode]

__Weather__
/weather [zipcode]
/temp [zipcode]
/daily [zipcode]
/forecast [zipcode] [hours]
/wear [zipcode]
/precip [zipcode]
/historicalrain [zipcode]
/warnings [zipcode]
/outdoorplanning [zipcode]

__Reminders__
/setreminder (hours) (minutes) 
/getreminder

__Zipcode and Preference__
/setzip (zipcode)
/getzip
/setpref (preference)
/getpref

__Help__
/help [command name]"""
    # else:
    else:
        match cmd:
            case "temp":
                ret += """Returns the current temperature
Optionally takes a zipcode, otherwise uses default location
Usage: /temp (zipcode)"""
            case "weather":
                ret += """Returns current weather conditions
Optionally takes a zipcode, otherwise uses default location
Usage: /weather (zipcode)"""
            # case 'remind':
            #   ret += """Sets a reminder
            #        FINISH WRITING REMINDER, THEN CHANGE THIS"""
            case "forecast":
                ret += """Returns future temperature for a location
Optionally takes a zipcode and number of hours,
otherwise uses default location and 3 hour
Usage: /forecast [zipcode] [hours]"""
            case "daily":
                ret += """Returns the daily high and low for a location
Optionally takes a zipcode, otherwise uses default location
Usage: /daily (zipcode)"""
            case "warnings":
                ret += """Returns the current weather warnings for a location
Optionally takes a zipcode, otherwise uses default location
Usage /warnings (zipcode)"""
            case "setreminder":
                ret += """Sets a weather reminder for the specified time
Optionally takes a zipcode, otherwise uses user's set location or default location
Usage: /set_reminder (hour) (minute) [zipcode]"""
            case "outdoorplanning":
                ret += """Finds the best time to go outside according to the user's preferences
You must set your preferences with /setpref (preference [0-10]) to use this
Optionally can provide the number of hours to search in the future
Usage: /outdoorplanning [zipcode] [hour]"""
            case "precip":
                ret += """Returns the daily total precipitation in inches. Includes snowfall if applicable
Usage: /precip [zipcode]"""
            case "wear":
                ret += """Returns a suggestion on what to wear based on preference and weather conditions
Requires /setpref to have been called to set a user preference
Usage: /wear [zipcode]"""
            case "setpref":
                ret += """Allows user to set their preference level from 0-10
Needed before /wear will function correctly
Usage: /setpref (preference)"""
            case "getpref":
                ret += """Returns set preference value
Usage: /getpref"""
            case "setzip":
                ret += """Set default zipcode so the user doesn't have to pass it with every command
Usage: /setzip (zipcode)"""
            case "getzip":
                ret += """Returns set zipcode
Usage: /getzip"""
            case "historicalrain":
                ret += """Returns the historical average rainfall
Optionally takes a zipcode
Usage: /historicalrain [zipcode]"""
            case "getreminder":
                ret += """Returns the time set to be reminded at
Usage: /getreminder"""
            case other:
                ret += "Command " + cmd + " not found."
            # check args[0] for specific command
            # print more detailed help
    if cmd is not None:
        embed = discord.Embed(
            title=f"Help - ({cmd})", description=ret, color=discord.Color.dark_gold()
        )
    else:
        embed = discord.Embed(
            title="Help", description=ret, color=discord.Color.dark_gold()
        )
    await interaction.response.send_message(embed=embed)


client.run(token)
