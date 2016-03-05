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
    radio = Radio(bytes([0,0,3]),100)
    return radio
    

def main():
    radio = setup_radio()
    last_seq = {}
            
    while True:
        if radio.available():
            data = radio.read()
            if (len(data)==12):
                value = struct.unpack('=BlBfBB', data)
                                    # 0 - id
                                    # 1 - battery
                                    # 2 - status
                                    # 3 - temperature
                                    # 4 - seqential no
                                    # 5 - retry no
                sensor_id = str(value[0])

                print_with_time ("ID:{}: Msg {}#{} from node: {} => {}".format(sensor_id,value[4],value[5],sensor_id,value) )
                seq_no = value[4]
                if sensor_id in last_seq.keys():
                    delta_seq = seq_no-last_seq[sensor_id]
                    if delta_seq != 1 & delta_seq != 255:
                        print_with_time("ID:{}: Lost packets? Seq diff: {}".format(sensor_id,delta_seq))
                    if delta_seq == 0:
                        print_with_time("ID:{}: Duplicate packet? Seq diff = 0".format(sensor_id))
                last_seq[sensor_id] = seq_no



            else:
                if (len(data) > 32):
                    radio = setup_radio()
                    print_with_time("Got {} bytes, not recognized as proper message, resetting radio".format(len(data)) )
                print_with_time(data)