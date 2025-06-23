from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Define a User-Agent string for api.weather.gov requests
USER_AGENT = "(myweatherapp.com, contact@myweatherapp.com)"

@app.route('/weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not lat or not lon:
        return jsonify({"error": "Missing 'lat' or 'lon' parameter"}), 400

    try:
        # Validate lat/lon format if necessary (e.g., ensure they are numbers)
        float(lat)
        float(lon)
    except ValueError:
        return jsonify({"error": "Invalid 'lat' or 'lon' parameter format"}), 400

    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    headers = {"User-Agent": USER_AGENT}

    try:
        points_response = requests.get(points_url, headers=headers, timeout=10)
        points_response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to weather.gov points API timed out"}), 504
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"weather.gov points API returned status {e.response.status_code}", "details": str(e)}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to weather.gov points API", "details": str(e)}), 500

    try:
        points_data = points_response.json()
        forecast_url = points_data['properties']['forecast']
        forecast_office_id = points_data['properties']['gridId'] # Using gridId as forecast_office
    except (KeyError, TypeError) as e:
        return jsonify({"error": "Failed to parse forecast URL or office ID from weather.gov points response", "details": str(e)}), 500

    try:
        forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_response.raise_for_status()
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to weather.gov forecast API timed out"}), 504
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"weather.gov forecast API returned status {e.response.status_code}", "details": str(e)}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not connect to weather.gov forecast API", "details": str(e)}), 500

    try:
        forecast_data = forecast_response.json()
        if not forecast_data.get('properties') or not forecast_data['properties'].get('periods') or not forecast_data['properties']['periods']:
            return jsonify({"error": "Forecast data is missing expected 'periods' structure"}), 500
        current_forecast_period = forecast_data['properties']['periods'][0]
    except (KeyError, IndexError, TypeError) as e:
        return jsonify({"error": "Failed to parse current forecast period from weather.gov forecast response", "details": str(e)}), 500

    # Construct the success JSON response
    success_response = {
        "requested_latitude": float(lat),
        "requested_longitude": float(lon),
        "forecast_office": forecast_office_id,
        "forecast_generated_at": datetime.utcnow().isoformat() + 'Z',
        "current_forecast": {
            "name": current_forecast_period.get("name"),
            "startTime": current_forecast_period.get("startTime"),
            "endTime": current_forecast_period.get("endTime"),
            "isDaytime": current_forecast_period.get("isDaytime"),
            "temperature": current_forecast_period.get("temperature"),
            "temperatureUnit": current_forecast_period.get("temperatureUnit"),
            "temperatureTrend": current_forecast_period.get("temperatureTrend"),
            "windSpeed": current_forecast_period.get("windSpeed"),
            "windDirection": current_forecast_period.get("windDirection"),
            "icon": current_forecast_period.get("icon"),
            "shortForecast": current_forecast_period.get("shortForecast"),
            "detailedForecast": current_forecast_period.get("detailedForecast")
        }
    }

    return jsonify(success_response), 200

if __name__ == '__main__':
    # Note: For production, use a WSGI server like Gunicorn or uWSGI
    app.run(host='0.0.0.0', port=5000, debug=True)
