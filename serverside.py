#!/usr/bin/env python3

import random
import asyncio
import logging
import concurrent.futures
import math
from binascii import hexlify, unhexlify


log = logging.getLogger(__name__)
clients = {}  # task -> (reader, writer)

stored_data = None
random_string = None


def accept_client(client_reader, client_writer):
    task = asyncio.Task(handle_client(client_reader, client_writer))
    clients[task] = (client_reader, client_writer)

    def client_done(task):
        del clients[task]
        client_writer.close()
        log.info("connection closed")

    task.add_done_callback(client_done)

@asyncio.coroutine
def read_line_safe(client_reader):
    try:
        if client_reader.at_eof():
            log.info("client terminated")
            return None
        try:
            data = yield from asyncio.wait_for(client_reader.readline(), timeout=30.0)
        except concurrent.futures.TimeoutError:
            #log.info("timeout")
            return None
        if data is None:
            log.warning("Received no data")
            return None
        if not data.endswith(b"\n"):
            log.warning("read partial data:`%s'" % data)
            return None
        data = data.decode().rstrip()
        if not data:
            log.warning("no data")
            data = ""
        return data
    except Exception as e:
        log.error("EXCEPTION (read_line_safe): %s (%s)" % (e, type(e)))
        return None

@asyncio.coroutine
def handle_client(client_reader, client_writer):
    ip_hash = None
    try:
        remote = client_writer.get_extra_info('peername')
        if remote is None:
            log.error("Could not get ip of client")
            return
        ip_hash= hash(remote[0]) # not cryptographical
        remote = "%s:%s" % (remote[0], remote[1])
        log.info("new connection from: %s" % remote)
    except Exception as e:
        log.error("EXCEPTION (get peername): %s (%s)" % (e, type(e)))
        return

    try:
        client_writer.write(stored_data)

    except Exception as e:
        if hasattr(e.__traceback__, 'tb_lineno'):
            line = "line %s" % e.__traceback__.tb_lineno
            import traceback
            traceback.print_tb(e.__traceback__)
        else:
            line = "no traceback"
        log.error("EXCEPTION (handle connection): %s (%s) %s" % (e, type(e), line))
        try:
            error = "something went wrong with your previous message! "
            error += "Error: " + str(e) + "\n"
            client_writer.write(error.encode())
        except Exception as s:
            log.error("Exception while handling exception: %s" % s)
            return

def main():
    global stored_data
    global random_string

    with open('index.html', 'rb') as d:
        stored_data = d.read()

    stored_data = hexlify(stored_data)

    random_string = str(random.randint(1000,200000))

    #start server
    loop = asyncio.get_event_loop()
    f = asyncio.start_server(accept_client, host=None, port = 80)
    print("Server waiting for connections!")
    log.info("Server waiting for connections")
    loop.run_until_complete(f)
    loop.run_forever()



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='netsec02.log', format="%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s")

    # "INFO:asyncio:poll took 25.960 seconds" is annyoing
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    main()
