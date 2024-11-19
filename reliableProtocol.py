import socket
from customPacket import CustomPacket
class ReliableProtocol:
# Protocol class to manage packets
    def __init__(self):
        self.packets = []

    def connect(self, socket, target_ip, taget_port_num):
        sequence_num = 0
        acknowledgment_num = 0
        message = "SYN"
        packet = CustomPacket(sequence_num, acknowledgment_num)
        packet.create_header()
        packet_payload = packet.create_packet_payload(message)
        socket.sendto(packet_payload.encode(), (target_ip, taget_port_num))
        self.packets.append(packet)

        response, server_address = socket.recvfrom(1024)
        if response:
            message = response.decode()
            flag_spit_message = message.split("Seq")
            flag = flag_spit_message[0]
            # flag = message[0:3]
            if flag == "ACK":
                print("Server responded with ACK")
            print("connection established")

            

    def accept(self, socket):
        seq_num = 0
        if self.packets:
            seq_num = self.packets[0].sequence_num
        raw_message, client_address = socket.recvfrom(1024)
        message = raw_message.decode()
        if "SYN" in message and seq_num == 0:
            packet = CustomPacket(seq_num+1, seq_num+1)
            packet.create_header()
            packet_payload = packet.create_packet_payload("")
            print("SYN packet recieved")
            socket.sendto(packet_payload.encode(), client_address)
            print("ACk sent")

    def close(socket):
        
        socket.close()