from time import localtime, strftime, sleep
import urllib.parse
import urllib.request
from urllib.error import URLError, HTTPError
import sys
import socket
import signal


DOMO_URL = 'http://10.10.1.2:8080/'
DOMO_USER = 'nettigo'
DOMO_PASS = 'haslo'
radio = ''

def get_battery_percentage(batt,vmin=2500,vmax=3900):
    delta = vmax - vmin
    ret = ((batt-vmin)/delta)*100//1
    if (ret < 0):
        ret = 0
    if (ret > 100):
       ret = 100
    return ret

def setup_domoticz_password():
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

    # Add the username and password.
    # If we knew the realm, we could use it instead of None.
    top_level_url = DOMO_URL
    password_mgr.add_password(None, top_level_url, DOMO_USER, DOMO_PASS)

    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

    # create "opener" (OpenerDirector instance)
    opener = urllib.request.build_opener(handler)

    # use the opener to fetch a URL
    try:
        opener.open(DOMO_URL)
    except (URLError, socket.error) as e:
        print_with_time('We failed to reach a server. Reason: '+ str(e.reason) )
    except HTTPError as e:
        print_with_time('The server couldn\'t fulfill the request. Error code: '+str(e.code) )
    # Install the opener.
    # Now all calls to urllib.request.urlopen use our opener.
    urllib.request.install_opener(opener)


def domo():
    setup_domoticz_password()
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

                    model = {
                            'type': 'command', 
                            'param': 'udevice',
                            'idx': domo_id,
                            'nvalue': 0,
                            'svalue': temp,
                            'battery': batt
                            }

                    params = urllib.parse.urlencode(model)
                    url = '{url}json.htm?{params}'.format(params=params,url=DOMO_URL)
                    print_with_time(url)
#                    try:
#                        req = urllib.request.urlopen(url)
#                        data = req.read()
#                    except HTTPError as e:
#                        print_with_time('The server couldn\'t fulfill the request. Error code: '+str(e.code) )
#                    except URLError as e:
#                        print_with_time('We failed to reach a server. Reason: '+ str(e.reason) )
#                    except socket.error as e:
#                        print_with_time('We failed to reach a server. Reason: '+ str(e.reason) )

#        sleep(0.1)
            else:
                print_with_time(data)