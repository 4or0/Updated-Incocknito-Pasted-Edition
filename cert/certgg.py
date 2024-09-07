from cert.utils.base import fetch_roblox_pid, initialize, initialize_script_hook, random_string
from cert.utils.bytecode import Bytecode as RBXBytecode
from cert.utils.utils import Offsets, getAutoExec
from cert.utils.logger import debug, offset, info, error, bridge, send_message

from cert.utils.instance import Instance, FetchRenderView, Process

from cert.bridge.bridge import Bridge as RBXBridge
from cert.bridge.bridge_callbacks import register_callbacks
import cert.init_script as init_script

import time, os, base64, psutil, threading

DEFAULT_CLIENT_INFO = [-1, None]

init_script_bytecode = None

if init_script.debug_mode:
    init_script_bytecode = RBXBytecode.Compile(init_script.content)
else:
    bytecode = base64.b64decode(init_script.content.encode(encoding="ascii", errors="ignore"))
    init_script_bytecode = [bytecode, len(bytecode)]

class CertAPI:
    __InjectStatus = 0
    __ClientInfo = None

    ClientBridge = None
    __Configuration: dict[str, any] = None

    def __init__(self):
        self.ClientBridge = RBXBridge()
        self.__Configuration = {}   
        
    def Inject(self) -> int:
        if self.__InjectStatus > 2 and (self.__ClientInfo and self.__ClientInfo[0] == fetch_roblox_pid()):
            return 0x1

        success, new_pid = initialize()
        if not success:
            self.__InjectStatus = 0
            return 0x2

        self.__InjectStatus = 2
        info("ProcessId: " + str(new_pid))

        RenderView = FetchRenderView(new_pid)

        DataModelAddyHolder = Process.read_longlong(RenderView + Offsets.DataModelHolder)

        DataModelAddy = Process.read_longlong(DataModelAddyHolder + Offsets.DataModel) if DataModelAddyHolder else None
        if not (DataModelAddy and DataModelAddy > 1000):
            GuiRootAddy = Process.pattern_scan(b"\x47\x75\x69\x52\x6F\x6F\x74\x00\x47\x75\x69\x49\x74\x65\x6D",)

            DataModelAddy = Process.read_longlong(
                Process.read_longlong(GuiRootAddy + 0x38) + 0x198
            )

            if not (DataModelAddy and DataModelAddy > 1000):
                self.__InjectStatus = 1
                return 0x3
            
        DataModel = Instance(DataModelAddy)
        offset("DataModel: " + str(DataModel.Address))

        CoreGui = DataModel.FindFirstChildOfClass("CoreGui")
        ScriptContext = DataModel.FindFirstChildOfClass("ScriptContext")
        RobloxReplicatedStorage = DataModel.FindFirstChildOfClass("RobloxReplicatedStorage")

        RobloxGui = CoreGui.FindFirstChild("RobloxGui")
        Modules = RobloxGui.FindFirstChild("Modules")

        offset(CoreGui, RobloxGui, Modules)
        offset(RobloxReplicatedStorage, ScriptContext)

        if ScriptContext.FindFirstChild("StarterScript").Address > 1000:
            info("Ingame Attaching")
            
            PlayerList = Modules.FindFirstChild("PlayerList")
            PlayerListManager = PlayerList.FindFirstChild("PlayerListManager")

            offset(PlayerList, PlayerListManager)

            if PlayerListManager.Address < 1000:
                self.__InjectStatus = 1
                return 0x4
            
            CorePackages = DataModel.FindFirstChild("CorePackages")
            JestGlobals = CorePackages.FindFirstChild("JestGlobals", True)

            offset(CorePackages, JestGlobals)
            
            JestGlobals.SetModulesBypass()
            PlayerListManager.Spoof(JestGlobals)

            JestGlobals.Bytecode = init_script_bytecode
            initialize_script_hook()

            time.sleep(1)

            PlayerListManager.Spoof(PlayerListManager)
            JestGlobals.ResetModules()

            info("Ingame Attached")
        else:
            info("Homescreen Attaching")
            
            ChatUtil = Modules.FindFirstChild("ChatUtil")

            ChatUtil.Bytecode = init_script_bytecode
        
            info("Homescreen Attached")

            self.__InjectStatus = 4
            RobloxProcess, RobloxTerminated = psutil.Process(new_pid), False

            while (not RobloxTerminated):
                try:
                    if (RobloxProcess.status() == "dead"):
                        RobloxTerminated = True
                        break
                except psutil.NoSuchProcess:
                    RobloxTerminated = True
                    break

                NewDataModelHolderAddy = Process.read_longlong(RenderView + Offsets.DataModelHolder)
                if NewDataModelHolderAddy != DataModelAddyHolder:
                    DataModelAddy = Process.read_longlong(NewDataModelHolderAddy + Offsets.DataModel) if NewDataModelHolderAddy else None

                    if (DataModelAddy and DataModelAddy > 1000):
                        break

                time.sleep(1)

            if RobloxTerminated:
                self.__InjectStatus = 1
                return 0x5

            DataModel = Instance(DataModelAddy)
            RobloxReplicatedStorage = DataModel.FindFirstChildOfClass("RobloxReplicatedStorage")
            
            offset(DataModel, RobloxReplicatedStorage)

        bridge("Preparing Bridge")

        BridgeContainer = RobloxReplicatedStorage.WaitForChild("Bridge", 15)
        offset(BridgeContainer)

        if BridgeContainer.Address < 1000:
            error("Dead Bridge.")
            self.__InjectStatus = 1
            return 0x6
        
        info("Injection Completed!")

        bridge("Starting Bridge")
        self.ClientBridge.Start(new_pid, BridgeContainer)

        self.__InjectStatus = 5
        self.__ClientInfo = [new_pid, "skibidi ohio sigma rizz party"]
        register_callbacks(Bridge=self.ClientBridge)

        bridge("Bridge Started")

        self.SkiddedFileSystem()
        self.RunScript(getAutoExec())

        if ("AutoExecutePath" in self.__Configuration) and os.path.isdir(self.__Configuration["AutoExecutePath"]):
            for file in os.listdir(self.__Configuration["AutoExecutePath"]):
                full_path = self.__Configuration["AutoExecutePath"] + f"\\{file}"

                if os.path.isfile(full_path):
                    with open(full_path, "rb") as file:
                        file_content = file.read().decode(errors="ignore")
                        self.RunScript(file_content)
                        time.sleep(0.05)

        return 0x0

    def GetStatus(self) -> int:
        return self.__InjectStatus

    def GetClientInfo(self):
        if self.__InjectStatus != 5:
            return DEFAULT_CLIENT_INFO

        return self.__ClientInfo

    def SetAutoExecPath(self, autoexec_path: str):
        if os.path.isdir(autoexec_path):
            self.__Configuration["AutoExecutePath"] = autoexec_path
            return

        return Exception("Path of the directory is invalid") 

    def SkiddedFileSystem(self):
        def loop_sync():
            while True:
                self.ClientBridge.Send("synchronize_files")
                time.sleep(3)

        threading.Thread(target=loop_sync, daemon=True).start()

    def RunScript(self, source: str):
        if self.__InjectStatus == 5 and not self.ClientBridge.RobloxTerminated:
            CurrentScript = self.ClientBridge.ModulesHolder.Value

            CurrentScript.SetModulesBypass()
            CurrentScript.Bytecode = RBXBytecode.Compile(
                f"return function(...) {source} \nend",
                f"execute-{random_string()}.btc"
            )

            self.ClientBridge.Send("load_script")
