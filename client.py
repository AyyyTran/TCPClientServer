import socket
from reliable_protocol import ReliableProtocol
import argparse


class Client:
    def __init__(self, server_ip, server_port, timeout=5):
        """
        Initialize the client with server details.
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = ReliableProtocol(timeout=self.timeout)

    def connect(self):
        """
        Establish a connection to the server.
        """
        try:
            print("Connecting to server...")
            self.protocol.connect(self.socket, self.server_ip, self.server_port)
            print("Connected to server.")
        except Exception as e:
            print(f"Error during connection: {e}")
            self.close()
            exit(1)

    def send_message(self):
        """
        Continuously prompt the user to send messages to the server.
        """
        try:
            while True:
                # Prompt the user for input
                message = input("Enter message to send (or type 'exit' to quit): ")
                if message.lower() == "exit":
                    print("Exiting...")
                    break

                # Send the message with SYN + Payload
                self.protocol.send_message(self.socket, self.server_ip, self.server_port, message)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Closing connection.")
        finally:
            self.close()

    def close(self):
        """
        Close the client socket and gracefully terminate the connection.
        """
        try:
            self.protocol.close(self.socket, self.server_ip, self.server_port)
        except Exception as e:
            print(f"Error during disconnection: {e}")
        finally:
            self.socket.close()
            print("Client socket closed.")


# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client")
    parser.add_argument("--server-ip", required=True, help="IP address of the server")
    parser.add_argument("--server-port", type=int, required=True, help="Port number of the server")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds for message acknowledgment")
    args = parser.parse_args()

    client = Client(args.server_ip, args.server_port, timeout=args.timeout)
    client.connect()
    client.send_message()
