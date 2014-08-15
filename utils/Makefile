CC = i686-w64-mingw32-gcc
CFLAGS = -Wall -Wextra -s -O2

SRC = $(wildcard *.c)
EXE = $(SRC:%.c=%.exe)

all: $(EXE)

%.exe: %.c
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	rm -rf $(EXE)
