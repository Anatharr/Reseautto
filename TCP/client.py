import socket
adresseIP = "127.0.0.1"  # Ici, le poste local
port = 50033  # Se connecter sur le port 50000
i = 0

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((adresseIP, port))
print("Connecté au serveur")

client.send("Bonjour, je suis le client\n".encode("utf-8"))
client.send("Bonjour, je suis le client\n".encode("utf-8"))
client.send("Bonjour, je suis le client\n".encode("utf-8"))

while i < 20:
    reponse = client.recv(255)
    print(reponse.decode("utf-8"))
    i += 1
print("Connexion fermée")
client.close()
