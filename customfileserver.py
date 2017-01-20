import socket

c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
c.bind(('', 1234))
c.listen(1)
s,a = c.accept()

while True:
    data = s.recv(1024)
    cmd = data[:data.find('\n')]

    if cmd == 'get':
        x, file_name, x = data.split('\n', 2)
        s.sendall('ok')
        with open(file_name, 'rb') as f:
            data = f.read()
        s.sendall('%16d' % len(data))
        s.sendall(data)
        s.recv(2)

    if cmd == 'end':
        s.close()
        c.close()
        break






