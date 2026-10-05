import socket
import json


SERVER_IP = "192.168.0.104"   # PC1 IP
SERVER_PORT = 5000


def send_request(request):

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        client_socket.connect(
            (SERVER_IP, SERVER_PORT)
        )

        message = json.dumps(request) + "\n"

        client_socket.sendall(
            message.encode("utf-8")
        )

        data = b""

        while b"\n" not in data:

            chunk = client_socket.recv(4096)

            if not chunk:
                break

            data += chunk

        response = json.loads(
            data.decode("utf-8").strip()
        )

        return response

    finally:

        client_socket.close()


# =========================
# Registration Test
# =========================

registration_request = {
    "type": "REGISTER",
    "name": "Test Student",
    "email": "student@test.com",
    "password": "123456"
}

print("Testing registration...\n")

response = send_request(
    registration_request
)

print(response)


# =========================
# Login Test
# =========================

login_request = {
    "type": "LOGIN",
    "email": "student@test.com",
    "password": "123456"
}

print("\nTesting login...\n")

response = send_request(
    login_request
)

print(response)