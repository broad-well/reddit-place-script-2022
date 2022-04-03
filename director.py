import asyncio
import pathlib
import ssl
import websockets
import threading
from aioconsole import ainput


workers_lock = threading.Lock()
workers = set()

target = '370 281 https://cdn.discordapp.com/attachments/958338474950422558/960228246878822471/botversion.jpg'

async def echo(websocket):
    with workers_lock:
        workers.add(websocket)
    try:
        async for msg in websocket:
            if msg == 'ok':
                print('ack ', end='')
            elif msg == 'pong':
                print(websocket, 'says pong')
            elif msg == 'bye':
                break
            elif msg == 'hello':
                await websocket.send('target ' + target)
            else:
                print('unrecognized msg from worker: ' + msg)
    finally:
        workers.remove(websocket)

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# key = 'server-key.pem'
# ssl_context.load_cert_chain(key)

async def main():
    global target
    async with websockets.serve(echo, '0.0.0.0', 4227): #ssl=ssl_context):
        while True:
            cmd = await ainput('>>')
            if cmd == 'start':
                websockets.broadcast(workers, 'start')
            elif cmd == 'stop':
                websockets.broadcast(workers, 'stop')
            elif cmd.startswith('target'):
                target = ' '.join(cmd.split(' ')[1:])
                websockets.broadcast(workers, 'target ' + target)
            elif cmd == '?numworkers':
                print('we have', len(workers), 'connected')
        # await asyncio.Future()

asyncio.run(main())