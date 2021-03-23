from typing import List

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    playlist: str = "A Playlist"
    artists: List[str] = ['An Artist']
    url: str = 'https://open.spotify.com/track/7GhIk7Il098yCjg4BQjzvb'
    total_tracks: int = 10
    duration_seconds: float = 4300.5


class CityInformation(BaseModel):
    city: str
    state: str = Field(..., max_length=2, strip_whitespace=True)
    country: str = Field(..., max_length=2, strip_whitespace=True)


class GeoPosition(BaseModel):
    latitude: float
    longitude: float
