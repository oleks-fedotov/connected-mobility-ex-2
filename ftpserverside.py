import socket, sys, os, threading, time

listenAddr = '0.0.0.0'
listenPort = 80


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
        self.isSocketClosed = False

    def run(self):

        self.controlSock.send(b'READY')

        while True:

            if self.isSocketClosed:
                log('Client disconnected.', self.clientAddr)
                break

            isComandHandled = False
            commandArgs = None

            raw_data = self.controlSock.recv(self.bufSize)

            try:
                cmd = raw_data.decode('ascii')
                splitedData = cmd.split()

                if len(splitedData) > 0:
                    command = splitedData[0].upper()

                if len(splitedData) > 1:
                    commandArgs = splitedData[1]

                isComandHandled = self.handleCommand(command, commandArgs)

            except UnicodeDecodeError:
                cmd = raw_data[0:len(raw_data)]

            if cmd == '':  # Connection closed
                self.controlSock.close()
                log('Client disconnected.', self.clientAddr)
                break

            if not isComandHandled:
                file = open(self.filename, 'ab')
                try:
                    file.write(cmd)
                except TypeError:
                    file.write(cmd.encode('ascii'))

                file.close()

                self.receivedChunkNumber += 1
                self.controlSock.send(str(self.receivedChunkNumber).encode('ascii'))

    def handleCommand(self, command, args):

        if command == 'FILENAME':  # FILENAME

            if args:
                self.filename = args
            else:
                self.controlSock.send(b'Error - filename not provided')

            if os.path.isfile(self.filename):
                os.remove(self.filename)

            self.receivedChunkNumber = 0
            self.controlSock.send('0'.encode('ascii'))

            return True

        elif command == 'FINISH':  # FINISH FILE TRANSFER
            self.controlSock.send(b'FINISH ' + str(self.receivedChunkNumber).encode('ascii'))
            self.controlSock.close()
            self.isSocketClosed = True

            return True

        return False


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
