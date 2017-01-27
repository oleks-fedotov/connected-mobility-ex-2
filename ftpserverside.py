import socket, sys, os, threading, time

listenAddr = '0.0.0.0'
listenPort = 8089


def log(message, clientAddr=None):
    ''' Write log '''
    if clientAddr == None:
        print('[%s] %s' % (time.strftime(r'%H:%M:%S, %m.%d.%Y'), message))
    else:
        print('[%s] %s:%d %s' % (time.strftime(r'%H:%M:%S, %m.%d.%Y'), clientAddr[0], clientAddr[1], message))


class FTPServer(threading.Thread):
    ''' FTP server handler '''

    def __init__(self, controlSock, clientAddr):
        super().__init__()

        self.filename = ''
        self.receivedChunkNumber = 0

        self.bufSize = 1024
        self.controlSock = controlSock
        self.clientAddr = clientAddr

    def run(self):
        self.controlSock.send(b'READY')
        while True:

            cmd = None
            raw_data = self.controlSock.recv(self.bufSize)

            try:
                cmd = raw_data.decode('ascii')
            except UnicodeDecodeError:
                cmd = raw_data
                log('data length - ' + str(cmd))

            if cmd == '':  # Connection closed
                self.controlSock.close()
                log('Client disconnected.', self.clientAddr)
                break



            cmdHead = cmd.split()[0].upper()

            if cmdHead == 'FILENAME':  # FILENAME
                self.filename = cmd.split()[1]

                if os.path.isfile(self.filename):
                    os.remove(self.filename)

                self.receivedChunkNumber = 0
                self.controlSock.send('0'.encode('ascii'))

            elif cmdHead == 'FINISH':  # FINISH FILE TRANSFER
                self.controlSock.send(b'FINISH ' + str(self.receivedChunkNumber).encode('ascii'))
                self.controlSock.close()

            else:
                with open(self.filename, 'ab') as file:
                    file.write(cmd)

                self.receivedChunkNumber += 1
                self.controlSock.send(str(self.receivedChunkNumber).encode('ascii'))


if __name__ == '__main__':
    listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listenSock.bind((listenAddr, listenPort))
    listenSock.listen(5)
    log('Server started.')
    while True:
        (controlSock, clientAddr) = listenSock.accept()
        FTPServer(controlSock, clientAddr).start()
        log("Connection accepted.", clientAddr)
