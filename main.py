import machine
import network
import time,utime
import xtools
import hx711
from machine import Pin
from urlencode import urlencode
from umqtt.simple import MQTTClient
import urequests
import json
import gc
from machine import RTC
import ntptime
from machine import lightsleep

data = []  # 存储Excel数据的数组
device=2
num=4
settime=0
# Wi-Fi 設定
#WIFI_SSID = "Mi 10 Pro"
#WIFI_PASSWORD = "lingningken"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Load Cell 和 HX711 的引腳設定
DT_PIN = 12
SCK_PIN = 13

# 初始化 HX711
print("0")
hx = hx711.HX711(DT_PIN, SCK_PIN)
reference_unit = 100000  # 校準單位(重量單位對應的數值)
offset = 0  # 零點偏移量
print("1")
hx.set_scale(reference_unit)
print("2")
hx.set_offset(offset)
print("3")
#hx.reset()
print("4")
hx.tare()

# 初始化 Wi-Fi 連線
def connect_wifi(ssid, passwd):
    ch=1;
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
       time.sleep(1)
       print("Connecting to network...")
       wlan.connect(ssid, passwd)
       while not wlan.isconnected():
          pass
    print("Wi-Fi 連線成功")
    #print("IP 地址:", wlan.ifconfig()[0])
    try:
        ntptime.settime()
    except OSError as e:
        while(ch):
            try:
                utime.sleep(1)
                ntptime.settime()
                ch=0
            except OSError:
                pass
def openw():
    connect_wifi(WIFI_SSID,WIFI_PASSWORD)
def close():
    print("Entering modem sleep mode...")
    wlan.disconnect()  # 斷開 Wi-Fi 連接
    wlan.active(False)  # 關閉 Wi-Fi 模塊
# 檢查衛生紙是否已用完並發送郵件
def check_paper_status():
    global num
    weight_threshold = 0.3  # 設定衛生紙用盡的重量閾值,根據實際情況進行調整
    weight_7 = 2.1
    weight_3 = 0.9
    weight = get_paper_weight()
    #weight= float(weight/100000.00) #变成kg
    weight = float("{:.6f}".format(weight))
    print(weight)
    if weight < weight_threshold and num!=0:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight < weight_threshold and num!=0:
            print("卫生纸用完了,发送line {}".format(weight))
            #send_email_notification()
            del weight
            openw()
            gc.collect()
            utime.sleep(2)
            send_line_notification(0)
            gc.collect()
            utime.sleep(2)
            up(device,0)
            num=0;
            close()
    elif weight >= weight_threshold and weight < weight_3 and num!=3:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight >= weight_threshold and weight < weight_3 and num!=3:
            print("卫生纸3-1成,发送line {}".format(weight))
            #send_email_notification()
            del weight
            openw()
            gc.collect()
            utime.sleep(2)
            send_line_notification(3)
            gc.collect()
            utime.sleep(2)
            up(device,3)
            num=3;
            close()
    elif weight >= weight_3 and weight < weight_7 and num!=2:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight >= weight_3 and weight < weight_7 and num!=2:
            print("卫生纸7-3成,发送line {}".format(weight))
            #send_email_notification()
            del weight
            openw()
            gc.collect()
            utime.sleep(2)
            send_line_notification(2)
            gc.collect()
            utime.sleep(2)
            up(device,2)
            num=2;
            close()
    elif weight >= weight_7  and num!=1:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight >= weight_7  and num!=1:
            print("卫生纸10-7成,发送line {}".format(weight))
            #send_email_notification()
            del weight
            openw()
            gc.collect()
            utime.sleep(2)
            send_line_notification(1)
            gc.collect()
            utime.sleep(2)
            up(device,1)
            num=1;
            close()
# 取得衛生紙重量
def get_paper_weight():
    #raw_value = hx.read()
    #weight = hx.get_weight(raw_value)
    #hx.set_offset(-480)
    weight = hx.get_grams()
    return weight
# 发送line 通知
def send_line_s():
    
    token = "Yix7M9OnmZMAymB6vgoJxJW1NfkmfMaoofsA06rSc7p" #个人
    #token = "nR0xfmsQBZNyFW7sF9Xnk7Z3RDH3dK55T12gW8SULIY" # 群line 通知 
    message = "可以放置卫生纸"
    xtools.line_msg(token, message)
# 发送line 通知
def send_line_notification(x):
    
    token = "Yix7M9OnmZMAymB6vgoJxJW1NfkmfMaoofsA06rSc7p" #个人
    #token = "nR0xfmsQBZNyFW7sF9Xnk7Z3RDH3dK55T12gW8SULIY" # 群line 通知
    if x == 0:
        message = "卫生纸要用完了"
    elif x==1:
         message = "卫生纸10-7成"
    elif x==2:
         message = "卫生纸7-3成"
    elif x==3:
         message = "卫生纸3-1成"
    xtools.line_msg(token, message)
# 发送line 通知
def send_line_notification_auto(x):
    token = "Yix7M9OnmZMAymB6vgoJxJW1NfkmfMaoofsA06rSc7p" #个人
    #token = "nR0xfmsQBZNyFW7sF9Xnk7Z3RDH3dK55T12gW8SULIY" # 群line 通知
    if x == 0:
        message = "卫生纸启动卫生纸要用完了"
    elif x==1:
         message = "卫生纸启动卫生纸10-7成"
    elif x==2:
         message = "卫生纸启动卫生纸7-3成"
    elif x==3:
         message = "卫生纸启动卫生纸3-1成"
    xtools.line_msg(token, message)
# 發送郵件通知
def send_email_notification():
    API_KEY = "HGc0Nm1eyvZ6B7el8zT9V"
    WEBHOOK_URL="https://maker.ifttt.com/trigger/button/with/key/" + API_KEY
    params = { "value1": "卫生纸要用完了"}
    WEBHOOK_URL+="/?" + urlencode(params)
    xtools.webhook_get(WEBHOOK_URL)
    
#装上卫生纸自动启动
def auto():
    global num
    weight_threshold = 0.3  # 設定衛生紙用盡的重量閾值,根據實際情況進行調整
    weight_7 = 2.1
    weight_3 = 0.9
    weight = get_paper_weight()
    #weight= float(weight/100000.00) #变成kg
    weight = float("{:.6f}".format(weight))
    print(weight)
    if weight < weight_threshold and num==4:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight < weight_threshold and num==4:
            print("卫生纸用完了,发送line {}".format(weight))
            #send_email_notification()
            del weight
            gc.collect()
            utime.sleep(2)
            send_line_notification_auto(0)
            gc.collect()
            utime.sleep(2)
            up(device,0)
            num=0;
    elif weight >= weight_threshold and weight < weight_3 and num==4:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight > weight_threshold and weight < weight_3 and num==4:
            print("卫生纸安装上,启动{}".format(weight))
            #send_email_notification()
            del weight
            gc.collect()
            utime.sleep(2)
            send_line_notification_auto(3)
            gc.collect()
            utime.sleep(2)
            up(device,3)
            num=3
    elif weight >= weight_3 and weight < weight_7 and num==4:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight >= weight_3 and weight < weight_7 and num==4:
            print("卫生纸7-3成,发送line {}".format(weight))
            #send_email_notification()
            del weight
            gc.collect()
            utime.sleep(2)
            send_line_notification_auto(2)
            gc.collect()
            utime.sleep(2)
            up(device,2)
            num=2;
    elif weight >= weight_7  and num==4:
        print("检测中...")
        utime.sleep(10)#10
        #utime.sleep(60)#60
        weight = get_paper_weight()
        if weight >= weight_7  and num==4:
            print("卫生纸10-7成,发送line {}".format(weight))
            #send_email_notification()
            del weight
            gc.collect()
            utime.sleep(2)
            send_line_notification_auto(1)
            gc.collect()
            utime.sleep(2)
            up(device,1)
            num=1;
# 选择Excel文件并读取数据
def load_excel_data():
    global data

    url = 'https://script.google.com/macros/s/AKfycbyO9SeDmMcJeTrK97PrQ6Xjg441P79ktDeUOLzdiJsHUjd9ZJONHhNgNB3fFhv2VCwM9Q/exec'
    response = urequests.get(url)
    sheetData = response.json()['content']

    data = parseSheetData(sheetData)
        # 过滤掉全空数据
    displayData = data[:]
    response.close()
    #print(data)
    
    


# 更新Excel数据
def update_excel_data():
    global data
    jsonData = json.dumps(data)  # 将数据转换为JSON字符串
    url = "https://script.google.com/macros/s/AKfycbyO9SeDmMcJeTrK97PrQ6Xjg441P79ktDeUOLzdiJsHUjd9ZJONHhNgNB3fFhv2VCwM9Q/exec"
    #print(jsonData)
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, data=jsonData, headers=headers)
    print('Data uploaded successfully!')
    response.close()

# 解析Sheet数据的函数(只提取一列数据)
def parseSheetData(sheetData):
    # 存储提取的数据=
    data = []
    
    for row in sheetData:
        if len(row) > 1:  # 确保该行至少包含两列
            row_data = [row[0], row[1],row[2] ]
            data.append(row_data)

    return data
#修改上传时间
def uptime(num):
    global data
    rtc = RTC()
    utc = utime.mktime(utime.localtime())
    year,month,day,hour,minute,second,week,days=utime.localtime(utc+28800)
    a="{}/{:02d}/{:02d}".format(year, month, day)
    b="{}:{:02d}:{:02d}".format(hour,minute,second)
    load_excel_data()
    data[num-1][1]=[a]
    data[num-1][2]=[b]
#修改上传数据
def up(num,x):
    global data
    uptime(device)
    data[num-1][0]=[x]
    #print(data[num-1])
    update_excel_data()
                          
def main():
    global settime
    connect_wifi(WIFI_SSID,WIFI_PASSWORD)
    print("connect")
    gc.collect()
    utime.sleep(1)
    load_excel_data()
    print("放卫生纸")
    send_line_s()
    while True:
        if settime==300: #故障检测
            settime=0
            openw()
            uptime(device)
            update_excel_data()
            close()
            utime.sleep(1)
            gc.collect()
            #machine.deepsleep(10 * 1000)  # 休眠10秒（以毫秒為單位）
        #client.check_msg()
        #utime.sleep(1)
        if num <= 3:
            check_paper_status()
            utime.sleep(1)
            gc.collect()
        else:
            auto()
            gc.collect()
        settime+=1
        gc.collect()


def sub_cb(topic, msg):
    global num
    print("收到訊息: ", msg.decode())
    if msg.decode() == "ON":
        print("On")
        num=0;


main()












