#!/usr/bin/python3
#Sam George's modified lab 9 TCP Listener (enabled public facing).
#adapting for use as a chat manager.

import socket
import threading
import urllib.request
import netifaces as ni
import os
if(os.name == "nt"):
    import winreg as wr
import platform

print("Executing on: " + platform.platform())

#function to get string names of windows interfaces (only necessary on Windows devices).
def GetDeviceNames(iface_nums):
    iface_names = ['(unkown)' for i in range(len(iface_nums))]
    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
    reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    for i in range(len(iface_nums)):
        try:
            reg_subkey = wr.OpenKey(reg_key, iface_nums[i] + r'\Connection')
            iface_names[i] = wr.QueryValueEx(reg_subkey, 'Name')[0]
        except FileNotFoundError:
            pass
    return iface_names
#Set listening IP to Wi-Fi address.
if(os.name == "nt"):
    ifaces = GetDeviceNames(ni.interfaces())
    ip = ni.ifaddresses(ni.interfaces()[3])[ni.AF_INET][0]['addr']
    print(ifaces[3] + ": " + ip);
elif(os.name == "posix"):
    ip = ni.ifaddresses(ni.interfaces()[1])[ni.AF_INET][0]['addr']

#Get the machine's local IPv4 Address
# Defaults to eth0 - ignoring # myLocalIP = socket.gethostbyname(socket.getfqdn())
if(os.name == "nt"):
    port = 9999
elif(os.name == "posix"):
    port = 9998

bindData = (ip, port)

#Get public facing IPv4 Address
url = "http://ip.42.pl/raw"
request = urllib.request.urlopen(url).read()
myPublicIP = request.decode("ASCII");
print("[!] Your public IP is: " + myPublicIP + ", and should be forwarded to local IP: %s on port: %d" % (bindData[0], bindData[1]))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# allow listening despite TIME_WAIT sockets
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind to ip & port
server.bind(bindData)

server.listen(5)

print("[*] Listening on %s:%d" % (bindData[0], bindData[1]))

# this is our client handling thread
def handle_client(client_socket):

    # just print out what the client sends
    request = client_socket.recv(1024)
    request.decode("ASCII");
    request = request[:len(request) - 1];
    print ("[*] Received: \"%s\"" % request.decode("ASCII"))
           
    # send back a packet
    client_socket.send(b'ACK\n')
    print (client_socket.getpeername())
    client_socket.close()


while True:

    # accept a connection
    client,addr = server.accept()
    
    print ("[*] Accepted connection from: %s:%d" % (addr[0],addr[1]))

    # spin up our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()
