import requests

try:
    update = requests.get("https://raw.githubusercontent.com/Atillart-One/AshesLauncher"
                 "/main/launcher.py", timeout=3)
    open('launcher.py', 'wb').write(update.content)
except Exception:
    pass

import launcher
launcher.main()