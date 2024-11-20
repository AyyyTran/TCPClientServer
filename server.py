import socket
from custom_packet import CustomPacket


class Server:
    def __init__(self, listen_ip, listen_port):
        """
        Initialize the server with the IP and port to listen on.
        """
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.listen_ip, self.listen_port))
        self.client_address = None
        self.sequence_num = 1  # Server's sequence number starts at 1
        self.acknowledgment_num = 0  # Acknowledgment number starts at 0

    def start(self):
        """
        Start the server to handle client communication.
        """
        print(f"Server listening on {self.listen_ip}:{self.listen_port}")
        print("Server started. Waiting for connections...")

        while True:
            try:
                # Receive a packet
                packet, client_address = self.server_socket.recvfrom(1024)
                self.client_address = client_address
                print(f"Received packet from client: {packet.decode()}")

                # Parse the packet
                parsed_packet = CustomPacket.parse_packet(packet.decode())
                flag = parsed_packet["flag"]
                payload = parsed_packet["payload"]

                # Handle SYN (Connection Establishment + First Message)
                if flag == "SYN":
                    print(f"Received SYN with payload: {payload}")
                    self.acknowledgment_num = parsed_packet["sequence_num"] + 1

                    # Log the message (if any) in the SYN payload
                    if payload:
                        print(f"Message received from client: {payload}")

                    # Send ACK
                    print("Sending ACK...")
                    ack_packet = CustomPacket(seq_num=self.sequence_num, ack_num=self.acknowledgment_num)
                    ack_payload = ack_packet.create_packet_payload("ACK", "")
                    self.server_socket.sendto(ack_payload.encode(), client_address)
                    print("ACK sent.")

                # Handle FIN (Connection Termination)
                elif flag == "FIN":
                    print("Received FIN. Closing connection...")
                    self.server_socket.close()
                    print("Server socket closed.")
                    break

            except KeyboardInterrupt:
                print("\nServer shutting down.")
                break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="UDP Server")
    parser.add_argument("--listen-ip", type=str, required=True, help="IP address for server to listen on")
    parser.add_argument("--listen-port", type=int, required=True, help="Port for server to listen on")
    args = parser.parse_args()

    server = Server(args.listen_ip, args.listen_port)
    server.start()
