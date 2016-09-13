#
# makefile for crc library
#

TARGET = harness
CC     = /usr/bin/gcc
CFLAGS = -O2 -fPIC
OBJS   = harness.o
SRC    = harness.c


$(TARGET):	$(OBJS)
		$(CC) $(CFLAGS) $(OBJS) ../c/crc.o -o $(TARGET)

.c.o:
	$(CC) $(CFLAGS) -c $<
 
clean:
	rm -f $(TARGET) harness.o
 

