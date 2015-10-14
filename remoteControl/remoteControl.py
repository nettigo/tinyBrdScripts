#import tinybrd
from tinybrd import Radio

import struct
from time import localtime, strftime, sleep, time
import sys
import socket
import signal

remote = bytes([3,0,0])

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def print_with_time(val):
    print("{0}{1}".format(strftime("%d %b %Y %H:%M:%S: ", localtime()),val))            

def setup_radio():
    radio = Radio(bytes([0,0,3]),100)
    return radio

def set_led(r,nr):
    b=bytes([102,nr])
    r.write(remote,b)
    r.flush()    

def map_value(x, min_x, max_x, min_res, max_res):
    ret = x/(max_x-min_x)*(max_res-min_res) + min_res    
    if ret > max_res:
        ret = max_res
    if ret < min_res:
        ret = min_res
    return ret

def read_analog(r):
    b = bytes([99])
    r.write(remote,b)
    r.flush()
#    print_with_time("Command sent")

def read_data():
    radio = setup_radio()
    cnt = time()
    response = False
    while True:
#        sleep(0.05);
        if (time() - cnt > 0.1 or response):
            read_analog(radio)
            cnt = time()
            response = False
        
        if radio.available():
#            print_with_time("Got response")
            data = radio.read()
            response = True
#            print_with_time(data)
            if (len(data)==3):
                value = struct.unpack('=BH', data)
                                    # 0 - id
                                    # 1 - potentiometer
                sensor_id = value[0]
                pot = value[1]
                mapped = bytes([int(map_value(pot,0,1023,0,3))])
                print_with_time ("ID:{}: AnalogRead:{}, map {}".format(sensor_id,pot,mapped))
                set_led(radio,pot)

while True:
    print_with_time("Start")
    read_data()
        