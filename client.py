import socket
import sys
import os
import signal


def do_child(s,addr,name):
    # 發送請求
    while True:
        text = input('說>>>')
        if text == '88':
            msg = 'Q '+name+'退出'
            s.sendto(msg.encode(),addr)
            os.kill(os.getppid(),signal.SIGKILL)
            sys.exit(0)
        else:
            msg = 'T %s %s'%(name,text)
            s.sendto(msg.encode(),addr)


def do_father(s):
    # 接收消息
    while True:
        msg,addr = s.recvfrom(1024)
        print(msg.decode()+'\n說>>>',end='')


def main():
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)

    # 創建udp套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 防止埠號重用
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while True:
        name = input('輸入姓名:')
        msg = 'S '+name
        s.sendto(msg.encode(),ADDR)
        data, addr = s.recvfrom(1024)
        #判斷姓名是否存在
        if data.decode() == 'OK':
            break
        else:
            print('用戶名已存在')
    
    # 處理殭屍進程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # 創建進程
    pid = os.fork()

    if pid < 0:
        print('創建失敗')
        return
    elif pid == 0:
        '''子進程'''
        do_child(s,addr,name)
    else:
        '''父進程'''
        do_father(s)


if __name__ == '__main__':
    main()
