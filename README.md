# Campus Help System

Campus Help is a desktop application for submitting and managing campus support requests over a local network. Students can create requests, follow their status, and exchange attachments. Administrators can review requests, update statuses, and send responses. Email notifications are optional.

## Project Layout

- `client/`: PySide6 desktop application and network client.
- `server/`: TCP request server, UDP discovery, FTP attachment service, HTTP status page, and database/admin utilities.
- `database/`: SQLite database persisted across Docker container restarts.
- `files/attachments/`: Uploaded attachments persisted across Docker container restarts.

## Requirements

- Python 3.13 (the Docker image uses Python 3.13).
- Docker and Docker Compose for the containerized server, or Python to run it locally.
- PySide6 to run the desktop client.

Install the server dependencies from the project root:

```powershell
python -m pip install -r requirements.txt
python -m pip install PySide6
```

## Run with Docker

From the project root, build and start the server:

```powershell
docker compose up --build -d
```

View server logs or stop the service with:

```powershell
docker compose logs -f
docker compose down
```

The HTTP status page is available at `http://localhost:8000`. Its `/health` and `/stats` endpoints provide health and request statistics.

## Run the Server Locally

Install the dependencies, then start the server from its directory:

```powershell
cd server
python server.py
```

The server initializes the SQLite database on startup. Keep the terminal open while using the client.

## Create an Administrator

With the server stopped, run the setup utility from the `server/` directory and follow its prompts:

```powershell
python create_admin.py
```

To change an existing administrator's password, run `python reset_admin.py` from the same directory.

## Run the Desktop Client

Start the server first. Then, in a separate terminal, run the client from its directory:

```powershell
cd client
python login.py
```

For access across a LAN, set `SERVER_IP` in `client/network_client.py` to the server machine's reachable IPv4 address. The client uses that address for UDP discovery and as a fallback; the server must be reachable on the same network. The separate `client/client.py` script is a basic TCP connectivity test, not the main desktop application.

## Network Ports

Allow these inbound ports through the server machine's firewall when needed:

| Port(s) | Protocol | Purpose |
| --- | --- | --- |
| 5000 | TCP | Application requests |
| 5001 | UDP | Server discovery |
| 2121 | TCP | FTP attachment transfers |
| 30000-30009 | TCP | FTP passive data connections |
| 8000 | TCP | HTTP status page and statistics |

The Docker Compose configuration publishes these ports. On a LAN, use the server's LAN address rather than `localhost` on the client computer.

## Optional Email Notifications

The server reads SMTP settings from environment variables. Docker Compose reads these from a root `.env` file. Set the values below to enable email notifications; leave them unset to run without email. Do not commit real credentials.

```dotenv
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-account
SMTP_PASSWORD=your-password
SMTP_FROM=helpdesk@example.com
SMTP_USE_TLS=true
```

After changing these values, recreate the server container with `docker compose up -d`.

## Data and Configuration Notes

- SQLite data is stored in `database/CampusHelp.db`; attachment files are stored under `files/attachments/`.
- Docker mounts both directories from the project, so these files persist when the container is recreated.
- FTP credentials are currently defined in both `server/ftp_server.py` and `client/network_client.py`. Change both together before deploying beyond a trusted development network.
