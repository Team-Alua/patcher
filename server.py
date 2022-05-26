import asyncio
import websockets
import json
from base64 import b64decode, b64encode

from config import *
from editor import edit

# create handler for each connection

async def handler(websocket, path):
    print("New Request")
    data = await websocket.recv()
    try:
        data = json.loads(data)
        if "savedata" in data and "edits" in data:
            processed_data = edit(b64decode(data["savedata"].encode('ascii')), data["edits"])
            print("Save Edited")
            await websocket.send(json.dumps({"Success": True, "savedata": b64encode(processed_data).decode('ascii')}))
        else:
            raise Exception("Invaild Request")
    except Exception as e:
        print("Exception: " + str(e))
        await websocket.send(json.dumps({"Success": False, "Reason": str(e)}))



start_server = websockets.serve(handler, "localhost", port, max_size = 10485760)

asyncio.get_event_loop().run_until_complete(start_server)

asyncio.get_event_loop().run_forever()