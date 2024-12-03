import argparse
import socket
import sys

from reliableProtocol import ReliableProtocol 

def start_client(target_ip, target_port, timeout_in_secs):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    reliable_protocol = ReliableProtocol()

    try:
        reliable_protocol.connect(client_socket, target_ip, target_port, timeout_in_secs)
        timeout_limit = 10
        counter = 0
        # message user enters
        while True:
            try:
                message = input("Enter message to send: ")
                if not message:
                    print("Message can't be empty! Please enter some text.")
                    continue
                seq_num = reliable_protocol.packets[-1].sequence_num
                print("sending packet with seq: " + str(seq_num))
                # client_socket.sendto(message.encode(), (target_ip, target_port))
                # print(reliable_protocol.packets)
                for packet in reliable_protocol.packets:
                    print(packet)
                    print(packet.sequence_num)
                reliable_protocol.send(client_socket, message,seq_num, target_ip, target_port)
                client_socket.settimeout(timeout_in_secs) 
                # Need while looop so client recieves the ack back from first response otherwise doesnt
                while True:
                    if (counter == timeout_limit):
                        print("Resent packet " + str(timeout_limit) + " times.")
                        print("\nLimit reached. Closing client connection...")
                        client_socket.close()
                        sys.exit("Client socket closed. Exiting...")
                    try:
                        # ack_message, server_address = client_socket.recvfrom(1024)
                        # flag, message, sender_address = reliable_protocol.recieve(client_socket)
                        flag,seq, message, sender_address  = reliable_protocol.recieve(client_socket)
                        print("Seq from server:" + str(seq))
                        packet_added = reliable_protocol.packet_added(flag, seq, message)
                        if packet_added:
                            print(f"Acknowledgment from server: {flag}: {seq}")
                            counter = 0
                            break
                    except socket.timeout:
                        print("No acknowledgment received. Timeout!")
                        reliable_protocol.send(client_socket, message,seq_num, target_ip, target_port)
                        counter+=1
                        print("Resending message: " + message)
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully inside the loop
                print("\nCtrl+C detected while waiting for input. Closing client connection...")
                client_socket.close()
                sys.exit("Client socket closed. Exiting...")
    except KeyboardInterrupt:
                # Handle Ctrl+C gracefully inside the loop
                print("\nCtrl+C detected while running. Closing client connection...")
                client_socket.close()
                sys.exit("Client socket closed. Exiting...")
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred: {e}")
        
        

def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--target-ip",type=str, required=True)
    parser.add_argument("--target-port",type=int, required=True)
    parser.add_argument("--timeout",type=int, default=2)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    try:
        # Parse command-line arguments and start the client
        arguments = parse_arguments()
        start_client(arguments.target_ip, arguments.target_port, arguments.timeout)
    except KeyboardInterrupt:
        print("\nCtrl+C detected in main. Exiting.")
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred in main: {e}")