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


def reconfigure_settings(settings):
    user_option = input("To change settings press 1 and hit enter: ") 
    if user_option == "1":
        print("If you want to leave a setting unchanged leave it blank and hit enter")
        listen_ip = input("listen port: ")
        if listen_ip:
            settings["listen_ip"] = listen_ip

        listen_port = input("listen port: ") 
        if listen_port:
            settings["listen_port"] = int(listen_port)

        target_ip = input("target ip: ")
        if target_ip:
            settings["target_ip"] = target_ip

        target_port = input("target port: ")
        if target_port:
            settings["target_port"] = int(target_port)

        client_drop = input("client drop rate: ")
        if client_drop:
            settings["client_drop"] = int(client_drop)

        server_drop = input("server drop rate: ")
        if server_drop:
            settings["server_drop"] = int(server_drop)

        client_delay = input("client delay rate: ")
        if client_delay:
            settings["client_delay"] = int(client_delay)

        server_delay = input("server delay rate: ")
        if server_delay:
            settings["server_delay"] = int(server_delay)
        client_delay_time = input("client delay time(ms): ")
        if client_delay_time:
            settings["client_delay_time"] = int(client_delay_time)

        server_delay_time = input("server delay time(ms): ")
        if server_delay_time:
            settings["server_delay_time"] = int(server_delay_time)

    
def intialize_settings(args):
    settings = {}  
    settings["listen_ip"] = args.listen_ip
    settings["listen_port"] = args.listen_port
    settings["target_ip"] = args.target_ip
    settings["target_port"] = args.target_port
    settings["client_drop"] = args.client_drop
    settings["server_drop"] = args.server_drop
    settings["client_delay"] = args.client_delay
    settings["server_delay"] = args.server_delay
    settings["client_delay_time"] = args.client_delay_time
    settings["server_delay_time"] = args.server_delay_time
    return settings

def start_proxy(args):
    """Start the proxy to forward packets between client and server."""

    # listen_ip = args.listen_ip
    # listen_port = args.listen_port
    # target_ip = args.target_ip
    # target_port = args.target_port
    # client_drop = args.client_drop
    # server_drop = args.server_drop
    # client_delay = args.client_delay
    # server_delay = args.server_delay
    # client_delay_time = args.client_delay_time
    # server_delay_time = args.server_delay_time
    settings = intialize_settings(args)

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_socket.bind((settings["listen_ip"], settings["listen_port"]))
    print(f"Proxy listening on {settings["listen_ip"]}:{settings["listen_port"]}")
    print(f"Proxy forwarding to {settings["target_ip"]}:{settings["target_port"]}")

    protocol = ReliableProtocol()
    client_recv_port = 0
    while True:
        try:
            # Receive packet from client or server
            packet, sender_address = proxy_socket.recvfrom(1024)
            sender_ip, sender_port = sender_address

            # Determine direction of the packet based on ip
            if sender_ip == settings["listen_ip"]:
                # Packet from client to server
                print(f"Received packet from client: {packet.decode()}")
                client_recv_port = sender_port
                # Apply drop and delay logic for client-to-server packets
                if should_apply(settings["client_drop"]):
                    print(f"Client packet dropped: {packet.decode()}")
                    continue
                if should_apply(settings["client_delay"]):
                    print(f"Delaying client packet by {settings["client_delay_time"]} ms: {packet.decode()}")
                    introduce_delay(settings["client_delay_time"])

                # Forward to server
                forward_packet(proxy_socket, protocol, packet, settings["target_ip"], settings["target_port"])

            elif sender_ip == settings["target_ip"]:
                # Packet from server to client
                print(f"Received packet from server: {packet.decode()}")

                # Apply drop and delay logic for server-to-client packets
                if should_apply(settings["server_drop"]):
                    print(f"Server packet dropped: {packet.decode()}")
                    continue
                if should_apply(settings["server_delay"]):
                    print(f"Delaying server packet by {settings["server_delay_time"]} ms: {packet.decode()}")
                    introduce_delay(settings["server_delay_time"])
                # protocol.acknowledgment_num += 1
                # Forward to client changed defintion to add socket
                forward_packet(proxy_socket,protocol, packet, settings["listen_ip"], client_recv_port)
                print("\n")
                # reconfigure_settings(settings)
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
