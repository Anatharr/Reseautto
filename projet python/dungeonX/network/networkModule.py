#!/usr/bin/python3
import socket, random, os, time
import sys, signal
import threading

HEADER = b"Reseautto pipe vBeta1.0"

class NetworkModule(threading.Thread):
    def __init__(self,connection_addr=None):
        """
            connection_addr : tuple, (ip,port) representing an address in the network in order to connect to it
        """
        threading.Thread.__init__(self, daemon=True)
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
            if connection_addr:
                addr = ':'.join(connection_addr)
                os.execv("dungeonX/network/client", ("dungeonX/network/client", str(port), addr )) # (ip, port) d'une machine dans le reseau
            else:
                os.execv("dungeonX/network/client", ("dungeonX/network/client", str(port)))
            os._exit(os.EX_OSERR)

        signal.signal(signal.SIGCHLD, signal.SIG_IGN) # Ignore SIGCHLD to avoid child zombies
        self.cSock, addr  = self.sock.accept()
        self.cSock.send(HEADER)
        print("Pipe successfully created.\nPython (pid "+str(os.getpid())+" on ('127.0.0.1', "+ str(port) +")) =============================== C (pid "+ str(pid) +" on "+ str(addr) + ")")

    def run(self):
        while False:
            time.sleep(0.3)
            print("waiting for msg...")

    def recv(self, size):
        return self.cSock.recv(size)

    def send(self, msg):
        return self.cSock.send(msg)

    def close(self):
        self.cSock.close()
        self.sock.close()








