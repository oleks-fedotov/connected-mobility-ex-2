import sys, socket, os, re, time

def log(message, clientAddr = None):
    ''' Write log '''
    if clientAddr == None:
        print('[%s] %s' % (time.strftime(r'%H:%M:%S, %m.%d.%Y'), message))
    else:
        print('[%s] %s:%d %s' % (time.strftime(r'%H:%M:%S, %m.%d.%Y'), clientAddr[0], clientAddr[1], message))

class FTPClient():
    def __init__(self):
        self.controlSock = None
        self.bufSize = 1024
        self.connected = False
        self.loggedIn = False
        self.dataMode = 'PORT'
        self.dataAddr = None
    
    def connect(self, hosts, port):
        if self.controlSock != None: # Close existing socket first
            self.connected = False
            self.loggedIn = False
            self.controlSock.close()
        self.controlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.controlSock.settimeout(None) # Timeout forever

        while True:
            for host in hosts:
                try:
                    print("attempt connection on host - " + host)
                    self.controlSock.connect((host, port))
                    #if self.parseReply()[0] <= 3:
                    self.connected = True
                    break
                except socket.error as msg:
                    print("connection attempt failed, host - " + host)
                    print(msg)
            if self.connected:
                break
            else:
                time.sleep(2)
                
    def quit(self):
        if not self.connected:
            return
        self.controlSock.send(b'FINISH')
        self.connected = False
        self.loggedIn = False
        self.controlSock.close()
        self.controlSock = None
    def parseReply(self):
        if self.controlSock == None:
            return
        try:
            reply = self.controlSock.recv(self.bufSize).decode('ascii')
            log(reply)
            chunkNumber = int(reply[0])
            self.sendData(chunkNumber)
        except (socket.timeout):
            return
        else:
            if 0 < len(reply):
                print('<< ' + reply.strip().replace('\n', '\n<< '))
                return (int(reply[0]), reply)
            else: # Server disconnected
                self.connected = False
                self.loggedIn = False
                self.controlSock.close()
                self.controlSock = None
                
    def sendFilename(self):
        self.controlSock.send(b'FILENAME receive.txt\r\n')
        self.parseReply()
    def sendData(self, chunkNumber):
        file = open('send.txt', 'rb')
        file.seek(chunkNumber * 1024)
        data = file.read(1024)
        self.controlSock.send(data)
        length = len(data)
        if (length == 1024):
            self.parseReply()

hosts = {'127.0.0.1'}

ftpclient = FTPClient()

ftpclient.connect(hosts, 8089)
time.sleep(1)
print("continue moving")
ftpclient.sendFilename()
ftpclient.quit()

