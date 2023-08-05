import asyncio
import socket
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import paramiko
from .ssh_server import SSHServer


class SSHService:
    def __init__(self, port=2222):
        self.port = port
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.sock = None

    async def run(self):
        logging.basicConfig(level=logging.INFO)
        current_directory = os.path.dirname(os.path.abspath(__file__))
        rsa_key_fullpath = os.path.join(current_directory, "../../../certificates/id_rsa")
        host_key = paramiko.RSAKey(filename=rsa_key_fullpath)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", self.port))
        self.sock.listen(100)

        loop = asyncio.get_running_loop()

        while True:
            try:
                client, addr = await loop.run_in_executor(
                    self.executor, self.sock.accept
                )
            except socket.error as err:
                logging.error("Failed to accept client: %s", err)

            asyncio.create_task(self.handle_client(client, addr, host_key, loop))

    def stop(self):
        # Close the listening socket to stop accepting new connections
        if self.sock:
            self.sock.close()

        # Wait for the executor's tasks to finish (existing connections)
        self.executor.shutdown(wait=True)

    async def handle_client(self, client, addr, host_key, loop):
        transport = None
        try:
            transport = paramiko.Transport(client, (socket.getfqdn(""), 0))
            transport.load_server_moduli()
            transport.add_server_key(host_key)
            server = SSHServer(transport, addr[0], loop)
            transport.start_server(server=server)

            logging.info("SSH connection received from %s", addr)

            while transport.is_active():
                await asyncio.sleep(1)
        except socket.error as err:
            logging.error("Failed to handle client: %s", str(err))
        finally:
            if transport is not None:
                transport.close()
