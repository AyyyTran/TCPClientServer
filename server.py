import argparse
import socket
import sys
import csv
import time
from reliableProtocol import ReliableProtocol

# Open log file for server events
log_file = open("server_log.csv", "w", newline="")
log_writer = csv.writer(log_file)
log_writer.writerow(["Timestamp", "Event", "Seq_Num", "Message"])

def log_event(event, seq_num, message=""):
    """
    Log events to the CSV file.
    Tracks events like packets received, processed, and duplicate packets detected.
    """
    log_writer.writerow([time.time(), event, seq_num, message])

def start_server(listen_ip, listen_port):
    reliable_protocol = ReliableProtocol()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((listen_ip, listen_port))
    print(f"Server listening on {listen_ip}:{listen_port}")

    try:
        while True:
            flag, seq, message, sender_address = reliable_protocol.recieve(server_socket)
            log_event("Packet Received", seq, message)  # Log packet reception
            print(f"Server: Received packet - Flag: {flag}, Seq: {seq}, Message: {message}")

            if flag == "SYN":
                reliable_protocol.accept()
                log_event("Connection Established", seq, "")  # Log connection establishment

            # Check if the packet is new or a duplicate
            packet_added = reliable_protocol.packet_added(flag, seq, message)
            if packet_added:
                print(f"Server: Packet with Seq: {seq} added successfully.")
                log_event("Packet Processed", seq, message)  # Log packet processing
                if flag == "SYN":
                    print("Accepting ACK sent")
                else:
                    print(f"Server: Received message: {message}")
                    print("Server: Sending back ACK")
                seq += 1
                reliable_protocol.send(server_socket, "", seq, sender_address)
                log_event("ACK Sent", seq)  # Log ACK sent
            else:
                print(f"Server: Duplicate packet with Seq: {seq}, dropping.")
                log_event("Duplicate Packet Detected", seq, message)  # Log duplicate packet
                if reliable_protocol.packets:
                    resend_seq = reliable_protocol.packets[-1].sequence_num + 1
                    print(f"Server: Resending ACK for Seq: {resend_seq}")
                    reliable_protocol.send(server_socket, "", resend_seq, sender_address)
                    log_event("ACK Resent", resend_seq)  # Log ACK resent
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Closing server socket...")
    finally:
        # Close the server socket and log file
        server_socket.close()
        log_file.close()  # Ensure log file is closed properly
        print("Server socket closed. Exiting...")

def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--listen-ip", type=str, required=True)
    parser.add_argument("--listen-port", type=int, required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    arguments = parse_arguments()
    start_server(arguments.listen_ip, arguments.listen_port)
