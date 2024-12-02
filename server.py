import argparse
import socket
import sys

from reliableProtocol import ReliableProtocol 

def start_server(listen_ip, listen_port):
    reliable_protocol = ReliableProtocol()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((listen_ip, listen_port))
    print(f"Server listening on {listen_ip}:{listen_port}")

    try:
        while True:
            flag, seq, message, sender_address = reliable_protocol.recieve(server_socket)
            if flag == "SYN":
                reliable_protocol.accept()
            packet_added = reliable_protocol.packet_added(flag, seq, message)
            
            if packet_added:
                if flag == "SYN":
                    print("Accepting ACK sent")
                else:
                    print(f"Received message: {message} from {sender_address}")
                    print("Sending back ACK")
                seq += 1
                reliable_protocol.send(server_socket, "", seq, sender_address)
            else:
                print("Duplicate packet with seq: " + str(seq) + " dropping")
                print("Resending ACK " + str(reliable_protocol.packets[-1].sequence_num + 1))
                reliable_protocol.send(server_socket, "", reliable_protocol.packets[-1].sequence_num + 1, sender_address)
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Closing server socket...")
    finally:
        server_socket.close()
        print("Server socket closed. Exiting...")



def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--listen-ip",type=str, required=True)
    parser.add_argument("--listen-port",type=int, required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    arguments = parse_arguments()
    start_server(arguments.listen_ip, arguments.listen_port)
