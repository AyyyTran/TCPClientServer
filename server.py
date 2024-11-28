import argparse
import socket
import sys

from reliableProtocol import ReliableProtocol 

def start_server(listen_ip, listen_port, timeout_in_secs):
    reliable_protocol = ReliableProtocol()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((listen_ip, listen_port))
    print(f"Server listening on {listen_ip}:{listen_port}")

    reliable_protocol.accept(server_socket)
    # message user recieves

    while True:
        try:
            server_socket.settimeout(timeout_in_secs) 
            # message, client_address = server_socket.recvfrom(1024)  # buffer size 1024 bytes
            # flag, message, sender_address = reliable_protocol.recieve(server_socket) 
            flag, ack, message, sender_address  = reliable_protocol.recieve(server_socket)
            packet_added = reliable_protocol.packet_added(flag, ack, message)

            if packet_added:
                print(f"Received message: {message} from {sender_address}")
                ack += 1

                reliable_protocol.send(server_socket, "",ack, sender_address)
                print("sending back ACK")
            else:
                print("Duplicate packet with ack" + str(ack) + " dropping")
            # ack_message = "ACK"
            # server_socket.sendto(ack_message.encode(), client_address)
        except socket.timeout:
            # Handle timeout by resending the last acknowledgment
                print("No acknowledgment received. Timeout!")
                reliable_protocol.send(server_socket, "", ack, sender_address)
                print(f"Timeout! Resending ACK {ack} to {sender_address}")


def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--listen-ip",type=str, required=True)
    parser.add_argument("--listen-port",type=int, required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    arguments = parse_arguments()
    start_server(arguments.listen_ip, arguments.listen_port, timeout_in_secs=2)