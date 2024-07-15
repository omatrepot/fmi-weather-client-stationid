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
    time: Optional[datetime]
    temperature: Optional[Value]
    dew_point: Optional[Value] = None
    pressure: Optional[Value] = None
    humidity: Optional[Value] = None
    wind_direction: Optional[Value] = None
    wind_speed: Optional[Value] = None
    wind_u_component: Optional[Value] = None
    wind_v_component: Optional[Value] = None
    wind_max: Optional[Value] = None # Max 10 minutes average
    wind_gust: Optional[Value] = None # Max 3 seconds average
    symbol: Optional[Value] = None
    cloud_cover: Optional[Value] = None
    cloud_low_cover: Optional[Value] = None
    cloud_mid_cover: Optional[Value] = None
    cloud_high_cover: Optional[Value] = None

    # Amount of rain in the past 1h
    precipitation_amount: Optional[Value] = None

    # Short wave radiation (light, UV) accumulation
    radiation_short_wave_acc: Optional[Value] = None

    # Short wave radiation (light, UV) net accumulation on the surface
    radiation_short_wave_surface_net_acc: Optional[Value] = None

    # Long wave radiation (heat, infrared) accumulation
    radiation_long_wave_acc: Optional[Value] = None

    # Long wave radiation (light, UV) net accumulation on the surface
    radiation_long_wave_surface_net_acc: Optional[Value] = None

    # Diffused short wave
    radiation_short_wave_diff_surface_acc: Optional[Value] = None

    geopotential_height: Optional[Value] = None
    land_sea_mask: Optional[Value] = None

    # Calculated "feels like" temperature
    feels_like: Optional[Value] = None

class Weather(NamedTuple):
    """Represents a weather"""
    place: str
    id: int
    lat: float
    lon: float
    data_updated_time: datetime
    data: WeatherData

class Forecast(NamedTuple):
    """Represents weather forecast at a station"""
    place: str
    id: int
    data: float
    lon: float
    data_updated_time: datetime
    forecasts: List[WeatherData]
    #forecasts: WeatherData

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Forecast':
        
        print(data)

        return cls(
            id=data.get('id', 0),
            data_updated_time=datetime.fromisoformat(data.get('dataUpdatedTime', '')),
            forecasts=WeatherData.from_json(data)
        )