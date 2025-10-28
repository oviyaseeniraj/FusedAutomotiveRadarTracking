CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -O2
LDFLAGS =

SRCS = master.c slave.c
PROGS = master slave

all: $(PROGS)

master: master.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@.a $<

slave: slave.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@.a $<

clean:
	rm -f $(PROGS) *.o

install: all
	@echo "No install step defined. Copy the binaries where you need them."

.PHONY: all clean install

run-master: master
	./master

run-slave: slave
	./slave

