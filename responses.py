import random
import weather
import weather_warnings

def get_response(message: str,) -> str:
    p_message = message.lower()

    if p_message == 'weather':
        return str(weather.current_weather(38.8315, -77.3117))
    
    if p_message == 'daily':
        return(str(weather.daily_high_low(38.8315,-77.3117)))

    if p_message == 'hello':
        return 'Hey there!'

    if p_message == 'roll':
        return str(random.randint(1,6))

    if p_message == '!help':
        return '`Help`'
    
    if p_message == 'warnings':
        response = weather_warnings.weather_warnings(38.8315,-77.3117)
        if len(response) == 0:
            return 'There are no current warnings in your area'
        else:
            return response

    if p_message == 'andy':
        return 'That guy SUCKS!'

    return '???'