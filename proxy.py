import socket
import argparse
import sys

def start_proxy(proxy_params):

    listen_ip_addr = proxy_params.listen_ip
    listen_port_num = proxy_params.listen_port
    target_ip_addr = proxy_params.target_ip
    target_port_num = proxy_params.target_port
    client_drop_rate = proxy_params.client_drop
    server_drop_rate = proxy_params.server_drop
    client_delay_time = proxy_params.client_delay_time
    server_delay_time = proxy_params.server_delay_time

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((listen_ip_addr, listen_port_num))
    print(f"Proxy send/recv to client on {listen_ip_addr}:{listen_port_num}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((target_ip_addr, target_port_num))
    print(f"Proxy will send/recv to server on {target_ip_addr}:{target_port_num}")

    while True:
        # message recieved from client
        message, client_address = client_socket.recvfrom(1024)  # buffer size 1024 bytes
        print(f"Received message: {message.decode()} from {client_address}")
        # Add client delay and drop functions here to do before sending 

        server_socket.sendto(message.encode(), (target_ip_addr, target_port_num))

        


        # server ACK response
        message, server_address = server_socket.recvfrom(1024)  # buffer size 1024 bytes
        print(f"Received ack: {message.decode()} from {server_address}")
        # Add server delay and drop functions here to do before sending 
        
        client_socket.send(message)

# Parsing arguments
def parse_arguments():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--listen-ip",type=str, required=True)
    parser.add_argument("--listen-port",type=int, required=True)
    parser.add_argument("--target-ip",type=str, required=True)
    parser.add_argument("--target-port",type=int, required=True)
    # Made rest of args optional for now change to required later
    parser.add_argument("--client-drop",type=int)
    parser.add_argument("--server-drop",type=int)
    parser.add_argument("--client-delay",type=int)
    parser.add_argument("--server-delay",type=int) 
    parser.add_argument("--client-delay-time",type=int) 
    parser.add_argument("--server-delay-time",type=int) 
    # parser.print_help()
    # print("\n")
    args = parser.parse_args()
    print(args)
    return args

if __name__ == "__main__":
    arguments = parse_arguments()
    start_proxy(arguments)