from concurrent.futures import ThreadPoolExecutor
import queue
import socket
import argparse
import random
from threading import Lock, Thread
import time
import os
import sys
import csv  # Import CSV for logging
from customPacket import CustomPacket
from reliableProtocol import ReliableProtocol

# Open log file for proxy events
log_file = open("proxy_log.csv", "w", newline="")
log_writer = csv.writer(log_file)
log_writer.writerow(["Timestamp", "Event", "Direction", "Seq_Num", "Message"])

def log_event(event, direction, seq_num="", message=""):
    """
    Log events to the CSV file.
    Tracks events like packet drops, delays, and successful forwarding.
    """
    log_writer.writerow([time.time(), event, direction, seq_num, message])

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
    flag, seq_num, message = CustomPacket.unpack_packet(packet.decode())
    protocol.send(proxy_socket, message, seq_num, target_ip, target_port_num=target_port)
    log_event("Packet Forwarded", f"{target_ip}:{target_port}", seq_num, message)

def reconfigure_settings(settings):
    while True:
        user_option = input("To change settings, press 1 at any point and hit enter (or leave blank to continue): ")
        if user_option == "1":    
            print("If you want to leave a setting unchanged leave it blank and hit enter")
            listen_ip = input("listen ip: ")
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
                settings["client_delay_time"] = str(client_delay_time)

            server_delay_time = input("server delay time(ms): ")
            if server_delay_time:
                settings["server_delay_time"] = str(server_delay_time)

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

def handle_client_to_server(proxy_socket, protocol, packet, sender_address, settings, settings_lock):
    """Handle packets from client to server."""
    sender_ip, sender_port = sender_address
    print(f"Received packet from client: {packet.decode()}")
    flag, seq_num, message = CustomPacket.unpack_packet(packet.decode())
    log_event("Packet Received", "Client->Server", seq_num, message)

    with settings_lock:
        current_settings = settings.copy()

    # Apply drop logic
    if should_apply(current_settings["client_drop"]):
        print(f"Client packet dropped: {packet.decode()}")
        log_event("Packet Dropped", "Client->Server", seq_num, message)
        return

    # Apply delay logic
    if should_apply(current_settings["client_delay"]):
        delay_time = random.randint(0, int(current_settings["client_delay_time"]))
        print(f"Delaying client packet by {delay_time} ms: {packet.decode()}")
        log_event("Packet Delayed", "Client->Server", seq_num, message)
        introduce_delay(delay_time)

    # Forward to server
    print(f"Forwarding packet from client to server.")
    forward_packet(proxy_socket, protocol, packet, current_settings["target_ip"], current_settings["target_port"])

def handle_server_to_client(proxy_socket, protocol, packet, client_recv_ip, client_recv_port, settings, settings_lock):
    """Handle packets from server to client."""
    print(f"Received packet from server: {packet.decode()}")
    flag, seq_num, message = CustomPacket.unpack_packet(packet.decode())
    log_event("Packet Received", "Server->Client", seq_num, message)

    with settings_lock:
        current_settings = settings.copy()

    # Apply drop logic
    if should_apply(current_settings["server_drop"]):
        print(f"Server packet dropped: {packet.decode()}")
        log_event("Packet Dropped", "Server->Client", seq_num, message)
        return

    # Apply delay logic
    if should_apply(current_settings["server_delay"]):
        delay_time = random.randint(0, int(current_settings["server_delay_time"]))
        print(f"Delaying server packet by {delay_time} ms: {packet.decode()}")
        log_event("Packet Delayed", "Server->Client", seq_num, message)
        introduce_delay(delay_time)

    # Forward to client
    print(f"Forwarding packet from server to client.")
    forward_packet(proxy_socket, protocol, packet, client_recv_ip, client_recv_port)

def start_proxy(args):
    """Start the proxy to forward packets between client and server."""
    settings = intialize_settings(args)
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_socket.bind((settings["listen_ip"], settings["listen_port"]))
    print(f"Proxy listening on {settings['listen_ip']}:{settings['listen_port']}")
    print(f"Proxy forwarding to {settings['target_ip']}:{settings['target_port']}")

    protocol = ReliableProtocol()
    client_recv_port = 0
    client_recv_ip = 0
    settings_lock = Lock()
    reconfigure_thread = Thread(target=reconfigure_settings, args=(settings,), daemon=True)
    reconfigure_thread.start()

    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            while True:
                try:
                    packet, sender_address = proxy_socket.recvfrom(1024)
                    sender_ip, sender_port = sender_address

                    if sender_ip != settings["target_ip"]:
                        print(f"Proxy: Packet from client.")
                        client_recv_port = sender_port
                        client_recv_ip = sender_ip
                        executor.submit(handle_client_to_server, proxy_socket, protocol, packet, sender_address, settings, settings_lock)
                    elif sender_ip == settings["target_ip"]:
                        print(f"Proxy: Packet from server.")
                        executor.submit(handle_server_to_client, proxy_socket, protocol, packet, client_recv_ip, client_recv_port, settings, settings_lock)
                    else:
                        print(f"Proxy: Unknown sender: {sender_ip}")
                except socket.timeout:
                    print("Proxy: Socket timeout.")
    except KeyboardInterrupt:
        print("\nProxy: CTRL+C detected.")
    finally:
        proxy_socket.close()
        log_file.close()
        print("\nProxy socket closed. Exiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Proxy with drop and delay simulation")
    parser.add_argument("--listen-ip", type=str, required=True, help="Proxy listen IP")
    parser.add_argument("--listen-port", type=int, required=True, help="Proxy listen port")
    parser.add_argument("--target-ip", type=str, required=True, help="Target server IP address")
    parser.add_argument("--target-port", type=int, required=True, help="Target server port")
    parser.add_argument("--client-drop", type=int, default=0, choices=range(0, 101), help="Drop chance for client packets (0-100)")
    parser.add_argument("--server-drop", type=int, default=0, choices=range(0, 101), help="Drop chance for server packets (0-100)")
    parser.add_argument("--client-delay", type=int, default=0, choices=range(0, 101), help="Delay chance for client packets (0-100)")
    parser.add_argument("--server-delay", type=int, default=0, choices=range(0, 101), help="Delay chance for server packets (0-100)")
    parser.add_argument("--client-delay-time", default=0, help="Delay time for client packets (ms)")
    parser.add_argument("--server-delay-time", default=0, help="Delay time for server packets (ms)")
    args = parser.parse_args()
    start_proxy(args)
