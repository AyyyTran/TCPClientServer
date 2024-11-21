import socket
from customPacket import CustomPacket
class ReliableProtocol:
# Protocol class to manage packets
    def __init__(self):
        self.packets = []
        # self.sequence_num = 0
        self.acknowledgment_num = 0

    def connect(self, socket, target_ip, taget_port_num):
        # packet = CustomPacket(sequence_num, acknowledgment_num)
        # packet.create_header()
        # packet_payload = packet.create_packet_payload(message)
        # socket.sendto(packet_payload.encode(), (target_ip, taget_port_num))
        # self.packets.append(packet)

        # Yep so basically I made a function in sutom protocol to create the packet instead
        # And then now Im using custom send and recieve functions in this class
        self.send(socket, "",  target_ip, taget_port_num)

        flag, response ,sender_address  = self.recieve(socket)
        if flag:
            # flag = message[0:3]
            # self.acknowledgment_num += 1
            if flag == "ACK":
            #     print("Server responded with ACK")
                self.acknowledgment_num += 1
                print("connection established")

            

    def accept(self, socket):
        # # seq_num = 0
        # if self.packets:
        #     # seq_num = self.packets[0].sequence_num
        #     seq_num = self.packets[0].sequence_num
        flag, message,sender_address = self.recieve(socket)
        # print("Flag: " + flag)
        # print(message)
        if "SYN" == flag and self.acknowledgment_num == 0:
            print("SYN packet recieved")
            self.acknowledgment_num += 1
            self.send(socket, "", sender_address)
            print("accepting ACk sent")

   
    def send(self, socket,message,target_ip_addr, target_port_num = None):
        # packet = CustomPacket(self.sequence_num, self.acknowledgment_num)
        packet = CustomPacket(self.acknowledgment_num)
        packet_payload = packet.create_payload(message)
        print("sent Payload: " + packet_payload)
        encoded_payload = packet_payload.encode()
        target_info = target_ip_addr
        if target_port_num:
            target_info = (target_ip_addr, target_port_num) 
        socket.sendto(encoded_payload, target_info)

 
    def recieve(self, socket):
        byte_message, sender_address = socket.recvfrom(1024)
        flag, message = CustomPacket.unpack_packet(byte_message)
        print("recieved payload: " + byte_message.decode())
        return flag, message, sender_address
        
        

    def close(socket):
        socket.close()