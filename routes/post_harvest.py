from flask import Blueprint, request, jsonify
from services.agro_shops_service import get_nearby_agro_shops, get_nearby_shops_by_type
from services.markets_service import get_nearby_markets
from services.storage_service import get_nearby_cold_storage

post_harvest_bp = Blueprint("post_harvest", __name__, url_prefix='/post-harvest')


# ============================================================
#  AGRO SHOPS — returns BOTH govt & organic for client filter
# ============================================================
@post_harvest_bp.route("/agro-shops", methods=["POST"])
def agro_shops():
    """Get all nearby agro shops (government + organic) for client-side filtering."""
    data = request.json

    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "latitude and longitude are required"}), 400

    try:
        latitude  = float(data["latitude"])
        longitude = float(data["longitude"])
        radius    = float(data.get("radius", 20))

        result = get_nearby_agro_shops(latitude, longitude, radius)
        return jsonify(result), 200

    except ValueError:
        return jsonify({"error": "Invalid coordinate values"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
#  AGRO SHOPS BY TYPE — server-side filter (optional endpoint)
# ============================================================
@post_harvest_bp.route("/agro-shops/by-type", methods=["POST"])
def agro_shops_by_type():
    """
    Get nearby agro shops filtered by type.
    Body: { latitude, longitude, radius, shop_type: 'organic' | 'chemical' | 'all' }
    """
    data = request.json

    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "latitude and longitude are required"}), 400

    try:
        latitude  = float(data["latitude"])
        longitude = float(data["longitude"])
        radius    = float(data.get("radius", 20))
        shop_type = data.get("shop_type")  # 'organic', 'chemical', or None/'all'

        result = get_nearby_shops_by_type(latitude, longitude, radius, shop_type)
        return jsonify(result), 200

    except ValueError:
        return jsonify({"error": "Invalid coordinate values"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
#  MARKETS
# ============================================================
@post_harvest_bp.route("/markets", methods=["POST"])
def markets():
    """Get nearby markets."""
    data = request.json

    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "latitude and longitude are required"}), 400

    try:
        latitude  = float(data["latitude"])
        longitude = float(data["longitude"])
        radius    = float(data.get("radius", 20))

        result = get_nearby_markets(latitude, longitude, radius)
        return jsonify(result), 200

    except ValueError:
        return jsonify({"error": "Invalid coordinate values"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
#  COLD STORAGE
# ============================================================
@post_harvest_bp.route("/storage", methods=["POST"])
def storage():
    """Get nearby cold storage facilities."""
    data = request.json

    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "latitude and longitude are required"}), 400

    try:
        latitude  = float(data["latitude"])
        longitude = float(data["longitude"])
        radius    = float(data.get("radius", 20))

        result = get_nearby_cold_storage(latitude, longitude, radius)
        return jsonify(result), 200

    except ValueError:
        return jsonify({"error": "Invalid coordinate values"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500