class CustomPacket:
    def __init__(self, seq_num, ack_num):
        """
        Initialize a packet with sequence and acknowledgment numbers.
        """
        self.flags = ["SYN", "ACK", "FIN", "RST"]
        self.sequence_num = seq_num
        self.acknowledgment_num = ack_num
        self.header = ""

    def create_header(self, flag):
        """
        Create a header for the packet using the flag, sequence number, and acknowledgment number.
        """
        if flag not in self.flags:
            raise ValueError(f"Invalid flag '{flag}'. Must be one of {self.flags}.")
        self.header = f"{flag}|Seq:{self.sequence_num}|Ack:{self.acknowledgment_num}"

    def create_packet_payload(self, flag, message):
        """
        Create a full packet by combining the header with the payload.
        """
        self.create_header(flag)  # Generate the header first
        return f"{self.header}|Payload:{message}"

    @staticmethod
    def parse_packet(packet_str):
        """
        Parse a packet string into its components.
        """
        try:
            print(f"Parsing packet: {packet_str}")  # Debug the raw packet
            parts = packet_str.split('|')
            if len(parts) < 3:
                raise ValueError(f"Malformed packet: {packet_str}")
            
            flag = parts[0]
            seq_part = parts[1]
            ack_part = parts[2]
            payload = parts[3] if len(parts) > 3 else ""

            if not seq_part.startswith("Seq:") or not ack_part.startswith("Ack:"):
                raise ValueError(f"Invalid packet format: {packet_str}")

            sequence_num = int(seq_part[4:])
            acknowledgment_num = int(ack_part[4:])
            return {
                "flag": flag,
                "sequence_num": sequence_num,
                "ack_num": acknowledgment_num,
                "payload": payload
            }
        except Exception as e:
            print(f"Error while parsing packet: {type(e).__name__}, {e}")
            raise

    def __str__(self):
        """
        String representation of the packet for debugging.
        """
        return f"CustomPacket(Header: {self.header})"
