import os

from pyowm.owm import OWM
from langchain_core.tools import tool

owm = OWM(os.getenv("OPENWEATHERMAP_API_KEY"))
mgr = owm.weather_manager()

@tool("get_weekend_forecast", description="Get the weather forecast for the upcoming weekend in a specified location.")
def get_weekend_forecast(location: str = 'Columbus,US,OH') -> str:
    from datetime import datetime, timedelta
    from pytz import timezone
    print(f"Fetching weekend weather forecast for {location}...")
    eastern = timezone('US/Eastern')
    three_h_forecast = mgr.forecast_at_place(location, "3h").forecast
    weekend_days = []
    today = datetime.now()
    for i in range(0, 7):
        day = today + timedelta(days=i)
        if day.weekday() in [5, 6]:
            weekend_days.append(day.date())
            if len(weekend_days) == 2:
                break
    weather_by_day = {d: [] for d in weekend_days}
    for w in three_h_forecast:
        w_time_utc = w.reference_time('date')
        w_time_est = w_time_utc.astimezone(eastern)
        if w_time_est.hour >= 8 and w_time_est.hour <= 20:
            w_time = w_time_est.date()
            if w_time in weather_by_day:
                weather_by_day[w_time].append((w, w_time_est))
    output = []
    for d in weekend_days:
        if not weather_by_day[d]:
            output.append(f"No forecast available for {d}.")
            continue
        output.append(f"Forecasts for {location} on {d} (8AM-8PM EST):")
        for w, w_time_est in weather_by_day[d]:
            forecast_time = w_time_est.strftime('%Y-%m-%d %I:%M %p EST')
            detailed_status = w.detailed_status
            wind = w.wind()
            humidity = w.humidity
            temperature = w.temperature('fahrenheit')
            rain = w.rain
            heat_index = w.heat_index
            clouds = w.clouds
            output.append(
                f"  At {forecast_time}:\n"
                f"    Detailed status: {detailed_status}\n"
                f"    Wind speed: {wind.get('speed', 'N/A')} m/s, direction: {wind.get('deg', 'N/A')}°\n"
                f"    Humidity: {humidity}%\n"
                f"    Temperature: \n"
                f"      - Current: {temperature.get('temp', 'N/A')}°F\n"
                f"      - Feels like: {temperature.get('feels_like', 'N/A')}°F\n"
                f"    Rain: {rain}\n"
                f"    Heat index: {heat_index}\n"
                f"    Cloud cover: {clouds}%"
            )
    return "\n\n".join(output)
