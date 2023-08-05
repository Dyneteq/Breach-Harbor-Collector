import asyncio
import datetime
import threading
import logging
import paramiko
import aiohttp
from src.incidents.incident import Incident

class SSHServer(paramiko.ServerInterface):
    def __init__(self, transport, client_ip_addr, loop):
        self.completion_event = threading.Event()
        self.transport = transport
        self.client_ip_addr = client_ip_addr
        self.loop = loop

    def check_auth_password(self, username, password):
        logging.info(
            'Login attempt from %s with username "%s" and password "%s"', 
            self.client_ip_addr, username, password
        )

        data = {
            "client_ip_addr": self.client_ip_addr,
            "username": username,
            "password": password,
        }
        asyncio.run_coroutine_threadsafe(
            self.create_incident(data), self.loop
        )  # Use run_coroutine_threadsafe
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True

    def create_payload(self, data):
        timestamp = datetime.datetime.now().isoformat()
        return {
            "ip_addr": data["client_ip_addr"],
            "incident_type": "BH-SSH",
            "happened_at": timestamp,
            "metadata": {
                "username": data["username"],
                "password": data["password"],
            },
        }

    async def create_incident(self, data):
        try:
            payload = self.create_payload(data)
            incident = Incident(payload)
            await incident.create()
        except aiohttp.ClientConnectionError as error:
            logging.error("Failed to create incident: %s", str(error))
