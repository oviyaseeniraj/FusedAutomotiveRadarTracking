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

static char* netmask = "192.168.0.255";
void pinhigh(void) __attribute__((weak));
void pinhigh(void) { }

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
     
    // Allow broadcast if we send to the broadcast address
    int opt = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt)) < 0) {
        perror("setsockopt SO_BROADCAST failed");
        /* not fatal on all systems */
    }

    // Set destination addresses
    // const char *dest = (argc > 1) ? argv[1] : "192.168.0.97";
    // const char *dest2 = (argc > 2) ? argv[2] : "192.168.0.22"; /* second IP */


    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(8000);
    if (inet_aton(netmask, &servaddr.sin_addr) == 0) {
        fprintf(stderr, "Invalid second destination address: %s\n", netmask);
        close(sockfd);
        exit(1);
    }

    printf("Sending UDP to %s:8000 and %s:8000\n", netmask);

    /*
    END BK stuff
    */

    while(1){
        usleep(10000);
        //"broadcasting 50 packets"
        for(int i=0; i<50; i++){
            sendto(sockfd, "1", 1, 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
        }
    // pinhigh();
    }
    exit(0);
}
