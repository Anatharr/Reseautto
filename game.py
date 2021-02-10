#!/usr/bin/python3

import socket, random

header = b"Reseautto pipe vBeta1.0"

sock = socket.socket()

# Pick a random unused port
while True:
	port = random.randrange(1024, 65536)
	try:
		sock.bind(('127.0.0.1', port))
		break
	except OSError:
		pass

sock.listen(1)
print("Pipe waiting for connection on " + str(port))
cSock, addr  = sock.accept()
cSock.send(header)

print("Connected to " + str(addr))

inpt = ""
while inpt!="exit":
	inpt = input()
	cSock.send(inpt.encode())
	print(cSock.recv(1024).decode())


sock.close()

