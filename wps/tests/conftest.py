from json import dumps
from unittest import mock

import pytest
from models import Recommendation
from services import OpenWeatherAPI, SpotifyAPI


class ResponseMock:
    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response
        self.text = dumps(response)

    def json(
        self,
    ):
        return self.response


@pytest.fixture
def ow_api():
    return OpenWeatherAPI()


@pytest.fixture
def get_mock():
    with mock.patch('services.requests.get') as requests_mock:
        yield requests_mock


@pytest.fixture
def post_mock():
    with mock.patch('services.requests.post') as requests_mock:
        yield requests_mock


@pytest.fixture
def ow_success_response():
    response = {'main': {'temp': 28.58}}
    return ResponseMock(200, response)


@pytest.fixture
def ow_location_fail_response():
    response = {'cod': '404', 'message': 'city not found'}
    return ResponseMock(404, response)


@pytest.fixture
def ow_generic_failure_response():
    response = {'cod': '400', 'message': 'Nothing to geocode'}
    return ResponseMock(400, response)


@pytest.fixture
def ow_requests_exceeded():
    response = {
        'cod': '429',
        'message': (
            'Your account is temporary blocked due to exceeding of requests '
            'limitation of your subscription type. Please choose the proper '
            'subscription http://openweathermap.org/price'
        ),
    }
    return ResponseMock(429, response)


@pytest.fixture
def spotify_api():
    return SpotifyAPI()


@pytest.fixture
def spotify_token_success_response():
    response = {'access_token': 'token'}
    return ResponseMock(200, response)


@pytest.fixture
def spotify_token_fail_response():
    response = {'error': 'invalid_client'}
    return ResponseMock(400, response)


@pytest.fixture
def spotify_valid_recommendation_response():
    return {
        'tracks': [
            {
                'album': {'name': 'album name', 'total_tracks': 11},
                'external_urls': {
                    'spotify': 'https://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb'
                },
                'artists': [{'name': 'artist_1'}, {'name': 'artist_2'}],
                'duration_ms': 11700,
            }
            for _ in range(2)
        ]
    }


@pytest.fixture
def recommendations():
    return [
        Recommendation(
            **{
                'playlist': 'album name',
                'url': 'https://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb',
                'artists': ['artist_1', 'artist_2'],
                'total_tracks': 11,
                'duration_seconds': round(11700 / 60, 2),
            }
        )
        for _ in range(2)
    ]
