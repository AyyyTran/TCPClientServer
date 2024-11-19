import argparse
import socket
import sys

from reliableProtocol import ReliableProtocol 

def start_client(target_ip, target_port, timeout_in_secs):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    reliable_protocol = ReliableProtocol()
    reliable_protocol.connect(client_socket, target_ip, target_port)

    while True:
        message = input("Enter message to send: ")
        if not message:
            break

        client_socket.sendto(message.encode(), (target_ip, target_port))

        try:
            client_socket.settimeout(timeout_in_secs)  # 2-second timeout
            ack_message, server_address = client_socket.recvfrom(1024)
            print(f"Acknowledgment from server: {ack_message.decode()}")
        except socket.timeout:
            print("No acknowledgment received. Timeout!")

def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--target-ip",type=str, required=True)
    parser.add_argument("--target-port",type=int, required=True)
    # timput has default value of 2 and optional for now make required
    parser.add_argument("--timeout",type=int, default=2)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    arguments = parse_arguments()
    start_client(arguments.target_ip, arguments.target_port,arguments.timeout)
