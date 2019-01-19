import socket
import sys
import os
import signal


def do_login(s,user,name,addr):
	for i in user:
		if i == name or name == '板手':
			s.sendto('失敗'.encode(),addr)
			return
	#先告知其他用戶有人登入
	s.sendto('OK'.encode(),addr)
	msg = '\n%s登入'%name
	for i in user:
		s.sendto(msg.encode(),user[i])
	user[name] = addr
	return

def do_say(s,user,tmp):
	msg = '\n%s >>> %s'%(tmp[1],' '.join(tmp[2:]))
	#給所有人發消息除了自己
	for i in user:
		if i != tmp[1]:
			s.sendto(msg.encode(),user[i])
	return

def do_quit(s,user,name):
	del user[name]
	msg = '\n'+name+'退出'
	for i in user:
		s.sendto(msg.encode(),user[i])
	return

def do_child(s):
	#發送請求
	user = {}
	while True:
		msg, addr = s.recvfrom(1024)
		msg = msg.decode()
		tmp = msg.split(' ')
		if tmp[0] == 'S':
			do_login(s,user,tmp[1],addr)
		elif tmp[0] == 'T':
			do_say(s,user,tmp)
		elif tmp[0] == 'Q':
			do_quit(s,user,tmp[1])


def do_father(s,addr):
	#發送系統消息
	name = 'T 板手 '
	while True:
		msg = input('板手發布消息：')
		msg = name + msg
		s.sendto(msg.encode(),addr)
	s.close()
	sys.exit(0)

def main():
	#從終端輸入
	HOST = sys.argv[1] 
	PORT = int(sys.argv[2])
	ADDR = (HOST,PORT)

	#創建udp套接字
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	#防止埠號重用
	s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
	s.bind(ADDR)

	#處理殭屍進程
	signal.signal(signal.SIGCHLD,signal.SIG_IGN)

	#創建進程
	pid = os.fork()

	if pid < 0:
		print('創建失敗')
		return
	elif pid == 0:
		'''子進程'''
		do_child(s)
	else:
		'''父進程'''
		do_father(s,ADDR)


if __name__ == '__main__':
	main()