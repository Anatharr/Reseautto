#ifndef FDPROTOCOL_H
#define FDPROTOCOL_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>


#define MAX_PENDING_MESSAGES 30
#define MAX_MESSAGE_LEN 1024

#define CMD_UPDATE 1
#define CMD_JOIN 2
#define CMD_LEAVE 3

/*
struct p_mesg {
	char *msg;
	struct sockaddr_in dest;
	int flags;
	int msg_id;
}
*/

extern struct sockaddr_in **playersAddresses;
extern int playersNumber;

//int initSocket(int sockfd);

int sendTo(int sockfd, char *msg, const struct sockaddr_in *to);
int replyTo(int sockfd, char *msg, const struct sockaddr_in *to);
int broadcast(int sockfd, char *msg);

#endif
