from datetime import datetime
import ipaddress
import logging
from typing import Any, Dict
import aiohttp
from src.helpers.configuration.configuration import Configuration
from .incident_type_enum import IncidentType

CONFIG: Dict[str, Any] = Configuration().get_config()


class Incident:
    def __init__(self, data=None):
        self.data = data

    async def create(self):
        logging.info(self.data)
        self.validate()
        if not CONFIG.get("API_ENABLED"):
            return None

        await self.send_to_api()

    def validate(self):
        if not self.data:
            raise ValueError("Data is None. Please provide valid data.")

        required_keys = ["ip_address", "incident_type", "metadata", "happened_at"]

        missing_keys = [key for key in required_keys if key not in self.data]
        if missing_keys:
            raise ValueError(
                f"Invalid data - missing required key(s): {', '.join(missing_keys)}"
            )

        # Check IP address format
        try:
            ipaddress.ip_address(self.data["ip_address"])
        except ValueError as exc:
            raise ValueError("Invalid IP address format.") from exc

        # Check incident_type is a valid enum value
        if self.data["incident_type"] not in [
            incident_type.value for incident_type in IncidentType
        ]:
            raise ValueError("Invalid incident type.")

        # Check happened_at is a valid date in ISO format
        try:
            datetime.fromisoformat(self.data["happened_at"])
        except ValueError as exc:
            raise ValueError("Invalid date format. Must be in ISO format.") from exc

    async def send_to_api(self):
        if not CONFIG.get("API_TOKEN") or not CONFIG.get("API_POST_URL") or not CONFIG.get("COLLECTOR_ID"):
            logging.error(
                        "Missing arguments: API_TOKEN, API_POST_URL and COLLECTOR_ID must all be set up",
                    )
            return None
        self.data['collector_name'] = CONFIG.get("COLLECTOR_ID")
        print(self.data)
        headers = {"authorization": f"Bearer {CONFIG.get('API_TOKEN')}"}
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url=CONFIG.get("API_POST_URL"),
                headers=headers,
                json=self.data,
            ) as response:
                if response.status != 201:
                    logging.error(
                        "Failed to send incident to API, status code: %s",
                        response.status,
                    )
