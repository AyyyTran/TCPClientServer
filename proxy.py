import socket



def start_proxy(self, proxy_params):

    listen_ip_addr = proxy_params.listen_ip_addr
    listen_port_num = proxy_params.listen_port_num
    target_ip_addr = proxy_params.target_ip_addr
    target_port_num = proxy_params.target_port_num
    client_drop_rate = proxy_params.client_drop_rate
    server_drop_rate = proxy_params.server_drop_rate
    client_delay_rate = proxy_params.client_delay_rate
    server_delay_rate = proxy_params.client_delay_rate
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

if __name__ == "__main__":
    start_proxy("0.0.0.0", 5000)