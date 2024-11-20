import socket
import random
import time
import argparse
from custom_packet import CustomPacket


class Proxy:
    def __init__(self, listen_ip, listen_port, target_ip, target_port,
                 client_drop=0, server_drop=0, client_delay=0, server_delay=0,
                 client_delay_time=0, server_delay_time=0):
        """
        Initialize the proxy with drop and delay probabilities and time settings.
        """
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.target_ip = target_ip
        self.target_port = target_port
        self.client_drop = client_drop
        self.server_drop = server_drop
        self.client_delay = client_delay
        self.server_delay = server_delay
        self.client_delay_time = client_delay_time
        self.server_delay_time = server_delay_time

        self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.proxy_socket.bind((self.listen_ip, self.listen_port))
        print(f"Proxy listening on {self.listen_ip}:{self.listen_port}")

    def should_apply(self, chance):
        """
        Determine if an event should occur based on probability (0-100).
        """
        return random.randint(1, 100) <= chance

    def introduce_delay(self, delay_time):
        """
        Introduce a delay in milliseconds.
        """
        time.sleep(delay_time / 1000)  # Convert milliseconds to seconds

    def start(self):
        """
        Start the proxy to handle packet forwarding with drops and delays.
        """
        print("Proxy started. Intercepting traffic...")
        while True:
            try:
                # Intercept packet from Client → Proxy → Server
                print("Waiting for a packet from the client...")
                client_packet, client_address = self.proxy_socket.recvfrom(1024)
                print(f"Received packet from client: {client_packet.decode()}")

                # Parse the packet
                parsed_packet = CustomPacket.parse_packet(client_packet.decode())
                flag = parsed_packet["flag"]

                # Log flag and payload for debugging
                print(f"Packet flag: {flag}, Payload: {parsed_packet['payload']}")

                # Forward initial SYN (Connection Establishment)
                if flag == "SYN" and parsed_packet["payload"] == "":
                    print("Forwarding initial SYN to server...")
                    self.proxy_socket.sendto(client_packet, (self.target_ip, self.target_port))
                    continue

                # Apply drop/delay logic for SYN + Payload (Message)
                if flag == "SYN" and parsed_packet["payload"] != "":
                    if self.should_apply(self.client_drop):
                        print("Dropped client message packet.")
                        continue

                    if self.should_apply(self.client_delay):
                        print(f"Delaying client message packet by {self.client_delay_time} ms...")
                        self.introduce_delay(self.client_delay_time)

                    self.proxy_socket.sendto(client_packet, (self.target_ip, self.target_port))
                    print(f"Forwarded client message: {parsed_packet['payload']} to server.")

                # Intercept packet from Server → Proxy → Client
                print("Waiting for a packet from the server...")
                server_packet, server_address = self.proxy_socket.recvfrom(1024)
                print(f"Received packet from server: {server_packet.decode()}")

                # Parse the server packet
                parsed_server_packet = CustomPacket.parse_packet(server_packet.decode())
                server_flag = parsed_server_packet["flag"]

                # Apply drop/delay logic for ACKs
                if server_flag == "ACK":
                    if self.should_apply(self.server_drop):
                        print("Dropped server ACK.")
                        continue

                    if self.should_apply(self.server_delay):
                        print(f"Delaying server ACK by {self.server_delay_time} ms...")
                        self.introduce_delay(self.server_delay_time)

                    self.proxy_socket.sendto(server_packet, client_address)
                    print("Forwarded server ACK to client.")

            except KeyboardInterrupt:
                print("\nProxy shutting down.")
                break
            except Exception as e:
                print(f"Error during proxy operation: {type(e).__name__}: {e}")



# Entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Proxy")
    parser.add_argument("--listen-ip", type=str, required=True, help="IP address for proxy to listen on")
    parser.add_argument("--listen-port", type=int, required=True, help="Port for proxy to listen on")
    parser.add_argument("--target-ip", type=str, required=True, help="Target server's IP address")
    parser.add_argument("--target-port", type=int, required=True, help="Target server's port")
    parser.add_argument("--client-drop", type=int, default=0, help="Drop chance (0-100) for client packets")
    parser.add_argument("--server-drop", type=int, default=0, help="Drop chance (0-100) for server ACKs")
    parser.add_argument("--client-delay", type=int, default=0, help="Delay chance (0-100) for client packets")
    parser.add_argument("--server-delay", type=int, default=0, help="Delay chance (0-100) for server ACKs")
    parser.add_argument("--client-delay-time", type=int, default=0, help="Delay time in ms for client packets")
    parser.add_argument("--server-delay-time", type=int, default=0, help="Delay time in ms for server ACKs")
    args = parser.parse_args()

    proxy = Proxy(
        listen_ip=args.listen_ip,
        listen_port=args.listen_port,
        target_ip=args.target_ip,
        target_port=args.target_port,
        client_drop=args.client_drop,
        server_drop=args.server_drop,
        client_delay=args.client_delay,
        server_delay=args.server_delay,
        client_delay_time=args.client_delay_time,
        server_delay_time=args.server_delay_time
    )
    proxy.start()
