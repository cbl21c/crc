/* Library for CRC calculation */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "crc.h"

#define TRUE  1
#define FALSE 0
#define NONE  0

/* lookup table for table driven CRC algorithm */
uint32_t crcLookupTable[256];
uint32_t lastPoly = 0;

/* function to reflect byte values in-position */
int _reflect(int size, uint8_t *data)
{
    int n;
    int b;
    uint8_t bit;
    uint8_t ch;
    uint8_t reflected;

    if (size <= 0)
        return -1;

    for (n = 0; n < size; n++)
    {
        reflected = 0;
        ch = data[n];

        for (b = 0; b < 8; b++)
        {
            bit = ch % 2;
            reflected = (reflected << 1) + bit;
            ch = ch >> 1;
        }

        data[n] = reflected;
    }

    return 0;
}


int _buildLookupTable(uint32_t poly, uint32_t width)
{
    int m;
    int n;
    int control;
    int done;
    uint8_t  index;
    uint8_t  hibit;
    uint8_t  iter;
    uint8_t  endOfChain;
    uint8_t  pipeline[256];
    uint8_t  numStore;
    uint32_t reg;
    uint32_t operand;
    uint32_t wmask;
    uint32_t mask;
    uint32_t store[256];

    /* width should be byte aligned, and a maximum of 32 */
    if ((width % 8 != 0) || width > 32)
        return -1;

    /* calculate a mask to restrict the value to width bits */
    wmask = 0;
    for (n = 0; n < width / 8; n++)
        wmask = (wmask << 8) + 0xff;

    /* bitwise AND the poly in case it runs over width bits */
    lastPoly = poly;
    poly = poly & wmask;

    /* zero the lookup table */
    memset(crcLookupTable, 0, 256 * sizeof(uint32_t));
    memset(pipeline, 0, 256);

    /*
    ** calculate the lookup table by using chains:
    ** at each iteration, the top byte of reg contains a control value
    ** drive the algorithm until the mask is calculated for the
    ** control value in reg
    */
    for (control = 1; control < 256; control++)
    {
        /*
        ** the only time the mask value is 0 is when the control value is 0
        ** use this fact to determine if the mask has been calculated or not
        ** skip this control value if mask has already been calculated
        */
        if (crcLookupTable[control] > 0)
            continue;

        /* load the top byte of register with the control value */
        reg = control << (width - 8);

        /*
        ** store[i] holds the control value at iteration i-8
        ** this allows us to calculate the mask value at the end
        ** clear the store before each calculation chain;
        ** pipeline[i] identifies control values that are in the current
        ** chain and will be calculated
        */
        memset(store, NONE, 256 * sizeof(uint32_t));
        numStore = 8;

        iter = 0;
        done = FALSE;
        endOfChain = 8;

        while (iter <= endOfChain)
        {
            if (store[iter] != NONE)
            {
                index = store[iter] >> (width - 8);
                operand = (store[iter] << 8) & wmask;
                mask = operand ^ reg;
                crcLookupTable[index] = mask;
            }

            index = reg >> (width - 8);

            /*
            ** check if mask has been calculated or is in the pipeline
            ** for current control value...
            */
            if (crcLookupTable[index] == NONE && index > 0 && !pipeline[index] && !done)
            {
                /*
                ** ...not yet, so store the whole register contents
                ** the top byte is the control value
                ** advance the endOfChain and flag index as being in the pipeline
                */
                store[numStore++] = reg;
                endOfChain = iter + 8;
                pipeline[index] = 1;
            }
            else
            {
                store[numStore++] = NONE;
                done = TRUE;
            }

            /* the simple algorithm... shift and xor */
           hibit = reg >> (width - 1);
           reg = (reg << 1) & wmask;

           if (hibit)
               reg = reg ^ poly;

           /* next iteration */
           iter++;
        }
    }

    return 0;
}


int _dumpLookupTable(void)
{
    int m, n;

    for (m = 0; m < 16; m++)
    {
        for (n = 0; n < 16; n++)
            printf("%04x  ", crcLookupTable[m * 16 + n]);

        printf("\n");
    }

    return 0;
}


uint8_t crc8_onewire(uint32_t size, uint8_t *m)
{
    crc_t crcpars;
    uint8_t cksum;

    crcpars.poly   = 0x31;
    crcpars.width  = 8;
    crcpars.init   = 0x00;
    crcpars.refin  = TRUE;
    crcpars.refout = TRUE;
    crcpars.xorout = 0x00;

    cksum = (uint8_t) crc(&crcpars, size, m);
    return cksum;
}


uint16_t crc16_arc(uint32_t size, uint8_t *m)
{
    crc_t crcpars;
    uint16_t cksum;

    crcpars.poly   = 0x8005;
    crcpars.width  = 16;
    crcpars.init   = 0x0000;
    crcpars.refin  = TRUE;
    crcpars.refout = TRUE;
    crcpars.xorout = 0x0000;

    cksum = (uint16_t) crc(&crcpars, size, m);
    return cksum;
}


uint16_t crc16_ccitt(uint32_t size, uint8_t *m)
{
    crc_t crcpars;
    uint16_t cksum;

    crcpars.poly   = 0x1021;
    crcpars.width  = 16;
    crcpars.init   = 0xffff;
    crcpars.refin  = FALSE;
    crcpars.refout = FALSE;
    crcpars.xorout = 0x0000;

    cksum = (uint16_t) crc(&crcpars, size, m);
    return cksum;
}


uint16_t crc16_xmodem(uint32_t size, uint8_t *m)
{
    crc_t crcpars;
    uint16_t cksum;

    crcpars.poly   = 0x8408;
    crcpars.width  = 16;
    crcpars.init   = 0x0000;
    crcpars.refin  = TRUE;
    crcpars.refout = TRUE;
    crcpars.xorout = 0x0000;

    cksum = (uint16_t) crc(&crcpars, size, m);
    return cksum;
}


uint32_t crc32(uint32_t size, uint8_t *m)
{
    crc_t crcpars;
    uint32_t cksum;

    crcpars.poly   = 0x04c11db7;
    crcpars.width  = 32;
    crcpars.init   = 0xffffffff;
    crcpars.refin  = TRUE;
    crcpars.refout = TRUE;
    crcpars.xorout = 0xffffffff;

    cksum = (uint32_t) crc(&crcpars, size, m);
    return cksum;
}


uint32_t crc32c(uint32_t size, uint8_t *m)
{
    crc_t crcpars;
    uint32_t cksum;

    crcpars.poly   = 0x1edc6f41;
    crcpars.width  = 32;
    crcpars.init   = 0xffffffff;
    crcpars.refin  = FALSE;
    crcpars.refout = FALSE;
    crcpars.xorout = 0x00000000;

    cksum = (uint32_t) crc(&crcpars, size, m);
    return cksum;
}


uint32_t crc(crc_t *p, uint32_t size, uint8_t *m)
{
    int n;
    uint32_t reg;
    uint32_t regout;
    uint8_t regbytes[4];
    uint8_t index;
    uint8_t hireg;
    uint8_t *data;
    uint32_t wmask;

    data = NULL;

    /* calculate a mask to restrict the value to width bits */
    wmask = 0;
    for (n = 0; n < p->width / 8; n++)
        wmask = (wmask << 8) + 0xff;

    /* build the lookup table if necessary */
    if (lastPoly != p->poly)
    {
        _buildLookupTable(p->poly, p->width);
        // _dumpLookupTable();
    }

    /* make a copy of the data... */
    data = malloc(size);
    memcpy(data, m, size);

    /* and reflect it if necessary */
    if (p->refin)
        _reflect(size, data);

    /* load initial register value */
    reg = p->init;

    for (n = 0; n < size; n++)
    {
        /* pop one byte from register, and use it to calculate next index */
        hireg = (reg >> (p->width - 8)) & 0xff;
        reg = (reg << 8) & wmask;

        index = hireg ^ data[n];
        reg = reg ^ crcLookupTable[index];
    }

    /* we don't need the data copy any more */
    free(data);

    /*
    ** if the register value is to be reflected, the register must be treated
    ** as a single value and reflected; equivalently we can reverse the byte
    ** order of byte-wise reflected values
    */
    regout = reg;
    if (p->refout)
    {
        /* decompose reg into bytes... */
        for (n = 0; n < p->width / 8; n++)
        {
            regbytes[n] = regout & 0xff;
            regout = regout >> 8;
        }

        /* ... reflect... */
        _reflect(p->width / 8, regbytes);

        /* ... and reconstruct */
        regout = 0;
        for (n = 0; n < p->width / 8; n++)
            regout = (regout << 8) + regbytes[n];
    }

    /* xor register before returning its value */
    regout = regout ^ p->xorout;

    return regout;
}

