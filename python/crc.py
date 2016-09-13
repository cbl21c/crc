#!/usr/bin/python

#
# CRC calculation and support functions
#
# limitations:
#   width must be multiple of 8 (ie. length of polynomial is on a byte boundary)
#

#
# function to reflect the byte values in a series of bytes (could be a single byte)
#
def reflect_bytes(S):
    # S is either an integer or a list of bytes

    ref = 0

    if (type(S) is int):
        s = S

        for j in range(8):
            ref = (ref << 1) + s % 2
            s = s >> 1

        return ref

    elif (type(S) is list):
        M = []

        for i in range(len(S)):
            # check that each element in S is an int
            s = S[i]
            if (type(s) is not int):
                return None

            ref = 0
            for j in range(8):
                ref = (ref << 1) + s % 2
                s = s >> 1

            M.append(ref)

        return M

    # invalid type
    else:
        return None

    return None


#
# function to calculate mask values for a table driven algorithm
#
def buildLookupTable(poly, width):
    # width should be byte aligned
    if (width < 8 or width % 8 != 0):
        return None

    wbytes = width / 8

    # calculate a mask to restrict the values to width bits
    wmask = 0
    for n in range(wbytes):
        wmask = (wmask << 8) + 0xff

    # AND the poly just in case it runs over width bits
    poly = poly & wmask

    # initialise the lookup table
    lookup = [None] * 256

    # mask value for 0x00 is always 0x00
    lookup[0] = 0x00

    for control in range(256):
        # skip this control value if mask has already been calculated
        if lookup[control] >= 0:
            # print "already defined for ", control
            continue

        # load the top byte of register with the control value
        reg = control << (width - 8)

        # store[i] holds the control value at iteration i-8
        # this allows us to calculate the mask value at the end
        # clear the store before each calculation chain
        store = [None, None, None, None, None, None, None, None]

        iter = 0
        done = False
        endOfChain = 8
        numDone = 0

        while iter <= endOfChain:
            # print "iter: %d  reg: %04x" %(iter, reg)

            if store[iter] is not None:
                # we now have the mask for the control value 8 iterations ago
                index = store[iter] >> (width - 8)
                operand = (store[iter] << 8) & wmask
                mask = operand ^ reg
                lookup[index] = mask
                # print "index: %02x  reg: %04x  operand: %04x" %(index, reg, operand)

            index = reg >> (width - 8)

            if (lookup[index] is None) and (not done):
                # mask has not yet been calculated for current control value
                # store the whole register contents; the top byte is the control
                # and advance the endOfChain
                store.append(reg)
                endOfChain = iter + 8

                # use value -1 to identify control values that are in the pipeline
                lookup[index] = -1

                # l = len(store) - 1
                # print "    store[%d] = %02x" %(l, reg)
                # print "    endOfChain =", endOfChain
            else:
                # mask value has been calculated or is in the pipeline
                store.append(None)
                done = True
                # print "    done"

            # the simple algorithm... shift and xor
            hibit = reg >> (width - 1)
            reg = (reg << 1) & wmask

            if hibit == 1:
                reg = reg ^ poly

            # next iteration
            iter = iter + 1

        # print "End of chain\n"

    return lookup


def dumpLookupTable(table):
    for i in range(16):
        for j in range(16):
            print "%04x " %(table[i * 16 + j]),
        print


#
# crc calculation using the table driven algorithm
#
def crc(msg, width, poly, init, refin, refout, xorout):
    # width should be byte aligned
    if (width < 8 or width % 8 != 0):
        return None

    wbytes = int(width / 8)

    # calculate a mask to restrict the values to width bits
    wmask = 0
    for n in range(wbytes):
        wmask = (wmask << 8) + 0xff

    # AND the poly just in case it runs over width bits
    poly = poly & wmask

    # msg could be a string or a list of bytes
    # if it is a string convert it to a list of bytes
    if (type(msg) is str):
        M = []

        for n in range(len(msg)):
            if refin:
                M.append(reflect_bytes(ord(msg[n])))
            else:
                M.append(ord(msg[n]))

    elif (type(msg) is list):
        # check that each element in msg is an int
        for x in (msg):
            if (type(x) is not int):
                return None

        if refin:
            M = reflect_bytes(msg)
        else:
            M = msg

    # invalid type
    else:
        return None

    # generate the lookup table
    table = buildLookupTable(poly, width)
    if table is None:
        return None
    # dumpLookupTable(table)

    reg = init
    mlen = len(M)


    for n in range(mlen):
        # print "%2d %08x" %(n, reg)
        hireg = reg >> (width - 8)

        reg = (reg << 8) & wmask
        index = hireg ^ M[0]
        mask = table[index]

        M.pop(0)
        reg = reg ^ mask

    if (refout):
        # need to decompose reg into bytes...
        regbytes = []
        for n in range(wbytes):
            regbytes.append(reg & 0xff)
            reg = (reg >> 8)

        # ... reflect...
        refbytes = reflect_bytes(regbytes)

        # ... and then reconstruct
        reg = 0
        for n in range(wbytes):
            reg = (reg << 8) + refbytes[n]

    reg = reg ^ xorout

    return reg


def crc1w(msg):
    # CRC 1-Wire
    poly     = 0x31
    width    = 8
    init     = 0x00
    refin    = True
    refout   = True
    xorout   = 0x00
    return crc(msg, width, poly, init, refin, refout, xorout)

def crc16_arc(msg):
    # CRC16/ARC
    poly     = 0x8005
    width    = 16
    init     = 0x0000
    refin    = True
    refout   = True
    xorout   = 0x0000
    return crc(msg, width, poly, init, refin, refout, xorout)

def crc16_ccitt(msg):
    # CRC16/CCITT
    poly     = 0x1021
    width    = 16
    init     = 0xffff
    refin    = False
    refout   = False
    xorout   = 0x0000
    return crc(msg, width, poly, init, refin, refout, xorout)

def crc16_xmodem(msg):
    # CRC16/XMODEM
    poly     = 0x8408
    width    = 16
    init     = 0x0000
    refin    = True
    refout   = True
    xorout   = 0x0000
    return crc(msg, width, poly, init, refin, refout, xorout)

def crc32(msg):
    # CRC32
    poly     = 0x04C11DB7
    width    = 32
    init     = 0xffffffff
    refin    = True
    refout   = True
    xorout   = 0xffffffff
    return crc(msg, width, poly, init, refin, refout, xorout)

def crc32c(msg):
    # CRC32c
    poly     = 0x1EDC6F41
    width    = 32
    init     = 0xffffffff
    refin    = False
    refout   = False
    xorout   = 0x00000000
    return crc(msg, width, poly, init, refin, refout, xorout)

