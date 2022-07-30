import socket
import sys

host=('127.0.0.1', 56789)

# UDP datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # creates a socket in the specified domain and of the specified type. AF_INET refers to the address-family ipv4 


sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # The SO_REUSEADDR socket option allows a socket to forcibly bind to a port in use by another socket.
sock.bind(host)

users = int(sys.argv[1])	# number of users will be passed when this program will run
c=0	
clients = []			# for storing the port number of each user

while True:
    data, address = sock.recvfrom(128)
    clients.append(address)
    data=data.decode()
    print(data)
    if (data=='ready'):	        
        c+=1
    if c==users:	# After helper receives 'ready' message from all users it sends 'start' message to all the users	
        # sock.sendto(b'ready', address)
        break

for x in clients:
    print(x)
    sock.sendto(b'start', x)
    # print
    
c=0
clients = []
while True:
    data, address = sock.recvfrom(128)
    clients.append(address)
    data=data.decode()
    print(data)
    if (data=='seen'):	
        c+=1
    # After helper receives 'seen' message from all users it sends 'resume' message to all the users indicating them that they can now start reading next line
    if c==users:	
        for x in clients:
        	print(x)
        	sock.sendto(b'resume', x)
        c = 0	
        clients = []
