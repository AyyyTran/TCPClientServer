import socket
from reliable_protocol import ReliableProtocol


class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = ReliableProtocol(timeout=5, max_retries=5)

    def connect(self):
        try:
            print("Connecting to server...")
            # Establish connection using the protocol
            self.protocol.connect(self.socket, self.server_ip, self.server_port, "")
            print("Connected to server.")
        except Exception as e:
            print(f"Error during connection: {type(e).__name__}, {e}")

    def send_message(self):
        while True:
            try:
                # Prompt the user for a message
                message = input("Enter message to send (or type 'exit' to quit): ")
                if message.lower() == "exit":
                    break

                # Use the reliable protocol to send the message
                self.protocol.send_message(self.socket, self.server_ip, self.server_port, message)
                print(f"Message '{message}' sent successfully.")
            except Exception as e:
                print(f"Error during message transmission: {type(e).__name__}, {e}")

    def close(self):
        print("Closing client socket...")
        self.socket.close()
        print("Client socket closed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Client to connect to server through proxy")
    parser.add_argument("--server-ip", type=str, required=True, help="Server's IP address")
    parser.add_argument("--server-port", type=int, required=True, help="Server's port")
    args = parser.parse_args()

    client = Client(args.server_ip, args.server_port)
    client.connect()
    client.send_message()
    client.close()
