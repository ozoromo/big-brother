from lupa import LuaRuntime, LuaError
import threading
import multiprocessing
import time
import webbrowser
import requests
from datetime import datetime, timedelta, timezone

# Create a Lua runtime with restricted libraries.
lua = LuaRuntime(unpack_returned_tuples=True)

def print_sandbox(input):
    print("from lua Sandbox: ", input)
    
def open_webpage(url):
    webbrowser.open(url)
    return f"{url}"
timers = {}

def start_timer(timer_name):
    if timer_name in timers:
        return "timer_started"
    timers[timer_name] = time.time()
    return f"Timer '{timer_name}' started."

def stop_timer(timer_name):
    """Stop a timer and return the elapsed time."""
    global timers
    if timer_name in timers:
        elapsed_time = time.time() - timers[timer_name]
        del timers[timer_name]  # Remove the timer after stopping
        return f"Timer '{timer_name}' stopped. Elapsed time: {elapsed_time:.2f} seconds."
    else:
        return f"Timer '{timer_name}' not found."
    
# Function to convert UNIX timestamp to local time in Germany
def unix_to_local_time(unix_timestamp, timezone_offset):
    """Convert UNIX timestamp to local time given a timezone offset."""
    utc_time = datetime.utcfromtimestamp(unix_timestamp)
    local_time = utc_time + timedelta(seconds=timezone_offset)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

def weather_info(City_name):
    # Define the API key and URL
    API_KEY = 'bd5e378503939ddaee76f12ad7a97608'  # Replace with your actual OpenWeatherMap API key
    CITY = City_name
    URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}'

    # Make the API request
    response = requests.get(URL)
    data = response.json()

    # Check if the response is successful
    if response.status_code == 200:
        # Extract city and country information
        city_name = data['name']
        country_code = data['sys']['country']
        
        # Extract weather information
        weather_main = data['weather'][0]['main']
        weather_description = data['weather'][0]['description']
        weather_icon = data['weather'][0]['icon']
        
        # Extract temperature information
        temp_kelvin = data['main']['temp']
        temp_celsius = temp_kelvin - 273.15  # Convert Kelvin to Celsius
        temp_min_kelvin = data['main']['temp_min']
        temp_min_celsius = temp_min_kelvin - 273.15  # Convert Kelvin to Celsius
        temp_max_kelvin = data['main']['temp_max']
        temp_max_celsius = temp_max_kelvin - 273.15  # Convert Kelvin to Celsius
        feels_like_kelvin = data['main']['feels_like']
        feels_like_celsius = feels_like_kelvin - 273.15  # Convert Kelvin to Celsius
        
        # Extract humidity and pressure information
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        
        # Extract visibility
        visibility = data['visibility']
        
        # Extract wind information
        wind_speed = data['wind']['speed']
        wind_deg = data['wind']['deg']
        
        # Extract cloud coverage
        cloud_coverage = data['clouds']['all']
        
        # Extract sunrise and sunset times
        sunrise = data['sys']['sunrise']
        sunset = data['sys']['sunset']
        
        # Extract timezone offset
        timezone_offset = data['timezone']
        
        # Convert UNIX timestamps to local time in Germany
        sunrise_local = unix_to_local_time(sunrise, timezone_offset)
        sunset_local = unix_to_local_time(sunset, timezone_offset)
        data_calc_time_local = unix_to_local_time(data['dt'], timezone_offset)
        
        # Format the information as a string
        weather_report = (
            f"City: {city_name}, {country_code}\n"
            f"Weather: {weather_main} - {weather_description.capitalize()}\n"
            f"Icon URL: http://openweathermap.org/img/wn/{weather_icon}.png\n"
            f"Temperature: {temp_celsius:.2f} °C (Min: {temp_min_celsius:.2f} °C, Max: {temp_max_celsius:.2f} °C)\n"
            f"Feels Like: {feels_like_celsius:.2f} °C\n"
            f"Humidity: {humidity}%\n"
            f"Pressure: {pressure} hPa\n"
            f"Visibility: {visibility} meters\n"
            f"Wind Speed: {wind_speed} m/s\n"
            f"Wind Direction: {wind_deg} degrees\n"
            f"Cloud Coverage: {cloud_coverage}%\n"
            f"Sunrise: {sunrise_local}\n"
            f"Sunset: {sunset_local}\n"
            f"Timezone Offset: {timezone_offset} seconds from UTC\n"
            f"Data Calculation Time: {data_calc_time_local}"
        )

        return weather_report

    else:
        # Return the error message if the API request was not successful
        return (f"Error: {data['message']}\n"
                f"HTTP Status Code: {response.status_code}")

# Default sanbox only allows printing and acess to math functions
safe_globals = {
    'print': print_sandbox,  # Allow print statements from Lua to appear in Python output
    'math': lua.globals().math,  # Expose the math library
    'os': {
        'date': lua.globals().os.date  # Expose the date function from os library
    },
    'open_webpage': open_webpage,
    'start_timer': start_timer,  # Expose the start_timer function to Lua
    'stop_timer': stop_timer,     # Expose the stop_timer function to Lua
    'weather_info': weather_info
}

def lua_runner(lua_code, safe_globals, queue):
    try:
        lua_func = lua.eval("""
            function(sandbox, code)
                local env = setmetatable({}, { __index = sandbox })
                local func = load(code, nil, 't', env)
                return func()
            end
        """)
        # Execute the Lua code in the sandboxed environment
        result = lua_func(safe_globals, lua_code)
        queue.put(result)
    except LuaError as e:
        queue.put(f"LuaError: {e}")
last_script = ""
def run_lua_in_sandbox(lua_code, safe_globals=safe_globals, timeout=30):
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=lua_runner, args=(lua_code, safe_globals, queue))

    process.start()
    process.join(timeout)
    global last_script
    if process.is_alive():
        process.terminate()
        process.join()
        return last_script
    else:
        if not queue.empty():
            last_script = queue.get()
        return last_script

# Besipiels lua code
# lua_code = """
# print(math.sqrt(16))
# return "Hello from Lua"
# """

# Lua code kann ausefuehrt werden und optional kann erweiterte sandbox mit gegeben werden
#output = run_lua_in_sandbox(lua_code)

#print(output)
