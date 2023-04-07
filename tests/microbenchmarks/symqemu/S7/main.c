#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main(int argc, char* argv[]) {
    if (argc == 1) return -1;
    int fd = open(argv[1], O_RDONLY);
    char value;
    int res = read(fd, &value, sizeof(value));

    int f = value + 1 < 0xB;
    if (f)
        printf("OK\n");
    else
        printf("KO\n");
    printf("%d\n", f);

    return 0;
}
