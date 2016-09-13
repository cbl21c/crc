#!/usr/bin/python

#
# test harness for crc algorithm check
#

import crc

s = [
0x71, 0xbe, 0x71, 0xbe, 0x15, 0x5c, 0xf8, 0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x1f,
0x8b, 0xe7, 0xbe, 0x13, 0x00, 0x03, 0x79, 0x78, 0x00, 0x00, 0x00, 0x00, 0x07, 0x01, 0x08, 0x59,
0x50, 0x30, 0x28, 0x37, 0x31, 0x76, 0x55, 0x16, 0x02, 0x89, 0x04
]

s = "123456789"
# checksum should be 0x4e5ef910


# CRC32c
poly     = 0x1EDC6F41
width    = 32
init     = 0xffffffff
refin    = False
refout   = False
xorout   = 0x00000000

# CRC32
poly     = 0x04C11DB7
width    = 32
init     = 0xffffffff
refin    = True
refout   = True
xorout   = 0xffffffff
# checksum should be cbf43926
# cksum = crc.crc(s, width, poly, init, refin, refout, xorout)
# print "CRC32 checksum = %08x" % cksum

# CRC16/CCITT
poly     = 0x1021
width    = 16
init     = 0xffff
refin    = False
refout   = False
xorout   = 0x0000
# checksum should be
cksum = crc.crc(s, width, poly, init, refin, refout, xorout)
print "CRC16/CCITT checksum = %04x" % cksum

# CRC16/ARC
poly     = 0x8005
width    = 16
init     = 0x0000
refin    = True
refout   = True
xorout   = 0x0000
# checksum should be
cksum = crc.crc(s, width, poly, init, refin, refout, xorout)
print "CRC16/ARC checksum = %04x" % cksum

# CRC16/XMODEM
poly     = 0x8408
width    = 16
init     = 0x0000
refin    = True
refout   = True
xorout   = 0x0000
# checksum should be
cksum = crc.crc(s, width, poly, init, refin, refout, xorout)
print "CRC16/XMODEM checksum = %04x" % cksum

# CRC8
poly     = 0x31
# CRC8
poly     = 0x31
width    = 8
init     = 0x00
refin    = True
refout   = True
xorout   = 0x00


# CRC16 passed

# CCITT and CRC32 only pass with OPTIMISED algorithm
# non-zero initial value fails in SIMPLE and TABLE algorithms


# CRC8
poly     = 0x31
width    = 8
init     = 0x00
refin    = True
refout   = True
xorout   = 0x00

# CRC16
poly     = 0x8005
width    = 16
init     = 0x0000
refin    = True
refout   = True
xorout   = 0x0000

s = [0x6d, 0x01, 0x4b, 0x46, 0x7f, 0xff, 0x03, 0x10]
# following example from ibutton appendix
s = [0x02, 0x1c, 0xb8, 0x01, 0x00, 0x00, 0x00]
# following example from DS18B20
s = [0x2d, 0x00, 0x4b, 0x46, 0xff, 0xff, 0x08, 0x10]
s = [0x44, 0x01, 0x1e, 0x0a, 0x7f, 0xff, 0x0c, 0x10]
# cksum = crc.crc(s, width, poly, init, refin, refout, xorout)
# print "checksum = %02x" % cksum


