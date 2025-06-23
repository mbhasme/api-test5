# Python Weather Service for api.weather.gov

This is a simple Python web service built with Flask that fetches weather forecast data from the U.S. National Weather Service API (`api.weather.gov`).

## Features

-   Accepts latitude and longitude as input.
-   Queries `api.weather.gov` to get the relevant forecast grid.
-   Fetches the latest forecast for the specified location.
-   Returns a JSON response containing details of the current or next upcoming forecast period.

## Prerequisites

-   Python 3.7+
-   Flask (`pip install Flask`)
-   Requests (`pip install requests`)

## Setup and Installation

1.  **Clone the repository (if applicable) or ensure `weather_service.py` is in your project directory.**

2.  **Install dependencies:**
    Open your terminal and navigate to the project directory. It's recommended to use a virtual environment.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install Flask requests
    ```

## Running the Service

To start the Flask development server:

```bash
python weather_service.py
```

The service will typically start on `http://127.0.0.1:5000/` (or `http://0.0.0.0:5000/` as configured in the script).

## API Documentation

### Endpoint: `/weather`

-   **Method:** `GET`
-   **Description:** Retrieves the weather forecast for a given latitude and longitude.

#### Request Parameters (Query String)

-   `lat` (float, required): The latitude for the desired forecast location.
-   `lon` (float, required): The longitude for the desired forecast location.

**Example Request:**
`GET /weather?lat=39.7456&lon=-97.0892`

#### Success Response (200 OK)

The service returns a JSON object with the following structure:

```json
{
  "requested_latitude": 39.7456,
  "requested_longitude": -97.0892,
  "forecast_office": "TOP",
  "forecast_generated_at": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
  "current_forecast": {
    "period_name": "Tonight",
    "start_time": "YYYY-MM-DDTHH:MM:SSZ",
    "end_time": "YYYY-MM-DDTHH:MM:SSZ",
    "is_daytime": false,
    "temperature": 55,
    "temperature_unit": "F",
    "wind_speed": "5 to 10 mph",
    "wind_direction": "S",
    "icon": "https://api.weather.gov/icons/land/night/sct?size=medium",
    "short_forecast": "Mostly Clear",
    "detailed_forecast": "Mostly clear, with a low around 55. South wind 5 to 10 mph."
  }
}
```

#### Error Responses

-   **400 Bad Request:** If `lat` or `lon` parameters are missing or invalid.
    ```json
    {
      "error": "Missing or invalid 'lat' or 'lon' query parameters."
    }
    ```
-   **500 Internal Server Error:** If there's an issue fetching data from `api.weather.gov` or an unexpected server error occurs.
    ```json
    {
      "error": "Failed to process request",
      "details": "Specific error message from the server or external API."
    }
    ```
-   **502 Bad Gateway:** If `api.weather.gov` returns an error.
    ```json
    {
      "error": "Bad Gateway to api.weather.gov",
      "details": "Received status X from api.weather.gov/points or /forecast"
    }
    ```
-   **504 Gateway Timeout:** If a request to `api.weather.gov` times out.
    ```json
    {
      "error": "Gateway Timeout",
      "details": "Request to api.weather.gov timed out."
    }
    ```

## Development Notes

-   The service uses a `User-Agent` string `(myweatherapp.com, contact@myweatherapp.com)` for requests to `api.weather.gov` as per their API guidelines.
-   Error handling is included for common issues like missing parameters, external API failures, and parsing problems.
```
