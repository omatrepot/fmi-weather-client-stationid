import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import math
#import xmltodict
import json

from digitraffic_weather_client.models import FMIPlace, Forecast, Value, WeatherData

_LOGGER = logging.getLogger(__name__)

class Forecast:
    def __init__(self, station_name, station_lat, station_lon, forecasts):
        self.station_name = station_name
        self.station_lat = station_lat
        self.station_lon = station_lon
        self.forecasts = forecasts

def parse_forecast(json_data: str):
    data = json.loads(json_data)
    sensor_values = {entry['shortName']: entry for entry in data['sensorValues']}

    print("*********")
    #print(sensor_values)

    def get_value(sensor_name: str) -> Optional[Value]:
        sensor = sensor_values.get(sensor_name)
        if sensor:
            return Value(value=sensor['value'], unit=sensor['unit'])
        return None

    #print(data)
    station = _get_place(data)
    _LOGGER.debug("Received place: %s (%d, %d)", station.name, station.lat, station.lon)

    times = _get_datetimes(data)
    _LOGGER.debug("Received time points: %d", len(times))

    print("times")
    print(len(times))
    print(times)
    
    types = _get_value_types(data)
    _LOGGER.debug("Received types: %d", len(types))

    print("types")
    print(len(types))
    print(types)

    value_sets = _get_values(data)
    _LOGGER.debug("Received value sets: %d", len(value_sets))

    print("value_sets")
    print(len(value_sets))
    print(value_sets)

    value_sets2 = WeatherData(
        time= datetime.now(), #datetime.fromisoformat(data['dataUpdatedTime'].replace('Z', '+00:00')),
        temperature=get_value('Ilma'),
        dew_point=get_value('KastP'),
        pressure=None,  # Assuming pressure data is not in the provided JSON
        humidity=get_value('Koste'),
        wind_direction=get_value('TSuunt'),
        wind_speed=get_value('KTuuli'),
        wind_u_component=None,  # Assuming wind U component data is not in the provided JSON
        wind_v_component=None,  # Assuming wind V component data is not in the provided JSON
        wind_max=get_value('MTuuli'),
        wind_gust=None,  # Assuming wind gust data is not in the provided JSON
        symbol=None,  # Assuming symbol data is not in the provided JSON
        cloud_cover=None,  # Assuming cloud cover data is not in the provided JSON
        cloud_low_cover=None,  # Assuming cloud low cover data is not in the provided JSON
        cloud_mid_cover=None,  # Assuming cloud mid cover data is not in the provided JSON
        cloud_high_cover=None,  # Assuming cloud high cover data is not in the provided JSON
        precipitation_amount=get_value('S-Sum'),
        radiation_short_wave_acc=None,  # Assuming radiation data is not in the provided JSON
        radiation_short_wave_surface_net_acc=None,  # Assuming radiation data is not in the provided JSON
        radiation_long_wave_acc=None,  # Assuming radiation data is not in the provided JSON
        radiation_long_wave_surface_net_acc=None,  # Assuming radiation data is not in the provided JSON
        radiation_short_wave_diff_surface_acc=None,  # Assuming radiation data is not in the provided JSON
        geopotential_height=None,  # Assuming geopotential height data is not in the provided JSON
        land_sea_mask=None,  # Assuming land/sea mask data is not in the provided JSON
        feels_like=None  # Assuming feels-like temperature data is not in the provided JSON
    )

    _LOGGER.debug("Received value sets: %d", len(value_sets2))

    #print()
    #print(value_sets2)
    #print()
    # Combine values with types
    typed_value_sets: List[Dict[str, float]] = []
    for value_set in value_sets:
        typed_value_set = {}
        for idx, value in enumerate(value_sets2):
            typed_value_set[types[idx]] = value
        typed_value_sets.append(typed_value_set)

    # Combine typed values with times
    forecasts = []
    for idx, time in enumerate(times):
        if _is_non_empty_forecast(typed_value_sets[idx]):
            forecasts.append(_create_weather_data(time, typed_value_sets[idx]))

    _LOGGER.debug("Received non-empty value sets: %d", len(forecasts))


    #print("*********")
    #print(weather_data)

    return Forecast(station.name, station.lat, station.lon, forecasts)
    #return weather_data

# Helper functions to extract data from JSON structure

def _get_place_from_json(data: Dict[str, Any]) -> FMIPlace:
    place_data = data['place']  # Example structure: {'place': {'name': 'Place Name', 'lat': 123.456, 'lon': 456.789}}
    return FMIPlace(place_data['name'], place_data['lat'], place_data['lon'])

def _get_datetimes_from_json(data: Dict[str, Any]) -> List[datetime]:
    datetime_list = data['times']  # Example structure: {'times': ['2024-07-14T12:00:00Z', '2024-07-14T15:00:00Z']}
    return [datetime.fromisoformat(dt) for dt in datetime_list]

def _get_value_types_from_json(data: Dict[str, Any]) -> List[str]:
    types_list = data['types']  # Example structure: {'types': ['Temperature', 'WindSpeed', 'Humidity']}
    return types_list

#def _get_values_from_json(data: Dict[str, Any]) -> List[List[float]]:
#    values_list = data['values']  # Example structure: {'values': [[20.5, 2.3, 60], [21.0, 2.5, 55]]}
#    return values_list


def _get_place(data: Dict[str, Any]) -> FMIPlace:
    #place_data = (data['wfs:FeatureCollection']['wfs:member']['omso:GridSeriesObservation']
    #                  ['om:featureOfInterest']['sams:SF_SpatialSamplingFeature']['sams:shape']
    #                  ['gml:MultiPoint']['gml:pointMembers']['gml:Point'])

    #coordinates = place_data['gml:pos'].split(' ', 1)
    #lat = float(coordinates[0])
    #lon = float(coordinates[1])

    #return FMIPlace(place_data['gml:name'], lat, lon)
    return FMIPlace("stest", 0, 0)

def _get_datetimes(data: Dict[str, Any]) -> List[datetime]:
    result = []
    # Extract 'measuredTime' from each sensor value in the 'sensorValues' array
    sensor_values = data.get('sensorValues', [])
    for sensor in sensor_values:
        measured_time = sensor.get('measuredTime', '')
        if measured_time:
            # Parse the ISO 8601 datetime string directly
            timestamp = datetime.fromisoformat(measured_time.rstrip('Z')).replace(tzinfo=timezone.utc)
            result.append(timestamp)

    return result


def _get_value_types(data) -> List[str]:
    result = []
    # Assuming 'sensorValues' contains the types of values you're interested in
    sensor_values = data.get('sensorValues', [])

    for sensor in sensor_values:
        # Assuming you want the 'unit' as the value type
        result.append(sensor.get('shortName'))

    return result


def _get_values(data) -> List[float]:
    result = []
    # Assuming 'sensorValues' contains the values you're interested in
    sensor_values = data.get('sensorValues', [])
    
    # Create a dictionary to group values by time
    value_dict = {}
    
    for sensor in sensor_values:
        result.append(sensor.get('value', 0.0))
        #measured_time = sensor.get('measuredTime', '')
        #if measured_time not in value_dict:
        #    value_dict[measured_time] = []
        #value_dict[measured_time].append(sensor.get('value', 0.0))

    # Convert dictionary values to list of lists
    result = result#list(value_dict.values())

    return result


def _is_non_empty_forecast(forecast: Dict[str, float]) -> bool:
    """
    Check if forecast contains proper values
    :param forecast: Forecast dictionary
    :return: True if forecast contains values; False otherwise
    """
    for _, value in forecast.items():
        if not math.isnan(value):
            return True

    return False

def _summer_simmer(temperature: float, humidity_percent: float):
    if temperature <= 14.5:
        return temperature

    # Humidity value is expected to be on 0..1 scale
    humidity = humidity_percent / 100.0
    humidity_ref = 0.5

    # Calculate the correction
    return (1.8*temperature - 0.55*(1-humidity) * (1.8*temperature - 26) - 0.55*(1-humidity_ref)*26) \
        / (1.8*(1 - 0.55*(1-humidity_ref)))

def _feels_like(vals: Dict[str, float]) -> float:
    # Feels like temperature, ported from:
    # https://github.com/fmidev/smartmet-library-newbase/blob/master/newbase/NFmiMetMath.cpp#L535
    # For more documentation see:
    # https://tietopyynto.fi/tietopyynto/ilmatieteen-laitoksen-kayttama-tuntuu-kuin-laskentakaava/
    # https://tietopyynto.fi/files/foi/2940/feels_like-1.pdf
    temperature = vals.get("Temperature", None)
    wind_speed = vals.get("WindSpeedMS", None)
    humidity = vals.get("Humidity", None)
    radiation = vals.get("RadiationGlobal", None)

    if temperature is None:
        return None
    if wind_speed is None or wind_speed < 0.0 or humidity is None:
        return temperature

    # Wind chilling factor
    chill = 15 + (1-15/37)*temperature + 15/37*pow(wind_speed+1, 0.16)*(temperature-37)
    # Heat index
    heat = _summer_simmer(temperature, humidity)

    # Add corrections together
    feels = temperature + (chill - temperature) + (heat - temperature)

    # Perform radiation correction only when radiation is available
    if radiation is not None:
        absorption = 0.07
        feels += 0.7 * absorption * radiation / (wind_speed + 10) - 0.25

    return feels

def _create_weather_data(time, values: Dict[str, float]) -> WeatherData:
    """Create weather data from raw values"""

    def to_value(vals: Dict[str, float], variable_name: str, unit: str) -> Value:
        value = vals.get(variable_name, None)
        return Value(value, unit)

    # Some fields were available in HIRLAM forecasts, but are not
    # available in HARMONIE forecasts. These fields are kept here
    # for backward compatibility. Value of those fields will
    # always be None.
    return WeatherData(
        time=datetime.now(),
        temperature=to_value(values, 'Ilma', '°C'),
        #dew_point=to_value(values, 'DewPoint', '°C'),
        #pressure=to_value(values, 'Pressure', 'hPa'),
        #humidity=to_value(values, 'Humidity', '%'),
        #wind_direction=to_value(values, 'WindDirection', '°'),
        #wind_speed=to_value(values, 'WindSpeedMS', 'm/s'),
        #wind_u_component=to_value(values, 'WindUMS', 'm/s'),
        #wind_v_component=to_value(values, 'WindVMS', 'm/s'),
        #wind_max=to_value(values, 'MaximumWind', 'm/s'),  # Not supported
        #wind_gust=to_value(values, 'WindGust', 'm/s'),
        #symbol=to_value(values, 'WeatherSymbol3', ''),
        #cloud_cover=to_value(values, 'TotalCloudCover', '%'),
        #cloud_low_cover=to_value(values, 'LowCloudCover', '%'),
        #cloud_mid_cover=to_value(values, 'MediumCloudCover', '%'),
        #cloud_high_cover=to_value(values, 'HighCloudCover', '%'),
        #precipitation_amount=to_value(values, 'Precipitation1h', 'mm/h'),
        #radiation_short_wave_acc=to_value(values, 'RadiationGlobalAccumulation', 'J/m²'),
        #radiation_short_wave_surface_net_acc=to_value(values, 'RadiationNetSurfaceSWAccumulation', 'J/m²'),
        #radiation_long_wave_acc=to_value(values, 'RadiationLWAccumulation', 'J/m²'),  # Not supported
        #radiation_long_wave_surface_net_acc=to_value(values, 'RadiationNetSurfaceLWAccumulation', 'J/m²'),
        #radiation_short_wave_diff_surface_acc=to_value(values, 'RadiationDiffuseAccumulation', 'J/m²'),  # Not supported
        #geopotential_height=to_value(values, 'GeopHeight', 'm'),
        #land_sea_mask=to_value(values, 'LandSeaMask', ''),  # Not supported
        #feels_like=Value(_feels_like(values), '°C')
        )