import json
import os
from utils.distance import haversine_distance


def load_govt_shops():
    current_dir = os.path.dirname(__file__)
    data_path = os.path.join(current_dir, '..', 'data', 'govt_agro_shops.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('shops', [])


def load_organic_shops():
    current_dir = os.path.dirname(__file__)
    data_path = os.path.join(current_dir, '..', 'data', 'organic_shops.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('shops', [])


def calculate_and_filter_shops(shops, latitude, longitude, radius):
    nearby = []
    for shop in shops:
        try:
            shop_lat = float(shop['latitude'])
            shop_lon = float(shop['longitude'])
            distance = haversine_distance(latitude, longitude, shop_lat, shop_lon)
            if distance <= radius:
                shop_copy = shop.copy()
                shop_copy['distance_km'] = round(distance, 2)
                nearby.append(shop_copy)
        except (KeyError, ValueError, TypeError) as e:
            print(f"[SHOP PROCESS ERROR]: {e}")
            continue
    nearby.sort(key=lambda x: x['distance_km'])
    return nearby


def get_nearby_agro_shops(latitude, longitude, radius=20):
    """Returns both government (chemical) and organic shops."""
    govt    = load_govt_shops()
    organic = load_organic_shops()
    return {
        "government_shops": calculate_and_filter_shops(govt,    latitude, longitude, radius),
        "organic_shops":    calculate_and_filter_shops(organic, latitude, longitude, radius)
    }


def get_nearby_shops_by_type(latitude, longitude, radius=20, shop_type=None):
    """
    Filter by type:
      shop_type = 'organic'   -> only organic shops
      shop_type = 'chemical'  -> only government/chemical shops
      shop_type = None / 'all'-> both
    """
    govt    = load_govt_shops()
    organic = load_organic_shops()

    if shop_type == 'organic':
        shops = calculate_and_filter_shops(organic, latitude, longitude, radius)
        return {"type": "organic", "count": len(shops), "shops": shops}

    elif shop_type == 'chemical':
        shops = calculate_and_filter_shops(govt, latitude, longitude, radius)
        return {"type": "chemical", "count": len(shops), "shops": shops}

    else:
        # Return both separately so frontend can filter client-side
        return get_nearby_agro_shops(latitude, longitude, radius)