import httpx
from core.config import settings
from core.errors import ErrorCodes, raise_error


async def fetch_kakao_routes(start_lat, start_lon, end_lat, end_lon):
    url = "https://apis-navi.kakaomobility.com/v1/directions"

    headers = {
        "Authorization": f"KakaoAK {settings.KAKAO_API_KEY}"
    }

    params = {
        "origin": f"{start_lon},{start_lat}",
        "destination": f"{end_lon},{end_lat}",
        "alternatives": "true"
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, params=params)
            res.raise_for_status()
            return res.json()

    except Exception:
        raise_error(ErrorCodes.SERVER_ERROR)
