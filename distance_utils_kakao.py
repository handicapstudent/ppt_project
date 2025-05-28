# distance_utils_kakao.py
import requests
import math

KAKAO_REST_API_KEY = "ac9310410d0c11cfb1985ddbde806acd"

def get_coordinates_by_address(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": address}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        if result["documents"]:
            x = float(result["documents"][0]["x"])
            y = float(result["documents"][0]["y"])
            return (y, x)  # (latitude, longitude)
    return None

def haversine(coord1, coord2):
    R = 6371000  # 지구 반지름 (미터)
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # 거리 (미터)

def get_distance_text(from_address, to_address):
    from_coord = get_coordinates_by_address(from_address)
    to_coord = get_coordinates_by_address(to_address)
    if not from_coord or not to_coord:
        return "거리 정보 없음"

    dist_m = haversine(from_coord, to_coord)
    if dist_m < 1000:
        return f"{int(dist_m)}m"
    else:
        return f"{dist_m / 1000:.1f}km"
