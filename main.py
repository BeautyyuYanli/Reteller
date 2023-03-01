import websockets
import asyncio
import os
import json
from modules.translator import Translator
from logging import warning


async def generate(text: str, cookies: dict, exclude: list | None):
    if exclude is None:
        exclude = []
    t = Translator(cookies, exclude)
    async for i in t.translate(text):
        try:
            yield json.dumps(i)
        except GeneratorExit:
            warning("GeneratorExit")
            break
    await t.close()


async def serve(websocket, path):
    async for message in websocket:
        j = json.loads(message)
        break

    async for i in generate(j["text"], j["cookies"], j.get("exclude")):
        try:
            await websocket.send(i)
        except websockets.exceptions.ConnectionClosed:
            warning("ConnectionClosed: may be closed by client")
            break
    await websocket.close()


async def main():
    async with websockets.serve(serve, os.getenv("WS_HOST"), os.getenv("WS_PORT")):
        await asyncio.Future()

asyncio.run(main())
