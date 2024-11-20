import argparse
import socket
import sys

from reliableProtocol import ReliableProtocol 

def start_client(target_ip, target_port, timeout_in_secs):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    reliable_protocol = ReliableProtocol()
    reliable_protocol.connect(client_socket, target_ip, target_port)
    
    # message user enters
    while True:
        message = input("Enter message to send: ")
        if not message:
            break

        # client_socket.sendto(message.encode(), (target_ip, target_port))
        reliable_protocol.send(client_socket, message, target_ip, target_port)
        # receives teh message need to increment ack here cause I have two instaces of reliabel protcol 
        
        try:
            client_socket.settimeout(timeout_in_secs)  # 2-second timeout
            # ack_message, server_address = client_socket.recvfrom(1024)
            flag, message, sender_address = reliable_protocol.recieve(client_socket)
            print(f"Acknowledgment from server: {flag}")
            # reliable_protocol.sequence_num += 1
            reliable_protocol.acknowledgment_num += 1
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
