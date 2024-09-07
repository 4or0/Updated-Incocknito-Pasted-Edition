import ctypes, os, shutil, urllib.request, pyautogui, time, uvicorn, threading, logging, subprocess
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from cert.utils.logger import debug, info, error, bridge, send_message, downloadCompiler
from cert.utils.utils import ClearLog
from cert.mempy.CryptGuard import CryptGuard

downloadCompiler()

from cert.certgg import CertAPI

if __name__ == "__main__":
    CryptGuard()
    while True:
        time.sleep(1)