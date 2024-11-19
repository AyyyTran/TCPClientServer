import argparse
import socket
import sys

from reliableProtocol import ReliableProtocol 

def start_server(listen_ip, listen_port):
    reliable_protocol = ReliableProtocol()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((listen_ip, listen_port))
    print(f"Server listening on {listen_ip}:{listen_port}")

    reliable_protocol.accept(server_socket)
    # message user recieves
    while True:
        message, client_address = server_socket.recvfrom(1024)  # buffer size 1024 bytes
        print(f"Received message: {message.decode()} from {client_address}")
        
        ack_message = "ACK"
        server_socket.sendto(ack_message.encode(), client_address)

def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--listen-ip",type=str, required=True)
    parser.add_argument("--listen-port",type=int, required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    arguments = parse_arguments()
    start_server(arguments.listen_ip, arguments.listen_port)
