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

def parse_forecast(body: str) -> Forecast:
    """
    Parse forecast response body in JSON format to create Forecast object
    :param body: Forecast response body in JSON format
    :return: Forecast object containing station information and weather forecasts
    """
    data = json.loads(body)

    # Extract station information
    station_name = data['sensorValues'][0]['name']
    station_lat = None  # Replace with actual latitude if available in JSON
    station_lon = None  # Replace with actual longitude if available in JSON

    # Extract forecasts
    forecasts = []
    for sensor_value in data['sensorValues']:
        time = datetime.fromisoformat(sensor_value['measuredTime'])
        value = sensor_value['value']
        unit = sensor_value['unit']
        description = sensor_value.get('sensorValueDescriptionEn', '')

        # Here you can customize based on how you want to map sensor names to types
        # Example: Mapping sensor names to types
        type_mapping = {
            'ILMA': 'Temperature',
            'ILMA_DERIVAATTA': 'TemperatureDerivative',
            # Add more mappings as needed
        }

        # Check if the sensor name exists in type_mapping
        if sensor_value['name'] in type_mapping:
            weather_type = type_mapping[sensor_value['name']]
            forecasts.append({
                'time': time,
                'type': weather_type,
                'value': value,
                'unit': unit,
                'description': description
            })

    # Return Forecast object
    return Forecast(station_name, station_lat, station_lon, forecasts)

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

def _get_values_from_json(data: Dict[str, Any]) -> List[List[float]]:
    values_list = data['values']  # Example structure: {'values': [[20.5, 2.3, 60], [21.0, 2.5, 55]]}
    return values_list


def _get_place(data: Dict[str, Any]) -> FMIPlace:
    place_data = (data['wfs:FeatureCollection']['wfs:member']['omso:GridSeriesObservation']
                      ['om:featureOfInterest']['sams:SF_SpatialSamplingFeature']['sams:shape']
                      ['gml:MultiPoint']['gml:pointMembers']['gml:Point'])

    coordinates = place_data['gml:pos'].split(' ', 1)
    lat = float(coordinates[0])
    lon = float(coordinates[1])

    return FMIPlace(place_data['gml:name'], lat, lon)


def _get_datetimes(data: Dict[str, Any]) -> List[datetime]:
    result = []
    forecast_datetimes = (data['wfs:FeatureCollection']['wfs:member']['omso:GridSeriesObservation']
                              ['om:result']['gmlcov:MultiPointCoverage']['gml:domainSet']
                              ['gmlcov:SimpleMultiPoint']['gmlcov:positions'].split('\n'))
    for forecast_datetime in forecast_datetimes:
        parts = forecast_datetime.strip().replace('  ', ' ').split(' ')
        timestamp = datetime.utcfromtimestamp(int(parts[2])).replace(tzinfo=timezone.utc)
        result.append(timestamp)

    return result


def _get_value_types(data) -> List[str]:
    result = []
    value_types = (data['wfs:FeatureCollection']['wfs:member']['omso:GridSeriesObservation']
                       ['om:result']['gmlcov:MultiPointCoverage']['gmlcov:rangeType']['swe:DataRecord']
                       ['swe:field'])

    for value_type in value_types:
        result.append(value_type['@name'])

    return result


def _get_values(data: Dict[str, Any]) -> List[List[float]]:
    result = []
    value_sets = (data['wfs:FeatureCollection']['wfs:member']['omso:GridSeriesObservation']
                      ['om:result']['gmlcov:MultiPointCoverage']['gml:rangeSet']['gml:DataBlock']
                      ['gml:doubleOrNilReasonTupleList'].split('\n'))

    for forecast_value_set in value_sets:
        forecast_values = forecast_value_set.strip().split(' ')
        value_set = []
        for value in forecast_values:
            value_set.append(float(value))

        result.append(value_set)

    return result
