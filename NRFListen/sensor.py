from tinybrd import Radio

import csv
import struct
from time import localtime, strftime, sleep
import urllib.parse
import urllib.request
from urllib.error import URLError, HTTPError
import sys
import socket
import signal

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

radio = ''

def print_with_time(val):
    print("{0}{1}".format(strftime("%d %b %Y %H:%M:%S: ", localtime()),val))            

def setup_radio():
    radio = Radio(bytes([99,0,3]),100)
    return radio
    

def main():
    radio = setup_radio()
    last_seq = {}
            
    while True:
        if radio.available():
            data = radio.read()
            if (len(data)==5):
                value = struct.unpack('=Bf', data)
                                    # 0 - id
                                    # 1 - temperature
                sensor_id = str(value[0])

                print_with_time ("ID:{}: Msg from node: {} => {}".format(sensor_id,sensor_id,value) )



            else:
                if (len(data) > 32):
                    radio = setup_radio()
                    print_with_time("Got {} bytes, not recognized as proper message, resetting radio".format(len(data)) )
                print_with_time(data)