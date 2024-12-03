import argparse
import socket
import sys
import csv
import time
from reliableProtocol import ReliableProtocol 

# Open log file for client events
log_file = open("client_log.csv", "w", newline="")
log_writer = csv.writer(log_file)
log_writer.writerow(["Timestamp", "Event", "Seq_Num", "Message"])

def log_event(event, seq_num, message=""):
    """
    Log events to the CSV file.
    Tracks events like packets sent, acknowledgments received, and retransmissions.
    """
    log_writer.writerow([time.time(), event, seq_num, message])

def start_client(target_ip, target_port, timeout_in_secs):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    reliable_protocol = ReliableProtocol()

    try:
        reliable_protocol.connect(client_socket, target_ip, target_port, timeout_in_secs)
        log_event("Connection Established", 0, f"Target IP: {target_ip}, Target Port: {target_port}")
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
                
                # Log packet being sent
                log_event("Packet Sent", seq_num, message)

                # client_socket.sendto(message.encode(), (target_ip, target_port))
                # print(reliable_protocol.packets)
                for packet in reliable_protocol.packets:
                    print(packet)
                    print(packet.sequence_num)
                reliable_protocol.send(client_socket, message, seq_num, target_ip, target_port)
                client_socket.settimeout(timeout_in_secs) 
                # Need while loop so client receives the ack back from first response otherwise doesn't
                while True:
                    if (counter == timeout_limit):
                        print("Resent packet " + str(timeout_limit) + " times.")
                        print("\nLimit reached. Closing client connection...")
                        log_event("Max Retransmissions Reached", seq_num, message)
                        client_socket.close()
                        sys.exit("Client socket closed. Exiting...")
                    try:
                        # ack_message, server_address = client_socket.recvfrom(1024)
                        # flag, message, sender_address = reliable_protocol.recieve(client_socket)
                        flag, seq, message, sender_address  = reliable_protocol.recieve(client_socket)
                        print("Seq from server:" + str(seq))
                        packet_added = reliable_protocol.packet_added(flag, seq, message)
                        if packet_added:
                            print(f"Acknowledgment from server: {flag}: {seq}")
                            log_event("ACK Received", seq, message)  # Log acknowledgment received
                            counter = 0
                            break
                    except socket.timeout:
                        print("No acknowledgment received. Timeout!")
                        log_event("Timeout Occurred", seq_num, message)  # Log timeout
                        reliable_protocol.send(client_socket, message, seq_num, target_ip, target_port)
                        counter += 1
                        print("Resending message: " + message)
                        log_event("Packet Retransmitted", seq_num, message)  # Log retransmission
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully inside the loop
                print("\nCtrl+C detected while waiting for input. Closing client connection...")
                log_event("Client Terminated", -1, "Keyboard Interrupt")
                client_socket.close()
                sys.exit("Client socket closed. Exiting...")
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully inside the loop
        print("\nCtrl+C detected while running. Closing client connection...")
        log_event("Client Terminated", -1, "Keyboard Interrupt")
        client_socket.close()
        sys.exit("Client socket closed. Exiting...")
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred: {e}")
        log_event("Error", -1, str(e))
    finally:
        log_file.close()  # Ensure log file is closed

def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--target-ip", type=str, required=True)
    parser.add_argument("--target-port", type=int, required=True)
    parser.add_argument("--timeout", type=int, default=2)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    try:
        # Parse command-line arguments and start the client
        arguments = parse_arguments()
        start_client(arguments.target_ip, arguments.target_port, arguments.timeout)
    except KeyboardInterrupt:
        print("\nCtrl+C detected in main. Exiting.")
        log_event("Client Terminated", -1, "Keyboard Interrupt")
        log_file.close()
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred in main: {e}")
        log_event("Error", -1, str(e))
        log_file.close()
