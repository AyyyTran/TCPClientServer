import socket
import argparse
import sys
import random
import time


def should_apply(chance):
    """
    Determine if an event should occur based on probability (0-100).
    """
    return random.randint(1, 100) <= chance


def introduce_delay(delay_time):
    """
    Introduce a delay in milliseconds.
    """
    time.sleep(delay_time / 1000)  # Convert milliseconds to seconds


def start_proxy(proxy_params):
    listen_ip_addr = proxy_params.listen_ip
    listen_port_num = proxy_params.listen_port
    target_ip_addr = proxy_params.target_ip
    target_port_num = proxy_params.target_port
    client_drop_rate = proxy_params.client_drop
    server_drop_rate = proxy_params.server_drop
    client_delay_chance = proxy_params.client_delay
    server_delay_chance = proxy_params.server_delay
    client_delay_time = proxy_params.client_delay_time
    server_delay_time = proxy_params.server_delay_time

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_socket.bind((listen_ip_addr, listen_port_num))
    print(f"Proxy listening on {listen_ip_addr}:{listen_port_num}")
    print(f"Proxy forwarding to {target_ip_addr}:{target_port_num}")

    while True:
        try:
            # Intercept packet from Client to Proxy to  Server
            client_packet, client_address = proxy_socket.recvfrom(1024)
            packet_content = client_packet.decode()

            # Parse the packet
            parsed_packet = packet_content.split("|")
            flag = parsed_packet[0].strip()
            payload = parsed_packet[-1].strip()

            # Always forward connection establishment packets
            if flag == "SYN" and payload == "":
                print("Forwarding SYN for connection establishment...")
                proxy_socket.sendto(client_packet, (target_ip_addr, target_port_num))
                continue

            # Drop/Delay logic for client-to-server message packets (SYN with payload)
            if should_apply(client_drop_rate):
                print(f"Client message packet dropped: {packet_content}")
                continue
            if should_apply(client_delay_chance):
                print(f"Delaying client message packet by {client_delay_time} ms: {packet_content}")
                introduce_delay(client_delay_time)

            # Forward client packet to the server
            print(f"Forwarding client packet to server: {packet_content}")
            proxy_socket.sendto(client_packet, (target_ip_addr, target_port_num))

            # Intercept packet from Server → Proxy → Client
            server_packet, server_address = proxy_socket.recvfrom(1024)
            packet_content = server_packet.decode()

            # Parse the packet
            parsed_server_packet = packet_content.split("|")
            server_flag = parsed_server_packet[0].strip()
            server_payload = parsed_server_packet[-1].strip()

            # Always forward connection establishment ACK packets
            if server_flag == "ACK" and server_payload == "":
                print("Forwarding ACK for connection establishment...")
                proxy_socket.sendto(server_packet, client_address)
                continue

            # Drop/Delay logic for server-to-client message ACKs
            if should_apply(server_drop_rate):
                print(f"Server ACK packet dropped: {packet_content}")
                continue
            if should_apply(server_delay_chance):
                print(f"Delaying server ACK packet by {server_delay_time} ms: {packet_content}")
                introduce_delay(server_delay_time)

            # Forward server packet to the client
            print(f"Forwarding server packet to client: {packet_content}")
            proxy_socket.sendto(server_packet, client_address)

        except KeyboardInterrupt:
            print("\nProxy shutting down.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Proxy with drop and delay simulation")
    parser.add_argument("--listen-ip", type=str, required=True, help="Proxy listen IP")
    parser.add_argument("--listen-port", type=int, required=True, help="Proxy listen port")
    parser.add_argument("--target-ip", type=str, required=True, help="Target server IP")
    parser.add_argument("--target-port", type=int, required=True, help="Target server port")
    parser.add_argument("--client-drop", type=int, default=0, help="Drop chance for client packets (0-100)")
    parser.add_argument("--server-drop", type=int, default=0, help="Drop chance for server packets (0-100)")
    parser.add_argument("--client-delay", type=int, default=0, help="Delay chance for client packets (0-100)")
    parser.add_argument("--server-delay", type=int, default=0, help="Delay chance for server packets (0-100)")
    parser.add_argument("--client-delay-time", type=int, default=0, help="Delay time for client packets (ms)")
    parser.add_argument("--server-delay-time", type=int, default=0, help="Delay time for server packets (ms)")
    args = parser.parse_args()

    start_proxy(args)
