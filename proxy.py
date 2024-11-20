import socket
import argparse
from custom_packet import CustomPacket


class Proxy:
    def __init__(self, listen_ip, listen_port, target_ip, target_port):
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.target_ip = target_ip
        self.target_port = target_port
        self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.proxy_socket.bind((self.listen_ip, self.listen_port))
        print(f"Proxy listening on {self.listen_ip}:{self.listen_port}")

    def start(self):
        print("Proxy started. Intercepting traffic...")
        while True:
            try:
                # Intercept packet from Client → Proxy → Server
                print("Waiting for a packet from the client...")
                client_packet, client_address = self.proxy_socket.recvfrom(1024)
                print(f"Received packet from client: {client_packet.decode()}")
                self.proxy_socket.sendto(client_packet, (self.target_ip, self.target_port))
                print(f"Forwarded packet to server at {self.target_ip}:{self.target_port}")

                # Intercept packet from Server → Proxy → Client
                print("Waiting for a packet from the server...")
                server_packet, server_address = self.proxy_socket.recvfrom(1024)
                print(f"Received packet from server: {server_packet.decode()}")
                self.proxy_socket.sendto(server_packet, client_address)
                print(f"Forwarded packet to client at {client_address}")
            except KeyboardInterrupt:
                print("\nProxy shutting down.")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Proxy to forward packets between client and server")
    parser.add_argument("--listen-ip", type=str, required=True, help="IP address for proxy to listen on")
    parser.add_argument("--listen-port", type=int, required=True, help="Port for proxy to listen on")
    parser.add_argument("--target-ip", type=str, required=True, help="Target server's IP address")
    parser.add_argument("--target-port", type=int, required=True, help="Target server's port")
    args = parser.parse_args()

    proxy = Proxy(
        listen_ip=args.listen_ip,
        listen_port=args.listen_port,
        target_ip=args.target_ip,
        target_port=args.target_port
    )
    proxy.start()
