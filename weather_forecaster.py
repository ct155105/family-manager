import os

from pyowm.owm import OWM
from langchain_core.tools import tool

owm = OWM(os.getenv("OPENWEATHERMAP_API_KEY"))
mgr = owm.weather_manager()

@tool("get_weather_forecast", description="Get the weather forecast for the upcoming weekend in a specified location.")
def get_weekend_forecast(location: str = 'Columbus,OH,US') -> str:
    from datetime import datetime, timedelta
    from pytz import timezone
    print(f"Fetching weekend weather forecast for {location}...")
    eastern = timezone('US/Eastern')
    forecaster = mgr.forecast_at_place(location, "3h")
    three_h_forecast = forecaster.forecast
    next_days = []
    today = datetime.now()
    for i in range(0, 3):
        day = today + timedelta(days=i)
        next_days.append(day.date())
    weather_by_day = {d: [] for d in next_days}
    for w in three_h_forecast:
        w_time_utc = w.reference_time('date')
        w_time_est = w_time_utc.astimezone(eastern)
        if w_time_est.hour >= 8 and w_time_est.hour <= 20:
            w_time = w_time_est.date()
            if w_time in weather_by_day:
                weather_by_day[w_time].append((w, w_time_est))
    output = []
    for d in next_days:
        if not weather_by_day[d]:
            output.append(f"No forecast available for {d}.")
            print(f"No forecast available for {d}.")
            continue
        
        # Calculate daily high and low temperatures
        temps = [w.temperature('fahrenheit').get('temp', 0) for w, _ in weather_by_day[d]]
        daily_high = max(temps) if temps else 'N/A'
        daily_low = min(temps) if temps else 'N/A'
        
        # Get the most common weather condition
        conditions = [w.detailed_status for w, _ in weather_by_day[d]]
        most_common_condition = max(set(conditions), key=conditions.count) if conditions else 'N/A'
        
        output.append(f"Forecast for {location} on {d}:")
        output.append(f"  HIGH: {daily_high}°F | LOW: {daily_low}°F")
        output.append(f"  Conditions: {most_common_condition}")
        output.append(f"\n  Hourly Details (8AM-8PM EST):")
        print(f"Forecast for {location} on {d}: HIGH {daily_high}°F, LOW {daily_low}°F - {most_common_condition}")
        
        for w, w_time_est in weather_by_day[d]:
            forecast_time = w_time_est.strftime('%Y-%m-%d %I:%M %p EST')
            detailed_status = w.detailed_status
            wind = w.wind()
            humidity = w.humidity
            temperature = w.temperature('fahrenheit')
            rain = w.rain
            heat_index = w.heat_index
            clouds = w.clouds
            log_line = (
                f"  At {forecast_time}: {detailed_status}, "
                f"Temp: {temperature.get('temp', 'N/A')}°F, "
                f"Humidity: {humidity}%, Wind: {wind.get('speed', 'N/A')} m/s, Clouds: {clouds}%"
            )
            print(log_line)
            output.append(
                f"    {forecast_time}: {detailed_status}, "
                f"Temp: {temperature.get('temp', 'N/A')}°F, "
                f"Humidity: {humidity}%, Wind: {wind.get('speed', 'N/A')} m/s, Clouds: {clouds}%"
            )
    return "\n\n".join(output)
