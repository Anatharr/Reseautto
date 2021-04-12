#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <signal.h>
#include <errno.h>

#define CMD_ACK 1
#define CMD_END 2
#define CMD_JOIN 3
#define CMD_LEAVE 4
#define CMD_UPDATE 5
#define CMD_CONTINUE 6

#define JOIN_FLAG_SEND_TABLE 1
#define JOIN_FLAG_DONT_SEND 2

#define BUF_SIZE 1024

struct sockaddr_in **playersAddresses = NULL;
int playersNumber = 0;
int pythonsock = -1, fdpsock = -1;

int handleCommand(char *recvBuffer, struct sockaddr_in from);
void showPlayers();

void stop(char *msg) {
	if (pythonsock>=0) close(pythonsock);
	if (fdpsock>=0) close(fdpsock);
	perror(msg);
	exit(EXIT_FAILURE);
}

void exit_handler() {
	if (pythonsock>=0) close(pythonsock);
	if (fdpsock>=0) close(fdpsock);
	exit(EXIT_SUCCESS);
}

int main(int argc, char **argv) {

	if (argc<2 || argc>3) {
		printf("\e[1mUsage : %s <local port> [host:port]\n\e[0m", argv[0]);
		exit(EXIT_FAILURE);
	}

	int lPort=-1;
	sscanf(argv[1], "%d", &lPort);
	if (lPort<0) {
		printf("Error : Invalid port number.\n");
		exit(EXIT_FAILURE);
	}

	char host[16];
	int port=-1;
	bzero(host, 16);
	if (argc==3) {
		int i;
		for (i=0;i<strlen(argv[2]);i++) {
			if (argv[2][i]==':') {
				argv[2][i] = '\0';
				sscanf(argv[2]+i+1, "%d", &port);
				sscanf(argv[2], "%15s", host);
				break;
			}
		}
		if (port<0) {
			printf("Error : Invalid host '%s'.\n", argv[2]);
			exit(EXIT_FAILURE);
		}
	}

	struct sockaddr_in pythonaddr, fdpaddr, tmp_addr;
	bzero(&pythonaddr, sizeof(pythonaddr));
	bzero(&fdpaddr, sizeof(fdpaddr));
	bzero(&tmp_addr, sizeof(tmp_addr));
	socklen_t len = sizeof(fdpaddr);

	/* Socket Creation */
	pythonsock = socket(AF_INET, SOCK_STREAM, 0);
	if (pythonsock < 0) {
		stop("pythonsock creation");
	}
	fdpsock = socket(AF_INET, SOCK_DGRAM, 0);
	if (fdpsock < 0) {
		stop("fdpsock creation");
	}

	/* Assign IP and Port */
	pythonaddr.sin_family = AF_INET;
	pythonaddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
	pythonaddr.sin_port = htons(lPort);

	fdpaddr.sin_family = AF_INET;
	fdpaddr.sin_addr.s_addr = INADDR_ANY;
	fdpaddr.sin_port = 0; // Let the kernel decide

	/* Bind and configure UDP socket */
	if (bind(fdpsock, (struct sockaddr*)&fdpaddr, sizeof(fdpaddr)) < 0) {
		stop("bind");
	}
	if (getsockname(fdpsock, (struct sockaddr *)&fdpaddr, &len) < 0) {
		stop("getsockname");
	}
	printf("binded to port \x1b[31m%d\x1b[0m\n", ntohs(fdpaddr.sin_port));
	struct timeval timeout;
	timeout.tv_sec = 0;
	timeout.tv_usec = 100000;
	if (setsockopt(fdpsock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
		perror("setsockopt");
	}

	/* Connect to python pipe */
	if (connect(pythonsock, (struct sockaddr*)&pythonaddr, sizeof(pythonaddr)) < 0) {
		stop("connect");
	}

	int n, i;
	char pythonBuff[BUF_SIZE+1];
	char fdpBuff[BUF_SIZE+1];
	bzero(pythonBuff, BUF_SIZE+1);
	bzero(fdpBuff, BUF_SIZE+1);
	pythonBuff[0] = 1;

	if (read(pythonsock, pythonBuff, BUF_SIZE) < 0) {
		stop("read");
	}
	if (strncmp(pythonBuff, "Reseautto pipe v", 16)!=0) {
		printf("Wrong pipe header : %s\n", pythonBuff);
		errno = EBADMSG;
		stop("pipe connection");
	}


	/* Join a game if third argument has been specified */
	if (port != -1) {
		bzero(&fdpaddr, sizeof(fdpaddr));
		fdpaddr.sin_family = AF_INET;
		fdpaddr.sin_addr.s_addr = inet_addr(host);
		fdpaddr.sin_port = htons(port);
		while (fdpBuff[0]!=CMD_ACK) {
			bzero(fdpBuff, BUF_SIZE);
			printf("Sending JOIN command...\n");
			fdpBuff[0] = CMD_JOIN;
			fdpBuff[1] = JOIN_FLAG_SEND_TABLE;
			sendto(fdpsock, fdpBuff, 2, 0, (struct sockaddr*)&fdpaddr, sizeof(fdpaddr));
			n = recvfrom(fdpsock, fdpBuff, BUF_SIZE, 0, (struct sockaddr*)&tmp_addr, &len);
			fdpBuff[n] = '\0';
			if (tmp_addr.sin_addr.s_addr != fdpaddr.sin_addr.s_addr || tmp_addr.sin_port != fdpaddr.sin_port) continue;
		}
		i=0;
		while (fdpBuff[0]!=CMD_END) {
			n = recvfrom(fdpsock, fdpBuff, BUF_SIZE, 0, (struct sockaddr*)&tmp_addr, &len);
			fdpBuff[n] = '\0';
			if (tmp_addr.sin_addr.s_addr != fdpaddr.sin_addr.s_addr || tmp_addr.sin_port != fdpaddr.sin_port) continue;

			if (fdpBuff[0]==CMD_JOIN || fdpBuff[0]==CMD_CONTINUE) {
				int len;
				if (fdpBuff[0]==CMD_JOIN) {
					memcpy(&playersNumber, fdpBuff+1, sizeof(playersNumber));
					free(playersAddresses);
					playersAddresses = malloc(playersNumber * sizeof(struct sockaddr_in *));
					len=1+sizeof(playersNumber);
					i=0;
				}
				else len=1;
				while (i<playersNumber && fdpBuff[len]!='\0' && len<=BUF_SIZE-sizeof(struct sockaddr_in)) {
					struct sockaddr_in *player = malloc(sizeof(struct sockaddr_in));
					memcpy(player, fdpBuff+len, sizeof(struct sockaddr_in));
					len+=sizeof(struct sockaddr_in);
					playersAddresses[i] = player;
					i++;
				}
			}
		}
		showPlayers();

		/* Inform other players */
		for(int i = 0; i<playersNumber-1; i++) {
			if (fdpaddr.sin_addr.s_addr != playersAddresses[i]->sin_addr.s_addr || fdpaddr.sin_port != playersAddresses[i]->sin_port) {
				int count = 3;
				while (count>0 && fdpBuff[0]!=CMD_ACK) {
					bzero(fdpBuff, BUF_SIZE+1);
					fdpBuff[0] = CMD_JOIN;
					fdpBuff[1] = JOIN_FLAG_DONT_SEND;
					sendto(fdpsock, fdpBuff, 3, 0, (struct sockaddr*) playersAddresses[i], sizeof(struct sockaddr_in));
					count--;
					n = recvfrom(fdpsock, fdpBuff, BUF_SIZE, 0, (struct sockaddr*)&tmp_addr, &len);
					fdpBuff[n] = '\0';
					if (tmp_addr.sin_addr.s_addr != fdpaddr.sin_addr.s_addr || tmp_addr.sin_port != fdpaddr.sin_port) continue;
				}
			}
		}
	}


	int max, activity;
	fd_set readfds;

	/* Main loop */
	while (strcmp(pythonBuff, "exit")!=0) {
		FD_ZERO(&readfds);
		FD_SET(pythonsock, &readfds);
		FD_SET(fdpsock, &readfds);
		max = fdpsock>pythonsock ? fdpsock : pythonsock;

		activity = select(max+1, &readfds, NULL, NULL, NULL);
		if (activity<0 && errno!=EINTR) {
			stop("Select error");
		}

		if (FD_ISSET(fdpsock, &readfds)) {
			/* Handle communication incoming from other players */
			bzero(fdpBuff, BUF_SIZE);
			n = recvfrom(fdpsock, fdpBuff, BUF_SIZE, 0, (struct sockaddr*)&fdpaddr, &len);
			if (n<0) {
				stop("Reading from fdpsock\n");
			}
			fdpBuff[n]='\0';
			handleCommand(fdpBuff, fdpaddr);
		}

		if (FD_ISSET(pythonsock, &readfds)) {
			/* Handle communication incoming from python game */
			bzero(pythonBuff, sizeof(pythonBuff));
			n = read(pythonsock, pythonBuff, sizeof(pythonBuff));
			if (n<0) {
				stop("Reading from pythonsock\n");
			}
			pythonBuff[n] = '\0';
			printf("C program received : '%s'\n", pythonBuff);
			if(!strcmp(pythonBuff, "player")) showPlayers();
		}
	}

	/* Cleanup */
	for (i=0; i<playersNumber; i++) {
		free(playersAddresses[i]);
	}
	free(playersAddresses);

	close(fdpsock);
	close(pythonsock);
	return EXIT_SUCCESS;
}


int handleCommand(char *recvBuffer, struct sockaddr_in from) {
	if (recvBuffer==NULL || recvBuffer[0]==0) return -1;

	int i;

	switch (recvBuffer[0]) {
	case CMD_JOIN: {
		
		/* Acknowledge reception */
		bzero(recvBuffer, BUF_SIZE);
		recvBuffer[0] = CMD_ACK;
		sendto(fdpsock, recvBuffer, 2, 0, (struct sockaddr*) &from, sizeof(struct sockaddr_in));

		/* Expand playersAddresses */
		struct sockaddr_in **tmp = realloc(playersAddresses, (playersNumber+1) * sizeof(struct sockaddr_in*));
		if (tmp==NULL) {
			printf("Error : Could not add player");
			return -1;
			}

		/* Copy the struct sockaddr_in as we don't want to lose it */
		struct sockaddr_in *newPlayer = malloc(sizeof(struct sockaddr_in));
		bzero(newPlayer, sizeof(*newPlayer));
		newPlayer->sin_family = from.sin_family;
		newPlayer->sin_port = from.sin_port;
		newPlayer->sin_addr.s_addr = from.sin_addr.s_addr;

		/* Apply changes */
		playersAddresses = tmp;
		playersAddresses[playersNumber] = newPlayer;
		playersNumber++;

		showPlayers();
		if (recvBuffer[1]==JOIN_FLAG_SEND_TABLE) {
			/* Send information to newPlayer */
			bzero(recvBuffer, BUF_SIZE+1);
			recvBuffer[0] = CMD_JOIN;
			memcpy(recvBuffer+1, &playersNumber, sizeof(playersNumber));
			int len = 1+sizeof(playersNumber);
			for (i=0; i<playersNumber; i++) {
				memcpy(recvBuffer+len, playersAddresses[i], sizeof(struct sockaddr_in));
				len += sizeof(struct sockaddr_in);
				if (len > BUF_SIZE-sizeof(struct sockaddr_in)) {
					sendto(fdpsock, recvBuffer, len+1, 0, (struct sockaddr*) newPlayer, sizeof(*newPlayer));
					bzero(recvBuffer,BUF_SIZE);
					recvBuffer[0] = CMD_CONTINUE;
					len = 1;
				}
			}
			sendto(fdpsock, recvBuffer, len+1, 0, (struct sockaddr*) newPlayer, sizeof(*newPlayer));
			bzero(recvBuffer, BUF_SIZE);
			recvBuffer[0] = CMD_END;
			sendto(fdpsock, recvBuffer, 2, 0, (struct sockaddr*) newPlayer, sizeof(*newPlayer));
		}	
		return 0;		
	}
	case CMD_CONTINUE:
		printf("Warning : Unexpected CMD_CONTINUE message received.\n");
		return -1;
	case CMD_END:
		printf("Warning : Unexpected CMD_END message received.\n");
		return -1;
	default:
		printf("Warning : Unknown command '%d'\n", recvBuffer[0]);
		return -1;
	}

	return 0;
}



void showPlayers() {
	int i;
	printf("\x1b[34m -------------------- \n|\x1b[32m Connected Players  \x1b[34m|\n|--------------------|\n");
	for (i=0; i<playersNumber; i++) {
		printf("|\x1b[31m %d \x1b[34m|\x1b[33m %d\x1b[0m:\x1b[35m%d \x1b[34m|\n", i, playersAddresses[i]->sin_addr.s_addr,playersAddresses[i]->sin_port);
	}
	printf(" -------------------- \x1b[0m\n");
}