from datetime import datetime
from typing import List, Optional, NamedTuple, Dict, Any, Union


class FMIPlace(NamedTuple):
    """Represent a place in FMI response"""
    name: str
    lat: float
    lon: float

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lon})"


class Value(NamedTuple):
    """Represents a sensor value"""
    value: Optional[Union[float, int]]
    unit: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Value':
        return cls(
            value=data.get('value'),
            unit=data.get('unit', '')
        )

    def __str__(self):
        return f"{self.value} {self.unit}" if self.value is not None else "-"

class SensorValue(NamedTuple):
    """Represents a sensor value entry"""
    id: int
    station_id: int
    name: str
    short_name: str
    measured_time: datetime
    value: Value

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'SensorValue':
        return cls(
            id=data.get('id', 0),
            station_id=data.get('stationId', 0),
            name=data.get('name', ''),
            short_name=data.get('shortName', ''),
            measured_time=datetime.fromisoformat(data.get('measuredTime', '')),
            value=Value.from_json(data)
        )


class WeatherData(NamedTuple):
    """Represents a weather"""
    time: datetime
    temperature: Value
    dew_point: Value
    pressure: Value
    humidity: Value
    wind_direction: Value
    wind_speed: Value
    wind_u_component: Value
    wind_v_component: Value
    wind_max: Value  # Max 10 minutes average
    wind_gust: Value  # Max 3 seconds average
    symbol: Value
    cloud_cover: Value
    cloud_low_cover: Value
    cloud_mid_cover: Value
    cloud_high_cover: Value

    # Amount of rain in the past 1h
    precipitation_amount: Value

    # Short wave radiation (light, UV) accumulation
    radiation_short_wave_acc: Value

    # Short wave radiation (light, UV) net accumulation on the surface
    radiation_short_wave_surface_net_acc: Value

    # Long wave radiation (heat, infrared) accumulation
    radiation_long_wave_acc: Value

    # Long wave radiation (light, UV) net accumulation on the surface
    radiation_long_wave_surface_net_acc: Value

    # Diffused short wave
    radiation_short_wave_diff_surface_acc: Value

    geopotential_height: Value
    land_sea_mask: Value

    # Calculated "feels like" temperature
    feels_like: Value

class Weather(NamedTuple):
    """Represents a weather"""
    place: str
    lat: float
    lon: float
    data: WeatherData

class Forecast(NamedTuple):
    """Represents weather forecast at a station"""
    id: int
    data_updated_time: datetime
    weather_data: WeatherData

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Forecast':
        
        print(data)

        return cls(
            id=data.get('id', 0),
            data_updated_time=datetime.fromisoformat(data.get('dataUpdatedTime', '')),
            weather_data=WeatherData.from_json(data)
        )