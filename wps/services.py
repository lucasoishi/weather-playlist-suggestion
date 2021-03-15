import abc
import base64
import logging
from typing import Dict, List, Union

import requests
import settings
import unidecode
from exceptions import InvalidLocation, NoContentFound, RequestLimitExceeded
from models import CityInformation, GeoPosition, Recommendation

logger = logging.getLogger()


class WeatherAPI(abc.ABC):
    @abc.abstractmethod
    def get_location_weather(self, params: Dict[str, str]) -> Dict:
        pass

    @abc.abstractmethod
    def get_location_temperature(
        self, location: Union[CityInformation, GeoPosition]
    ) -> float:
        pass


class OpenWeatherAPI(WeatherAPI):
    def __init__(self) -> None:
        self.url = 'https://api.openweathermap.org/data/2.5/weather'
        self.api_key = settings.OPENWEATHER_API_KEY

    def get_location_weather(self, params: Dict[str, str]) -> Dict:
        headers = {'Accept': 'application/json'}
        params.update({'appid': self.api_key, 'units': 'metric'})
        response = requests.get(self.url, params=params, headers=headers)
        if (
            response.status_code == 404
            and response.json().get('message') == 'city not found'
        ):
            raise InvalidLocation(
                f"Couldn't retrieve location weather. {response.text}"
            )
        if response.status_code == 429:
            raise RequestLimitExceeded(
                'Service temporarily unavailable, try again in a few minutes'
            )
        if response.status_code != 200:
            raise requests.exceptions.RequestException(response.text)
        return response.json()

    def get_location_temperature(
        self, location: Union[GeoPosition, CityInformation]
    ) -> float:
        if isinstance(location, CityInformation):
            str_location = ','.join(
                [
                    location.city.lower(),
                    location.state.lower(),
                    location.country.lower(),
                ]
            )
            str_location = unidecode.unidecode(str_location)
            params = {'q': str_location}
        else:
            params = {
                'lat': str(location.latitude),
                'lon': str(location.longitude),
            }
        weather_data = self.get_location_weather(params)
        return weather_data['main']['temp']


def get_weather_api() -> WeatherAPI:
    return OpenWeatherAPI()


class PlaylistRecommendationAPI(abc.ABC):
    @abc.abstractmethod
    def get_recommendations(
        self, genres: Union[List[str], str]
    ) -> List[Recommendation]:
        pass


class SpotifyAPI(PlaylistRecommendationAPI):
    def __init__(self) -> None:
        self.headers = {'Authorization': f'Bearer {self._get_access_token()}'}
        self.recommendation_limit = '5'
        self.base_url = 'https://api.spotify.com/v1'

    @staticmethod
    def _get_access_token() -> str:
        client_id = settings.SPOTIFY_CLIENT_ID
        client_secret = settings.SPOTIFY_CLIENT_SECRET
        b64_client = base64.b64encode(
            f'{client_id}:{client_secret}'.encode()
        ).decode()
        headers = {
            'Authorization': f'Basic {b64_client}',
            'Accept': 'application/json',
        }
        data = {'grant_type': 'client_credentials'}
        url = 'https://accounts.spotify.com/api/token'
        response = requests.post(url, data=data, headers=headers, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(response.text)
        access_token = response.json().get('access_token')
        return access_token

    @staticmethod
    def _format_recommendation_response(
        response: dict,
    ) -> List[Recommendation]:
        if not response or not response.get('tracks'):
            raise NoContentFound(
                f'Invalid or missing content in response {response}'
            )
        formatted_data = []
        recommendations = response['tracks']
        for recommendation in recommendations:
            formatted_data.append(
                Recommendation(
                    **{
                        'playlist': recommendation['album']['name'],
                        'url': recommendation['external_urls']['spotify'],
                        'artists': [
                            artist['name']
                            for artist in recommendation['artists']
                        ],
                        'total_tracks': round(
                            recommendation['album']['total_tracks']
                        ),
                        'duration_seconds': round(
                            recommendation['duration_ms'] / 60, 2
                        ),
                    }
                )
            )
        return formatted_data

    def get_recommendations(
        self, genres: Union[List[str], str]
    ) -> List[Recommendation]:
        url = self.base_url + '/recommendations'
        if isinstance(genres, list):
            genres = str(genres).replace(' ', '')[1:-1]
        params = {
            'limit': self.recommendation_limit,
            'seed_genres': genres,
        }
        response = requests.get(
            url, params=params, headers=self.headers, timeout=30
        )
        if response.status_code != 200:
            raise requests.exceptions.RequestException(response.text)
        return self._format_recommendation_response(response.json())


def get_playlist_api() -> PlaylistRecommendationAPI:
    return SpotifyAPI()


def get_genre(temperature: float) -> str:
    if temperature > 30:
        return 'party'
    if temperature > 14:
        return 'pop'
    if temperature > 10:
        return 'rock'
    return 'classical'


def get_playlists_recommendations(
    location: Union[CityInformation, GeoPosition]
) -> List[Recommendation]:
    weather_api = get_weather_api()
    playlist_api = get_playlist_api()
    logger.info(f'Using location {location}')
    location_temperature = weather_api.get_location_temperature(location)
    logger.info(
        f'Current temperature for {location} is {location_temperature}ºC'
    )
    genre = get_genre(location_temperature)
    logger.info(f'Using {genre} as genreseed for recommendations api')
    recommendations = playlist_api.get_recommendations(genre)
    logger.info('Recommendations retrieved successfully')
    return recommendations
