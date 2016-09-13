#include <stdio.h>
#include "../c/crc.h"

int main(void)
{
    uint32_t cksum;
    uint8_t  msg[8] = {0x44, 0x01, 0x1e, 0x0a, 0x7f, 0xff, 0x0c, 0x10};
    unsigned char s[10] = "123456789";

    cksum = 0;
    // cksum = crc8_onewire(8, msg);
    // printf("CRC1W checksum = %04x\n", cksum);

    cksum = crc16_arc(9, s);
    printf("CRC16/ARC checksum = %04x\n", cksum);
    cksum = crc16_ccitt(9, s);
    printf("CRC16/CCITT checksum = %04x\n", cksum);
    cksum = crc16_xmodem(9, s);
    printf("CRC16/XMODEM checksum = %04x\n", cksum);
    cksum = crc32(9, s);
    printf("CRC32 checksum = %08x\n", cksum);

    return 0;
}

