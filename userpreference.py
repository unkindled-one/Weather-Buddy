import database


def get_weather_pref(Userid: str):
    # first check local cache has it

    # check if database has it
    x = database.get_preference(Userid)
    return x


def set_weather_pref(Userid: str, pref: str):
    # first check local cache has it

    # check if database has it
    x = database.add_preference(Userid, pref)
    return x


def update_weather_pref(Userid: str, pref: str):
    # first check local cache has it

    # check if database has it
    x = database.update_preference((Userid, pref))
    return x

