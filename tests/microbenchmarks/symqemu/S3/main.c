#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <arpa/inet.h>

int main(int argc, char* argv[]) {
    if (argc == 1) return -1;
    int fd = open(argv[1], O_RDONLY);
    
    int value;
    int res = read(fd, &value, sizeof(value));
    
    value = ntohl(value);

    if (value == 10)
        printf("OK\n");
    else
        printf("KO\n");
    printf("Value: %d\n", value);
    return 0;
}