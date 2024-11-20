from custom_packet import CustomPacket
import socket


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

    def connect(self, socket, target_ip, target_port, message):
        """
        Establish a connection using a SYN handshake and send the first message.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                print(f"Attempting to connect to {target_ip}:{target_port} (Retry {retries + 1}/{self.max_retries})")
                
                # Step 1: Send SYN with an optional message payload
                syn_packet = CustomPacket(seq_num=self.sequence_num, ack_num=0)
                syn_payload = syn_packet.create_packet_payload("SYN", message)
                socket.sendto(syn_payload.encode(), (target_ip, target_port))
                print(f"Sent SYN to {target_ip}:{target_port} with message: '{message}'")

                # Step 2: Wait for ACK
                socket.settimeout(self.timeout)
                response, _ = socket.recvfrom(1024)
                print(f"Received response: {response.decode()}")  # Debug the raw response

                parsed_packet = CustomPacket.parse_packet(response.decode())
                if parsed_packet["flag"] == "ACK":
                    print(f"Received ACK: {response.decode()}")
                    self.acknowledgment_num = parsed_packet["sequence_num"] + 1
                    print("Connection established successfully.")
                    return  # Connection established
                else:
                    print("Received unexpected packet. Retrying...")
            except socket.timeout:
                retries += 1
                print(f"Timeout: No ACK received. Retrying... ({retries}/{self.max_retries})")
            except Exception as e:
                print(f"Unexpected error during connection: {type(e).__name__}, {e}")
                raise
        print("Failed to establish connection after maximum retries.")
        raise ConnectionError("Unable to connect to the server.")

    def send_message(self, socket, target_ip, target_port, message):
        """
        Send a message to the server and wait for an acknowledgment.
        Retries if no acknowledgment is received within a timeout.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                print(f"Attempting to send message: {message} (Retry {retries + 1}/{self.max_retries})")

                # Step 1: Create and send the data packet
                data_packet = CustomPacket(seq_num=self.sequence_num, ack_num=self.acknowledgment_num)
                data_payload = data_packet.create_packet_payload("SYN", message)
                socket.sendto(data_payload.encode(), (target_ip, target_port))
                print(f"Sent message: {message} with Seq:{self.sequence_num}, Ack:{self.acknowledgment_num}")

                # Step 2: Wait for ACK
                socket.settimeout(self.timeout)
                response, _ = socket.recvfrom(1024)
                print(f"Received response: {response.decode()}")

                # Parse the response
                parsed_packet = CustomPacket.parse_packet(response.decode())
                if parsed_packet["flag"] == "ACK" and parsed_packet["ack_num"] == self.sequence_num + 1:
                    print(f"Received valid ACK for Seq:{self.sequence_num}.")
                    self.sequence_num += 1  # Increment sequence number for the next message
                    self.acknowledgment_num = parsed_packet["sequence_num"] + 1  # Update expected ACK
                    return  # Message acknowledged
                else:
                    print("Invalid ACK. Retrying...")
            except socket.timeout:
                retries += 1
                print(f"Timeout. Resending message... ({retries}/{self.max_retries})")
            except Exception as e:  # Properly catching exceptions
                print(f"Unexpected error during message send: {type(e).__name__}, {e}")
                raise  # Re-raise the exception to exit the loop
        print("Failed to send message after maximum retries.")
        raise ConnectionError("Unable to send message to the server.")
