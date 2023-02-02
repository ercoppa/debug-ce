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
    
    lseek(fd, 1, SEEK_CUR);
    res = read(fd, &buf[1], 1);

    if (buf[1] == 10)
        printf("OK\n");
    else
        printf("KO\n");
    
    return 0;
}