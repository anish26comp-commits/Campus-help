import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


# ============================================================
# FTP Configuration
# ============================================================

FTP_HOST = "0.0.0.0"
FTP_PORT = 2121

FTP_USERNAME = "campusftp"
FTP_PASSWORD = "CampusFTP@123"

PASSIVE_START = 30000
PASSIVE_END = 30009

FTP_ROOT = "/app/files/attachments"


# ============================================================
# Start FTP Server
# ============================================================

def start_ftp_server():

    # Make sure the FTP storage directory exists
    os.makedirs(
        FTP_ROOT,
        exist_ok=True
    )

    # --------------------------------------------------------
    # FTP User
    # --------------------------------------------------------

    authorizer = DummyAuthorizer()

    authorizer.add_user(
        FTP_USERNAME,
        FTP_PASSWORD,
        FTP_ROOT,
        perm="elradfmwMT"
    )

    # --------------------------------------------------------
    # FTP Handler
    # --------------------------------------------------------

    # IMPORTANT:
    # Do NOT write FTPHandler().
    #
    # FTPServer creates FTPHandler instances automatically
    # whenever a client connects.
    handler = FTPHandler

    handler.authorizer = authorizer

    # Passive FTP data ports
    handler.passive_ports = range(
        PASSIVE_START,
        PASSIVE_END + 1
    )

    handler.banner = (
        "Campus Help FTP Server Ready"
    )

    # --------------------------------------------------------
    # FTP Server
    # --------------------------------------------------------

    server = FTPServer(
        (
            FTP_HOST,
            FTP_PORT
        ),
        handler
    )

    print("=" * 50)

    print(
        "Campus Help FTP Server Started"
    )

    print(
        f"FTP Port: {FTP_PORT}"
    )

    print(
        f"FTP Storage: {FTP_ROOT}"
    )

    print(
        f"Passive Ports: "
        f"{PASSIVE_START}-{PASSIVE_END}"
    )

    print("=" * 50)

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nFTP server stopped."
        )

    finally:

        server.close_all()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    start_ftp_server()