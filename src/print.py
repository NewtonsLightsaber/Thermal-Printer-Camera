#!/usr/bin/python
# esc-pos-image.py - print image files given as command line arguments
#                    to simple ESC-POS image on stdout
# scruss - 2014-07-26 - WTFPL (srsly)

# if you want a proper CUPS driver for a 58mm thermal printer
# that uses this command set, go here:
#            https://github.com/klirichek/zj-58

import sys
from PIL import Image
import PIL.ImageOps
import struct

# give usage and exit if no arguments
if len(sys.argv) == 1:
    print 'Usage:', sys.argv[0], \
           'image1 image2 ... [ > printer_device ]'
    exit(1)

# print all of the images!
for i in sys.argv[1:]:
    im = Image.open(i)
    width = float(im.size[0])
    height = float(im.size[1])
    ratio = height/width

    if width < 400.0:
        im = im.resize( (400, (int)(400.0*ratio)), Image.BICUBIC )

    elif width > 400.0:
        im.thumbnail( (400, (int)(400.0*ratio)), Image.ANTIALIAS )

    tempIm = Image.new("RGB", (400, (int)(400.0*ratio) + 145), 'white')
    tempIm.paste(im, (0, 0))
    im = tempIm

    # if image is not 1-bit, convert it
    if im.mode != '1':
        im = im.convert('1')

    # Invert image, via greyscale for compatibility
    #  (no, I don't know why I need to do this)
    im = PIL.ImageOps.invert(im.convert('L'))
    # ... and now convert back to single bit
    im = im.convert('1')

    # output header (GS v 0 \000), width, height, image data
    sys.stdout.write(''.join(('\x1d\x76\x30\x00',
                              struct.pack('2B', im.size[0] / 8 % 256,
                                          im.size[0] / 8 / 256),
                                          struct.pack('2B', im.size[1] % 256,
                                                      im.size[1] / 256),
                                                      im.tobytes())))
