from custom_packet import CustomPacket
import socket
import time


class ReliableProtocol:
    def __init__(self, timeout=5, max_retries=5):
        """
        Initialize the reliable protocol with sequence and acknowledgment numbers,
        a timeout value, and maximum retries.
        """
        self.sequence_num = 0
        self.acknowledgment_num = 0
        self.timeout = timeout  # Timeout in seconds for waiting for an ACK
        self.max_retries = max_retries  # Limit retries to prevent infinite loops

    def connect(self, socket, target_ip, target_port):
        """
        Establish a connection using a SYN handshake.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                # Step 1: Send SYN without payload
                syn_packet = CustomPacket(seq_num=self.sequence_num, ack_num=0)
                syn_payload = syn_packet.create_packet_payload("SYN", "")
                socket.sendto(syn_payload.encode(), (target_ip, target_port))
                print(f"Sent SYN to {target_ip}:{target_port}")

                # Step 2: Wait for ACK
                socket.settimeout(self.timeout)
                response, _ = socket.recvfrom(1024)
                parsed_packet = CustomPacket.parse_packet(response.decode())
                if parsed_packet["flag"] == "ACK":
                    print(f"Received ACK: {response.decode()}")
                    self.acknowledgment_num = parsed_packet["sequence_num"] + 1
                    return  # Connection established
                else:
                    print("Received unexpected packet. Retrying...")
            except socket.timeout:
                retries += 1
                print(f"Timeout: No ACK received. Retrying... ({retries}/{self.max_retries})")
            except Exception as e:
                print(f"Unexpected error during connection: {type(e).__name__}: {e}")
                raise
        print("Failed to establish connection after maximum retries.")
        raise ConnectionError("Unable to connect to the server.")

    def send_message(self, socket, target_ip, target_port, message):
        """
        Send a message to the server with a SYN flag and wait for an acknowledgment.
        Retries if no acknowledgment is received within a timeout.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                # Step 1: Create and send the SYN + Payload packet
                data_packet = CustomPacket(seq_num=self.sequence_num, ack_num=self.acknowledgment_num)
                data_payload = data_packet.create_packet_payload("SYN", message)
                socket.sendto(data_payload.encode(), (target_ip, target_port))
                print(f"Sent message with SYN: {message}")

                # Step 2: Wait for ACK
                socket.settimeout(self.timeout)
                response, _ = socket.recvfrom(1024)
                parsed_packet = CustomPacket.parse_packet(response.decode())

                if parsed_packet["flag"] == "ACK" and parsed_packet["ack_num"] == self.sequence_num + 1:
                    print("Received ACK for message.")
                    self.sequence_num += 1
                    return  # Message acknowledged
                else:
                    print("Invalid ACK. Retrying...")
            except socket.timeout:
                retries += 1
                print(f"Timeout. Resending message... ({retries}/{self.max_retries})")
            except Exception as e:
                print(f"Unexpected error during message send: {type(e).__name__}: {e}")
                raise
        print("Failed to send message after maximum retries.")
        raise ConnectionError("Unable to send message to the server.")

    def close(self, socket, target_ip, target_port):
        """
        Close the connection gracefully by sending a FIN packet.
        """
        try:
            fin_packet = CustomPacket(seq_num=self.sequence_num, ack_num=self.acknowledgment_num)
            fin_payload = fin_packet.create_packet_payload("FIN", "")
            socket.sendto(fin_payload.encode(), (target_ip, target_port))
            print(f"Sent FIN to {target_ip}:{target_port}")
        except Exception as e:
            print(f"Error while closing connection: {type(e).__name__}: {e}")
