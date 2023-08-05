import asyncio
import unittest
from unittest.mock import patch
from src.services.ssh.ssh_service import SSHService


class TestSSHService(unittest.TestCase):
    def setUp(self):
        self.port = 2222
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def test_run(self):
        with patch.object(SSHService, "run", return_value=None) as mock_run:
            ssh_service = SSHService(self.port)
            self.loop.run_until_complete(ssh_service.run())
            mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
