#ifndef __crc_h__
#define __crc_h__


#include <stdint.h>

#define TRUE  1
#define FALSE 0

// typedef u_int8 uint8_t;

typedef struct crc
{
    uint32_t poly;
    uint8_t  width;
    uint32_t init;
    uint8_t  refin;
    uint8_t  refout;
    uint32_t xorout;
} crc_t;

    
extern uint32_t crc(crc_t*, uint32_t size, uint8_t*);

/* common crc algorithms, so users do not have to construct the parameter set */
extern uint8_t crc1w(uint32_t, uint8_t*);
extern uint16_t crc16_arc(uint32_t, uint8_t*);
extern uint16_t crc16_ccitt(uint32_t, uint8_t*);
extern uint16_t crc16_xmodem(uint32_t, uint8_t*);
extern uint32_t crc32(uint32_t, uint8_t*);
extern uint32_t crc32c(uint32_t, uint8_t*);


#endif

