import unittest
from src.helpers.configuration.configuration import Configuration


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        # Define a valid configuration for testing
        self.valid_config = {
            "API_POST_URL": "http://example.com/api",
            "API_TOKEN": "example_token",
            "API_ENABLED": True,
            "LOGGING_LEVEL": "INFO",
            "LOGGING_ENABLED": True,
            "SERVICE_HTTP_ENABLED": True,
            "SERVICE_HTTP_PORT": 8080,
            "SERVICE_SSH_ENABLED": False,
            "SERVICE_SSH_PORT": 22,
        }

        # Define a few invalid configurations for testing
        self.missing_api_post_url_config = self.valid_config.copy()
        self.missing_api_post_url_config.pop("API_POST_URL")

        self.invalid_api_enabled_value_config = self.valid_config.copy()
        self.invalid_api_enabled_value_config["API_ENABLED"] = "not a boolean"

        self.invalid_service_http_port_config = self.valid_config.copy()
        self.invalid_service_http_port_config["SERVICE_HTTP_PORT"] = "not an integer"

    def test_validate_config(self):
        # Test validating a valid configuration
        Configuration.validate_config(self.valid_config)

        # Test validating an invalid configuration with missing 'API_POST_URL' key
        with self.assertRaises(ValueError):
            Configuration.validate_config(self.missing_api_post_url_config)

        # Test validating an invalid configuration with incorrect 'API_ENABLED' format
        with self.assertRaises(ValueError):
            Configuration.validate_config(self.invalid_api_enabled_value_config)

        # Test validating an invalid configuration with wrong 'SERVICE_HTTP_PORT' value
        with self.assertRaises(ValueError):
            Configuration.validate_config(self.invalid_service_http_port_config)


if __name__ == "__main__":
    unittest.main()
