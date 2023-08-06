# BREACH :: HARBOR Collector
[![Python Unit Tests](https://github.com/Dyneteq/breach_harbor_collector/actions/workflows/main.yml/badge.svg)](https://github.com/Dyneteq/breach_harbor_collector/actions/workflows/main.yml)

## About

BREACH::HARBOR Collector is a service that collects data from inbound attacks, logs them and sends them over to the BREACH::HARBOR Core API.

The service can be ran autonomously for research and monitoring purposes without any connection to the separate Core API service.



## Quick start

### Docker

Build:

```bash
docker build -t bh-collector .
```

Start:

```bash
# We need to mount a volume with the .env file in order to reftect the changes
docker run -p 80:8080 -p 22:2222 -v "$(pwd)/.env:/app/.env" bh-collector
```

## Development

### Prerequisities

Activate venv

```bash
source .venv/bin/activate
```

Copy .env.example to .env and setup the env variables:

```bash
API_POST_URL=https://api.breachharbor.local
API_TOKEN=jfxPSG2qugTvKIhWfXEv5t0kb0Stjh8ljDRhmA
API_ENABLED=true
LOGGING_LEVEL=INFO
LOGGING_ENABLED=false
SERVICE_HTTP_ENABLED=true
SERVICE_HTTP_PORT=8080
SERVICE_SSH_ENABLED=true 
SERVICE_SSH_PORT=2222
```

#### Generate an SSH key pair

You will need to create the SSH key pair If you wish to enable the SSH service:

```bash
ssh-keygen -t rsa -b 4096 -f ./certificates/id_rsa -N ""
```

#### Start the service

Run simply as your `$user` with ports over 1024 or with sudo for :80 access (not recommended):

```bash
sudo `which python3` start.py
```

## How to dock a new collector to the BREACH::HARBOR Core API

- Generate a new token on the _Add new collector page_
- Clone this repository on the collector
- Create or copy the .env file and fill in the variable values
- Run with docker or locally with python
- Verify the connection by checking the systemd status and the cloud collector page
  
## Services that are (or will) supported by each collector

- [ ] [20] FTP (File Transfer Protocol - Data)
- [ ] [21] FTP (File Transfer Protocol - Control)
- [x] [22] SSH (Secure Shell)
- [ ] [23] Telnet
- [ ] [25] SMTP (Simple Mail Transfer Protocol)
- [ ] [53] DNS (Domain Name System)
- [x] [80] HTTP (Hypertext Transfer Protocol)
- [ ] [110] POP3 (Post Office Protocol - Version 3)
- [ ] [143] IMAP (Internet Message Access Protocol)
- [ ] [443] HTTPS (Hypertext Transfer Protocol Secure)
- [ ] [3389] RDP (Remote Desktop Protocol)
- [ ] [445] SMB (Server Message Block)
- [ ] [465] SMTPS (Simple Mail Transfer Protocol Secure)
- [ ] [587] SMTP Submission (Message Submission Agent)
- [ ] [993] IMAPS (IMAP Secure)
- [ ] [995] POP3S (Post Office Protocol - Version 3 Secure)
- [ ] [1433] MSSQL (Microsoft SQL Server)
- [ ] [1723] PPTP (Point-to-Point Tunneling Protocol)
- [ ] [3306] MySQL (Database System)
- [ ] [8080] HTTP Proxy (Commonly Used for Web Proxies)

## Security best practices

> **WARNING: Always ensure that the rest of your network is secure and that the machine running the service is isolated from other systems.**
> 
## License

This project is licensed under the terms of the GNU General Public License v3.0. For the full license text, please see the [LICENSE](LICENSE) file in the project root.
