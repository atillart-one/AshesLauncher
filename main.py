import traceback
import ctypes
import sys

try:
    import winreg
    import atexit
    import os
    import os.path
    import tkinter
    from tkinter import filedialog, messagebox
    import shutil
    import random
    from pathlib import Path
    from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
    import webbrowser
    import threading
    import requests
    import configparser
    import subprocess

except Exception:
    ctypes.windll.user32.MessageBoxW(0, traceback.format_exc(), "Error", 0)
    sys.exit(0)
try:
    server_version = requests.get("https://raw.githubusercontent.com/Atillart-One/AshesLauncher/main/version.txt",
                                  timeout=3).text

    try:
        client_version = open("version.txt", 'r').read()
    except Exception:
        client_version = '0'

    if client_version != server_version:
        update = requests.get("https://raw.githubusercontent.com/Atillart-One/AshesLauncher"
                              "/main/launcher.py", timeout=3)
        open('launcher.py', 'wb').write(update.content)
        open("version.txt", 'w').write(server_version)

except Exception:
    pass

sys.path.append(os.path.dirname(sys.executable))
import launcher
launcher.set_game_folder()
launcher.main()
