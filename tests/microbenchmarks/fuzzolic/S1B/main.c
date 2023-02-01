#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <sys/vfs.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char* argv[]) {
    if (argc == 1) return -1;
    int fd = open(argv[1], O_RDONLY);
    
    unsigned char buf[4] = { 0 };
    int res = read(fd, &buf[0], 1);
    
    if (buf[0] == 10)
        printf("OK\n");
    else
        printf("KO\n");
    
    lseek(fd, 0, SEEK_SET);
    res = read(fd, &buf[1], 1);

    if (buf[1] == 10)
        printf("OK\n");
    else
        printf("KO\n");
    // printf("Value: %d\n", buf[1]);

    /*
    struct statfs* buf = malloc(sizeof(struct statfs));

    int* value = (int*)&buf;
    int res = read(fd, value, sizeof(int));

    statfs(argv[1], buf);

    if (*value == 10)
        printf("OK\n");
    else
        printf("KO\n");
    printf("Value: %d\n", *value);
    */
    return 0;
}