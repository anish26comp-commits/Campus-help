import socket
import threading
import json
import secrets

from datetime import datetime, timedelta

from database import (
    initialize_database,
    register_user,
    authenticate_user,
    create_help_request,
    get_student_requests,
    get_student_request_details,
    get_all_requests,
    get_request_details,
    update_request_status,
    add_request_update,
    add_attachment
)

from ftp_server import start_ftp_server
from http_server import start_http_server
from smtp_service import send_request_notification


# ============================================================
# Server Configuration
# ============================================================

TCP_HOST = "0.0.0.0"
TCP_PORT = 5000

UDP_HOST = "0.0.0.0"
UDP_PORT = 5001


# ============================================================
# Session Management
# ============================================================

SESSIONS = {}

SESSION_LOCK = threading.Lock()

SESSION_DURATION = timedelta(
    hours=8
)


def create_session(user):

    token = secrets.token_urlsafe(
        32
    )

    session = {
        "user_id": user["id"],
        "role": user["role"],
        "name": user["name"],
        "created_at": datetime.now()
    }

    with SESSION_LOCK:

        SESSIONS[token] = session

    return token


def validate_session(
    token,
    required_role=None
):

    if not token:
        return None

    with SESSION_LOCK:

        session = SESSIONS.get(
            token
        )

        if session is None:
            return None

        if (
            datetime.now()
            - session["created_at"]
            > SESSION_DURATION
        ):

            del SESSIONS[token]

            return None

        if (
            required_role is not None
            and session["role"] != required_role
        ):

            return None

        return session


def remove_session(token):

    if not token:
        return

    with SESSION_LOCK:

        SESSIONS.pop(
            token,
            None
        )


# ============================================================
# SMTP Notification Helper
# ============================================================

def send_notification_async(
    request_id,
    status,
    message
):

    def worker():

        try:

            result = get_request_details(
                request_id
            )

            if not result.get(
                "success"
            ):
                return

            request = result[
                "request"
            ]

            send_request_notification(
                request["student_email"],
                request["student_name"],
                request_id,
                request["subject"],
                status,
                message
            )

        except Exception as error:

            print(
                f"[SMTP] Notification error: {error}"
            )

    notification_thread = threading.Thread(
        target=worker,
        daemon=True
    )

    notification_thread.start()


# ============================================================
# Send JSON Response
# ============================================================

def send_response(
    client_socket,
    response
):

    message = (
        json.dumps(response)
        + "\n"
    )

    client_socket.sendall(
        message.encode("utf-8")
    )


# ============================================================
# Process Request
# ============================================================

def process_request(request):

    request_type = request.get(
        "type"
    )

    token = request.get(
        "session_token"
    )

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    if request_type == "REGISTER":

        name = request.get(
            "name",
            ""
        ).strip()

        email = request.get(
            "email",
            ""
        ).strip()

        password = request.get(
            "password",
            ""
        )

        if (
            not name
            or not email
            or not password
        ):

            return {
                "success": False,
                "message": (
                    "All registration fields are required."
                )
            }

        return register_user(
            name,
            email,
            password
        )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    elif request_type == "LOGIN":

        email = request.get(
            "email",
            ""
        ).strip()

        password = request.get(
            "password",
            ""
        )

        if not email or not password:

            return {
                "success": False,
                "message": (
                    "Email and password are required."
                )
            }

        result = authenticate_user(
            email,
            password
        )

        if result.get(
            "success"
        ):

            result["session_token"] = (
                create_session(
                    result["user"]
                )
            )

        return result

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    elif request_type == "LOGOUT":

        remove_session(
            token
        )

        return {
            "success": True,
            "message": "Logged out successfully."
        }

    # --------------------------------------------------------
    # CREATE REQUEST
    # --------------------------------------------------------

    elif request_type == "CREATE_REQUEST":

        session = validate_session(
            token,
            required_role="student"
        )

        if session is None:

            return {
                "success": False,
                "message": "Authentication required."
            }

        category = request.get(
            "category",
            ""
        ).strip()

        subject = request.get(
            "subject",
            ""
        ).strip()

        description = request.get(
            "description",
            ""
        ).strip()

        priority = request.get(
            "priority",
            "Normal"
        ).strip()

        if (
            not category
            or not subject
            or not description
        ):

            return {
                "success": False,
                "message": (
                    "All help request fields are required."
                )
            }

        return create_help_request(
            session["user_id"],
            category,
            subject,
            description,
            priority
        )

    # --------------------------------------------------------
    # GET MY REQUESTS
    # --------------------------------------------------------

    elif request_type == "GET_MY_REQUESTS":

        session = validate_session(
            token,
            required_role="student"
        )

        if session is None:

            return {
                "success": False,
                "message": "Authentication required."
            }

        return get_student_requests(
            session["user_id"]
        )

    # --------------------------------------------------------
    # GET MY REQUEST DETAILS
    # --------------------------------------------------------

    elif request_type == "GET_MY_REQUEST_DETAILS":

        session = validate_session(
            token,
            required_role="student"
        )

        if session is None:

            return {
                "success": False,
                "message": "Authentication required."
            }

        request_id = request.get(
            "request_id"
        )

        try:

            request_id = int(
                request_id
            )

        except (
            TypeError,
            ValueError
        ):

            return {
                "success": False,
                "message": "Invalid request ID."
            }

        return get_student_request_details(
            session["user_id"],
            request_id
        )

    # --------------------------------------------------------
    # GET ALL REQUESTS
    # ADMIN ONLY
    # --------------------------------------------------------

    elif request_type == "GET_ALL_REQUESTS":

        session = validate_session(
            token,
            required_role="admin"
        )

        if session is None:

            return {
                "success": False,
                "message": (
                    "Administrator authentication required."
                )
            }

        return get_all_requests()

    # --------------------------------------------------------
    # GET REQUEST DETAILS
    # ADMIN ONLY
    # --------------------------------------------------------

    elif request_type == "GET_REQUEST_DETAILS":

        session = validate_session(
            token,
            required_role="admin"
        )

        if session is None:

            return {
                "success": False,
                "message": (
                    "Administrator authentication required."
                )
            }

        request_id = request.get(
            "request_id"
        )

        try:

            request_id = int(
                request_id
            )

        except (
            TypeError,
            ValueError
        ):

            return {
                "success": False,
                "message": "Invalid request ID."
            }

        return get_request_details(
            request_id
        )

    # --------------------------------------------------------
    # UPDATE REQUEST STATUS
    # ADMIN ONLY
    # --------------------------------------------------------

    elif request_type == "UPDATE_REQUEST_STATUS":

        session = validate_session(
            token,
            required_role="admin"
        )

        if session is None:

            return {
                "success": False,
                "message": (
                    "Administrator authentication required."
                )
            }

        request_id = request.get(
            "request_id"
        )

        status = request.get(
            "status",
            ""
        ).strip()

        try:

            request_id = int(
                request_id
            )

        except (
            TypeError,
            ValueError
        ):

            return {
                "success": False,
                "message": "Invalid request ID."
            }

        allowed_statuses = {
            "Pending",
            "In Progress",
            "Resolved"
        }

        if status not in allowed_statuses:

            return {
                "success": False,
                "message": "Invalid status."
            }

        result = update_request_status(
            request_id,
            status,
            session["user_id"]
        )

        if result.get(
            "success"
        ):

            send_notification_async(
                request_id,
                status,
                f"Your request status was changed to {status}."
            )

        return result

    # --------------------------------------------------------
    # ADD REQUEST UPDATE
    # ADMIN ONLY
    # --------------------------------------------------------

    elif request_type == "ADD_REQUEST_UPDATE":

        session = validate_session(
            token,
            required_role="admin"
        )

        if session is None:

            return {
                "success": False,
                "message": (
                    "Administrator authentication required."
                )
            }

        request_id = request.get(
            "request_id"
        )

        message = request.get(
            "message",
            ""
        ).strip()

        try:

            request_id = int(
                request_id
            )

        except (
            TypeError,
            ValueError
        ):

            return {
                "success": False,
                "message": "Invalid request ID."
            }

        if not message:

            return {
                "success": False,
                "message": (
                    "Update message cannot be empty."
                )
            }

        result = add_request_update(
            request_id,
            message,
            session["user_id"]
        )

        if result.get(
            "success"
        ):

            request_details = (
                get_request_details(
                    request_id
                )
            )

            if request_details.get(
                "success"
            ):

                current_status = (
                    request_details[
                        "request"
                    ][
                        "status"
                    ]
                )

                send_notification_async(
                    request_id,
                    current_status,
                    message
                )

        return result

    # --------------------------------------------------------
    # ADD ATTACHMENT
    # STUDENT ONLY
    # --------------------------------------------------------

    elif request_type == "ADD_ATTACHMENT":

        session = validate_session(
            token,
            required_role="student"
        )

        if session is None:

            return {
                "success": False,
                "message": "Authentication required."
            }

        request_id = request.get(
            "request_id"
        )

        filename = request.get(
            "filename",
            ""
        ).strip()

        filepath = request.get(
            "filepath",
            ""
        ).strip()

        try:

            request_id = int(
                request_id
            )

        except (
            TypeError,
            ValueError
        ):

            return {
                "success": False,
                "message": "Invalid request ID."
            }

        if not filename or not filepath:

            return {
                "success": False,
                "message": (
                    "Attachment information is incomplete."
                )
            }

        ownership_check = (
            get_student_request_details(
                session["user_id"],
                request_id
            )
        )

        if not ownership_check.get(
            "success"
        ):

            return {
                "success": False,
                "message": "Access denied."
            }

        return add_attachment(
            request_id,
            filename,
            filepath
        )

    # --------------------------------------------------------
    # UNKNOWN REQUEST
    # --------------------------------------------------------

    return {
        "success": False,
        "message": "Unknown request type."
    }


# ============================================================
# TCP Client Handler
# ============================================================

def handle_client(
    client_socket,
    client_address
):

    print(
        f"[TCP] Client connected: "
        f"{client_address}"
    )

    buffer = ""

    try:

        while True:

            data = client_socket.recv(
                4096
            )

            if not data:
                break

            buffer += data.decode(
                "utf-8"
            )

            while "\n" in buffer:

                message, buffer = (
                    buffer.split(
                        "\n",
                        1
                    )
                )

                if not message.strip():
                    continue

                try:

                    request = json.loads(
                        message
                    )

                    print(
                        f"[TCP] Request from "
                        f"{client_address}: "
                        f"{request.get('type')}"
                    )

                    response = process_request(
                        request
                    )

                    send_response(
                        client_socket,
                        response
                    )

                except json.JSONDecodeError:

                    send_response(
                        client_socket,
                        {
                            "success": False,
                            "message": (
                                "Invalid JSON request."
                            )
                        }
                    )

    except ConnectionResetError:

        print(
            f"[TCP] Client disconnected unexpectedly: "
            f"{client_address}"
        )

    except Exception as error:

        print(
            f"[TCP] Error with "
            f"{client_address}: {error}"
        )

    finally:

        client_socket.close()

        print(
            f"[TCP] Connection closed: "
            f"{client_address}"
        )


# ============================================================
# TCP Server
# ============================================================

def start_tcp_server():

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (
            TCP_HOST,
            TCP_PORT
        )
    )

    server_socket.listen(
        10
    )

    print("=" * 50)
    print("Campus LAN Help Request System")
    print("TCP Server Started")
    print(f"TCP Port: {TCP_PORT}")
    print("=" * 50)

    while True:

        try:

            client_socket, client_address = (
                server_socket.accept()
            )

            client_thread = threading.Thread(
                target=handle_client,
                args=(
                    client_socket,
                    client_address
                ),
                daemon=True
            )

            client_thread.start()

        except Exception as error:

            print(
                f"[TCP] Server error: {error}"
            )

            break

    server_socket.close()


# ============================================================
# UDP Discovery
# ============================================================

def start_udp_server():

    udp_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    udp_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    udp_socket.bind(
        (
            UDP_HOST,
            UDP_PORT
        )
    )

    print(
        f"[UDP] Discovery server started "
        f"on port {UDP_PORT}"
    )

    while True:

        try:

            data, client_address = (
                udp_socket.recvfrom(
                    1024
                )
            )

            message = data.decode(
                "utf-8"
            ).strip()

            print(
                f"[UDP] Discovery request from "
                f"{client_address}: {message}"
            )

            if message == "DISCOVER_SERVER":

                response = (
                    "CAMPUS_HELP_SERVER|"
                    "TCP_PORT=5000|"
                    "FTP_PORT=2121|"
                    "HTTP_PORT=8000"
                )

                udp_socket.sendto(
                    response.encode(
                        "utf-8"
                    ),
                    client_address
                )

                print(
                    f"[UDP] Discovery response sent "
                    f"to {client_address}"
                )

        except Exception as error:

            print(
                f"[UDP] Server error: {error}"
            )

            break

    udp_socket.close()


# ============================================================
# Main
# ============================================================

def main():

    print(
        "\nStarting Campus LAN "
        "Help Request Server...\n"
    )

    # Database
    initialize_database()

    # UDP
    udp_thread = threading.Thread(
        target=start_udp_server,
        daemon=True
    )

    udp_thread.start()

    # FTP
    ftp_thread = threading.Thread(
        target=start_ftp_server,
        daemon=True
    )

    ftp_thread.start()

    # HTTP
    http_thread = threading.Thread(
        target=start_http_server,
        daemon=True
    )

    http_thread.start()

    # TCP
    start_tcp_server()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()