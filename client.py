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
        ack_num = reliable_protocol.packets[-1].acknowledgment_num
        # client_socket.sendto(message.encode(), (target_ip, target_port))
        # print(reliable_protocol.packets)
        # for packet in reliable_protocol.packets:
        #     print(packet)
        #     print(packet.acknowledgment_num)
        reliable_protocol.send(client_socket, message,ack_num, target_ip, target_port)
        # Need while looop so client recieves the ack back from first response otherwise doesnt
        while True:
            try:
                client_socket.settimeout(timeout_in_secs)  # 2-second timeout
                # ack_message, server_address = client_socket.recvfrom(1024)
                # flag, message, sender_address = reliable_protocol.recieve(client_socket)
                flag,ack, message, sender_address  = reliable_protocol.recieve(client_socket)
                print(f"Acknowledgment from server: {flag}: {ack}")
                # reliable_protocol.sequence_num += 1
                # reliable_protocol.acknowledgment_num = ack
                reliable_protocol.packet_added(flag, ack, message)
                break
    

            except socket.timeout:
                print("No acknowledgment received. Timeout!")
                reliable_protocol.send(client_socket, message,ack_num, target_ip, target_port)
                print("Resending message: " + message)
            
            


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
