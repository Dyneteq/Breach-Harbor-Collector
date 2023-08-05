from datetime import datetime
import logging
import asyncio
from collections import defaultdict
from aiohttp import web
from src.incidents.incident import Incident

class HTTPService:
    def __init__(self, port=8888):
        self.app = web.Application(middlewares=[self.rate_limiter])
        self.app.router.add_route("*", "/{tail:.*}", self.handle_request)
        # Limit the number of concurrent requests to 100
        self.semaphore = asyncio.Semaphore(100)
        self.request_counts = defaultdict(int)
        self.port = port

    def run(self):
        web.run_app(self.app, port=self.port)

    @web.middleware
    async def rate_limiter(self, request, handler):
        client_ip = request.remote
        self.request_counts[client_ip] += 1

        if self.request_counts[client_ip] > 1000:
            return web.Response(status=429, text="Too many requests")

        return await handler(request)

    async def handle_request(self, request):
        response_text = self.create_response_content()
        response = web.Response(body=response_text, content_type="text/html")

        if request.method == "POST":
            request_payload = await request.text()
        else:
            request_payload = None

        asyncio.create_task(self.create_incident(request, request_payload))

        return response

    def create_response_content(self):
        return """
        <html>
            <head>
                <title>Welcome to My Server</title>
            </head>
            <body>
                <h1>Hello, world!</h1>
            </body>
        </html>
        """

    def create_payload(self, request, request_payload):
        # Get the current timestamp
        timestamp = datetime.now().isoformat()

        # Log the request details
        client_ip = request.remote
        user_agent = request.headers.get("User-Agent")
        request_method = request.method
        request_path = request.path
        request_headers = dict(request.headers)

        is_malformed = self.is_malformed(
            request_method, request_path, request_headers, request_payload
        )
        request_data = {
            "ip_addr": client_ip,
            "incident_type": "BH-HTTP",
            "happened_at": timestamp,
            "metadata": {
                "user_agent": user_agent,
                "method": request_method,
                "path": request_path,
                "headers": request_headers,
                "payload": request_payload,
                "is_malformed": is_malformed,
            },
        }

        return request_data

    def is_malformed(
        self, request_method, request_path, request_headers, request_payload
    ):
        # Check if the method is invalid
        if request_method not in ["GET", "POST", "PUT", "DELETE"]:
            return True

        # Check if a GET request has a payload
        if request_method == "GET" and request_payload:
            return True

        # Check if the path is invalid
        if (
            not request_path
            or ".." in request_path
            or not all(char.isprintable() for char in request_path)
        ):
            return True

        # Check if required headers are missing
        required_headers = ["Accept", "Host", "User-Agent"]
        if not all(header in request_headers for header in required_headers):
            return True

        # Check if the payload is too large
        if request_payload and len(request_payload) > 1024 * 1024:  # More than 1 MB
            return True

        # Check if a POST, PUT or DELETE request has no payload
        if request_method in ["POST", "PUT", "DELETE"] and not request_payload:
            return True

        return False

    async def create_incident(self, request, request_payload):
        try:
            payload = self.create_payload(request, request_payload)
            incident = Incident(payload)
            await incident.create()
        except Exception as error:
            logging.error("Failed to create incident: %s", str(error))


if __name__ == "__main__":
    logging.debug("HTTPService imported")
