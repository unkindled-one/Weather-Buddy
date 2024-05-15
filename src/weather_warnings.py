import requests


def weather_warnings(lat: float, long: float) -> str:
    """Returns string of current weather warnings to the ."""
    headers = {"User-Agent": "CS321 Weather Project"}
    response = requests.get(
        f"https://api.weather.gov/alerts/active?point={lat},{long}",
        headers=headers
    ).json()

    if "features" not in response:
        return "There are not current weather warnings in your area."

    alerts = response["features"]

    all_warnings = ""
    if len(alerts) == 0:
        return "There are not current weather warnings in your area."
    for alert in alerts:
        alert = alert["properties"]["headline"].split(" by")[0]
        emoji = ""
        if "Warning" in alert:
            emoji = ":warning:"  # can change emoji, just wanted to
        all_warnings += f"{emoji} {alert} {emoji}\n"
    return all_warnings
