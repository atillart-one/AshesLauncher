import requests

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

import launcher
launcher.set_game_folder()
launcher.main()
