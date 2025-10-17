#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>

#ifdef JETSON
    #include <jetgpio.h>
#endif

volatile sig_atomic_t stop = 0;

/* Hardware hook: pull a pin high when a packet arrives.
 * Provide a weak, empty default implementation so builds succeed on platforms
 * without a board-specific implementation. Users may provide their own
 * implementation (non-weak) to perform the actual GPIO operation.
 */
void pinhigh(void) __attribute__((weak));
void pinhigh(void) {
    #ifdef JETSON
    gpioWrite(7,1);
    usleep(100);
    gpioWrite(7,0);
    #endif
}
void setupin(void)  __attribute__((weak));
void setupin(void) {
    #ifdef JETSON
    gpioSetMode(7, JET_OUTPUT);
    #endif
    return;
}

void handle_sigint(int signo)
{
    (void)signo;
    stop = 1;
}

int main(int argc, char *argv[])
{
    int sockfd;
    struct sockaddr_in servaddr, cliaddr;
    socklen_t len;
    ssize_t n;
    char buf[2048];

    (void)argc; (void)argv;

    /* Create UDP socket */
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        exit(1);
    }

    int opt = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt SO_REUSEADDR failed");
        /* not fatal */
    }

    /* Bind to port 8000 on all interfaces */
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(8000);

    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("Bind failed");
        close(sockfd);
        exit(1);
    }

    /* Handle Ctrl-C to exit cleanly */
    signal(SIGINT, handle_sigint);

    printf("Listening for UDP packets on port 8000. Press Ctrl-C to exit.\n");

    while (!stop) {
        fd_set rfds;
        FD_ZERO(&rfds);
        FD_SET(sockfd, &rfds);

        struct timeval tv;
        tv.tv_sec = 1;  /* 1 second timeout to wake up and check stop flag */
        tv.tv_usec = 0;

        int rv = select(sockfd + 1, &rfds, NULL, NULL, &tv);
        if (rv < 0) {
            if (errno == EINTR) {
                /* interrupted by signal: check stop flag and exit loop if set */
                if (stop) break;
                continue;
            }
            perror("select failed");
            break;
        } else if (rv == 0) {
            /* timeout, loop again to check stop flag */
            continue;
        }

        if (FD_ISSET(sockfd, &rfds)) {
            len = sizeof(cliaddr);
            n = recvfrom(sockfd, buf, sizeof(buf) - 1, 0, (struct sockaddr *)&cliaddr, &len);
            if (n < 0) {
                if (errno == EINTR) {
                    if (stop) break;
                    continue;
                }
                perror("recvfrom failed");
                break;
            }

            buf[n] = '\0';

            /* Signal hardware that a packet arrived */
            pinhigh();
        }
    }
    close(sockfd);
    printf("Exiting.\n");
    return 0;
}
