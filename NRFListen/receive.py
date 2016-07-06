#!/usr/bin/env python3
import argparse
import struct

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('address', metavar='N', type=int, nargs=3, help='3 bytes of NRF24L01 receiver adddress')
parser.add_argument('--format',help="message format in ")
from sensor import *


args = parser.parse_args();

if (args.format):
     print(args.format)
     s=struct.Struct(args.format)
radio = setup_radio(args.address)
while True:
     if radio.available():
          data = radio.read()
          length = len(data)
          if (args.format and length ==  s.size):
               print_with_time(s.unpack(data))
          else:
               print_with_time("{} bytes: {}".format(len(data),data))
