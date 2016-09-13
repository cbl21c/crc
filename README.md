# CRC Library
This repository contains C and Python libraries for CRC calculation. CRC checksums
can be calculated for CRC polynomials whose width is a multiple of 8. The CRC
calculations are performed using a table driven algorithm.<br>
Common CRC algorithms are supported through direct call functions so that the CRC
parameters do not need to be configured by the user:<br>
<pre>
<b>crc8_onewire</b> for Dallas One Wire CRC
<b>crc16_arc</b> for a 16-bit CRC as used in ARC
<b>crc16_ccitt</b> for a 16-bit CRC defined in ITU-T recommendations
<b>crc16_xmodem</b> for a 16-bit CRC used in the Xmodem protocol
<b>crc32</b> for the CRC32 algorithm
<b>crc32c</b> for the CRC32C algorithm
</pre>

<h3>C</h3>
The general CRC calculation is invoked with a call to<br>

<pre>
<b>crc</b>(crc_t *p, uint32_t size, uint8_t *msg)
</pre>

where size is the size of the message and msg is an byte array containing the
message for which the checksum is to be calculated.<br>
The struct crc_t is defined as<br>
<pre>
typedef struct crc
{
    uint32_t poly;
    uint8_t  width;
    uint32_t init;
    uint8_t  refin;
    uint8_t  refout;
    uint32_t xorout;
} crc_t;
</pre>

The attributes follow the nomenclature presented in Ross Williams' "A Painless Guide
to CRC Error Detection Algorithms". A crc_t structure should be constructed with the
desired CRC parameters prior to calling the crc() function.<br>

<h3>Python</h3>
The general CRC calculation is invoked with a call to<br>

<pre>
<b>crc</b>(msg, width, poly, init, refin, refout, xorout)
</pre>

There is no crc_t data structure for the Python library calls. The CRC parameters
are passed into the functions individually. No size parameter is required because
the size of a list can be determined without triggering an exception.

