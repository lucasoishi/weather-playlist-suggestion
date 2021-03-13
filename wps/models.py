from typing import List

from pydantic import BaseModel


class Recommendation(BaseModel):
    playlist: str = "A Playlist"
    artists: List[str] = ['An Artist']
    url: str = 'https://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb'
    total_tracks: int = 10
    duration_seconds: float = 4300.5


class CityInformation(BaseModel):
    city: str
    state: str
    country: str


class Coordinates(BaseModel):
    latitude: float
    longitude: float
