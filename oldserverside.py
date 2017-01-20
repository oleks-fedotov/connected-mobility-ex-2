#import stuff

#read port

#create server socket

#send files

#send file metadata

#setup heartbeat
def main():
    loop = asyncio.get_event_loop()
    f = asyncio.start_server(accept_client, host=None, port = serverPort)
    log.info("Server waiting for connections")
    loop.run_until_complete(f)
    loop.run_forever()

#footer overhead
main()
