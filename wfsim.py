#
# quick WF simulator that runs for a few seconds
#
# this writes to stdout and broadcasts to udp/50222
# with example data good enough to run listener apps against
#
#

import calendar
import json
import socket
import sys
import time

# workaround WF using a bare 'null' word in some observations
#     https://stackoverflow.com/questions/27140090/how-can-json-data-with-null-value-be-converted-to-a-dictionary
null = None

# UDP broadcast ip and port
MYDEST = "255.255.255.255"
MYPORT = 50222

#--------------------------------------------------------------------------------
#
# example data from UDP API v143 2020-0208
#

INITIAL_EVT_PRECIP = { "serial_number": "SK-00008453", "type":"evt_precip", "hub_sn": "HB-00000001", 
                       "evt":[1493322445] }

INITIAL_EVT_STRIKE = { "serial_number": "AR-00004049", "type":"evt_strike", "hub_sn": "HB-00000001", 
                       "evt":[1493322445,27,3848] }

INITIAL_RAPID_WIND = { "serial_number": "SK-00008453", "type":"rapid_wind", "hub_sn": "HB-00000001", 
                       "ob":[1493322445,2.3,128] }

INITIAL_OBS_AIR = { "serial_number": "AR-00004049", "type":"obs_air", "hub_sn": "HB-00000001", 
                    "obs":[[1493164835,835.0,10.0,45,0,0,3.46,1]], "firmware_revision": 17 }

INITIAL_OBS_SKY = { "serial_number": "SK-00008453", "type":"obs_sky", "hub_sn": "HB-00000001", 
                    "obs":[[1493321340,9000,10,0.0,2.6,4.6,7.4,187,3.12,1,130,null,0,3]], "firmware_revision": 29 }

INITIAL_OBS_ST = { "serial_number": "ST-00000512", "type": "obs_st", "hub_sn": "HB-00000001", 
                    "obs": [ [1588948614,0.18,0.22,0.27,144,6,1017.57,22.37,50.26,328,0.03,3,0.000000,0,0,0,2.410,1] ], 
                    "firmware_revision": 129 }

INITIAL_DEVICE_STATUS = { "serial_number": "AR-00004049", "type": "device_status", "hub_sn": "HB-00000001", 
                          "timestamp": 1510855923, "uptime": 2189, "voltage": 3.50, "firmware_revision": 17, 
                          "rssi": -17, "hub_rssi": -87, "sensor_status": 0, "debug": 0 } 

INITIAL_HUB_STATUS = { "serial_number":"HB-00000001", "type":"hub_status", "firmware_revision":"35", 
                        "uptime":1670133, "rssi":-62, "timestamp":1495724691, "reset_flags": "BOR,PIN,POR", "seq": 48, 
                        "fs": [1, 0, 15675411, 524288], "radio_stats": [2, 1, 0, 3, 2839], "mqtt_stats": [1, 0] } 

#--------------------------------------------------------------------------------

# fake device serial numbers
HUB_SN="HB-00000001"
SKY_SN="SK-00000001"
AIR_SN="AR-00000001"
TEMPEST_SN="ST-00000001"

# initialize some python hashes
evtPrecip    = INITIAL_EVT_PRECIP
evtStrike    = INITIAL_EVT_STRIKE
rapidWind    = INITIAL_RAPID_WIND
obsAir       = INITIAL_OBS_AIR
obsSky       = INITIAL_OBS_SKY
obsSt        = INITIAL_OBS_ST
deviceStatus = INITIAL_DEVICE_STATUS
hubStatus    = INITIAL_HUB_STATUS

# use the Tempest serial number by default
evtPrecip['serial_number']    = TEMPEST_SN
evtStrike['serial_number']    = TEMPEST_SN
rapidWind['serial_number']    = TEMPEST_SN
deviceStatus['serial_number'] = TEMPEST_SN
obsSt['serial_number']        = TEMPEST_SN

def getNow():
  return calendar.timegm(time.gmtime(time.time()))

def broadcastUDP(data):

    # a little debugging
    # debugUDP(data)

    # references for this:
    #   https://github.com/ninedraft/python-udp/blob/master/server.py
    #   https://stackoverflow.com/questions/53348412/sending-json-object-to-a-tcp-listener-port-in-use-python

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.2)
    json_data = json.dumps(data)
    server.sendto(json_data.encode(), (MYDEST, MYPORT))

def debugUDP(data):
    print(data)

def calcRapidWind(data):
    data['ob'][0] = timestamp
    data['ob'][1] += 0.1          # add 1 m/s
    data['ob'][2] += 5            # move wind clockwise quickly
    if data['ob'][2]  > 359:      # keep wind between 0-359
        data['ob'][2] -= 360
    if data['ob'][1]  > 39:       # reset when it hits 39
        data['ob'][0] = 0
    broadcastUDP(data)

def calcHubStatus(data):
    data['timestamp'] = timestamp
    data['uptime'] = counter
    broadcastUDP(data)

def calcObsSt(data):
    data['obs'][0][0] = timestamp
    broadcastUDP(data)

def calcDeviceStatus(data):
    data['timestamp'] = timestamp
    broadcastUDP(data)


#--- main equivalent here ---

MAXCOUNTER = 75        # how many seconds to run before exiting
MAXCOUNTER = None  # uncomment to run forever
SLEEP=1                # seconds between loops in main()

# initialize
counter=0
while True:

    # if MAXCOUNTER is commented out, run forever
    if MAXCOUNTER is not None:
        if counter > MAXCOUNTER:
            sys.exit(1)

    timestamp = getNow()

    # rapid_wind is once per 3 secs
    if (counter % 3) == 0:
        calcRapidWind(rapidWind)

    # obs_hub is every 10 secs
    if (counter % 10) == 1:
        calcHubStatus(hubStatus)

    # obs_st is every 60 secs
    if (counter % 60) == 2:
        calcObsSt(obsSt)

    # device_status is every 60 secs
    if (counter % 60) == 5:
        calcDeviceStatus(deviceStatus)

    counter += 1
    time.sleep(1)

