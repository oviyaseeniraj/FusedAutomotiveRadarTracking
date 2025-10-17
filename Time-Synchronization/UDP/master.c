#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>


int main(int argc, char *argv[])
{
    int sockfd;
    struct sockaddr_in servaddr;

    // Create UDP socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        exit(1);
    }
     
    // Set server address
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(atoi("8000"));
    servaddr.sin_addr.s_addr = inet_addr("0.0.0.0");

    /*
    END BK stuff
    */

    while(1){
        usleep(10000);
        sendto(sockfd, "Hello, World!", 13, 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    }
    exit(0);
}
