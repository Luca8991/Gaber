import socket
import importlib
import json
import binascii

freeports=[1235,1236,1237, 1238]
occports=[]
threads=[]
adress="192.168.0.107"
serv_port=1234
path="users.json"
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((adress, serv_port))
sock.listen()

while(1):
	print("started")
	for thread in threads:
		if(not thread.isAlive()):
			uport=thread.port
			threads.remove(thread)
			occports.remove(uport)
			freeports.append(uport)

	so, adr=sock.accept()
	print("connected")
	mac=so.recv(1024)
	mac=binascii.hexlify(mac).decode()
	port=freeports[0]
	freeports.pop(0)
	occports.append(port)
	so.send(str(port).encode())
	so.close()
	rf=open(path, "r")
	dic=json.load(rf)
	username=dic[mac]
	print(username)
	rf.close()
	MyClass = getattr(importlib.import_module(username+".main"), "Main")
	user=MyClass(adress, port, username)
	threads.append(user)
	user.start()
	