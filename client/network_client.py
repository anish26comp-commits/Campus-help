import socket
import json
import os
import uuid

from ftplib import FTP


# ============================================================
# Server Configuration
# ============================================================

SERVER_IP = "192.168.0.103"

TCP_PORT = 5000
UDP_PORT = 5001
FTP_PORT = 2121

FTP_USERNAME = "campusftp"
FTP_PASSWORD = "CampusFTP@123"


# ============================================================
# Session
# ============================================================

SESSION_TOKEN = None


# ============================================================
# UDP Server Discovery
# ============================================================

def discover_server():

    udp_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    udp_socket.settimeout(
        3
    )

    try:

        message = "DISCOVER_SERVER"

        udp_socket.sendto(
            message.encode("utf-8"),
            (
                SERVER_IP,
                UDP_PORT
            )
        )

        data, address = (
            udp_socket.recvfrom(
                1024
            )
        )

        response = data.decode(
            "utf-8"
        )

        if response.startswith(
            "CAMPUS_HELP_SERVER"
        ):

            parts = response.split("|")

            discovered_tcp_port = TCP_PORT
            discovered_ftp_port = FTP_PORT

            for part in parts:

                if part.startswith(
                    "TCP_PORT="
                ):

                    discovered_tcp_port = int(
                        part.split("=")[1]
                    )

                elif part.startswith(
                    "FTP_PORT="
                ):

                    discovered_ftp_port = int(
                        part.split("=")[1]
                    )

            return {
                "ip": address[0],
                "tcp_port": discovered_tcp_port,
                "ftp_port": discovered_ftp_port
            }

    except (
        socket.timeout,
        OSError,
        ValueError
    ):

        return None

    finally:

        udp_socket.close()


# ============================================================
# Get Server Address
# ============================================================

def get_server_address():

    discovered = discover_server()

    if discovered:

        return (
            discovered["ip"],
            discovered["tcp_port"]
        )

    return (
        SERVER_IP,
        TCP_PORT
    )


# ============================================================
# Get FTP Server Address
# ============================================================

def get_ftp_server_address():

    discovered = discover_server()

    if discovered:

        return (
            discovered["ip"],
            discovered["ftp_port"]
        )

    return (
        SERVER_IP,
        FTP_PORT
    )


# ============================================================
# Send TCP Request
# ============================================================

def send_request(
    request
):

    global SESSION_TOKEN

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.settimeout(
        5
    )

    try:

        server_ip, server_port = (
            get_server_address()
        )

        server_socket.connect(
            (
                server_ip,
                server_port
            )
        )

        request_data = dict(
            request
        )

        if SESSION_TOKEN:

            request_data[
                "session_token"
            ] = SESSION_TOKEN

        message = (
            json.dumps(
                request_data
            )
            + "\n"
        )

        server_socket.sendall(
            message.encode(
                "utf-8"
            )
        )

        data = b""

        while b"\n" not in data:

            chunk = server_socket.recv(
                4096
            )

            if not chunk:
                break

            data += chunk

        if not data:

            return {
                "success": False,
                "message": (
                    "No response received from server."
                )
            }

        return json.loads(
            data.decode(
                "utf-8"
            ).strip()
        )

    except ConnectionRefusedError:

        return {
            "success": False,
            "message": (
                "Unable to connect to the server."
            )
        }

    except socket.timeout:

        return {
            "success": False,
            "message": (
                "Connection timed out."
            )
        }

    except json.JSONDecodeError:

        return {
            "success": False,
            "message": (
                "Invalid response from server."
            )
        }

    except OSError as error:

        return {
            "success": False,
            "message": (
                f"Network error: {error}"
            )
        }

    finally:

        server_socket.close()


# ============================================================
# Register
# ============================================================

def register_user(
    name,
    email,
    password
):

    return send_request({
        "type": "REGISTER",
        "name": name,
        "email": email,
        "password": password
    })


# ============================================================
# Login
# ============================================================

def login_user(
    email,
    password
):

    global SESSION_TOKEN

    response = send_request({
        "type": "LOGIN",
        "email": email,
        "password": password
    })

    if response.get(
        "success"
    ):

        SESSION_TOKEN = response.get(
            "session_token"
        )

    return response


# ============================================================
# Logout
# ============================================================

def logout_user():

    global SESSION_TOKEN

    if SESSION_TOKEN:

        response = send_request({
            "type": "LOGOUT"
        })

    else:

        response = {
            "success": True,
            "message": "Logged out."
        }

    SESSION_TOKEN = None

    return response


# ============================================================
# Create Help Request
# ============================================================

def create_help_request(
    student_id,
    category,
    subject,
    description,
    priority
):

    return send_request({
        "type": "CREATE_REQUEST",
        "student_id": student_id,
        "category": category,
        "subject": subject,
        "description": description,
        "priority": priority
    })


# ============================================================
# Student - Get My Requests
# ============================================================

def get_my_requests(
    student_id
):

    return send_request({
        "type": "GET_MY_REQUESTS",
        "student_id": student_id
    })


# ============================================================
# Student - Get My Request Details
# ============================================================

def get_my_request_details(
    request_id
):

    return send_request({
        "type": "GET_MY_REQUEST_DETAILS",
        "request_id": request_id
    })


# ============================================================
# Admin - Get All Requests
# ============================================================

def get_all_requests():

    return send_request({
        "type": "GET_ALL_REQUESTS"
    })


# ============================================================
# Admin - Get Request Details
# ============================================================

def get_request_details(
    request_id
):

    return send_request({
        "type": "GET_REQUEST_DETAILS",
        "request_id": request_id
    })


# ============================================================
# Admin - Update Status
# ============================================================

def update_request_status(
    request_id,
    status
):

    return send_request({
        "type": "UPDATE_REQUEST_STATUS",
        "request_id": request_id,
        "status": status
    })


# ============================================================
# Admin - Add Response
# ============================================================

def add_request_update(
    request_id,
    message
):

    return send_request({
        "type": "ADD_REQUEST_UPDATE",
        "request_id": request_id,
        "message": message
    })


# ============================================================
# FTP - Upload Attachment
# ============================================================

def upload_attachment(
    local_file,
    request_id
):

    if not os.path.isfile(
        local_file
    ):

        return {
            "success": False,
            "message": "Selected file does not exist."
        }

    ftp = FTP()

    try:

        server_ip, ftp_port = (
            get_ftp_server_address()
        )

        ftp.connect(
            server_ip,
            ftp_port,
            timeout=10
        )

        ftp.login(
            FTP_USERNAME,
            FTP_PASSWORD
        )

        remote_directory = (
            f"/request_{request_id}"
        )

        try:

            ftp.mkd(
                remote_directory
            )

        except Exception:

            pass

        ftp.cwd(
            remote_directory
        )

        extension = os.path.splitext(
            local_file
        )[1]

        unique_name = (
            f"{uuid.uuid4().hex}"
            f"{extension}"
        )

        with open(
            local_file,
            "rb"
        ) as file:

            ftp.storbinary(
                f"STOR {unique_name}",
                file
            )

        remote_path = (
            f"{remote_directory}/"
            f"{unique_name}"
        )

        ftp.quit()

        return {
            "success": True,
            "filename": os.path.basename(
                local_file
            ),
            "remote_filename": unique_name,
            "remote_path": remote_path
        }

    except Exception as error:

        try:
            ftp.quit()
        except Exception:
            pass

        return {
            "success": False,
            "message": (
                f"FTP upload failed: {error}"
            )
        }


# ============================================================
# Save Attachment Metadata
# ============================================================

def save_attachment_metadata(
    request_id,
    filename,
    filepath
):

    return send_request({
        "type": "ADD_ATTACHMENT",
        "request_id": request_id,
        "filename": filename,
        "filepath": filepath
    })


# ============================================================
# FTP - Download Attachment
# ============================================================

def download_attachment(
    remote_path,
    local_file
):

    ftp = FTP()

    try:

        server_ip, ftp_port = (
            get_ftp_server_address()
        )

        ftp.connect(
            server_ip,
            ftp_port,
            timeout=10
        )

        ftp.login(
            FTP_USERNAME,
            FTP_PASSWORD
        )

        remote_path = remote_path.replace(
            "\\",
            "/"
        )

        remote_directory = os.path.dirname(
            remote_path
        )

        remote_filename = os.path.basename(
            remote_path
        )

        if remote_directory:

            ftp.cwd(
                remote_directory
            )

        with open(
            local_file,
            "wb"
        ) as file:

            ftp.retrbinary(
                f"RETR {remote_filename}",
                file.write
            )

        ftp.quit()

        return {
            "success": True,
            "message": "Attachment downloaded successfully."
        }

    except Exception as error:

        try:
            ftp.quit()
        except Exception:
            pass

        return {
            "success": False,
            "message": (
                f"FTP download failed: {error}"
            )
        }