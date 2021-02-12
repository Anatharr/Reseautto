#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <signal.h>
#include <errno.h>

#include "FDProtocol.h"

#define BUF_SIZE 80

int pythonsock = -1, fdpsock = -1;

void stop(char *msg) {
	if (pythonsock>=0) close(pythonsock);
	if (fdpsock>=0) close(fdpsock);
	perror(msg);
	exit(EXIT_FAILURE);
}

int main(int argc, char **argv) {

	if (argc<2) {
		printf("\e[1mUsage : %s <Port>\n\e[0m", argv[0]);
		exit(EXIT_FAILURE);
	}

	int port=-1;
	sscanf(argv[1], "%d", &port);
	if (port<0) {
		printf("Error : Invalid port number.\n");
		exit(EXIT_FAILURE);
	}

	struct sockaddr_in pythonaddr, fdpaddr;

	/* Socket Creation */
	pythonsock = socket(AF_INET, SOCK_STREAM, 0);
	if (pythonsock == -1) {
		stop("socket creation");
	}
	fdpsock = socket(AF_INET, SOCK_DGRAM, 0);
	if (fdpsock == -1) {
		stop("socket creation");
	}

	/* Assign IP and Port */
	bzero(&pythonaddr, sizeof(pythonaddr));
	pythonaddr.sin_family = AF_INET;
	pythonaddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
	pythonaddr.sin_port = htons(port);

	bzero(&fdpaddr, sizeof(fdpaddr));
	fdpaddr.sin_family = AF_INET;
	fdpaddr.sin_addr.s_addr = INADDR_ANY;
	fdpaddr.sin_port = 0; // Let the kernel decide

	/* Bind socket for FDP transfer */
	if (bind(fdpsock, (struct sockaddr*)&fdpaddr, sizeof(fdpaddr)) != 0) {
		stop("bind");
	}

	/* Connect to python pipe */
	if (connect(pythonsock, (struct sockaddr*)&pythonaddr, sizeof(pythonaddr)) != 0) {
		stop("connect");
	}

	int n, pid;
	char recvBuff[BUF_SIZE+1];
	char sendBuff[BUF_SIZE+1];
	bzero(recvBuff, BUF_SIZE+1);
	bzero(sendBuff, BUF_SIZE+1);
	recvBuff[0] = 1;

	if (read(pythonsock, recvBuff, BUF_SIZE)<0) {
		stop("read");
	}
	if (strncmp(recvBuff, "Reseautto pipe v", 16)!=0) {
		printf("Wrong pipe header : %s\n", recvBuff);
		errno = EBADMSG;
		stop("pipe connection");
	}

	switch(pid=fork()) {
		case -1:
			stop("Process creation");
			break;
		case 0:
			while (0) { // Non utilisé pour l'instant
				bzero(sendBuff, BUF_SIZE);
				n = 0;
				while (n<BUF_SIZE && (sendBuff[n++] = getchar()) != '\n');
				sendBuff[n]='\0';
				write(pythonsock, sendBuff, BUF_SIZE);
			}
			exit(EXIT_SUCCESS);
		default:
			signal(SIGCHLD, SIG_IGN); // Ignore SIGCHLD signal to avoid zombie child
			printf("\e[1mC Program is connected to python game.\e[0m\n\n");
			while (recvBuff[0]!=0 && strcmp(recvBuff, "exit")!=0) {
				bzero(recvBuff, sizeof(recvBuff));
				if (read(pythonsock, recvBuff, sizeof(recvBuff))<0) {
					stop("read");
				}
				printf("C program received : '%s'\n", recvBuff);
			}
	}

	close(pythonsock);
	return EXIT_SUCCESS;
}
