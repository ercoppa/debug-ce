#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <arpa/inet.h>
#include <string.h>

int main(int argc, char* argv[]) {
    if (argc == 1) return -1;
    int fd = open(argv[1], O_RDONLY);
    
    uint8_t value[10];
    int res = read(fd, &value, sizeof(value));
    
    uint8_t expected[] = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    };
    
    if (memcmp(value, expected, sizeof(value)) == 0)
        printf("OK\n");
    else
        printf("KO\n");
    return 0;
}