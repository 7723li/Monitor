import socket,time,pygame
from pygame.locals import *
from sys import exit

# 服务器地址，初始化socket
host=str(input('connect to:'))
if not host or not isinstance(host,str):
    host=socket.gethostbyname(socket.gethostname())
ser_address=(host,1234)
cli_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 设置超时
cli_socket.settimeout(5)

while True:
    cli_socket.sendto('startcam'.encode('utf-8'),ser_address)
    try:
        message,address=cli_socket.recvfrom(65536)
        if str(message,encoding='utf-8') == 'startRcv':
            print(message)
            break
    except socket.timeout:
        pass
    except ConnectionResetError:
        break
try:
    cli_socket.recvfrom(65536)
    # 初始化视频窗口
    pygame.init()
    screen=pygame.display.set_mode((640,480))
    pygame.display.set_caption('实时监控中...')
    pygame.display.flip()

    # 设置时间，可以用来控制帧率
    clock=pygame.time.Clock()
except socket.timeout:
        pass

#主循环
while True:
    try:
        data,address=cli_socket.recvfrom(65536)
    except socket.timeout:
        break
    except ConnectionResetError:
        break
    camshot=pygame.image.frombuffer(data,(160,120),'RGB')
    camshot=pygame.transform.scale(camshot,(640,480))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cli_socket.sendto('quitcam'.encode('utf-8'),ser_address)
            cli_socket.close()
            pygame.quit()
            exit()

    #print(type(camshot),dir(camshot))
    screen.blit(camshot,(0,0))
    pygame.display.update()
    clock.tick(20)
