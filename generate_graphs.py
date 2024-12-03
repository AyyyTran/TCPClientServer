import pandas as pd
import matplotlib.pyplot as plt

# Load client, proxy, and server logs
client_log = pd.read_csv("client_log.csv")
proxy_log = pd.read_csv("proxy_log.csv")
server_log = pd.read_csv("server_log.csv")

def generate_bar_chart(data, title, labels, colors):
    """
    Helper function to generate and display a color-coded bar chart.
    """
    plt.figure(figsize=(10, 6))
    plt.bar(labels, data, color=colors)
    plt.title(title)
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()  # Display the graph

# CLIENT LOG ANALYSIS
client_sent = client_log[client_log["Event"] == "Packet Sent"].shape[0]
client_acks = client_log[client_log["Event"] == "ACK Received"].shape[0]
client_retransmissions = client_log[client_log["Event"] == "Packet Retransmitted"].shape[0]  # Retransmissions

# PROXY LOG ANALYSIS
proxy_received_client = proxy_log[proxy_log["Direction"] == "Client->Server"].shape[0]
proxy_dropped_client = proxy_log[(proxy_log["Direction"] == "Client->Server") & (proxy_log["Event"] == "Packet Dropped")].shape[0]
proxy_forwarded_client = proxy_received_client - proxy_dropped_client  # Forwarded = Received - Dropped

proxy_received_server = proxy_log[proxy_log["Direction"] == "Server->Client"].shape[0]
proxy_dropped_server = proxy_log[(proxy_log["Direction"] == "Server->Client") & (proxy_log["Event"] == "Packet Dropped")].shape[0]
proxy_forwarded_server = proxy_received_server - proxy_dropped_server  # Forwarded = Received - Dropped

# SERVER LOG ANALYSIS
server_received = server_log[server_log["Event"] == "Packet Received"].shape[0]
server_duplicates = server_log[server_log["Event"] == "Duplicate Packet Detected"].shape[0]
server_acks_sent = server_log[server_log["Event"] == "ACK Sent"].shape[0]

# GRAPH 1: Client Overview (Sent vs. ACKs Received vs. Retransmissions)
generate_bar_chart(
    [client_sent, client_acks, client_retransmissions],
    "Client Overview: Packets Sent vs. ACKs Received vs. Retransmissions",
    ["Sent", "ACKs Received", "Retransmissions"],
    ["green", "blue", "orange"]
)

# GRAPH 2: Proxy Overview (Client->Server)
generate_bar_chart(
    [proxy_received_client, proxy_dropped_client, proxy_forwarded_client],
    "Proxy Overview: Packets Received vs. Dropped vs. Forwarded (Client->Server)",
    ["Received", "Dropped", "Forwarded"],
    ["green", "red", "blue"]
)

# GRAPH 3: Proxy Overview (Server->Client)
generate_bar_chart(
    [proxy_received_server, proxy_dropped_server, proxy_forwarded_server],
    "Proxy Overview: Packets Received vs. Dropped vs. Forwarded (Server->Client)",
    ["Received", "Dropped", "Forwarded"],
    ["green", "red", "blue"]
)

# GRAPH 4: Server Overview (Received vs. Duplicates vs. ACKs Sent)
generate_bar_chart(
    [server_received, server_duplicates, server_acks_sent],
    "Server Overview: Packets Received vs. Duplicates vs. ACKs Sent",
    ["Received", "Duplicates", "ACKs Sent"],
    ["green", "red", "blue"]
)

print("Graphs updated. Screenshot as needed!")
