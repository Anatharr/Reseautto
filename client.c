#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#define BUF_SIZE 80

void stop(char *msg) {
	perror(msg);
	exit(EXIT_FAILURE);
}

int main(int argc, char **argv) {

	if (argc!=2) {
		printf("\e[1mUsage : %s <Port>\n\e[0m", argv[0]);
		exit(EXIT_FAILURE);
	}

	int sockfd, port=-1;
	struct sockaddr_in pythonaddr;

	// socket creation
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd == -1) {
		stop("socket creation");
	}

	// assign IP and PORT
	bzero(&pythonaddr, sizeof(pythonaddr));
	pythonaddr.sin_family = AF_INET;
	pythonaddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
	sscanf(argv[1], "%d", &port);
	if (port<0) {
		printf("Error : Invalid port number.\n");
		exit(EXIT_FAILURE);
	}
	pythonaddr.sin_port = htons(port);

	// connect to the server
	if (connect(sockfd, (struct sockaddr*)&pythonaddr, sizeof(pythonaddr)) != 0) {
		stop("connect");
	}

	int n, pid;
	char recvBuff[BUF_SIZE+1];
	char sendBuff[BUF_SIZE+1];
	bzero(recvBuff, BUF_SIZE+1);
	bzero(sendBuff, BUF_SIZE+1);

	if (read(sockfd, recvBuff, BUF_SIZE)<0) {
		close(sockfd);
		stop("read");
	}
	if (strncmp(recvBuff, "Reseautto pipe v", 16)!=0) {
		close(sockfd);
		printf("Wrong game pipe header : %s\n", recvBuff);
		exit(EXIT_FAILURE);
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
				write(sockfd, sendBuff, BUF_SIZE);
			}
			exit(EXIT_SUCCESS);
			break;
		default:
			printf("\e[1mC Program is connected to python game.\e[0m\n\n");
			while (strcmp(recvBuff, "exit")!=0) {
				bzero(recvBuff, sizeof(recvBuff));
				if (read(sockfd, recvBuff, sizeof(recvBuff))<0) {
					stop("read");
				}
				printf("C program received : '%s'\n", recvBuff);
			}
	}

	close(sockfd);
	return EXIT_SUCCESS;
}
