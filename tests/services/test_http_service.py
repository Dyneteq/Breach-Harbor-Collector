import unittest
from src.services.http.http_service import HTTPService
from unittest.mock import Mock, patch

class TestHTTPService(unittest.TestCase):
    def setUp(self):
        self.service = HTTPService()
        self.request = Mock()
        self.request.method = "POST"
        self.request.path = "/"
        self.request.remote = "127.0.0.1"
        self.request.headers = {
            "User-Agent": "DummyAgent",
            "Accept": "text/html",
            "Host": "localhost",
        }

    def test_create_payload(self):
        request_payload = "test payload"
        payload = self.service.create_payload(self.request, request_payload)

        self.assertIsNotNone(payload["happened_at"])
        self.assertEqual(payload["ip_address"], "127.0.0.1")
        self.assertEqual(payload["incident_type"], "BH-HTTP")
        self.assertEqual(payload["metadata"]["user_agent"], "DummyAgent")
        self.assertEqual(payload["metadata"]["method"], "POST")
        self.assertEqual(payload["metadata"]["path"], "/")
        self.assertIsNotNone(payload["metadata"]["headers"])
        self.assertEqual(payload["metadata"]["payload"], request_payload)
        self.assertFalse(payload["metadata"]["is_malformed"])

    def test_is_malformed(self):
        # A GET request with no payload is not malformed
        is_malformed = self.service.is_malformed(
            "GET",
            "/",
            {"User-Agent": "DummyAgent", "Accept": "text/html", "Host": "localhost"},
            None,
        )
        self.assertFalse(is_malformed)

        # A POST request with no payload is malformed
        is_malformed = self.service.is_malformed(
            "POST",
            "/",
            {"User-Agent": "DummyAgent", "Accept": "text/html", "Host": "localhost"},
            None,
        )
        self.assertTrue(is_malformed)

        # A POST request with a payload is not malformed
        is_malformed = self.service.is_malformed(
            "POST",
            "/",
            {"User-Agent": "DummyAgent", "Accept": "text/html", "Host": "localhost"},
            "payload",
        )
        self.assertFalse(is_malformed)

        # A GET request with a payload is malformed
        is_malformed = self.service.is_malformed(
            "GET",
            "/",
            {"User-Agent": "DummyAgent", "Accept": "text/html", "Host": "localhost"},
            "payload",
        )
        self.assertTrue(is_malformed)

        # A request with a non-standard method is malformed
        is_malformed = self.service.is_malformed(
            "INVALID",
            "/",
            {"User-Agent": "DummyAgent", "Accept": "text/html", "Host": "localhost"},
            None,
        )
        self.assertTrue(is_malformed)

        # A request with missing required headers is malformed
        is_malformed = self.service.is_malformed(
            "GET", "/", {"User-Agent": "DummyAgent", "Host": "localhost"}, None
        )
        self.assertTrue(is_malformed)

    @patch("src.incidents.incident.Incident.create")
    def test_create_response(self, mock_create):
        mock_create.return_value = None
        response_content = self.service.create_response_content()
        self.assertTrue(isinstance(response_content, str))
        self.assertIn("<html>", response_content)
        self.assertIn("<title>Welcome to My Server</title>", response_content)
        self.assertIn("<h1>Hello, world!</h1>", response_content)

if __name__ == "__main__":
    unittest.main()
