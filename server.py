from VideoCapture import Device
from pygame.locals import *
from PIL import ImageEnhance, Image, ImageDraw, ImageFont
from threading import Thread
from cv2 import VideoCapture
import sys, pygame, time, socket, threading, traceback, cv2, numpy

# 全局变量
is_sending = False
cli_address = ('', 0)

# 主机地址和端口
host = socket.gethostbyname(socket.gethostname())
port = 1234

# 初始化UDP socket
ser_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ser_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ser_socket.bind((host, port))

# 接收线程类，用于接收客户端发送的消息
class UdpReceiver(threading.Thread):
    def __init__(self):
        super(UdpReceiver,self).__init__()
        self.thread_stop = False
                
    def run(self):
        print('run')
        while not self.thread_stop:
            # 声明全局变量，接收消息后更改
            global cli_address   
            global is_sending
            try:
                message, address = ser_socket.recvfrom(2048)
            except:
                #traceback.print_exc()
                continue
            print(message,cli_address)
            cli_address=address
            if str(message,encoding='utf-8') == 'startcam':
                print(message)
                is_sending=True
                ser_socket.sendto('startRcv'.encode('utf-8'),cli_address)

            if str(message,encoding='utf-8') == 'quitcam':
                is_sending=False
                print('Quit Camera')

    def stop(self):
        print('stop')
        self.thread_stop=True

if __name__ =='__main__':
    print('server at {}:{}'.format(host,str(port)))
    res=(640,480)
    cam=Device()
    cam.setResolution(res[0],res[1])

    brightness=1.0
    contrast=1.0
    shots=0

    receiveThread=UdpReceiver()
    receiveThread.setDaemon(True)# 该选项设置后使得主线程退出后子线程同时退出
    receiveThread.start()

    #主循环
    while True:
        if is_sending:
            camshot=ImageEnhance.Brightness(cam.getImage()).enhance(brightness)
            camshot = ImageEnhance.Contrast(camshot).enhance(contrast)
            clock=pygame.time.Clock()

            #获取图像
            img=cam.getImage()#PIL对象
            img=img.resize((160,120))
            '''
            cap=cv2.VideoCapture(0)
            success,img=cap.read()
            img.resize((160,120,3))
            '''
            
            #添加字体
            font = ImageFont.truetype('simsun.ttc',10)
            draw=ImageDraw.Draw(img)
            timestring,localtimelist='',list(time.localtime())
            for i in range(len(localtimelist)):
                if i == len(localtimelist)-1:
                        timestring+=(str(localtimelist[i]))
                else:
                        timestring+=(str(localtimelist[i])+'-')
            draw.text(xy=(0,0),text=timestring,font=font)
            
            data=img.tobytes()
            ser_socket.sendto(data,cli_address)
            time.sleep(0.05)
        else:
            time.sleep(1)

    receiveThread.stop()
    ser_socket.close()
