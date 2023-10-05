import asyncio
import sys
import logging
from multiprocessing import Process
from typing import Dict, Any
from src.helpers.configuration.configuration import Configuration
from src.services.http.http_service import HTTPService
from src.services.ssh.ssh_service import SSHService

CONFIG: Dict[str, Any] = Configuration().get_config()

log_level_str = CONFIG.get("LOGGING_LEVEL")
log_level = getattr(logging, log_level_str.upper(), logging.WARNING)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }

    RESET = "\033[0m"  # Reset all colors and styles

    def format(self, record):
        colored_record = record
        levelname = colored_record.levelname
        seq = self.COLORS.get(levelname, self.RESET)
        colored_levelname = f"{seq}{levelname}{self.RESET}"
        colored_record.levelname = colored_levelname
        return super().format(colored_record)


handler = logging.StreamHandler()
handler.setFormatter(
    ColoredFormatter(
        "%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)

logger = logging.getLogger()
logger.setLevel(log_level)
logger.addHandler(handler)


def start_http_service(port: int):
    logger.info("Starting HTTP Service pot")
    http_service = HTTPService(port)
    http_service.run()


def start_ssh_service(port: int):
    logger.info("Starting SSH Service pot")
    ssh_service = SSHService(port)
    asyncio.run(ssh_service.run())

def print_banner():
    print("""
        =======================================================
                                       https://breachharbor.com
        .__ .__ .___.__. __ .  .      .  ..__..__ .__ .__..__ 
        [__)[__)[__ [__]/  `|__| *  * |__|[__][__)[__)|  |[__)
        [__)|  \[___|  |\__.|  | *  * |  ||  ||  \[__)|__||  \\
        
        ================================= COLLECTOR v1.0 dev ==
        
    """)

if __name__ == "__main__":
    print_banner()
    processes = []

    try:
        if CONFIG.get("SERVICE_HTTP_ENABLED"):
            http_port = CONFIG.get("SERVICE_HTTP_PORT")
            p = Process(target=start_http_service, args=(http_port,))
            p.start()
            processes.append(p)

        if CONFIG.get("SERVICE_SSH_ENABLED"):
            ssh_port = CONFIG.get("SERVICE_SSH_PORT")
            p = Process(target=start_ssh_service, args=(ssh_port,))
            p.start()
            processes.append(p)

        # wait for all processes to finish
        for p in processes:
            p.join()

    except KeyboardInterrupt:
        logger.info("Caught keyboard interrupt. Gracefully terminating services...")

        # Stop all running processes
        for p in processes:
            p.terminate()
            p.join()

        logger.info("All services terminated. Exiting...")
        sys.exit(0)
