import socket

# =========================
# Server Configuration
# =========================

# Enter the IPv4 address of PC1 (server) here
SERVER_HOST = "192.168.0.108"   # CHANGE THIS
SERVER_PORT = 5000


# =========================
# TCP Client
# =========================

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("=" * 50)
        print("Campus LAN Student Help Request System")
        print("TCP Client")
        print("=" * 50)

        print(f"\nConnecting to server: {SERVER_HOST}:{SERVER_PORT}")

        client_socket.connect((SERVER_HOST, SERVER_PORT))

        print("Connected to server successfully!")

        # Send test message
        message = "HELLO_SERVER"

        client_socket.sendall(message.encode("utf-8"))

        print(f"Sent to server: {message}")

        # Receive response
        data = client_socket.recv(1024)

        if data:
            response = data.decode("utf-8")
            print(f"Received from server: {response}")

        print("\nTCP communication test completed successfully.")

    except ConnectionRefusedError:
        print("\nERROR: Connection refused.")
        print("Check whether the server is running on PC1.")

    except TimeoutError:
        print("\nERROR: Connection timed out.")
        print("Check the server IP, LAN connection and firewall.")

    except OSError as e:
        print(f"\nNETWORK ERROR: {e}")

    finally:
        client_socket.close()
        print("\nConnection closed.")


# =========================
# Main
# =========================

if __name__ == "__main__":
    start_client()