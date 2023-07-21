import asyncio
import pathlib
import ssl
import threading

import websockets
from aioconsole import ainput

import mappings

workers_lock = threading.Lock()
workers = set()

running = False
# canvas x y
target = '4 137 54 https://media.discordapp.net/attachments/958338474950422558/1131788232196096080/pixil-frame-0.png'
VERSION = 3

async def echo(websocket):
    with workers_lock:
        workers.add(websocket)
    try:
        async for msg in websocket:
            if msg == 'ok':
                pass
            elif msg == 'pong':
                print(websocket.remote_address, 'says pong')
            elif msg == 'bye':
                break
            elif msg.startswith('hello'):
                print(f'new client {websocket.remote_address}')
                bot_version = msg.split(' ')[1]
                await websocket.send('target ' + target)
                if int(bot_version) < VERSION:
                    await websocket.send('out-of-date')
                if running:
                    await websocket.send('start')
                else:
                    await websocket.send('stop')
            elif msg.startswith('placed'):
                (xs, ys, cs) = msg.split(' ')[1:]
                print(f'worker {websocket.remote_address} has placed {mappings.name_map[int(cs)]} at ({xs}, {ys})')
            elif msg.startswith('failed-to-place'):
                (xs, ys, cs) = msg.split(' ')[1:]
                print(f'worker {websocket.remote_address} failed to place {mappings.name_map[int(cs)]} at ({xs}, {ys})')
            else:
                print('unrecognized msg from worker: ' + msg)
    except Exception as e:
        print('error in worker communication:', e)
    finally:
        workers.remove(websocket)

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# key = 'server-key.pem'
# ssl_context.load_cert_chain(key)

async def main():
    global target, running
    async with websockets.serve(echo, '0.0.0.0', 4523): #ssl=ssl_context):
        while True:
            cmd = await ainput('>>')
            if cmd == 'start':
                running = True
                websockets.broadcast(workers, 'start')
            elif cmd == 'stop':
                running = False
                websockets.broadcast(workers, 'stop')
            elif cmd.startswith('target'):
                target = ' '.join(cmd.split(' ')[1:])
                websockets.broadcast(workers, 'target ' + target)
            elif cmd == '#?':
                print('we have', len(workers), 'connected')
        # await asyncio.Future()

asyncio.run(main())