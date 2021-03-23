import logging
from typing import Any, List

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from models import CityInformation, GeoPosition, Recommendation
from services import get_playlists_recommendations
from starlette.status import HTTP_400_BAD_REQUEST

app = FastAPI()
logger = logging.getLogger()


@app.get("/", include_in_schema=False)
def root() -> Any:
    return RedirectResponse(url="/docs")


@app.get("/recommendation/city/", response_model=List[Recommendation])
def recommendation_city_name(
    city: str = Query(..., description='City name'),
    state: str = Query(..., description='State code', max_length=2),
    country: str = Query(
        ..., description='Country code - ISO 3166', max_length=2
    ),
) -> Any:
    """
    Provide the city name, state code and country code (according to
    ISO 3166) to get playlist recommendations based on that place's
    current temperature.
    """
    location = CityInformation(city=city, state=state, country=country)
    try:
        recommendations = get_playlists_recommendations(location)
        return recommendations
    except Exception as error:
        logger.exception('')
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=str(error)
        ) from None


@app.get("/recommendation/geoposition/", response_model=List[Recommendation])
def recommendation_geoposition(
    latitude: float = Query(None, title='Query String'),
    longitude: float = Query(None, title='Query String'),
) -> Any:
    """
    Provide geoposition (latitute and longitude) of a place to get
    playlist recommendations based on that place's current temperature
    """
    location = GeoPosition(latitude=latitude, longitude=longitude)
    try:
        recommendation = get_playlists_recommendations(location)
        return recommendation
    except Exception as error:
        logger.exception('')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from None
