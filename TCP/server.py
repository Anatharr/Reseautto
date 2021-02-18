import socket
import os
import time
import subprocess
# import signal
from signal import signal, SIGPIPE, SIG_IGN

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
signal(SIGPIPE, SIG_IGN)
n = 0
reponse = ""

port_valid = True
port = 50001
while port_valid:
    try:
        serveur.bind(('', port))  # Écoute sur le port 50000
        # Check if the 2 following ports are available
        port_valid = False
    except:
        port += 1
serveur.listen(5)

subprocess.Popen("./server " + str(port) + " " + str(port + 1), shell=True)
client, infosClient = serveur.accept()
print("Client python connecté (coté python). Adresse " + infosClient[0])
client.setblocking(0)

while True:

    time.sleep(1)
    print("debut envoi python")
    reponse = "ENVOI PYTHON"
    # reponse = input()
    if (len(reponse) >= 1):
        print("envoie :", reponse)
        n = client.send(reponse.encode("utf-8"))

    if (n != len(reponse)):
        print("erreur envoi")
    else:
        print("message send in python")

    # Reçoit 255 octets. Vous pouvez changer pour recevoir plus de données
    # requete = client.recv(255)

    # print(requete.decode("utf-8"))
    # print("^ recv in python")

    # print("Connexion fermée")
    # client.close()
serveur.close()
