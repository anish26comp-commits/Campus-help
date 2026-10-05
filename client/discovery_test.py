import socket

SERVER_IP = "192.168.0.108"    # CHANGE to PC1's actual IP
UDP_PORT = 5001


def discover_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)

    try:
        print("Sending UDP discovery request...")

        message = "DISCOVER_SERVER"

        client_socket.sendto(
            message.encode("utf-8"),
            (SERVER_IP, UDP_PORT)
        )

        data, address = client_socket.recvfrom(1024)

        response = data.decode("utf-8")

        print(f"Response received from {address}")
        print(f"Server response: {response}")

    except socket.timeout:
        print("ERROR: No UDP response received.")

    except OSError as e:
        print(f"NETWORK ERROR: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    discover_server()