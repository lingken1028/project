import network
import time
import xtools
from network import WLAN

#WIFI_SSID = "ntou"
#WIFI_PASSWORD = "20011028"
#user="00957057"
#WIFI_SSID = "小米"
#WIFI_PASSWORD = "334510.com"


# 配置Wi-Fi连接信息
SSID = 'ntou-802.1x'
USERNAME = '0095707'
PASSWORD = '20011028'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.connect(SSID, auth=(network.WLAN.WPA2_ENT, USERNAME, PASSWORD))
    while not wlan.isconnected():
        time.sleep(1)
    print('Connected to', SSID)
    print('Network config:', wlan.ifconfig())
#connect_wifi()
#dir(network)
def connect_wifi1():
    wlan = WLAN(mode=WLAN.STA_IF)
    wlan.antenna(WLAN.EXT_ANT)  
connect_wifi1()