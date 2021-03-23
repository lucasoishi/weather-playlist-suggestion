from unittest.mock import patch

import pytest
import services
from exceptions import InvalidLocation, NoContentFound, RequestLimitExceeded
from models import CityInformation, GeoPosition
from requests.exceptions import RequestException


def test_get_playlist_api(post_mock, spotify_token_success_response):
    post_mock.return_value = spotify_token_success_response
    api = services.get_playlist_api()
    assert isinstance(api, services.PlaylistRecommendationAPI)
    assert isinstance(api, services.SpotifyAPI)


def test_get_weather_api():
    api = services.get_weather_api()
    assert isinstance(api, services.WeatherAPI)
    assert isinstance(api, services.OpenWeatherAPI)


class TestOpenWeatherAPI:
    @staticmethod
    def test_get_location_weather(ow_api, get_mock, ow_success_response):
        params = {'q': 'sao paulo,sp,br'}
        get_mock.return_value = ow_success_response
        data = ow_api.get_location_weather(params)
        assert ow_success_response.json() == data
        params = {'lat': 25, 'lon': 22}
        get_mock.return_value = ow_success_response
        data = ow_api.get_location_weather(params)
        assert ow_success_response.json() == data

    @staticmethod
    def test_get_weather_invalid_location(
        ow_api, get_mock, ow_location_fail_response
    ):
        params = {'q': 'fail'}
        get_mock.return_value = ow_location_fail_response
        with pytest.raises(InvalidLocation):
            ow_api.get_location_weather(params)

    @staticmethod
    def test_get_weather_exceeded_requests(
        ow_api, get_mock, ow_requests_exceeded
    ):
        get_mock.return_value = ow_requests_exceeded
        with pytest.raises(RequestLimitExceeded):
            ow_api.get_location_weather({})

    @staticmethod
    def test_get_weather_generic_failure(
        ow_api, get_mock, ow_generic_failure_response
    ):
        get_mock.return_value = ow_generic_failure_response
        with pytest.raises(RequestException):
            ow_api.get_location_weather({})

    @staticmethod
    def test_get_location_temperature(ow_api, get_mock, ow_success_response):
        location = CityInformation(
            **{'city': 'sao paulo', 'state': 'sp', 'country': 'br'}
        )
        get_mock.return_value = ow_success_response
        data = ow_api.get_location_temperature(location)
        temp = ow_success_response.json()['main']['temp']
        assert temp == data
        params = GeoPosition(**{'latitude': 25, 'longitude': 22})
        get_mock.return_value = ow_success_response
        data = ow_api.get_location_temperature(params)
        assert temp == data


class TestSpotifyAPI:
    @staticmethod
    def test_get_auth_token(post_mock, spotify_token_success_response):
        expected = spotify_token_success_response.json()['access_token']
        post_mock.return_value = spotify_token_success_response
        token = services.SpotifyAPI._get_access_token()
        assert token == expected

    @staticmethod
    def test_get_auth_token_error(post_mock, spotify_token_fail_response):
        post_mock.return_value = spotify_token_fail_response
        with pytest.raises(RequestException):
            services.SpotifyAPI._get_access_token()

    @staticmethod
    def test_format_recommendation_response_success(
        spotify_valid_recommendation_response,
        recommendations,
    ):
        expected = recommendations
        output = services.SpotifyAPI._format_recommendation_response(
            spotify_valid_recommendation_response
        )
        assert expected == output

    @staticmethod
    def test_format_recommendation_response_fail():
        with pytest.raises(NoContentFound):
            services.SpotifyAPI._format_recommendation_response({'tracks': []})


@pytest.mark.parametrize(
    'temperature,expected',
    [(35, 'party'), (16, 'pop'), (11, 'rock'), (-152, 'classical')],
)
def test_get_genre(temperature, expected):
    output = services.get_genre(temperature)
    assert expected == output


@patch(
    'services.SpotifyAPI._get_access_token',
    return_value='token',
)
@patch('services.OpenWeatherAPI.get_location_temperature', return_value=13)
@patch('services.SpotifyAPI.get_recommendations')
@pytest.mark.parametrize(
    'location',
    [
        (),
        (
            CityInformation(
                **{'city': 'Sao Paulo', 'state': 'SP', 'country': 'BR'}
            )
        ),
    ],
)
def test_get_playlists_recommendations_success(
    spotify_recommendations, _temp, _token, location, recommendations
):
    spotify_recommendations.return_value = recommendations
    output = services.get_playlists_recommendations(location)
    return output == recommendations
