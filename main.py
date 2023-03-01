import signal
import websockets
import asyncio
import os
import json
import ssl
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

    async for i in generate(j["text"], j["cookies"], j.get("excludes")):
        try:
            await websocket.send(i)
        except websockets.exceptions.ConnectionClosed:
            warning("ConnectionClosed: may be closed by client")
            break
    await websocket.close()


async def main():

    use_ssl = False
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_cert = os.getenv("SSL_CERT_FILE")
    ssl_key = os.getenv("SSL_KEY_FILE")
    if ssl_cert is not None and ssl_key is not None:
        use_ssl = True
        ssl_context.load_cert_chain(ssl_cert, ssl_key)

    async with websockets.serve(serve, "0.0.0.0", os.getenv("PORT"), ssl=ssl_context if use_ssl else None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
