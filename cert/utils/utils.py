import os, re, shutil, psutil, requests
from cert.utils.logger import debug, offset, info, error, bridge, send_message

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            return True
    return False

RBXPath = os.getenv("LOCALAPPDATA") + "\\Roblox\\logs"
RENDER_VIEW_PATTERN = r"\[FLog::SurfaceController\] SurfaceController\[_:\d\]::initialize view\([A-F0-9]{16}\)"

Version = "6.9"
ExecName = "Incocknito skid version"
InternalUI = "false"

class Offsets:
    # thanks to 4or0 for offsets
    DataModel = 0x198

    Name = 0x50
    Children = 0x58
    Parent = 0x68
    ClassDescriptor = 0x18

    ModuleFlags = 0x1a4

    DataModelHolder = 0x118

    BytecodeSize = 0x20
    Bytecode = {
        "LocalScript": 0x1c0,
        "ModuleScript": 0x160
    }

    LocalPlayer = 0x108
    ObjectValue = 0xc8


Capabilities = {
    0x0: "None",
    0x1: "Plugin",
    0x2: "LocalUser",
    0x4: "WritePlayer",
    0x8: "RobloxScriptSecurity",
    0x10: "RobloxEngine",
    0x20: "NotAccessible"
}

def GetLog():
    file_name = ""
    for dir in os.listdir(RBXPath):
        if dir.find("_Player_") > -1:
            file_name = dir

    return open(RBXPath + "\\" + file_name, "r", encoding="utf-8", errors="ignore")

def GetRenderViewFromLog():
    log_file = GetLog()
    if log_file:
        render_views = re.findall(RENDER_VIEW_PATTERN, log_file.read())
        log_file.close()

        if len(render_views) > 0:
            matched_str = render_views[-1]
            render_view_addy = re.search(r"[A-F0-9]{16}", matched_str)
            if not render_view_addy:
                return None

            return int(render_view_addy.group(0), 16)

        return None

def ClearLog():
    if os.path.exists(RBXPath):
        for filename in os.listdir(RBXPath):
            file_path = os.path.join(RBXPath, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except:
                print("")

def getAutoExec():
    try:
        response = requests.get("http://185.219.84.198/storage/autoexec.txt")
        response.raise_for_status()

        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
