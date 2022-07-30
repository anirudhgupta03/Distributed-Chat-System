#importing required packages/libraries
import socket
import sys
import threading
import time
import tkinter as tk

#GUI Chat Window
window = tk.Tk()

topFrame = tk.Frame(window)
topFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55, fg = "white")
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="white")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="black", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)

#Opening the text file and reading it 
file1 = open("input.txt","r+") 
lines=file1.readlines()


name_port={}	                               # map for mapping the name to the port
users = 0	                               # number of users in chat

clients=[]	                               # for storing the port number of each user

port=int(sys.argv[1])	                       # port number will be passed when this program will run
dport=5060		


host=('127.0.0.1', 56789)	               # IP and Port number of the helper 

# UDP datagram socket
sock1= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	# creates a socket in the specified domain and of the specified type. AF_INET refers to the address-family ipv4 

#sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

sock1.bind(('127.0.0.1', port))	               # With the help of bind() function binding host and port	

sock1.sendto(b'ready', host)	               # each user sends a 'ready' message to helper and after helper receives 'ready' message from all the users it sends 'start' message to all the users 

# each user waits till it receives a 'start' message from the helper so that everything is synchronized

data1 = sock1.recv(1024).decode()	       # data1 stores 'start' message
print(data1)


sock3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #The SO_REUSEADDR socket option allows a socket to forcibly bind to a port in use by another socket.
sock3.bind(('127.0.0.1', dport))			


# user starts reading the text file
c=1
for x in lines:
    if c==1:				        #on line 1 is the number of users in the chat
        users=int(x[0])
        
    elif c<=(users+1):		                #on next users line is Name and Port 
        x=x[:-1]
        
        words=x.split(" ")
        #print(words[0],":",words[1])
        
        name_port[words[0]]=int(words[1])	# storing the port number corresponding to user name
        
        if port == int(words[1]):
        	print("Welcome " + words[0] + " to the chat!!!")	
        	window.title(words[0])		# giving the GUI Chat window title
        
        clients.append(int(words[1]))		# storing the ports
    
    else:
        if x=="\n":
            break
            
        x=x[:-1]
        
        words=x.split(" ")
        sender=words[0]
        reciever=words[1]

        if port==name_port [reciever]:		# if the current port is equal to the port number of the receiver
            
            data2 = sock1.recv(1024)		# it might be possible that receiver starts first so in order to ensure proper ordering of messages receiver is made to wait for the sender to send the message
            
            print('\r{}: {}\n'.format(sender,data2.decode()), end='')
            
            #inserting the message on the GUI Chat window
            texts = tkDisplay.get("1.0", tk.END).strip()
            tkDisplay.config(state=tk.NORMAL)
            if len(texts) < 1:
            	tkDisplay.insert(tk.END, sender + ": " + data2.decode())
            else:
            	tkDisplay.insert(tk.END, "\n\n"+ sender + ": " + data2.decode())	
            tkDisplay.config(state=tk.DISABLED)
            tkDisplay.see(tk.END)
            
            # now after the receiver has received the message it sends a 'seen' message to the helper. After helper receives 'seen' message from all the users it sends a 'resume' message to the receiver indicating that all other users have read this particular line and now it can safely move to the next line. This is done to ensure synchronization
            
            # receiver waits till it receives 'resume' message from the helper
            sock1.sendto(b'seen', host)	       
            data4 = sock1.recv(1024).decode()	#data4 stores 'resume' message
            #print(data4)	
        
        
        elif port==name_port[sender]:		# if the current port is equal to the port number of the sender
            #
            msg=""	#stores the message to be sent
            cc=1
            
            for x in words:
                if cc>2:
                   msg+=x
                   msg+=" "
                cc+=1
           
            sock3.sendto(msg.encode(), ('127.0.0.1', name_port [reciever])) # sendto() is used for UDP SOCK_DGRAM unconnected datagram sockets.
            print('You -> ' + reciever + ': ' + msg)
            
            #inserting the message on the GUI Chat window
            texts = tkDisplay.get("1.0", tk.END).strip()
            tkDisplay.config(state=tk.NORMAL)
            if len(texts) < 1:
            	tkDisplay.insert(tk.END, "You->" + reciever + ": " + msg, "tag_your_message")
            else:
            	tkDisplay.insert(tk.END, "\n\n" + "You->" + reciever + ": " + msg, "tag_your_message")
            tkDisplay.config(state=tk.DISABLED)
            tkDisplay.see(tk.END)
            
            # now after the sender has send the message to the receiver it sends a 'seen' message to the helper. After helper receives 'seen' message from all the users it sends a 'resume' message to the sender indicating that all other users have read this particular line and now it can safely move to the next line. This is done to ensure synchronization
            
            # sender waits till it receives 'resume' message from the helper
            sock1.sendto(b'seen', host)
            data4 = sock1.recv(1024).decode()	#data4 stores 'resume' message
            #time.sleep(5)
            #print(data4)
        
        
        else:					# if the current port is neither equal to the sender port nor receiver port
        	
        	# user sends a 'seen' message to the helper. After helper receives 'seen' message from all the users it sends a 'resume' message to the sender indicating that all other users have read this particular line and now it can safely move to the next line. This is done to ensure synchronization
        	
        	# user waits till it receives 'resume' message from the helper
        	sock1.sendto(b'seen', host)
        	data4 = sock1.recv(1024).decode()	#user waits till it receives a 'resume' message from the helper
        	#time.sleep(5)		#data4 stores 'resume' message
        	#print(data4)
        time.sleep(3)			#just for showing the messages at a gap otherwise all messages will occur very fast and we won't be able to check the ordering and synchronization
    c+=1
window.mainloop()
