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
#ifdef JETSON
    #include <jetgpio.h>
#endif


void pinhigh(void) __attribute__((weak));
void pinhigh(void) { }

int main(int argc, char *argv[])
{
    int sockfd;
    struct sockaddr_in servaddr, servaddr2;

    // Create UDP socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        exit(1);
    }
     
    // Allow broadcast if we send to the broadcast address
    int opt = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt)) < 0) {
        perror("setsockopt SO_BROADCAST failed");
        /* not fatal on all systems */
    }

    // Set destination addresses
    const char *dest = (argc > 1) ? argv[1] : "169.231.219.60";
    const char *dest2 = (argc > 2) ? argv[2] : "169.231.20.38"; /* second IP */

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(8000);
    if (inet_aton(dest, &servaddr.sin_addr) == 0) {
        fprintf(stderr, "Invalid destination address: %s\n", dest);
        close(sockfd);
        exit(1);
    }

    memset(&servaddr2, 0, sizeof(servaddr2));
    servaddr2.sin_family = AF_INET;
    servaddr2.sin_port = htons(8000);
    if (inet_aton(dest2, &servaddr2.sin_addr) == 0) {
        fprintf(stderr, "Invalid second destination address: %s\n", dest2);
        close(sockfd);
        exit(1);
    }

    printf("Sending UDP to %s:8000 and %s:8000\n", dest, dest2);

    /*
    END BK stuff
    */

    while(1){
        usleep(10000);
        sendto(sockfd, "Hello, World!", 13, 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
        sendto(sockfd, "Hello, World!", 13, 0, (const struct sockaddr *)&servaddr2, sizeof(servaddr2));
    // pinhigh();
    }
    exit(0);
}
