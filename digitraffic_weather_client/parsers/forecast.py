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

#def parse_forecast(json_data: str):
#    data = json.loads(json_data)
#    sensor_values = {entry['shortName']: entry for entry in data['sensorValues']}


#    return Forecast(station.name, station.lat, station.lon, forecasts)
    #return weather_data

# Helper functions to extract data from JSON structure

