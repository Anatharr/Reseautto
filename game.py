#!/usr/bin/python3

import socket, random, os, time

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

print("Starting C program...")
pid = os.fork()
if pid==0:
	time.sleep(0.5) # wait for the parent to accept connections
	os.execv("client", ("client", str(port)))
	os._exit(os.EX_OSERR)

cSock, addr  = sock.accept()
cSock.send(header)

print("Pipe successfully created.\nPython (pid "+str(os.getpid())+" on ('127.0.0.1', "+ str(port) +")) =============================== C (pid "+ str(pid) +" on "+ str(addr) + ")")

inpt = ""
while inpt!="exit":
	inpt = input()
	cSock.send(inpt.encode())


cSock.close()
sock.close()

