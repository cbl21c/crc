#!/usr/bin/python

#
# CRC functions based on the descriptions in
# "A Painless Guide to CRC Error Detection Algorithms"
# by Ross Williams (1993)
#
# The CRC function is developed incrementally based on
# the sections in the guide
#


#########################################
#                                       #
#  reflect(x, width)                    #
#                                       #
#  function to reflect a single integer #
#  where the size (width) can be passed #
#  as a parameter                       #
#                                       #
#########################################

def reflect(x, width):
    wbytes = int(width / 8)
    wmask = 0
    for n in range(wbytes):
        wmask = (wmask << 8) + 0xff

    x = x & wmask
    ref = 0
    for n in range(width):
        ref = (ref << 1) + (x % 2)
        x = x >> 1

    return ref


########################################
#                                      #
#  reflect_bytes(S)                    #
#                                      #
#  function to reflect the byte values #
#  in a series of bytes                #
#  (could be a single byte)            #
#                                      #
########################################

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

    # invalid types will fall through there
    return None


###########################################
#                                         #
#  crcLookupTable(poly, width, reftable)  #
#                                         #
#  function to calculate mask values      #
#  for a table driven algorithm           #
#                                         #
###########################################

def crcLookupTable(poly, width, reftable):
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
            continue

        # load the top byte of register with the control value
        reg = control << (width - 8)

        # store[i] holds the control value at iteration i-8
        # this allows us to calculate the mask value at the end
        # clear the store before each calculation chain
        store = [None] * 8

        iter = 0
        done = False
        endOfChain = 8
        numDone = 0

        while iter <= endOfChain:
            if store[iter] is not None:
                # we now have the mask for the control value 8 iterations ago
                index = store[iter] >> (width - 8)
                operand = (store[iter] << 8) & wmask
                mask = operand ^ reg
                lookup[index] = mask

            index = reg >> (width - 8)

            if (lookup[index] is None) and (not done):
                # mask has not yet been calculated for current control value
                # enter the control value in store and advance the endOfChain
                store.append(reg)
                endOfChain = iter + 8

                # use value -1 to identify control values that are in the pipeline
                lookup[index] = -1
            else:
                # mask value has been calculated or is in the pipeline
                store.append(None)
                done = True

            # the simple algorithm... shift and xor
            hibit = reg >> (width - 1)
            reg = (reg << 1) & wmask

            if hibit == 1:
                reg = reg ^ poly

            # next iteration
            iter = iter + 1

    if reftable is False:
        return lookup

    # reftable is true so we need to reflect the table
    reflookup = [None] * 256

    for n in range(256):
        ref_index = reflect(n, 8)
        ref_value = reflect(lookup[n], 32)
        reflookup[ref_index] = ref_value

    return reflookup


#######################################
#                                     #
#  dumpTable(table, ncols)            #
#                                     #
#  dump the crc lookup table          #
#                                     #
#######################################

def dumpTable(table, width, ncols):

    if type(table) is not list:
        return None

    if len(table) != 256:
        return None

    nhex = width / 4
    fmt = "%%0%dx" % nhex

    nrows = int(256 / ncols)
    for j in range(nrows):
        for i in range(ncols):
            k = j * ncols + i
            print fmt % table[k],

        print


#
# Section 8: the simple algorithm
#
# accepts: message, width, poly, init, refin, refout, xorout
#
def s8crc(msg, width, poly, init, refin, refout, xorout):
    wbytes = int(width / 8)

    # check if we need to reflect the data bytes
    if refin:
        msg = reflect_bytes(msg)

    mbits = len(msg) * 8 + width
    reg = init
    hireg = 0

    # calculate the wmask
    wmask = 0
    for n in range(wbytes):
        wmask = (wmask << 8) + 0xff

    # AND the poly just in case it runs over width bits
    poly = poly & wmask

    for n in range(mbits):
        # print "%04x" % reg

        # calculate the top bit before shifting out of register
        hireg = reg >> (width - 1)
        reg = ((reg << 1) + (msg[0] >> 7)) & wmask

        if (hireg == 1):
            reg = reg ^ poly

        if (n % 8 == 7):
            # we have used up all the bits in the next message byte
            # so discard the first byte and append a zero byte
            # to the message to ensure that we don't access outside the list limits
            msg = msg[1:] + [0]
        else:
            msg[0] = (msg[0] << 1) & 0xff


    # check if we need to reflect the checksum
    if refout:
        reg = reflect(reg, width)

    reg = reg ^ xorout

    return reg


#
# Section 9: table driven implementation
#
# accepts: message, width, poly, init, refin, refout, xorout
#
def s9crc(msg, width, poly, init, refin, refout, reftable, xorout):
    wbytes = int(width / 8)

    # check if we need to reflect the data bytes
    if refin:
        msg = reflect_bytes(msg)

    # calculate a mask to restrict the values to width bits
    wmask = 0
    for n in range(wbytes):
        wmask = (wmask << 8) + 0xff

    # AND the poly just in case it runs over width bits
    poly = poly & wmask

    # generate the lookup table
    table = crcLookupTable(poly, width, reftable)
    if table is None:
        return None

    reg = init
    msg = msg + [0] * wbytes
    mlen = len(msg)

    for n in range(mlen):
        # print "%04x" % reg
        hireg = reg >> (width - 8)

        reg = ((reg << 8) & wmask) + msg[0]
        mask = table[hireg]

        msg.pop(0)
        reg = reg ^ mask

    # check if we need to reflect the checksum
    if refout:
        reg = reflect(reg, width)

    reg = reg ^ xorout

    return reg


#
# Section 10: optimised table driven implementation
#
# accepts: message, width, poly, init, refin, refout, reftable, xorout
#
def s10crc(msg, width, poly, init, refin, refout, reftable, xorout):

    wbytes = int(width / 8)

    # check if we need to reflect the data bytes
    if refin:
        msg = reflect_bytes(msg)

    # calculate a mask to restrict the values to width bits
    wmask = 0
    for n in range(wbytes):
        wmask = (wmask << 8) + 0xff

    # AND the poly just in case it runs over width bits
    poly = poly & wmask

    # generate the lookup table
    table = crcLookupTable(poly, width, reftable)
    if table is None:
        return None

    # dumpTable(table, width, 4)

    reg = init
    mlen = len(msg)

    for n in range(mlen):
        # print "%04x" % reg
        hireg = reg >> (width - 8)

        reg = (reg << 8) & wmask
        index = hireg ^ msg[0]
        mask = table[index]

        msg.pop(0)
        reg = reg ^ mask

    # check if we need to reflect the checksum
    if refout:
        reg = reflect(reg, width)

    reg = reg ^ xorout

    return reg


#
# Section 11: reflected table implementation
#
# accepts: message, width, poly, init, refin, refout, reftable, xorout
#
def s11crc(msg, width, poly, init, refin, refout, reftable, xorout):

    wbytes = int(width / 8)

    # check if we need to reflect the data bytes
    if refin:
        msg = reflect_bytes(msg)

    # calculate a mask to restrict the values to width bits
    wmask = 0
    for n in range(wbytes):
        wmask = (wmask << 8) + 0xff

    # AND the poly just in case it runs over width bits
    poly = poly & wmask

    # generate the lookup table
    table = crcLookupTable(poly, width, reftable)
    if table is None:
        return None

    reg = init
    mlen = len(msg)

    for n in range(mlen):
        # print "%04x" % reg
        loreg = reg & 0xff

        reg = reg >> 8
        index = loreg ^ msg[0]
        mask = table[index]

        msg.pop(0)
        reg = reg ^ mask

    # check if we need to reflect the checksum
    if refout:
        reg = reflect(reg, width)

    reg = reg ^ xorout

    return reg


######################################
#                                    #
#  crc()                             #
#                                    #
#  wrapper function for the various  #
#  crc algorithms                    #
#                                    #
######################################

def crc(msg, width, poly, init, refin, refout, reftable, xorout):
    #
    # validate and format the arguments
    #

    # width should be byte aligned
    if (width < 8 or width % 8 != 0):
        return None

    # msg could be a string or a list of bytes
    # if it is a string convert it to a list of bytes
    if (type(msg) is str):
        M = []

        for n in range(len(msg)):
            M.append(ord(msg[n]))

    elif (type(msg) is list):
        # check that each element in msg is an int
        for x in (msg):
            if (type(x) is not int):
                return None

        M = msg

    # invalid type
    else:
        return None


    # create a copy of M when passing to crc function
    # otherwise the reference M will be passed
    # and contents will be modified
    cksum = s8crc(M[:], width, poly, init, refin, refout, xorout)
    print "SIMPLE    algorithm: %08x" % cksum

    cksum = s9crc(M[:], width, poly, init, refin, refout, reftable, xorout)
    print "TABLE     algorithm: %08x" % cksum

    cksum = s10crc(M[:], width, poly, init, refin, refout, reftable, xorout)
    print "OPTIMISED algorithm: %08x" % cksum

    cksum = s11crc(M[:], width, poly, init, refin, refout, reftable, xorout)
    print "REFLECTED algorithm: %08x" % cksum


