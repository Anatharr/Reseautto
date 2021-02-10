#!/usr/bin/python3

import socket, random, os, time


HEADER = b"Reseautto pipe vBeta1.0"

class NetworkModule():
	def __init__(self):
		self.sock = socket.socket()

		# Pick a random unused port
		while True:
			port = random.randrange(1024, 65536)
			try:
				self.sock.bind(('127.0.0.1', port))
				break
			except OSError:
				pass

		self.sock.listen(1)

		print("Starting C module...")
		pid = os.fork()
		if pid==0:
			time.sleep(0.2) # wait for the parent to accept connections
			os.execv("client", ("client", str(port)))
			os._exit(os.EX_OSERR)

		self.cSock, addr  = self.sock.accept()
		self.cSock.send(HEADER)
		print("Pipe successfully created.\nPython (pid "+str(os.getpid())+" on ('127.0.0.1', "+ str(port) +")) =============================== C (pid "+ str(pid) +" on "+ str(addr) + ")")

	def recv(self, size):
		return self.cSock.recv(size)

	def send(self, msg):
		return self.cSock.send(msg)

	def close(self):
		self.cSock.close()
		self.sock.close()


if __name__=="__main__":

	mod = NetworkModule()

	inpt = ""
	while inpt!="exit":
		inpt = input()
		mod.send(inpt.encode())

	mod.close()

