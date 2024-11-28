import socket
from customPacket import CustomPacket
class ReliableProtocol:
# Protocol class to manage packets
    def __init__(self):
        self.packets = []
        # self.sequence_num = 0
        # self.acknowledgment_num = 0

    def connect(self, socket, target_ip, taget_port_num):
        # packet = CustomPacket(sequence_num, acknowledgment_num)
        # packet.create_header()
        # packet_payload = packet.create_packet_payload(message)
        # socket.sendto(packet_payload.encode(), (target_ip, taget_port_num))
        # self.packets.append(packet)

        # Yep so basically I made a function in sutom protocol to create the packet instead
        # And then now Im using custom send and recieve functions in this class
        acknowledgement_num = 0
        self.send(socket, "",acknowledgement_num,  target_ip, taget_port_num)

        flag,ack, message, sender_address  = self.recieve(socket)
        if flag:
            # flag = message[0:3]
            # self.acknowledgment_num += 1
            if flag == "ACK":
            #     print("Server responded with ACK")
                # ack += 1
                self.packet_added(flag, ack, message)
                print("connection established")
                self.packet_added(flag, ack, message)
            

    def accept(self, socket):
        # # seq_num = 0
        # if self.packets:
        #     # seq_num = self.packets[0].sequence_num
        #     seq_num = self.packets[0].sequence_num
        flag,ack, message, sender_address  = self.recieve(socket)
        print("recieved packet")
        print("Flag: " + flag)
        print("Ack: " + str(ack))
        if "SYN" == flag and ack == 0:
            print("SYN packet recieved")
            ack += 1
            self.send(socket, "",ack, sender_address)
            print("accepting ACk sent")

   
    def send(self, socket,message,ack,target_ip_addr, target_port_num = None):
        # packet = CustomPacket(self.sequence_num, self.acknowledgment_num)
        # print("sending " + message + str(ack))
        packet = CustomPacket(ack)
        packet_payload = packet.create_payload(message)
        # print("sent packet: " + str(packet))
        # print("sent payload: " + packet_payload)
        encoded_payload = packet_payload.encode()
        target_info = target_ip_addr
        if target_port_num:
            target_info = (target_ip_addr, target_port_num) 
        socket.sendto(encoded_payload, target_info)
        # print("sent " + message + str(encoded_payload))

 
    def recieve(self, socket):
        byte_payload, sender_address = socket.recvfrom(1024)
        packet_payload = byte_payload.decode()
        flag,ack, message = CustomPacket.unpack_packet(packet_payload)
        # print("recieved payload: " + packet_payload)
        return flag,ack, message, sender_address
        
    def packet_added(self, flag,ack, message):
        packet = CustomPacket(ack)
        packet_payload = packet.create_payload(message)
        # print(self.packets)
        if self.packets:
            print("Current: " + str(packet.acknowledgment_num) + "Prev:" + str(self.packets[-1].acknowledgment_num))
        if self.packets and (packet.acknowledgment_num == self.packets[-1].acknowledgment_num):
            # print("Duplicate packet with ack" + str(ack) + " ignoring")
            return False
        else:
            self.packets.append(packet)
            # print("Adding: " + str(packet_payload))
            # print(self.packets)
            return True
    def close(socket):
        socket.close()