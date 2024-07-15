from typing import Optional

import asyncio,datetime,json

from digitraffic_weather_client import http
from digitraffic_weather_client.models import Weather
from digitraffic_weather_client.parsers import forecast as forecast_parser

def weather_by_station_id(station_id: int) -> Optional[Weather]:
    """
    Get the latest weather information by FMI station ID.

    :param station_id: FMI station ID (e.g., 12345)
    :return: Latest weather information if available; None otherwise
    """
    # Tiesääaseman perustiedot https://tie.digitraffic.fi/api/weather/v1/stations/14028
    response_text = http.request_information_by_station_id(station_id)
    #print(stationInformation)

    # Parse the JSON string into a dictionary
    stationInformation = json.loads(response_text)

    # Extract coordinates and Finnish name
    latitude = stationInformation["geometry"]["coordinates"][0]
    longitude = stationInformation["geometry"]["coordinates"][1]
    fi_name = stationInformation["properties"]["names"]["fi"]

    # New code to extract and convert dataUpdatedTime
    data_updated_time_str = stationInformation["properties"]["dataUpdatedTime"]
    data_updated_time = datetime.datetime.strptime(data_updated_time_str, "%Y-%m-%dT%H:%M:%SZ")

    if (fi_name is not None and latitude is not None and longitude is not None):
        print(f"Station {station_id} is located at {latitude}, {longitude} ({fi_name}) and updated at {data_updated_time}")

    # Tiesääaseman data esim. https://tie.digitraffic.fi/api/weather/v1/stations/14028/data
    #stationData = http.request_weather_by_station_id(station_id)

    #forecast = forecast_parser.parse_forecast(stationData)
    
    

    #if len(forecast.forecasts) == 0:
    #    return None

    #weather_state = forecast.forecasts[-1]

    #print(weather_state)

    return Weather("stationData.place",3232, "stationData.lat", "stationData.lon",datetime.datetime.now(), "")

    #forecast = forecast_parser.parse_forecast(stationData)
    
    
    #print("sss*********")
    #print(forecast.)

    #print("************")
    #print(forecast)
    #if len(forecast.forecasts) == 0:
    #    return None

    
    #if len(forecast.forecasts) == 0:
    #    return None

    #weather_state = forecast[-1]

    #print("sss*********")
    #print(forecast)
    #weather_state = forecast.forecasts[-1]
    #print("************")
    #print(weather_state)
    #print("************")
    #weather_state = forecast.forecasts[0]
    #print("************")
    #print(weather_state)
    #print("************")
    #weather_state = forecast.forecasts[2]
    #print("************")
    #print(weather_state)
    #print("************")
    #wind_speed_value = weather_state.wind_speed.value
    #wind_speed_unit = weather_state.wind_speed.unit
    #print(f"Wind Speed: {wind_speed_value} {wind_speed_unit}")
    ##print(weather_state
    #print("************")

    # Check if wind speed data is available in the latest forecast
    #for entry in forecast.forecasts:
    #   if entry['type'] == 'AverageWindSpeed' or entry['type'] == 'MaxWindSpeed':
    #    wind_speed_value = entry['value']
    #    wind_speed_unit = entry['unit']
    #    break

    #if wind_speed_value is not None and wind_speed_unit is not None:
    #   print(f"Wind Speed: {wind_speed_value} {wind_speed_unit}")
    #else:
    #   print("Wind speed data not available")
    #return Weather(forecast.forecasts.place, forecast.lat, forecast.lon, weather_state)
    #return Forecast(station.name, station.lat, station.lon, forecasts)
    #return Weather(forecast.place, forecast.lat, forecast.lon, weather_state)

async def async_weather_by_station_id(station_id: int) -> Optional[Weather]:
    """
    Get the latest weather information by FMI station ID asynchronously.

    :param station_id: FMI station ID (e.g., 12345)
    :return: Latest weather information if available; None otherwise
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, weather_by_station_id, station_id)

def weather_by_coordinates(lat: float, lon: float) -> Optional[Weather]:
    """
    Get the latest weather information by coordinates.

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :return: Latest weather information if available; None otherwise
    """
    response = http.request_weather_by_coordinates(lat, lon)
    forecast = forecast_parser.parse_forecast(response)

    if len(forecast.forecasts) == 0:
        return None

    weather_state = forecast.forecasts[-1]
    return Weather(forecast.place, forecast.lat, forecast.lon, weather_state)


async def async_weather_by_coordinates(lat: float, lon: float) -> Optional[Weather]:
    """
    Get the latest weather information by coordinates asynchronously.

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :return: Latest weather information if available; None otherwise
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, weather_by_coordinates, lat, lon)


def weather_by_place_name(name: str) -> Optional[Weather]:
    """
    Get the latest weather information by place name.

    :param name: Place name (e.g. Kaisaniemi, Helsinki)
    :return: Latest weather information if available; None otherwise
    """
    response = http.request_weather_by_place(name)
    forecast = forecast_parser.parse_forecast(response)
    if len(forecast.forecasts) == 0:
        return None

    weather_state = forecast.forecasts[-1]
    return Weather(forecast.place, forecast.lat, forecast.lon, weather_state)


async def async_weather_by_place_name(name: str) -> Weather:
    """
    Get the latest weather information by place name asynchronously.

    :param name: Place name (e.g. Kaisaniemi, Helsinki)
    :return: Latest weather information if available, None otherwise
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, weather_by_place_name, name)


def forecast_by_place_name(name: str, timestep_hours: int = 24):
    """
    Get the latest forecast by place name.
    :param name: Place name
    :param timestep_hours: Hours between forecasts
    :return: Latest forecast
    """
    response = http.request_forecast_by_place(name, timestep_hours)
    return forecast_parser.parse_forecast(response)


async def async_forecast_by_place_name(name: str, timestep_hours: int = 24):
    """
    Get the latest forecast by place name asynchronously.
    :param name: Place name
    :param timestep_hours: Hours between forecasts
    :return: Latest forecast
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, forecast_by_place_name, name, timestep_hours)


def forecast_by_coordinates(lat: float, lon: float, timestep_hours: int = 24):
    """
    Get the latest forecast by coordinates
    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :param timestep_hours: Hours between forecasts
    :return: Latest forecast
    """
    response = http.request_forecast_by_coordinates(lat, lon, timestep_hours)
    return forecast_parser.parse_forecast(response)


async def async_forecast_by_coordinates(lat: float, lon: float, timestep_hours: int = 24):
    """
    Get the latest forecast by coordinates
    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :param timestep_hours: Hours between forecasts
    :return: Latest forecast
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, forecast_by_coordinates, lat, lon, timestep_hours)
