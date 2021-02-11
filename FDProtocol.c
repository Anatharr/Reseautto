#include "FDProtocol.h"

struct sockaddr_in **playersAddresses = NULL;
int playersNumber = 0;

/*struct p_mesg *pendingMessages[MAX_PENDING_MESSAGES];

void sendPendingMessages(int sockfd) {
	int i;
	struct p_mesg *msg;
	for (i=0; i<MAX_PENDING_MESSAGES; i++) {
		if (pendingMessages[i]!=0) {
			msg = pendingMessage[i];
			sendto(sockfd, msg->msg, msg->flags, msg->dest);
		}
	}
}
*/


/*
 * Send a message to a specific address, with a length prefix and a message ID
 *    ---------------------------------------------------------------------
 *   | n (4 bytes) | ID (4 bytes) |             msg (n-8 bytes)            |
 *    ---------------------------------------------------------------------
 * Return Value:
 *   0 on success
 *  -1 on failure
 */
int sendMsg(int sockfd, char *msg, int flags, const struct sockaddr_in *to) {
	int len = strnlen(msg, MAX_MESSAGE_LEN)*sizeof(char) + sizeof(int) + 1;
	char **buffer = malloc(len);

	if (buffer==NULL) return -1;

	memcpy(*buffer, &len, sizeof(len));
	*buffer[sizeof(len)]='\0';
	strncat(*buffer, msg, MAX_MESSAGE_LEN);

	return sendto(sockfd, *buffer, len, 0, (struct sockaddr*) to, sizeof(*to));
}

int sendTo(int sockfd, char *msg, const struct sockaddr_in *to) {
	return sendMsg(sockfd, msg, 0, to);
}

int replyTo(int sockfd, char *msg, const struct sockaddr_in *to) {
	return sendMsg(sockfd, msg, MSG_CONFIRM, to);
}


/*
int broadcast(int sockfd, char *msg, const int MAX_MESSAGE_LEN) {
	int i;
	for ()
}
*/



int handleCommand(char *recvBuffer, struct sockaddr_in from) {
	if (recvBuffer==NULL || recvBuffer[0]==0) return -1;

	switch (recvBuffer[0]) {
	case CMD_JOIN: {
		/* Expand playersAddresses */
		struct sockaddr_in **tmp = realloc(playersAddresses, playersNumber+1 * sizeof(struct sockaddr_in*));
		if (tmp==NULL) {
			printf("Error : Could not add player");
			return -1;
		}

		/* Copy the struct sockaddr_in as we don't want it to change */
		struct sockaddr_in *newPlayer = malloc(sizeof(struct sockaddr_in));
		newPlayer->sin_family = from.sin_family;
		newPlayer->sin_port = from.sin_port;
		newPlayer->sin_addr.s_addr = from.sin_addr.s_addr;

		/* Apply changes */
		playersAddresses = tmp;
		playersAddresses[playersNumber] = newPlayer;
		playersNumber++;
		break;
	}
	default:
		printf("Warning : Unknown command '%d'", recvBuffer[0]);
		return -1;
	}

	return 0;
}
