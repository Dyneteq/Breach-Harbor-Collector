from typing import Any, Dict
import unittest
from unittest.mock import patch, MagicMock
from aiohttp.test_utils import make_mocked_coro
from src.incidents.incident import Incident
from src.helpers.configuration.configuration import Configuration

config: Dict[str, Any] = Configuration().get_config()


class TestIncident(unittest.IsolatedAsyncioTestCase):
    @patch("aiohttp.ClientSession.post")
    async def test_incident_send_to_api(self, mock_post):
        # Mock the HTTP response from aiohttp.ClientSession.post
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = make_mocked_coro(return_value={})
        mock_post.return_value.__aenter__.return_value = mock_response

        # Sample data
        metadata = self.get_metadata()
        data = self.get_data(metadata)

        # Create Incident and call create
        incident = Incident(data)
        Configuration.set_config_item("API_ENABLED", True)
        await incident.create()

        # Ensure that aiohttp.ClientSession.post was called with the expected arguments
        mock_post.assert_called_once_with(
            url=config.get("API_POST_URL"),
            params={"token": config.get("API_TOKEN")},
            json=data,
        )

    @patch("logging.error")
    @patch("aiohttp.ClientSession.post")
    async def test_incident_send_to_api_404(self, mock_post, mock_log_error):
        # Mock the HTTP response from aiohttp.ClientSession.post
        mock_response = MagicMock()
        mock_response.status = 404
        mock_post.return_value.__aenter__.return_value = mock_response

        # Sample data
        metadata = self.get_metadata()
        data = self.get_data(metadata)

        # Create Incident and call create
        incident = Incident(data)
        Configuration.set_config_item("API_ENABLED", True)
        await incident.create()

        # Ensure that logging.error was called with the expected arguments
        mock_log_error.assert_called_with("Failed to send incident to API, status code: %s", 404)


    def get_metadata(self):
        return {
            "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "method": "GET",
            "path": "/",
            "headers": {
                "host": "localhost",
                "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.5",
                "accept-encoding": "gzip, deflate, br",
                "connection": "keep-alive",
                "cookie": 'username-localhost-8888="2|1:0|10:1690432826|23:username-localhost-8888|44:ZWYyNjA3NzNlNjU0NDRkYzk5ZDM1ZGM3MzRmODI0YzE=|ddeb34b6b8f258cf2368e3b92677d5ea1f11f6eaf86af98d2a57a5dc7d7cafbf"; _xsrf=2|b722e5b9|ba0ce72b74ac435c985fd5890c3f01f0|1690432826',
                "upgrade-insecure-requests": "1",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
            },
            "payload": None,
            "is_malformed": False,
        }

    def get_data(self, metadata):
        return {
            "ip_addr": "127.0.0.1",
            "incident_type": "BH-HTTP",
            "metadata": metadata,
            "happened_at": "2023-07-28T17:32:19.336395",
        }


if __name__ == "__main__":
    unittest.main()
