import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional

import requests
import xmltodict

from digitraffic_weather_client.errors import ClientError, ServerError

_LOGGER = logging.getLogger(__name__)


class RequestType(Enum):
    """Possible request types"""
    WEATHER = 0
    STATION = 1

def request_information_by_station_id(station_id: int) -> str:
    """
    Get the latest weather information by coordinates.

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :return: Latest weather information
    """
    params = _create_params(10, stationid=station_id)

    return _send_request(RequestType.STATION,params)


def request_weather_by_station_id(station_id: int) -> str:
    """
    Get the latest weather information by coordinates.

    :param lat: Latitude (e.g. 25.67087)
    :param lon: Longitude (e.g. 62.39758)
    :return: Latest weather information
    """
    params = _create_params(10, stationid=station_id)

    return _send_request(RequestType.WEATHER,params)


def _create_params(timestep_minutes: int,
                   stationid: int)-> Dict[str, Any]:
    """
    Create query parameters
    :param timestep_minutes: Timestamp minutes
    :param place: Place name
    :param lat: Latitude
    :param lon: Longitude
    :param stationid: Station id
    :return: Parameters
    """

    if (stationid is None):
        raise ValueError("Missing location parameter")

    #if request_type is RequestType.WEATHER:
    #    end_time = datetime.now.replace(tzinfo=timezone.utc)
    #    start_time = end_time - timedelta(minutes=10)
    #elif request_type is RequestType.FORECAST:
    #    start_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    #    end_time = start_time + timedelta(days=4)
    #else:
    #    raise ValueError(f"Invalid request_type {request_type}")

    params = {  
        #'Digitraffic-User': 'Junamies/FoobarApp 1.0' # Choose descriptive name, eg. your organisation and append it with your nickname (not real name)
        #'service': 'WFS',
        #'version': '2.0.0',
        #'request': 'getFeature',
        #'storedquery_id': 'fmi::forecast::harmonie::surface::point::multipointcoverage',
        #'timestep': timestep_minutes,
        #'starttime': start_time.isoformat(timespec='seconds'),
        #'endtime': end_time.isoformat(timespec='seconds'),
        #'parameters': (
        #    'Temperature,DewPoint,Pressure,Humidity,WindDirection,WindSpeedMS,'
        #    'WindUMS,WindVMS,WindGust,WeatherSymbol3,TotalCloudCover,LowCloudCover,'
        #    'MediumCloudCover,HighCloudCover,Precipitation1h,RadiationGlobalAccumulation,'
        #    'RadiationNetSurfaceSWAccumulation,RadiationNetSurfaceLWAccumulation,GeopHeight,LandSeaMask'
        #)
    }

    #if lat is not None and lon is not None and stationid is None:
    #    params['latlon'] = f'{lat},{lon}'

    #if place is not None and stationid is None:
    #    params['place'] = place.strip().replace(' ', '')

    #if stationid is not None:
    #    params['fmisid'] = f'{stationid}'

    return params

def _send_request(request_type: RequestType,
                  params: Dict[str, Any]) -> str:
    """
    Send a request to FMI service and return the body
    :param params: Query parameters
    :return: Response body
    """

    #$tiesaa_id = '14028'; # Find id from https://tie.digitraffic.fi/api/weather/v1/stations/


    if request_type is RequestType.WEATHER:
        url ='https://tie.digitraffic.fi/api/weather/v1/stations/14028/data'
    else:
        url ='https://tie.digitraffic.fi/api/weather/v1/stations/14028'

    #url = 'https://tie.digitraffic.fi/api/tms/v1/sensors'
    #url ='https://tie.digitraffic.fi/api/weather/v1/stations/14028/data'

    #print(params)

    _LOGGER.debug("GET request to %s. Parameters: %s", url, params)
    response = requests.get(url, params=params, timeout=10)

    #print(response.text)

    if response.status_code == 200:
        _LOGGER.debug("GET response from %s in %d ms. Status: %d.",
                      url,
                      response.elapsed.microseconds / 1000,
                      response.status_code)
    else:
        _handle_errors(response)

    return response.text



def _handle_errors(response: requests.Response):
    """Handle error responses from FMI service"""
    if 400 <= response.status_code < 500:
        data = xmltodict.parse(response.text)
        try:
            error_message = data['ExceptionReport']['Exception']['ExceptionText'][0]
            raise ClientError(response.status_code, error_message)
        except (KeyError, IndexError) as err:
            raise ClientError(response.status_code, response.text) from err

    raise ServerError(response.status_code, response.text)
