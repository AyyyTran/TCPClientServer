class CustomPacket:
    def __init__(self, seq_num, ack_num):
        self.flags = ["SYN", "ACK", "FIN", "RST"]  # Supported flags
        self.sequence_num = seq_num
        self.acknowledgment_num = ack_num
        self.header = ""

    def create_header(self, flag):
        """
        Create a packet header based on the specified flag, sequence number, and acknowledgment number.
        """
        if flag not in self.flags:
            raise ValueError(f"Invalid flag '{flag}'. Must be one of {self.flags}.")
        self.header = f"{flag}|Seq:{self.sequence_num}|Ack:{self.acknowledgment_num}"

    def create_packet_payload(self, flag, payload=""):
        """
        Combine the header and payload into a complete packet.
        """
        self.create_header(flag)  # Generate the header first
        return f"{self.header}|Payload:{payload}"

    @staticmethod
    def parse_packet(packet):
        """
        Parse a received packet into its components.
        """
        parts = packet.split("|")
        flag = parts[0]
        seq_num = int(parts[1].split(":")[1])
        ack_num = int(parts[2].split(":")[1])
        payload = parts[3].split(":")[1] if len(parts) > 3 else ""
        return {"flag": flag, "sequence_num": seq_num, "ack_num": ack_num, "payload": payload}

    def __str__(self):
        return f"CustomPacket(Header: {self.header})"
