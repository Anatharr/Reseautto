/**
	Handle multiple socket connections with select and fd_set on Linux
*/

#include <stdio.h>
#include <string.h> //strlen
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>    //close
#include <arpa/inet.h> //close
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/time.h> //FD_SET, FD_ISSET, FD_ZERO macros
#include <signal.h>
#include <fcntl.h>

#define TRUE 1
#define FALSE 0
#define PORT 50033
#define BUFFER_SIZE 512

int main(int argc, char *argv[])
{
    int opt = TRUE;
    int master_socket, addrlen, new_socket, client_socket[30], max_clients = 30, activity, i, j, valread, valreadpy, sd;
    int max_sd;

    int socket_py;
    struct sockaddr_in server;
    char buf[BUFFER_SIZE];
    int port_py;
    signal(SIGPIPE, SIG_IGN);

    // ----------- PYTHON PART -----------
    {
        //Create socket for python
        socket_py = socket(AF_INET, SOCK_STREAM, 0);
        if (socket_py == -1)
        {
            printf("Could not create socket for the python");
        }

        // Init of the python
        server.sin_addr.s_addr = inet_addr("127.0.0.1");
        server.sin_family = AF_INET;

        // ----------- Scan part of the command -----------

        if (sscanf(argv[1], "%d", &port_py) != 1)
        {
            puts("Erreur: Le paramètre NOMBRE doit être un nombre entier ! Port python");
            return EXIT_FAILURE;
        }

        server.sin_port = htons(port_py);

        // ----------- Connect part -----------

        //Connect to remote server python
        if (connect(socket_py, (struct sockaddr *)&server, sizeof(server)) < 0)
        {
            puts("connect error in the Python\n");
            return 1;
        }

        printf("Connected to python in port %d\n", port_py);

        // SOCKET AND STDIN non-blocking mode
        fcntl(socket_py, F_SETFL, fcntl(socket_py, F_GETFL) | O_NONBLOCK);
        fcntl(STDIN_FILENO, F_SETFL, fcntl(socket_py, F_GETFL) | O_NONBLOCK);
    }

    // ----------- PYTHON PART END -----------

    struct sockaddr_in address;

    char buffer[1025]; //data buffer of 1K

    //set of socket descriptors
    fd_set readfds;

    //initialise all client_socket[] to 0 so not checked
    for (i = 0; i < max_clients; i++)
    {
        client_socket[i] = 0;
    }

    //create a master socket
    if ((master_socket = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    //set master socket to allow multiple connections , this is just a good habit, it will work without this
    if (setsockopt(master_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) < 0)
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    //type of socket created
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    //bind the socket to localhost port 50002
    if (bind(master_socket, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
        perror("bind failed of the master socket");
        exit(EXIT_FAILURE);
    }
    printf("Listener on port %d \n", PORT);

    //try to specify maximum of 3 pending connections for the master socket
    if (listen(master_socket, 3) < 0)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    //accept the incoming connection
    addrlen = sizeof(address);
    // puts("Waiting for connections ...");

    while (TRUE)
    {
        //clear the socket set
        FD_ZERO(&readfds);

        //add master socket to set
        FD_SET(master_socket, &readfds);
        FD_SET(socket_py, &readfds);
        max_sd = master_socket;

        //add child sockets to set
        for (i = 0; i < max_clients; i++)
        {
            //socket descriptor
            sd = client_socket[i];

            //if valid socket descriptor then add to read list
            if (sd > 0)
                FD_SET(sd, &readfds);

            //highest file descriptor number, need it for the select function
            if (sd > max_sd)
                max_sd = sd;
        }

        //wait for an activity on one of the sockets , timeout is NULL , so wait indefinitely
        activity = select(max_sd + 2, &readfds, NULL, NULL, NULL);

        if ((activity < 0) && (errno != EINTR))
        {
            printf("select error");
        }

        //If something happened on the master socket , then its an incoming connection
        if (FD_ISSET(master_socket, &readfds))
        {
            if ((new_socket = accept(master_socket, (struct sockaddr *)&address, (socklen_t *)&addrlen)) < 0)
            {
                perror("accept");
                exit(EXIT_FAILURE);
            }

            //inform user of socket number - used in send and receive commands
            printf("New connection , socket fd is %d , ip is : %s , port : %d \n  ", new_socket, inet_ntoa(address.sin_addr), ntohs(address.sin_port));

            //add the new socket to array of sockets
            for (i = 0; i < max_clients; i++)
            {
                //if position is empty
                if (client_socket[i] == 0)
                {
                    client_socket[i] = new_socket;
                    break;
                }
            }
        }
        bzero(buf, 512);

        valreadpy = read(socket_py, buf, sizeof(buf));
        buf[valreadpy] = '\0';
        if (buf != "")
        {
            printf("L'envoi avec le python MARCHE : %d %s\n", socket_py, buf);
            printf("%d\n", buf);
            for (i = 0; i < max_clients; i++)
            {
                if (client_socket[i] != 0)
                {
                    send(client_socket[i], buf, strlen(buf), 0);
                }
            }
        }

        bzero(buf, 512);

        //else its some IO operation on some other socket :)
        for (i = 0; i < max_clients; i++)
        {
            sd = client_socket[i];

            if (FD_ISSET(sd, &readfds))
            {
                bzero(buffer, 1024);
                //Check if it was for closing , and also read the incoming message
                if ((valread = read(sd, buffer, 1024)) <= 0) // disconnect case
                {
                    //Somebody disconnected , get his details and print
                    getpeername(sd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
                    printf("Host disconnected , ip %s , port %d \n", inet_ntoa(address.sin_addr), ntohs(address.sin_port));

                    //Close the socket and mark as 0 in list for reuse
                    close(sd);
                    client_socket[i] = 0;
                }

                //Echo back the message that came in
                else
                {
                    //set the string terminating NULL byte on the end of the data read
                    buffer[valread] = '\0';
                    printf("%d %s\n", sd, buffer);
                    // for (j = 0; j < max_clients; j++)
                    // {
                    //     if (i != j && client_socket[j] != 0)
                    //     {
                    //         send(client_socket[j], buffer, strlen(buffer), 0);
                    //     }
                    // }
                }
            }
        }
    }

    return 0;
}