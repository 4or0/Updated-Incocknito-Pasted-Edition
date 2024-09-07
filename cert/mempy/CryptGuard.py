import psutil
import os, shutil, urllib.request, pyautogui, time, uvicorn, threading, logging, subprocess, ctypes
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from cert.utils.logger import debug, info, error, bridge, send_message, downloadCompiler
from cert.utils.utils import ClearLog
from ctypes import wintypes
from cert.certgg import CertAPI
from cert.utils.logger import printthread, printsinglethread, error

main_dir = os.path.dirname(os.path.abspath(__file__))
autoexec_path = os.path.join(main_dir, "autoexec")

global Cert
Cert = CertAPI()
Cert.SetAutoExecPath(autoexec_path)

def CryptGuard():
    threading.Thread(target=LaunchCertMain, daemon=True).start()

    time.sleep(1)




Cert_ERRORCODES = {
    0x0: "Successfully injected!",
    0x1: "Currently injecting!",
    0x2: "Failed to find Roblox process.",
    0x3: "Failed to fetch DataModel :(",
    0x4: "Failed to fetch certain modules.",
    0x5: "Roblox terminated while injecting!",
    0x6: "Failed to find Bridge!"
}

async def execute(code):
    input_value = code
    try:
        if Cert.GetStatus() == 5:
            Cert.RunScript(input_value)
        else:
            pyautogui.alert("Not Injected")
    except Exception as e:
        error(f"Error executing code: {e}")

app = FastAPI()

logging.getLogger("uvicorn.error").propagate = False
logging.getLogger("uvicorn.access").propagate = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await execute(data)
    except WebSocketDisconnect:
        print("WebSocket connection closed")

def start_websocket_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8050, log_level="info")
    server = uvicorn.Server(config)
    print("WebSocket Server Started")
    server.run()





def LaunchCertMain():
    launchstatus = Cert.Inject()

    if launchstatus == 0:
        send_message("Attached")
        print("")

        print("Starting webserver")
        threading.Thread(target=start_websocket_server, daemon=True).start()
    else:
        error_message = Cert_ERRORCODES.get(launchstatus, "Unknown error")
        send_message(error_message)
