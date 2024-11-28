import socket
import argparse
import random
import time
from customPacket import CustomPacket
from reliableProtocol import ReliableProtocol


def should_apply(chance):
    """Determine if an event should occur based on probability (0-100)."""
    return random.randint(1, 100) <= chance


def introduce_delay(delay_time):
    """Introduce a delay in milliseconds."""
    time.sleep(delay_time / 1000)  # Convert milliseconds to seconds


def forward_packet(proxy_socket, protocol, packet, target_ip, target_port=None):
    """
    Forward a packet using ReliableProtocol's send function.
    """
    print(f"Forwarding packet to {target_ip}:{target_port if target_port else 'unknown port'}")
    flag,ack, message = CustomPacket.unpack_packet(packet.decode())
    protocol.send(proxy_socket, message,ack, target_ip, target_port_num=target_port)
    

def start_proxy(args):
    """Start the proxy to forward packets between client and server."""

    listen_ip = args.listen_ip
    listen_port = args.listen_port
    target_ip = args.target_ip
    target_port = args.target_port
    client_drop = args.client_drop
    server_drop = args.server_drop
    client_delay = args.client_delay
    server_delay = args.server_delay
    client_delay_time = args.client_delay_time
    server_delay_time = args.server_delay_time

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_socket.bind((listen_ip, listen_port))
    print(f"Proxy listening on {listen_ip}:{listen_port}")
    print(f"Proxy forwarding to {target_ip}:{target_port}")

    protocol = ReliableProtocol()
    client_recv_port = 0
    while True:
        try:
            # Receive packet from client or server
            packet, sender_address = proxy_socket.recvfrom(1024)
            sender_ip, sender_port = sender_address

            # Determine direction of the packet based on ip
            if sender_ip == listen_ip:
                # Packet from client to server
                print(f"Received packet from client: {packet.decode()}")
                client_recv_port = sender_port
                # Apply drop and delay logic for client-to-server packets
                if should_apply(client_drop):
                    print(f"Client packet dropped: {packet.decode()}")
                    continue
                if should_apply(client_delay):
                    print(f"Delaying client packet by {client_delay_time} ms: {packet.decode()}")
                    introduce_delay(client_delay_time)

                # Forward to server
                forward_packet(proxy_socket, protocol, packet, target_ip, target_port)

            elif sender_ip == target_ip:
                # Packet from server to client
                print(f"Received packet from server: {packet.decode()}")

                # Apply drop and delay logic for server-to-client packets
                if should_apply(server_drop):
                    print(f"Server packet dropped: {packet.decode()}")
                    continue
                if should_apply(server_delay):
                    print(f"Delaying server packet by {server_delay_time} ms: {packet.decode()}")
                    introduce_delay(server_delay_time)
                # protocol.acknowledgment_num += 1
                # Forward to client changed defintion to add socket
                forward_packet(proxy_socket,protocol, packet, listen_ip, client_recv_port)
                print(f"Forwarded packet to client: {packet.decode()}")
                print("\n")

            else:
                print(f"Unknown sender: {sender_ip}")

        except KeyboardInterrupt:
            print("\nProxy shutting down.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Proxy with drop and delay simulation")
    parser.add_argument("--listen-ip", type=str, required=True, help="Proxy listen IP")
    parser.add_argument("--listen-port", type=int, required=True, help="Proxy listen port")
    parser.add_argument("--target-ip", type=str, required=True, help="Target server IP address")
    parser.add_argument("--target-port", type=int, required=True, help="Target server port")
    parser.add_argument("--client-drop", type=int, default=0, help="Drop chance for client packets (0-100)")
    parser.add_argument("--server-drop", type=int, default=0, help="Drop chance for server packets (0-100)")
    parser.add_argument("--client-delay", type=int, default=0, help="Delay chance for client packets (0-100)")
    parser.add_argument("--server-delay", type=int, default=0, help="Delay chance for server packets (0-100)")
    parser.add_argument("--client-delay-time", type=int, default=0, help="Delay time for client packets (ms)")
    parser.add_argument("--server-delay-time", type=int, default=0, help="Delay time for server packets (ms)")
    args = parser.parse_args()

    start_proxy(args)
