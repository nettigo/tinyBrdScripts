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

def read_nodes(n):
    with open('nodes.csv', newline='') as csvfile:
        nodes = csv.reader(csvfile, delimiter=',', quotechar='|')
        for node in nodes:
            if len(node) == 3:
                n[node[0]] = [node[1],node[2]]

def print_with_time(val):
    print("{0}{1}".format(strftime("%d %b %Y %H:%M:%S: ", localtime()),val))            

def get_battery_percentage(batt,vmin=2500,vmax=3900):
    delta = vmax - vmin
    ret = ((batt-vmin)/delta)*100//1
    if (ret < 0):
        ret = 0
    if (ret > 100):
       ret = 100
    return ret

def setup_radio():
    radio = Radio(bytes([0,0,3]),100)
    return radio
    

def main(nodes):
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
                node_data = nodes.get(sensor_id)
                if node_data != None:
                    domo_id = node_data[0]
                else:
                    domo_id = None

                if (domo_id is None):
                    print_with_time("Unknown node")
                else:
                    node_name = str(node_data[1])

                    print_with_time ("ID:{}: Msg {}#{} from node: {} => {}".format(sensor_id,value[4],value[5],node_name,value) )
                    seq_no = value[4]
                    if sensor_id in last_seq.keys():
                        delta_seq = seq_no-last_seq[sensor_id]
                        if delta_seq != 1 & delta_seq != 255:
                            print_with_time("ID:{}: Lost packets? Seq diff: {}".format(sensor_id,delta_seq))
                        if delta_seq == 0:
                            print_with_time("ID:{}: Duplicate packet? Seq diff = 0".format(sensor_id))
                    last_seq[sensor_id] = seq_no

                    temp = value[3]

                    batt = get_battery_percentage(value[1])

            else:
                print_with_time(data)