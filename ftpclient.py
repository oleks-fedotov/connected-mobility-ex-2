import sys, socket, os, re, time, math

def log(message, clientAddr = None):
    ''' Write log '''
    if clientAddr == None:
        print('[%s] %s' % (time.strftime(r'%H:%M:%S, %m.%d.%Y'), message))
    else:
        print('[%s] %s:%d %s' % (time.strftime(r'%H:%M:%S, %m.%d.%Y'), clientAddr[0], clientAddr[1], message))

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class FTPClient():
    def __init__(self):
        self.controlSock = None
        self.bufSize = 1024
        self.connected = False
        self.loggedIn = False
        self.dataMode = 'PORT'
        self.dataAddr = None
        self.chunkNumber = 0
        self.isFileReadCompletely = False
        self.fileName = "send.pdf"
    
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

        while True:

            if self.controlSock == None:
                return

            try:
                reply = self.controlSock.recv(self.bufSize).decode('ascii')
                log(reply)

                if reply.upper() == 'READY':
                    self.sendFilename()

                elif reply.startswith('FINISH '):
                    parts = reply.split()
                    if len(parts) < 2 or (not is_number(parts[1])):
                        log('FINISH message format is wrong. Cannot confirm correctness of transfered data.')

                    numberOfChunksToCheck = int(reply.split()[1])

                    file = open(self.fileName, 'rb')
                    data = file.read()
                    if not numberOfChunksToCheck == math.ceil(len(data) / self.bufSize):
                        log('Transfer finished. Data was not delivered correctly. :(')
                    else:
                        log('Transfer finished. Data was delivered correctly. :)')

                elif is_number(reply):

                    if self.isFileReadCompletely:
                        self.sendFinish()
                    else:
                        self.chunkNumber = int(reply)
                        self.sendData(self.chunkNumber)

                else:  # Server disconnected
                    self.connected = False
                    self.loggedIn = False
                    self.controlSock.close()
                    self.controlSock = None

            except (socket.timeout):
                return

    def sendFilename(self):
        self.controlSock.send(b'FILENAME receive.pdf\r\n')

    def sendData(self, chunkNumber):

        file = open(self.fileName, 'rb')
        file.seek(chunkNumber * self.bufSize)
        data = file.read(self.bufSize)

        file.close()

        log('data length - ' + str(len(data)))

        if len(data) < self.bufSize:
            self.isFileReadCompletely = True

        self.controlSock.send(data)

    def sendFinish(self):
        self.controlSock.send(b'FINISH')

hosts = {'10.1.0.3'}
# hosts = {'127.0.0.1'}

ftpclient = FTPClient()

ftpclient.connect(hosts, 80)
print("Connection established. Ready to send data.")
ftpclient.parseReply()
# ftpclient.sendFilename()
ftpclient.quit()

