import socket
from custom_packet import CustomPacket


class Server:
    def __init__(self, listen_ip, listen_port):
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection_established = False
        self.client_address = None
        self.last_processed_sequence_num = -1

    def start(self):
        """
        Start the server to listen for incoming client connections and messages.
        """
        self.socket.bind((self.listen_ip, self.listen_port))
        print(f"Server listening on {self.listen_ip}:{self.listen_port}")

        try:
            while True:
                # Receive a packet
                packet, addr = self.socket.recvfrom(1024)
                parsed_packet = CustomPacket.parse_packet(packet.decode())
                flag = parsed_packet["flag"]

                if not self.connection_established:
                    # Handle initial SYN for connection establishment
                    if flag == "SYN" and parsed_packet["payload"] == "":
                        print(f"Received SYN from {addr} with payload: {parsed_packet['payload']}")
                        print(f"Connection established with client at {addr}")
                        self.connection_established = True
                        self.client_address = addr

                        # Send ACK
                        ack_packet = CustomPacket(seq_num=1, ack_num=parsed_packet["sequence_num"] + 1)
                        ack_payload = ack_packet.create_packet_payload("ACK", "")
                        self.socket.sendto(ack_payload.encode(), addr)
                        print("Sent ACK.")
                    else:
                        print(f"Unexpected packet from {addr} during connection establishment. Ignoring.")

                elif self.connection_established and addr == self.client_address:
                    # Handle SYN + Payload (messages)
                    if flag == "SYN" and parsed_packet["payload"] != "":
                        # Check for duplicate sequence numbers
                        if parsed_packet["sequence_num"] <= self.last_processed_sequence_num:
                            print(f"Ignoring duplicate message: {parsed_packet['payload']}")
                            continue

                        print(f"Received message: {parsed_packet['payload']} from {addr}")
                        self.last_processed_sequence_num = parsed_packet["sequence_num"]

                        # Send ACK for the message
                        ack_packet = CustomPacket(seq_num=parsed_packet["sequence_num"] + 1,
                                                  ack_num=parsed_packet["sequence_num"] + 1)
                        ack_payload = ack_packet.create_packet_payload("ACK", "")
                        self.socket.sendto(ack_payload.encode(), addr)
                        print("Sent ACK.")

                    # Handle FIN to close connection
                    elif flag == "FIN":
                        print(f"Received FIN from {addr}. Closing connection.")
                        self.connection_established = False
                        self.client_address = None
                        break  # Exit the server loop

        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            self.socket.close()
            print("Server socket closed.")


# Entry point
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Server")
    parser.add_argument("--listen-ip", required=True, help="IP address to bind the server")
    parser.add_argument("--listen-port", type=int, required=True, help="Port number to listen on")
    args = parser.parse_args()

    server = Server(args.listen_ip, args.listen_port)
    server.start()
