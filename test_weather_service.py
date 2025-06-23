import unittest
from unittest.mock import patch, Mock
import json
import requests # Required for requests.exceptions.RequestException

# Assuming weather_service.py is in the same directory or accessible via PYTHONPATH
from weather_service import app

class TestWeatherService(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        # Ensure USER_AGENT is defined in weather_service, otherwise mock it if necessary
        # For example: patch('weather_service.USER_AGENT', 'TestAgent/1.0').start()
        # and self.addCleanup(patch.stopall) if you start it here.

    @patch('weather_service.requests.get')
    def test_get_weather_success(self, mock_get):
        # Configure mock for the first call (/points)
        mock_points_response = Mock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            'properties': {
                'gridId': 'TESTOFFICE',
                'forecast': 'https://api.weather.gov/gridpoints/TESTOFFICE/1,1/forecast'
            }
        }

        # Configure mock for the second call (/forecast)
        mock_forecast_response = Mock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {
            'properties': {
                'periods': [{
                    'name': 'Today',
                    'temperature': 70,
                    'temperatureUnit': 'F',
                    'shortForecast': 'Sunny',
                    'detailedForecast': 'Very sunny.',
                    'windSpeed': '5 mph',
                    'windDirection': 'N',
                    'icon': 'test_icon_url',
                    'startTime': 'test_start',
                    'endTime': 'test_end',
                    'isDaytime': True,
                    'temperatureTrend': None # Added to match typical structure
                }]
            }
        }

        mock_get.side_effect = [mock_points_response, mock_forecast_response]

        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['forecast_office'], 'TESTOFFICE')
        self.assertEqual(data['requested_latitude'], 12.34)
        self.assertEqual(data['requested_longitude'], 56.78)
        self.assertIn('forecast_generated_at', data)

        current_forecast = data['current_forecast']
        self.assertEqual(current_forecast['name'], 'Today')
        self.assertEqual(current_forecast['temperature'], 70)
        self.assertEqual(current_forecast['temperatureUnit'], 'F')
        self.assertEqual(current_forecast['shortForecast'], 'Sunny')
        self.assertEqual(current_forecast['detailedForecast'], 'Very sunny.')
        self.assertEqual(current_forecast['windSpeed'], '5 mph')
        self.assertEqual(current_forecast['windDirection'], 'N')
        self.assertEqual(current_forecast['icon'], 'test_icon_url')
        self.assertEqual(current_forecast['startTime'], 'test_start')
        self.assertEqual(current_forecast['endTime'], 'test_end')
        self.assertEqual(current_forecast['isDaytime'], True)

        self.assertEqual(mock_get.call_count, 2)
        # Check User-Agent header (optional, but good practice)
        expected_headers = {'User-Agent': app.config.get('USER_AGENT', '(myweatherapp.com, contact@myweatherapp.com)')}
        mock_get.assert_any_call('https://api.weather.gov/points/12.34,56.78', headers=expected_headers, timeout=10)
        mock_get.assert_any_call('https://api.weather.gov/gridpoints/TESTOFFICE/1,1/forecast', headers=expected_headers, timeout=10)


    def test_get_weather_missing_lat(self):
        response = self.client.get('/weather?lon=56.78')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        # The error message in the actual code is "Missing 'lat' or 'lon' parameter"
        # Or, if validation is more specific: "Invalid 'lat' or 'lon' parameter format"
        self.assertEqual(data['error'], "Missing 'lat' or 'lon' parameter")

    def test_get_weather_missing_lon(self):
        response = self.client.get('/weather?lat=12.34')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Missing 'lat' or 'lon' parameter")

    def test_get_weather_invalid_lat_lon_format(self):
        response = self.client.get('/weather?lat=abc&lon=xyz')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Invalid 'lat' or 'lon' parameter format")

    @patch('weather_service.requests.get')
    def test_get_weather_points_api_failure(self, mock_get):
        mock_points_response = Mock()
        mock_points_response.status_code = 500
        mock_points_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_points_response)
        mock_get.return_value = mock_points_response

        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 502) # As per weather_service.py logic for HTTPError
        data = json.loads(response.data)
        self.assertIn("weather.gov points API returned status 500", data['error'])

    @patch('weather_service.requests.get')
    def test_get_weather_forecast_api_failure(self, mock_get):
        mock_points_response = Mock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            'properties': {
                'gridId': 'TESTOFFICE',
                'forecast': 'https://api.weather.gov/gridpoints/TESTOFFICE/1,1/forecast'
            }
        }

        mock_forecast_response = Mock()
        mock_forecast_response.status_code = 500
        mock_forecast_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_forecast_response)

        mock_get.side_effect = [mock_points_response, mock_forecast_response]

        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 502) # As per weather_service.py logic for HTTPError
        data = json.loads(response.data)
        self.assertIn("weather.gov forecast API returned status 500", data['error'])

    @patch('weather_service.requests.get', side_effect=requests.exceptions.RequestException("Test connection error"))
    def test_get_weather_points_request_exception(self, mock_get):
        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        # The actual error message in weather_service.py includes the detail from the exception
        self.assertEqual(data['error'], "Could not connect to weather.gov points API")
        self.assertEqual(data['details'], "Test connection error")

    @patch('weather_service.requests.get')
    def test_get_weather_forecast_request_exception(self, mock_get):
        mock_points_response = Mock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            'properties': {
                'gridId': 'TESTOFFICE',
                'forecast': 'https://api.weather.gov/gridpoints/TESTOFFICE/1,1/forecast'
            }
        }
        # First call is successful, second call raises RequestException
        mock_get.side_effect = [
            mock_points_response,
            requests.exceptions.RequestException("Test connection error forecast")
        ]

        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Could not connect to weather.gov forecast API")
        self.assertEqual(data['details'], "Test connection error forecast")

    @patch('weather_service.requests.get')
    def test_get_weather_points_api_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Points API timed out")
        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 504)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Request to weather.gov points API timed out")

    @patch('weather_service.requests.get')
    def test_get_weather_forecast_api_timeout(self, mock_get):
        mock_points_response = Mock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            'properties': {
                'gridId': 'TESTOFFICE',
                'forecast': 'https://api.weather.gov/gridpoints/TESTOFFICE/1,1/forecast'
            }
        }
        mock_get.side_effect = [
            mock_points_response,
            requests.exceptions.Timeout("Forecast API timed out")
        ]
        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 504)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Request to weather.gov forecast API timed out")

    @patch('weather_service.requests.get')
    def test_get_weather_points_parsing_keyerror(self, mock_get):
        mock_points_response = Mock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {'properties': {}} # Missing 'forecast' or 'gridId'
        mock_get.return_value = mock_points_response

        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("Failed to parse forecast URL or office ID", data['error'])

    @patch('weather_service.requests.get')
    def test_get_weather_forecast_parsing_keyerror(self, mock_get):
        mock_points_response = Mock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            'properties': {
                'gridId': 'TESTOFFICE',
                'forecast': 'https://api.weather.gov/gridpoints/TESTOFFICE/1,1/forecast'
            }
        }
        mock_forecast_response = Mock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {'properties': {}} # Missing 'periods'

        mock_get.side_effect = [mock_points_response, mock_forecast_response]

        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("Forecast data is missing expected 'periods' structure", data['error'])

    @patch('weather_service.requests.get')
    def test_get_weather_forecast_parsing_indexerror(self, mock_get):
        mock_points_response = Mock()
        mock_points_response.status_code = 200
        mock_points_response.json.return_value = {
            'properties': {
                'gridId': 'TESTOFFICE',
                'forecast': 'https://api.weather.gov/gridpoints/TESTOFFICE/1,1/forecast'
            }
        }
        mock_forecast_response = Mock()
        mock_forecast_response.status_code = 200
        # 'periods' is empty, leading to IndexError
        mock_forecast_response.json.return_value = {'properties': {'periods': []}}

        mock_get.side_effect = [mock_points_response, mock_forecast_response]

        response = self.client.get('/weather?lat=12.34&lon=56.78')
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        # This specific error message comes from the check `if not ... or not ...['periods']`
        self.assertIn("Forecast data is missing expected 'periods' structure", data['error'])


if __name__ == '__main__':
    # To make USER_AGENT accessible in tests if not directly imported or part of app.config
    # This is a bit of a workaround. Better to have USER_AGENT in app.config
    if not hasattr(app, 'USER_AGENT') and not app.config.get('USER_AGENT'):
        app.config['USER_AGENT'] = '(myweatherapp.com, contact@myweatherapp.com)' # Default from weather_service.py
    unittest.main()
