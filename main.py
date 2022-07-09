import configparser
import requests


try:
    settings = requests.get("https://raw.githubusercontent.com/Atillart-One/AshesLauncher/settings.ini", timeout=3).text
    config = configparser.ConfigParser()
    config.read(settings)
    server_version = config['version']['version']

    config = configparser.ConfigParser()
    config.read("settings.ini")
    client_version = config['version']['version']

    if client_version != server_version:
        update = requests.get("https://raw.githubusercontent.com/Atillart-One/AshesLauncher"
                 "/main/launcher.py", timeout=3)
        open('launcher.py', 'wb').write(update.content)
except Exception:
    pass

import launcher
launcher.main()