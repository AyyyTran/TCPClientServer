# Purpose

In this program we created a reliable protocol like TCP that helps achieve reliable data transmission that was tested through a client server socket communication with a malicious proxy in between that can drop and delay packets in both directions from the client or server. 

# Demo Video


https://github.com/user-attachments/assets/adf021e1-8fbb-47b6-ae32-cd9668903cfd

# Running locally

**This requires you to have three devices one will be running the client, another running the server, and the last one will be running the proxy**

### Installing
```
git clone https://github.com/AyyyTran/TCPClientServer.git
```
### Building
Make sure you have python installed on all devices by running the commands:

Ubuntu:
```
sudo apt install python3
```

Manjaro:
```
sudo pacman python3
```
### Running
Make sure you are in the source directory can go there by going:
```
Cd TCPClientServer
```
```
Cd source
```
```
Cd src
```

Once in src you can start the program

Client (all arguments required):
```
Python3 client.py --target-ip <target-ip> --target-port <port_num> -- timeout <timeout_in_secs>
```
server (all arguments required):
```
Python3 server.py --listen-ip <target-ip> --listen-port <port_num>
```

proxy (all arguments required):
```
Python3 proxy.py --target-ip <target-ip> --target-port <port_num> --listen-ip <target-ip> --listen-port <port_num>
--client-drop <client drop rate> --server-drop <server drop rate>
--client-delay <client delay rate> --server-delay 15 <server delay rate>
--client delay-time <client delay time> --server-delay-time <server delay time>
```
**make sure that each machine has the reliableProtocol.py and customPakcet.py in the
same directory as the client,server, and proxy python files**


### Command Line Arguments
| Variable           | Purpose        |   
| -------------      |:--------------:| 
| listen-ip          | IP address to listen for  |
| listen-port        | Port number to listen at     |   
| target-ip          | IP address to target       |
| target-port        | Port number to target      |
| timeout            | Timeout that client waits for before retransmitting                  |
| client-drop        | Chance of client packet to server being dropped                      |
| server-drop        | Chance of server packet to client being dropped                      |
| client-delay       | Chance of client packet to server being delayed                      |
| server-delay       | Chance of server packet to client being delayed                      |
| client-delay-time  | Time client packet to server gets delayed by (in milliseconds)       |
| server-delay-time  | Time server packet to client gets delayed by (in milliseconds)       |

# Findings

We found out that there are many ways that a transmission can be affected. For example the client can timeout and retransmit if there is a 100% drop rate on server or client direction. 
The client can also retransmit when there is a delay time longer than the client timeout server or client direction.

### Client-Drop: 0%, Server-Drop: 0%

In this configuration, all packets sent by the client are successfully forwarded by the proxy and acknowledged by the server without any issues.
Since there are no drops, the client does not need to retransmit any packets. As a result, the server does not receive any duplicate packets. 
The absence of delays or drops ensures that all packets reach their intended destination on the first attempt, and all acknowledgments are returned promptly. 
This results in smooth communication between the client and server without any packet loss or retransmissions.

### Client-Drop: 50%, Server-Drop: 50%

When both the client-to-server and server-to-client drop rates are set to 50%, about half the packets are dropped in each direction. 
This leads to retransmissions by the client whenever packets are lost during their initial attempt to reach the server. 
As a result, the server occasionally receives duplicate packets, which occur when both the retransmitted packet and the original delayed packet eventually arrive. 
The drops in both directions reduce the total number of successfully delivered packets, and the client’s need to retransmit increases network traffic.

### Client-Drop: 0%, Server-Drop: 50%

In this configuration, no packets are dropped on the client-to-server path, so the client does not need to retransmit any packets. 
As all packets successfully reach the server, there are no duplicates observed. 
However, the 50% drop rate in the server-to-client direction causes acknowledgments from the server to be lost intermittently. 
This reduces the total number of acknowledgments received by the client, but it does not affect the server’s ability to process client requests, as all initial packets are successfully received.

### Client-Drop: 100%, Server-Drop: 0%

With a 100% drop rate for client-to-server packets, every packet sent by the client is lost during its initial transmission. 
This forces the client to retransmit each packet until it successfully reaches the server. Because of these retransmissions, the server often receives duplicate packets when delayed or retransmitted packets overlap.
On the server-to-client path, all acknowledgments are forwarded without issue since no drops occur in that direction. This configuration significantly increases the number of retransmissions and duplicate packets, creating redundant network traffic.

### Client-Drop: 0%, Server-Drop: 100%

In this setup, no packets are dropped on the client-to-server path, so the client does not need to retransmit packets, and the server does not receive duplicates. However, with a 100% drop rate for server-to-client packets, all acknowledgments sent by the server are lost. As a result, the client never receives confirmation that its packets were processed. Despite this, the server processes all client packets without any issues, but the lack of acknowledgments can make the client appear unresponsive.
Client-Delay: 100%, Server-Delay: 100%, Delay Time < Timeout
With a 100% delay rate and delay times below the client’s timeout, every packet is delayed in both directions but still acknowledged within the timeout period. Since the client receives timely acknowledgments for its packets, there are no retransmissions. This results in smooth communication, albeit with increased latency due to the delays. No duplicates are generated because the delayed packets are still delivered within the allowable timeframe. This configuration highlights the impact of guaranteed delays on communication when the delays remain below the timeout threshold.
Client-Delay: 100%, Server-Delay: 100%, Delay Time > Timeout
In this setup, the 100% delay rate and delay times exceeding the client's timeout lead to significant retransmissions.
When acknowledgments are delayed beyond the timeout period, the client assumes the packet was lost and retransmits it. 
Both the original delayed packet and the retransmitted packet eventually reach the server, resulting in duplicates for every packet. 
While no packets are dropped, the excessive delays cause redundant traffic, increasing network congestion. The server detects and logs these duplicates but still processes the first received copy of each packet. This configuration underscores how delays exceeding the timeout can lead to inefficiencies, even in the absence of packet drops.




