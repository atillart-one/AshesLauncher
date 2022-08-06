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
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
process_array = (ctypes.c_uint8 * 1)()
num_processes = kernel32.GetConsoleProcessList(process_array, 1)
if num_processes < 3: ctypes.WinDLL('user32').ShowWindow(kernel32.GetConsoleWindow(), 0)

os.system("taskkill /f /im DarkSoulsIII.exe")
print('Ignore ERROR: The process "DarkSoulsIII.exe" not found if it pops up.')
try:
    if os.path.isfile(os.path.abspath('.') + "/files/Git/cmd/git.exe") is True:
        os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = os.path.abspath('.') + "/files/Git/cmd/git.exe"
        import git

        git_enabled = 1
    else:
        git_enabled = 0
    FR_PRIVATE = 0x10
    FR_NOT_ENUM = 0x20

    """
    Path to resources used.
    """


    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path + "/data/" + relative_path)


    def loadfont(fontpath, private=True, enumerable=False):
        """
        Makes fonts located in file `fontpath` available to the font system.

        `private`     if True, other processes cannot see this font, and this
                      font will be unloaded when the process dies
        `enumerable`  if True, this font will appear when enumerating fonts

        See https://msdn.microsoft.com/en-us/library/dd183327(VS.85).aspx

        """
        # This function was taken from
        # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
        # This function is written for Python 2.x. For 3.x, you
        # have to convert the isinstance checks to bytes and str
        if isinstance(fontpath, bytes):
            pathbuf = create_string_buffer(fontpath)
            AddFontResourceEx = windll.gdi32.AddFontResourceExA

        elif isinstance(fontpath, str):
            pathbuf = create_unicode_buffer(fontpath)
            AddFontResourceEx = windll.gdi32.AddFontResourceExW
        else:
            raise TypeError('fontpath must be of type str or unicode')

        flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
        numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
        return bool(numFontsAdded)


    loadfont(resource_path("friz.otf"))
    loadfont(resource_path("Pro B.otf"))
    loadfont(resource_path("Pro M.otf"))

    """ 
    Removes title bar.
    """
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080


    def set_appwindow(root):
        hwnd = windll.user32.GetParent(root.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        root.wm_withdraw()
        root.after(10, lambda: root.wm_deiconify())


    """
    Creates (if file doesn't exist) and reads the needed variables.
    """
    Path("C:/ProgramData/AshesLauncher").mkdir(exist_ok=True)
    if os.path.isfile("settings.ini"):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        dir_path = config['settings']['Directory']
        lastmod = config['settings']['LastMod']
    else:
        dir_path = os.path.abspath('.')
        lastmod = ''

    def onObjectClick(event):
        os.system("taskkill /f /im git.exe")
        sys.exit(0)


    installing = 0
    private_servers = False
    gameRunner = ctypes.cdll.LoadLibrary('files/ChampionsAshesServerJoiner.dll')

    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror("Error", message=str(val))


    tkinter.Tk.report_callback_exception = report_callback_exception


    def set_game_folder():
        root = tkinter.Tk()
        title_icon = tkinter.PhotoImage(file=resource_path('icon.png'))
        root.wm_title("AshesLauncher")
        root.geometry('0x0')
        root.iconphoto(True, title_icon)
        root.resizable(False, False)
        root.overrideredirect(True)
        root.after(10, lambda: set_appwindow(root))

        def check():
            global dir_path
            if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
                if messagebox.askyesno("AshesLauncher", "Please select Game folder.") is True:
                    config = configparser.ConfigParser()
                    config.read('settings.ini')
                    dir_path = filedialog.askdirectory()
                    if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
                        check()
                    else:
                        config.set('settings', 'Directory', dir_path)
                        with open('settings.ini', 'w+') as file:
                            config.write(file)
                else:
                    sys.exit(0)

        check()
        global moddir
        global dir_path
        config = configparser.ConfigParser()
        config.read('settings.ini')
        moddir = config['settings']['Mods']
        if os.path.isdir(moddir) is False:
            moddir = dir_path + '/AshesLauncher'
        if moddir == '':
            moddir = dir_path + '/AshesLauncher'
        if moddir == '/':
            moddir = dir_path + '/AshesLauncher'
        if os.path.isfile(moddir + '/DarkSoulsIII.exe') is True:
            moddir = dir_path + '/AshesLauncher'
        Path(moddir + "/Ashes").mkdir(parents=True, exist_ok=True)
        root.destroy()


    mod_list = []
    user_list = []


    def main():
        root = tkinter.Tk()
        title_icon = tkinter.PhotoImage(file=resource_path('icon.png'))
        root.iconphoto(True, title_icon)
        root.wm_title("AshesLauncher")
        root.geometry(f'1280x720+{int(root.winfo_screenwidth() / 2 - 540)}+{int(root.winfo_screenheight() / 2 - 360)}')

        def play_vanilla(event):
            if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
                messagebox.showinfo("AshesLauncher", "Please select Game folder.")
                browse()
            else:
                vanilla()

        def play_mod(event):
            if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
                messagebox.showinfo("AshesLauncher", "Please select Game folder.")
                browse()
            elif mod_name.get() == "Ashes":
                ashes()
            elif mod_name.get() == "Champions-Ashes-Dev":
                ashes_dev()
            else:
                launch()

        def vanilla():
            delete()
            webbrowser.open('steam://rungameid/374320')

        def launch():
            delete()
            if Path(dir_path) in Path(moddir).parents:
                if os.path.islink(dir_path + '/mods') is True:
                    os.unlink(dir_path + '/mods')

                for modfiles in os.listdir(moddir + '/' + mod_name.get()):
                    if modfiles.endswith('.txt') is True:
                        shutil.copy(f'{moddir}/{mod_name.get()}/{modfiles}', dir_path + '/' + modfiles)
                    if modfiles.endswith('.ini') is True:
                        shutil.copy(f'{moddir}/{mod_name.get()}/{modfiles}', dir_path + '/' + modfiles)
                if os.path.isfile(moddir + '/' + mod_name.get() + '/modengine.ini ') is True:
                    config = configparser.ConfigParser()
                    config.read(os.path.abspath(f'{moddir}/{mod_name.get()}/modengine.ini'))
                    default_dir = config['files']['modOverrideDirectory'].replace('"',
                                                                                  '').replace(r"\AshesLauncher\Ashes",
                                                                                              "").replace(
                        r"\Champions-Ashes-Dev", "")
                    config.set('files', 'modOverrideDirectory',
                               fr'"\{moddir}\{mod_name.get()}{default_dir}"'.replace(f'{dir_path}/', ''))
                    with open(dir_path + '/modengine.ini', 'w+') as file:
                        config.write(file)

                shutil.copy("files/lazyLoad/lazyLoad.ini", dir_path + "/lazyLoad.ini")
                config = configparser.ConfigParser()
                config.read(os.path.abspath(f'{dir_path}/lazyLoad.ini'))
                config.set('LAZYLOAD', 'dllModFolderName',
                           f'{moddir}/{mod_name.get()}'.replace(f'{dir_path}/', ''))
                with open(dir_path + '/lazyLoad.ini', 'w+') as file:
                    config.write(file)
            else:
                if os.path.islink(dir_path + '/mods') is True:
                    os.unlink(dir_path + '/mods')
                elif os.path.isdir(dir_path + '/mods') is True:
                    os.rmdir(dir_path + '/mods')
                os.symlink(os.path.abspath(moddir + "/" + mod_name.get()), dir_path + r'/mods',
                           target_is_directory=True)

                for modfiles in os.listdir(moddir + '/' + mod_name.get()):
                    if modfiles.endswith('.txt') is True:
                        shutil.copy(dir_path + '/mods/' + modfiles, dir_path + '/' + modfiles)
                    if modfiles.endswith('.ini') is True:
                        shutil.copy(dir_path + '/mods/' + modfiles, dir_path + '/' + modfiles)
                if os.path.isfile(moddir + '/' + mod_name.get() + '/modengine.ini ') is True:
                    config = configparser.ConfigParser()
                    config.read(os.path.abspath(f'{moddir}/{mod_name.get()}/modengine.ini'))
                    default_dir = config['files']['modOverrideDirectory'].replace('"',
                                                                                  '').replace(r"\AshesLauncher\Ashes",
                                                                                              "")
                    config.set('files', 'modOverrideDirectory',
                               f'"/mods/{default_dir}"'.replace(f'{dir_path}/', ''))
                    with open(dir_path + '/modengine.ini', 'w+') as file:
                        config.write(file)

                shutil.copy("files/lazyLoad/lazyLoad.ini", dir_path + "/lazyLoad.ini")
            shutil.copy("files/lazyLoad/dinput8.dll", dir_path + "/dinput8.dll")
            global private_servers
            if private_servers is False:
                webbrowser.open('steam://rungameid/374320')
            else:
                gameRunner.join(bytes(dir_path + "/DarkSoulsIII.exe", 'utf-8'))

        if git_enabled == 1:
            class CloneProgress(git.RemoteProgress):
                def __init__(self):
                    super().__init__()
                    canvas.itemconfig('proglines', state='normal')
                    canvas.itemconfig(progress, state='normal')
                    global installing
                    installing = 1

                def update(self, op_code, cur_count, max_count=None, message=''):
                    x = cur_count * 964 // max_count
                    canvas.coords('progress', canvas.coords('progress')[0], canvas.coords('progress')[1],
                                  canvas.coords('progress')[0] + x,
                                  canvas.coords('progress')[3])
                    canvas.itemconfig(progress, text=self._cur_line)
                    if canvas.coords('progress')[2] == canvas.coords('progress')[0] + 964:
                        canvas.itemconfig(progress, text="Unpacking...")

            def install():
                try:
                    canvas.itemconfig(play_button, state='disabled')
                    ashes_panel_button1.config(state='disabled')
                    ashes_panel_button2.config(state='disabled')
                    ashes_panel_button3.config(state='disabled')
                    b1.config(state='disabled')
                    b2.config(state='disabled')

                    global installing
                    git.Repo.clone_from("https://github.com/SirHalvard/Champions-Ashes",
                                        moddir + "/Ashes", progress=CloneProgress(), depth=1)
                    canvas.itemconfig(progress, text="")
                    canvas.itemconfig('progress', state='hidden')
                    canvas.itemconfig('proglines', state='hidden')
                    launch()
                    installing = 0
                    canvas.itemconfig(play_button, state='normal')
                    ashes_panel_button1.config(state='normal')
                    ashes_panel_button2.config(state='normal')
                    ashes_panel_button3.config(state='normal')
                    b1.config(state='normal')
                    b2.config(state='normal')

                except Exception:
                    state = messagebox.askretrycancel('AshesLauncher',
                                                      "There was an error installing. Retry?")
                    if state is True:
                        install()
                    else:
                        switch = messagebox.askyesno('AshesLauncher', "Launch Game anyways?")
                        if switch is True:
                            launch()
                            installing = 0
                            canvas.itemconfig(play_button, state='normal')
                            ashes_panel_button1.config(state='normal')
                            ashes_panel_button2.config(state='normal')
                            ashes_panel_button3.config(state='normal')
                            b1.config(state='normal')
                            b2.config(state='normal')

                        else:
                            messagebox.showerror('AshesLauncher',
                                                 "Error for troubleshooting:\n" + traceback.format_exc())
                            installing = 0
                            canvas.itemconfig(play_button, state='normal')
                            ashes_panel_button1.config(state='normal')
                            ashes_panel_button2.config(state='normal')
                            ashes_panel_button3.config(state='normal')
                            b1.config(state='normal')
                            b2.config(state='normal')


            def update():
                try:
                    canvas.itemconfig(play_button, state='disabled')
                    ashes_panel_button1.config(state='disabled')
                    ashes_panel_button2.config(state='disabled')
                    ashes_panel_button3.config(state='disabled')
                    b1.config(state='disabled')
                    b2.config(state='disabled')

                    global installing
                    repo = git.Repo(moddir + "/Ashes")
                    repo.git.config('--global --add safe.directory ' + moddir + '/Ashes')
                    repo.git.fetch('--depth=1')
                    try:
                        repo.git.merge('--ff-only', '--allow-unrelated-histories', 'origin/master')
                    except Exception:
                        repo.git.merge('--autostash', '--ff-only', '--allow-unrelated-histories', 'origin/master')
                        repo.git.stash('drop')
                    canvas.itemconfig(progress, text="")
                    canvas.itemconfig('progress', state='hidden')
                    canvas.itemconfig('proglines', state='hidden')
                    launch()
                    installing = 0
                    canvas.itemconfig(play_button, state='normal')
                    ashes_panel_button1.config(state='normal')
                    ashes_panel_button2.config(state='normal')
                    ashes_panel_button3.config(state='normal')
                    b1.config(state='normal')
                    b2.config(state='normal')

                except Exception:
                    state = messagebox.askretrycancel('AshesLauncher',
                                                      "There was an error updating. Retry? "
                                                      "(Reset All Files in MOD tab may help if issue persists.)")
                    if state is True:
                        update()
                    else:
                        switch = messagebox.askyesno('AshesLauncher', "Launch Game anyways?")
                        if switch is True:
                            launch()
                            installing = 0
                            canvas.itemconfig(play_button, state='normal')
                            ashes_panel_button1.config(state='normal')
                            ashes_panel_button2.config(state='normal')
                            ashes_panel_button3.config(state='normal')
                            b1.config(state='normal')
                            b2.config(state='normal')

                        else:
                            messagebox.showerror('AshesLauncher',
                                                 "Error for troubleshooting:\n" + traceback.format_exc())
                            installing = 0
                            canvas.itemconfig(play_button, state='normal')
                            ashes_panel_button1.config(state='normal')
                            ashes_panel_button2.config(state='normal')
                            ashes_panel_button3.config(state='normal')
                            b1.config(state='normal')
                            b2.config(state='normal')


            def update_dev():
                try:
                    canvas.itemconfig(play_button, state='disabled')
                    ashes_panel_button1.config(state='disabled')
                    ashes_panel_button2.config(state='disabled')
                    ashes_panel_button3.config(state='disabled')
                    b1.config(state='disabled')
                    b2.config(state='disabled')

                    global installing
                    repo = git.Repo(moddir + "/Champions-Ashes-Dev")
                    repo.git.pull
                    canvas.itemconfig('progress', state='hidden')
                    canvas.itemconfig('proglines', state='hidden')
                    launch()
                    installing = 0
                    canvas.itemconfig(play_button, state='normal')
                    ashes_panel_button1.config(state='normal')
                    ashes_panel_button2.config(state='normal')
                    ashes_panel_button3.config(state='normal')
                    b1.config(state='normal')
                    b2.config(state='normal')

                except Exception:
                    state = messagebox.askretrycancel('AshesLauncher',
                                                      "There was an error updating. Retry? "
                                                      "(Reset All Files in MOD tab may help if issue persists.)")
                    if state is True:
                        update_dev()
                    else:
                        switch = messagebox.askyesno('AshesLauncher', "Launch Game anyways?")
                        if switch is True:
                            launch()
                            installing = 0
                            canvas.itemconfig(play_button, state='normal')
                            ashes_panel_button1.config(state='normal')
                            ashes_panel_button2.config(state='normal')
                            ashes_panel_button3.config(state='normal')
                            b1.config(state='normal')
                            b2.config(state='normal')

                        else:
                            messagebox.showerror('AshesLauncher',
                                                 "Error for troubleshooting:\n" + traceback.format_exc())
                            installing = 0
                            canvas.itemconfig(play_button, state='normal')
                            ashes_panel_button1.config(state='normal')
                            ashes_panel_button2.config(state='normal')
                            ashes_panel_button3.config(state='normal')
                            b1.config(state='normal')
                            b2.config(state='normal')

            def reset():
                for files in os.listdir(moddir + "/Ashes/.git"):
                    if files.endswith('.lock'):
                        os.remove(moddir + "/Ashes/.git/" + files)
                repo = git.Repo(moddir + "/Ashes")
                repo.git.reset('--hard', 'origin/master')

            def clean():
                for files in os.listdir(moddir + "/Ashes/.git"):
                    if files.endswith('.lock'):
                        os.remove(moddir + "/Ashes/.git/" + files)
                repo = git.Repo(moddir + "/Ashes")
                repo.git.clean('-xdf')
        else:
            def reset():
                messagebox.showinfo("AshesLauncher", "Git is disabled.")

            def clean():
                messagebox.showinfo("AshesLauncher", "Git is disabled.")

        def migrate():
            if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
                messagebox.showinfo("AshesLauncher", "Please select Game folder.")
                browse()
            else:
                config = configparser.ConfigParser()
                config.read('settings.ini')
                global moddir
                moddir = dir_path + "/AshesLauncher"
                config.set('settings', 'Mods', moddir)
                with open('settings.ini', 'w+') as file:
                    config.write(file)
                if len(moddir) >= 83:
                    mod_path.set("..." + moddir[-80:])
                else:
                    mod_path.set(moddir)
                global mod_list
                for radio in mod_list:
                    radio.destroy()
                mod_list = []
                mod_creation()
                count = 0
                for radio in mod_list:
                    radio.place(x=50, y=150 + count * 45)
                    count += 1

        def ashes():
            if git_enabled == 1:
                if os.path.isdir(moddir + "/Ashes/.git") is False:
                    Path(moddir + "/Ashes").mkdir(parents=True, exist_ok=True)
                    s = threading.Thread(target=install, daemon=True)
                    s.start()
                else:
                    for files in os.listdir(moddir + "/Ashes/.git"):
                        if files.endswith('.lock'):
                            os.remove(moddir + "/Ashes/.git/" + files)
                    s = threading.Thread(target=update, daemon=True)
                    s.start()
            else:
                launch()

        def ashes_dev():
            if git_enabled == 1:
                for files in os.listdir(moddir + "/Champions-Ashes-Dev/.git"):
                    if files.endswith('.lock'):
                        os.remove(moddir + "/Champions-Ashes-Dev/.git/" + files)
                s = threading.Thread(target=update_dev, daemon=True)
                s.start()
            else:
                launch()

        def delete():
            if os.path.isfile(dir_path + "/dinput8.dll"):
                try:
                    os.remove(dir_path + "/dinput8.dll")
                except PermissionError:
                    import stat
                    os.chmod(dir_path + "/dinput8.dll", stat.S_IWRITE)
                    os.remove(dir_path + "/dinput8.dll")
            if os.path.isfile(dir_path + "/modengine.ini"):
                os.remove(dir_path + "/modengine.ini")
            if os.path.isfile(dir_path + "/lazyLoad.ini"):
                os.remove(dir_path + "/lazyLoad.ini")

        def browse():
            global dir_path
            dir_path = filedialog.askdirectory()

            def check():
                global dir_path
                config = configparser.ConfigParser()
                config.read('settings.ini')

                if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
                    if messagebox.askyesno("AshesLauncher", "Please select Game folder.") is True:
                        dir_path = filedialog.askdirectory()
                        if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
                            check()
                        else:
                            config.set('settings', 'Directory', dir_path)
                            with open('settings.ini', 'w+') as file:
                                config.write(file)
                else:
                    config.set('settings', 'Directory', dir_path)
                    with open('settings.ini', 'w+') as file:
                        config.write(file)

            check()
            if len(dir_path) >= 83:
                game_path.set("..." + dir_path[-80:])
            else:
                game_path.set(dir_path)

        def browse_mod():
            global moddir
            moddir = filedialog.askdirectory()
            if os.path.isdir(moddir) is False:
                moddir = dir_path + '/AshesLauncher'
            if moddir == '/':
                moddir = dir_path + '/AshesLauncher'
            if os.path.isfile(moddir + '/DarkSoulsIII.exe') is True:
                moddir = dir_path + '/AshesLauncher'
            config = configparser.ConfigParser()
            config.read('settings.ini')
            config.set('settings', 'Mods', moddir)
            with open('settings.ini', 'w+') as file:
                config.write(file)
            if len(moddir) >= 83:
                mod_path.set("..." + moddir[-80:])
            else:
                mod_path.set(moddir)
            global mod_list
            for radio in mod_list:
                radio.destroy()
            mod_list = []
            mod_creation()
            count = 0
            for radio in mod_list:
                radio.place(x=50, y=150 + count * 45)
                count += 1

        """Lets user drag the window to reposition."""

        def start_move(event):
            root.x = event.x
            root.y = event.y

        def stop_move(event):
            root.x = None
            root.y = None

        def do_move(event):
            deltax = event.x - root.x
            deltay = event.y - root.y
            x = root.winfo_x() + deltax
            y = root.winfo_y() + deltay
            root.geometry(f"+{x}+{y}")

        """Other functions"""

        def mod_disabled(event):
            canvas.itemconfig(mod_button, image=disabled)
            canvas.tag_bind(mod_button, "<ButtonPress-1>", mod_enabled)
            canvas.tag_bind(mod_button, "<Enter>", lambda event: canvas.itemconfig(mod_button, image=disabled_select))
            canvas.tag_bind(mod_button, "<Leave>", lambda event: canvas.itemconfig(mod_button, image=disabled))
            canvas.tag_bind(play_button, "<ButtonPress-1>", play_vanilla)
            if(mod_name.get() == "Ashes"):
                canvas.itemconfig(checkbox, image=box)
                global private_servers
                private_servers = False

        def mod_enabled(event):
            canvas.itemconfig(mod_button, image=enabled)
            canvas.tag_bind(mod_button, "<ButtonPress-1>", mod_disabled)
            canvas.tag_bind(mod_button, "<Enter>", lambda event: canvas.itemconfig(mod_button, image=enabled_select))
            canvas.tag_bind(mod_button, "<Leave>", lambda event: canvas.itemconfig(mod_button, image=enabled))
            canvas.tag_bind(play_button, "<ButtonPress-1>", play_mod)
            if(mod_name.get() == "Ashes"):
                canvas.itemconfig(checkbox, image=tick)
                global private_servers
                private_servers = True


        def preset_vanilla(event):
            if os.path.isfile(moddir + "/Ashes/GraphicPresets/Enable_VANILLA.cmd") is True:
                cmd = subprocess.Popen(os.path.abspath(moddir + "/Ashes/GraphicPresets/Enable_VANILLA.cmd"),
                                       cwd=os.path.abspath(moddir + "/Ashes/GraphicPresets"), stdout=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
                while cmd.poll() is None:
                    if b'READY, Enjoy Ashes!\r\n' in cmd.stdout:
                        cmd.communicate(b'\r\n')
                messagebox.showinfo("Vanilla Preset", "Unchanged visuals.\nReady, Enjoy!")
            else:
                messagebox.showerror("AshesLauncher", "Please install the mod first.")

        def preset_default(event):
            if os.path.isfile(moddir + "/Ashes/GraphicPresets/Enable_PERFORMANCE.cmd") is True:
                cmd = subprocess.Popen(os.path.abspath(moddir + "/Ashes/GraphicPresets/Enable_PERFORMANCE.cmd"),
                                       cwd=os.path.abspath(moddir + "/Ashes/GraphicPresets"), stdout=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
                while cmd.poll() is None:
                    if b'READY, Enjoy Ashes!\r\n' in cmd.stdout:
                        cmd.communicate(b'\r\n')
                messagebox.showinfo("Default Preset", "Improved visuals with minimal performance loss.\nReady, Enjoy!")
            else:
                messagebox.showerror("AshesLauncher", "Please install the mod first.")

        def server_toggle(event):
            global private_servers
            if private_servers is False:
                canvas.itemconfig(checkbox, image=tick)
                private_servers = True

            else:
                canvas.itemconfig(checkbox, image=box)
                private_servers = False

        """ Swap Tabs"""

        def tab_select(i, event):
            if i == 'home':
                canvas.itemconfig('home', state='normal')
                canvas.itemconfig('graphics', state='hidden')
                canvas.itemconfig('mods', state='hidden')
                canvas_patch.place(x=50, y=250)
                if installing == 1:
                    canvas.itemconfig('proglines', state='normal')
                    canvas.itemconfig('progress', state='normal')
                    canvas.itemconfig(progress, state='normal')
                else:
                    canvas.itemconfig('proglines', state='hidden')
                    canvas.itemconfig('progress', state='hidden')
                    canvas.itemconfig(progress, state='hidden')
                for radio in mod_list:
                    radio.place_forget()
                for radio in user_list:
                    radio.place_forget()
                path_panel1.place_forget()
                path_panel2.place_forget()
                ashes_panel_button1.place_forget()
                ashes_panel_button2.place_forget()
                ashes_panel_button3.place_forget()
            if i == 'graphics':
                canvas.itemconfig('home', state='hidden')
                canvas.itemconfig('graphics', state='normal')
                canvas.itemconfig('mods', state='hidden')
                canvas_patch.place_forget()
                for radio in mod_list:
                    radio.place_forget()
                for radio in user_list:
                    radio.place_forget()
                path_panel1.place_forget()
                path_panel2.place_forget()
                ashes_panel_button1.place_forget()
                ashes_panel_button2.place_forget()
                ashes_panel_button3.place_forget()
            if i == 'mods':
                canvas.itemconfig('home', state='hidden')
                canvas.itemconfig('graphics', state='hidden')
                canvas.itemconfig('mods', state='normal')
                canvas_patch.place_forget()
                count = 0
                for radio in mod_list:
                    radio.place(x=50, y=150 + count * 45)
                    count += 1
                count = 0
                for radio in user_list:
                    radio.place(x=680, y=370 + count * 45)
                    count += 1
                path_panel1.place(x=50, y=605)
                path_panel2.place(x=50, y=660)
                ashes_panel_button1.place(x=680, y=150)
                ashes_panel_button2.place(x=680, y=195)
                ashes_panel_button3.place(x=680, y=240)

        canvas = tkinter.Canvas(width=1280, height=720, bg='black', highlightthickness=0)
        canvas.pack(expand=tkinter.YES, fill=tkinter.BOTH)

        """IMAGE PATHS"""
        cross_pic = tkinter.PhotoImage(file=resource_path('cross.png'))
        hold_pic = tkinter.PhotoImage(file=resource_path('hold.png'))
        panel = tkinter.PhotoImage(file=resource_path('panel.png'))
        play = tkinter.PhotoImage(file=resource_path('play.png'))
        play_select = tkinter.PhotoImage(file=resource_path('play_select.png'))
        enabled = tkinter.PhotoImage(file=resource_path('enabled.png'))
        enabled_select = tkinter.PhotoImage(file=resource_path('enabled_select.png'))
        disabled = tkinter.PhotoImage(file=resource_path('disabled.png'))
        disabled_select = tkinter.PhotoImage(file=resource_path('disabled_select.png'))
        patch = tkinter.PhotoImage(file=resource_path('patch.png'))
        up = tkinter.PhotoImage(file=resource_path('up.png'))
        down = tkinter.PhotoImage(file=resource_path('down.png'))
        graph = tkinter.PhotoImage(file=resource_path('graphics_panel.png'))
        vanilla_text = tkinter.PhotoImage(file=resource_path('vanilla.png'))
        default_text = tkinter.PhotoImage(file=resource_path('default.png'))
        graph_select = tkinter.PhotoImage(file=resource_path('graphics_panel_select.png'))
        discord = tkinter.PhotoImage(file=resource_path('discord.png'))
        changelog = tkinter.PhotoImage(file=resource_path('changelog.png'))
        wiki = tkinter.PhotoImage(file=resource_path('wiki.png'))
        home = tkinter.PhotoImage(file=resource_path('home.png'))
        home_select = tkinter.PhotoImage(file=resource_path('home_select.png'))
        mods_img = tkinter.PhotoImage(file=resource_path('mods.png'))
        paths_img = tkinter.PhotoImage(file=resource_path('paths.png'))
        ashes_img = tkinter.PhotoImage(file=resource_path('ashes.png'))
        accs_img = tkinter.PhotoImage(file=resource_path('accounts.png'))
        logo = tkinter.PhotoImage(file=resource_path('logo.png'))
        box = tkinter.PhotoImage(file=resource_path('box.png'))
        tick = tkinter.PhotoImage(file=resource_path('tick.png'))

        """BACKGROUND"""
        bg = tkinter.PhotoImage(file=resource_path('bg.png'))

        def get_bg():
            try:
                count = requests.get("https://raw.githubusercontent.com/Atillart-One/AshesLauncher"
                                     "/main/images/image_count.txt", timeout=3).text

                weight = []
                for i in range(1, int(count) + 1):
                    if i == 1:
                        weight.append(1)
                    elif i == 2:
                        weight.append(1)
                    elif i == 18:
                        weight.append(1)
                    elif i == 19:
                        weight.append(1)
                    else:
                        weight.append(round(46 / ((int(count) - 4))))
                num_img = random.choices(range(1, int(count) + 1), weights=weight)
                response = requests.get(
                    "https://raw.githubusercontent.com/Atillart-One/AshesLauncher/main/images/"
                    + str(num_img).replace('[', '').replace(']', '') + ".png", timeout=3)
                file = open("bg.png", "wb")
                file.write(response.content)
                file.close()
                canvas.newbg = tkinter.PhotoImage(file="bg.png")
                canvas.itemconfig('background', image=canvas.newbg)
                canvas_patch.itemconfig('background', image=canvas.newbg)
                os.remove("bg.png")

            except Exception:
                return

        s = threading.Thread(target=get_bg,daemon=True)
        s.start()
        """Main Canvas"""
        canvas.create_image(0, 0, image=bg, anchor=tkinter.NW, tags='background')
        canvas.create_image(0, 0, image=panel, anchor=tkinter.NW)
        hold = canvas.create_image(0, 0, image=hold_pic, anchor=tkinter.NW)
        home_button = canvas.create_text(60, 18, text='HOME', font=("Friz Quadrata Std", 16), fill='#ecd9ad',
                                         activefill="#e4dfd4", anchor=tkinter.NW)
        graphics_button = canvas.create_text(210, 18, text='GRAPHICS', font=("Friz Quadrata Std", 16), fill='#ecd9ad',
                                             activefill="#e4dfd4", anchor=tkinter.NW)
        mods_button = canvas.create_text(390, 18, text='MODS', font=("Friz Quadrata Std", 16), fill='#ecd9ad',
                                         activefill="#e4dfd4", anchor=tkinter.NW, state='normal')
        cross = canvas.create_image(1220, 18, image=cross_pic, anchor=tkinter.NW)

        """HOME"""
        progline1 = canvas.create_rectangle(80, 630, 1045, 632, fill='#bc9a4c', width=0, tags=['proglines', 'home'],
                                            state='hidden')
        progline2 = canvas.create_rectangle(80, 648, 1045, 650, fill='#bc9a4c', width=0, tags=['proglines', 'home'],
                                            state='hidden')
        canvas.create_rectangle(80, 634, 80, 646, fill='#ebd7aa', width=0, state='hidden',
                                tags=['progress', 'proglines', 'home'])
        progress = canvas.create_text(612, 614, text='', fill='#e4dfd4', font=('Friz Quadrata Std', 16), tags='home')
        play_button = canvas.create_image(1282, 600, image=play, anchor=tkinter.NE, tags='home')
        mod_button = canvas.create_image(1282, 600, image=disabled, anchor=tkinter.SE, tags='home')
        canvas.create_rectangle(0, 56, 1280, 58, fill='#ba9749', width=0)

        global moddir
        if os.path.isfile(moddir + "/Ashes/_version.txt"):
            version = open(moddir + "/Ashes/_version.txt", 'r').read()
            canvas.create_text(216, 672, text=f"| Champion's Ashes Version {version}",
                               font=("Friz Quadrata Std", 14), justify=tkinter.CENTER,
                               fill='#e4dfd4', anchor=tkinter.NW, tags='home')

        canvas.create_image(730, 355, image=discord, tags=('discord', 'home'), anchor=tkinter.NW)
        canvas.create_image(880, 355, image=wiki, tags=('wiki', 'home'), anchor=tkinter.NW)
        canvas.create_image(1030, 355, image=changelog, tags=('changelog', 'home'), anchor=tkinter.NW)

        discord_panel = canvas.create_image(730, 355, image=discord, tags='home', anchor=tkinter.NW)
        wiki_panel = canvas.create_image(880, 355, image=wiki, tags='home', anchor=tkinter.NW)
        changelog_panel = canvas.create_image(1030, 355, image=changelog, tags='home', anchor=tkinter.NW)

        canvas.create_image(650, 220, image=logo, tags='home', anchor=tkinter.NW)

        global private_servers
        if private_servers is True:
            checkbox = canvas.create_image(20, 670, image=tick, anchor=tkinter.NW, tags='home')

        else:
            checkbox = canvas.create_image(20, 670, image=box, anchor=tkinter.NW, tags='home')

        canvas.create_text(55, 672,
                           text='Use Private Servers',
                           fill='#e4dfd4', justify=tkinter.CENTER,
                           font=("Friz Quadrata Std", 14), tags='home', anchor=tkinter.NW)

        """Display Patch Notes"""
        canvas.create_image(-3, 135, image=patch, anchor=tkinter.NW, tags='home')
        canvas_patch = tkinter.Canvas(width=580, height=270, highlightthickness=0)
        canvas_patch.place(x=50, y=250)
        canvas_patch.create_image(-50, -250, image=bg, anchor=tkinter.NW, tags='background')
        canvas_patch.create_image(-50, -250, image=hold_pic, anchor=tkinter.NW)
        canvas_patch.create_image(-53, -115, image=patch, anchor=tkinter.NW)

        try:
            patchnotes = requests.get(
                "https://raw.githubusercontent.com/Atillart-One/AshesLauncher/main/patchnotes.txt", timeout=3).text
            patchnotes_text = canvas_patch.create_text(0, 10, text=patchnotes.replace('\r', ''), fill='#e4dfd4',
                                                       width=525,
                                                       font=("Friz Quadrata Std", 12), anchor=tkinter.NW)
        except Exception:
            patchnotes_text = canvas_patch.create_text(0, 10, text='Failed to get patch notes.'
                                                                   ' You may be disconnected from the internet.',
                                                       fill='#e4dfd4', width=525, font=("Friz Quadrata Std", 12),
                                                       anchor=tkinter.NW)

        canvas_patch.create_image(573, 265, image=down, anchor=tkinter.SE, tags='down')
        canvas_patch.create_image(573, 228, image=up, anchor=tkinter.SE, tags='up')

        def patch_up(event):
            if canvas_patch.coords(patchnotes_text)[1] + 50 < 10:
                canvas_patch.move(patchnotes_text, 0, 50)
            else:
                canvas_patch.move(patchnotes_text, 0, 10 - canvas_patch.bbox(patchnotes_text)[1])

        def patch_down(event):
            if canvas_patch.bbox(patchnotes_text)[3] - 50 > 280:
                canvas_patch.move(patchnotes_text, 0, -50)
            else:
                canvas_patch.move(patchnotes_text, 0, 280 - canvas_patch.bbox(patchnotes_text)[3])

        canvas_patch.tag_bind('up', "<ButtonPress-1>", patch_up)
        canvas_patch.tag_bind('down', "<ButtonPress-1>", patch_down)

        """GRAPHICS"""

        canvas.create_image(470, 365, image=graph, tags=('graphics', 'vanilla'), state='hidden')
        canvas.create_image(810, 365, image=graph, tags=('graphics', 'default'), state='hidden')

        canvas.create_image(470, 175, image=vanilla_text, tags='graphics', state='hidden')
        canvas.create_image(810, 175, image=default_text, tags='graphics',
                            state='hidden')

        canvas.create_text(350, 280,
                           text='The preset closest to the vanilla game. Easier to run than the default preset.\n\n'
                                'For those who prefer lighting closer to vanilla or have issues with '
                                'the default preset.',
                           fill='#e4dfd4', width=250, justify=tkinter.CENTER,
                           font=("Friz Quadrata Std", 14), tags='graphics', state='hidden', anchor=tkinter.NW)
        canvas.create_text(690, 280,
                           text="The default preset for Champion's Ashes. Features new and improved lighting.\n\n"
                                "For those who wish to experience the new graphical changes.",
                           fill='#e4dfd4', width=250, justify=tkinter.CENTER,
                           font=("Friz Quadrata Std", 14), tags='graphics', state='hidden', anchor=tkinter.NW)

        vanilla_panel = canvas.create_rectangle(315, 115, 625, 615, fill='', width=0, state='hidden', tags='graphics')
        default_panel = canvas.create_rectangle(685, 115, 965, 615, fill='', width=0, state='hidden', tags='graphics')

        '''MODS'''
        if lastmod == '':
            mod_name = tkinter.StringVar(root, value="Ashes")
        else:
            mod_name = tkinter.StringVar(root, value=lastmod)

        canvas.create_image(50, 100, image=mods_img, anchor=tkinter.NW, state='hidden', tags='mods')

        def modchosen():
            config = configparser.ConfigParser()
            config.read('settings.ini')
            config.set('settings', 'LastMod', mod_name.get())
            with open('settings.ini', 'w+') as file:
                config.write(file)

        def mod_creation():
            for mod in os.listdir(moddir):
                if os.path.isdir(moddir + "/" + mod):
                    if mod == "Ashes":
                        radio = tkinter.Radiobutton(root, indicatoron=0, text="Champion's Ashes",
                                                    variable=mod_name, value=mod,
                                                    width=45, bg='#141414', fg='#e4dfd4', selectcolor='#273355',
                                                    bd=1, activeforeground='#0f0f0f',
                                                    activebackground='#e4dfd4',
                                                    command=modchosen, font=("FOT-Matisse Pro M", 14),
                                                    relief=tkinter.GROOVE, offrelief=tkinter.GROOVE,
                                                    overrelief=tkinter.RIDGE)

                        mod_list.append(radio)
                    elif mod == "Champions-Ashes-Dev":
                        radio = tkinter.Radiobutton(root, indicatoron=0, text="Champion's Ashes Dev",
                                                    variable=mod_name, value=mod,
                                                    width=45, bg='#141414', fg='#e4dfd4', selectcolor='#273355',
                                                    bd=1, activeforeground='#0f0f0f',
                                                    activebackground='#e4dfd4',
                                                    command=modchosen, font=("FOT-Matisse Pro M", 14),
                                                    relief=tkinter.GROOVE, offrelief=tkinter.GROOVE,
                                                    overrelief=tkinter.RIDGE)

                        mod_list.append(radio)

                    else:
                        radio = tkinter.Radiobutton(root, indicatoron=0, text=mod, variable=mod_name, value=mod,
                                                    width=45, bg='#141414', fg='#e4dfd4', selectcolor='#273355',
                                                    bd=1, activeforeground='#0f0f0f',
                                                    activebackground='#e4dfd4',
                                                    command=modchosen, font=("FOT-Matisse Pro M", 14),
                                                    relief=tkinter.GROOVE, offrelief=tkinter.GROOVE,
                                                    overrelief=tkinter.RIDGE)

                        mod_list.append(radio)

        mod_creation()
        game_path = tkinter.StringVar(root)
        mod_path = tkinter.StringVar(root)
        if len(dir_path) >= 83:
            game_path.set("..." + dir_path[-80:])
        else:
            game_path.set(dir_path)
        if len(moddir) >= 83:
            mod_path.set("..." + moddir[-80:])
        else:
            mod_path.set(moddir)

        canvas.create_image(50, 555, image=paths_img, anchor=tkinter.NW, state='hidden', tags='mods')
        path_panel1 = tkinter.LabelFrame(root, bg='#141414', fg='#f0deb4', relief=tkinter.GROOVE, bd=1,
                                         font=('Friz Quadrata Std', 24))
        path_panel2 = tkinter.LabelFrame(root, bg='#141414', fg='#f0deb4', relief=tkinter.GROOVE, bd=1,
                                         font=('Friz Quadrata Std', 24))
        tkinter.Label(path_panel1, text='Game Path: ', font=("FOT-Matisse Pro B", 14), bg='#141414',
                      fg='#f0deb4').grid(column=0, row=0, padx=10)
        tkinter.Label(path_panel1, width=78, textvariable=game_path, font=("FOT-Matisse Pro M", 14), bg='#141414',
                      fg='#e4dfd4').grid(column=1, row=0, padx=0, pady=5)
        b1 = tkinter.Button(path_panel1, text='Browse', bd=0, font=('Friz Quadrata Std', 12), bg='#141414',
                            fg='#f0deb4', command=browse, relief=tkinter.FLAT, activeforeground='#0f0f0f',
                            activebackground='#e4dfd4')
        b1.grid(column=2, row=0, padx=10)
        tkinter.Label(path_panel2, text='Mods Path: ', font=("FOT-Matisse Pro B", 14), bg='#141414',
                      fg='#f0deb4').grid(column=0, row=0, padx=10)
        tkinter.Label(path_panel2, width=78, textvariable=mod_path, font=("FOT-Matisse Pro M", 14), bg='#141414',
                      fg='#e4dfd4').grid(column=1, row=0, pady=5, padx=2)
        b2 = tkinter.Button(path_panel2, text='Browse', bd=0, font=('Friz Quadrata Std', 12), bg='#141414',
                            fg='#f0deb4', command=browse_mod, relief=tkinter.FLAT,
                            activeforeground='#0f0f0f',
                            activebackground='#e4dfd4')
        b2.grid(column=2, row=0, padx=10)
        canvas.create_image(680, 100, image=ashes_img, state='hidden', anchor=tkinter.NW, tags='mods')

        ashes_panel_button1 = tkinter.Button(root, text='Reset All Files', bd=1, font=("FOT-Matisse Pro M", 14),
                                             bg='#141414', fg='#e4dfd4', command=reset, relief=tkinter.GROOVE,
                                             activeforeground='#0f0f0f', overrelief=tkinter.RIDGE,
                                             activebackground='#e4dfd4', width=45, pady=0)
        ashes_panel_button2 = tkinter.Button(root, text='Remove Extra Files', bd=1, font=("FOT-Matisse Pro M", 14),
                                             bg='#141414', overrelief=tkinter.RIDGE,
                                             fg='#e4dfd4', command=clean, relief=tkinter.GROOVE, pady=0,
                                             activeforeground='#0f0f0f', activebackground='#e4dfd4', width=45)
        ashes_panel_button3 = tkinter.Button(root, text='Use Default Mod Location', bd=1,
                                             font=("FOT-Matisse Pro M", 14),
                                             bg='#141414', overrelief=tkinter.RIDGE,
                                             fg='#e4dfd4', command=migrate, relief=tkinter.GROOVE,
                                             activeforeground='#0f0f0f', pady=0,
                                             activebackground='#e4dfd4', width=45)

        def switch_account():
            os.system("taskkill /f /im steam.exe")
            registry_steam = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            winreg.SetValueEx(registry_steam, 'AutoLoginUser', 0, winreg.REG_SZ, current_username.get())
            winreg.SetValueEx(registry_steam, 'RememberPassword', 0, winreg.REG_DWORD, 1)
            os.system("start steam:")
            winreg.CloseKey(registry_steam)

        if os.path.isfile('settings.ini'):
            config = configparser.ConfigParser()
            config.read('settings.ini')
            if config['enable']['enable'] == 'True':
                canvas.create_image(680, 330, image=accs_img, state='hidden', anchor=tkinter.NW, tags='mods')
                registry_steam = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
                current_username = tkinter.StringVar(root, winreg.QueryValueEx(registry_steam, 'AutoLoginUser')[0])
                winreg.CloseKey(registry_steam)
                config = configparser.ConfigParser()
                config.read('settings.ini')
                for username in config['usernames']:
                    radio = tkinter.Radiobutton(root, indicatoron=0, text=config['usernames'][username],
                                                variable=current_username, value=username,
                                                width=45, bg='#141414', fg='#e4dfd4', selectcolor='#273355',
                                                bd=1, activeforeground='#0f0f0f',
                                                activebackground='#e4dfd4',
                                                command=switch_account, font=("FOT-Matisse Pro M", 14),
                                                relief=tkinter.GROOVE, offrelief=tkinter.GROOVE,
                                                overrelief=tkinter.RIDGE)

                    user_list.append(radio)

        """BINDS"""
        canvas.tag_bind(cross, '<ButtonPress-1>', onObjectClick)
        canvas.tag_bind(hold, "<ButtonPress-1>", start_move)
        canvas.tag_bind(hold, "<ButtonRelease-1>", stop_move)
        canvas.tag_bind(hold, "<B1-Motion>", do_move)
        canvas.tag_bind(play_button, "<ButtonPress-1>", play_vanilla)
        canvas.tag_bind(play_button, "<Enter>", lambda event: canvas.itemconfig(play_button, image=play_select))
        canvas.tag_bind(play_button, "<Leave>", lambda event: canvas.itemconfig(play_button, image=play))
        canvas.tag_bind(mod_button, "<ButtonPress-1>", mod_enabled)
        canvas.tag_bind(mod_button, "<Enter>", lambda event: canvas.itemconfig(mod_button, image=disabled_select))
        canvas.tag_bind(mod_button, "<Leave>", lambda event: canvas.itemconfig(mod_button, image=disabled))
        canvas.tag_bind(checkbox, '<ButtonPress-1>', server_toggle)
        canvas.tag_bind(home_button, '<ButtonPress-1>', lambda event: tab_select('home', event))
        canvas.tag_bind(graphics_button, '<ButtonPress-1>', lambda event: tab_select('graphics', event))
        canvas.tag_bind(mods_button, '<ButtonPress-1>', lambda event: tab_select('mods', event))
        canvas.tag_bind(vanilla_panel, "<Enter>", lambda event: canvas.itemconfig('vanilla', image=graph_select))
        canvas.tag_bind(vanilla_panel, "<Leave>", lambda event: canvas.itemconfig('vanilla', image=graph))
        canvas.tag_bind(default_panel, "<Enter>", lambda event: canvas.itemconfig('default', image=graph_select))
        canvas.tag_bind(default_panel, "<Leave>", lambda event: canvas.itemconfig('default', image=graph))
        canvas.tag_bind(vanilla_panel, "<ButtonPress-1>", preset_vanilla)
        canvas.tag_bind(default_panel, "<ButtonPress-1>", preset_default)
        canvas.tag_bind(discord_panel, "<Enter>", lambda event: canvas.itemconfig(discord_panel, image=home_select))
        canvas.tag_bind(discord_panel, "<Leave>", lambda event: canvas.itemconfig(discord_panel, image=home))
        canvas.tag_bind(changelog_panel, "<Enter>", lambda event: canvas.itemconfig(changelog_panel, image=home_select))
        canvas.tag_bind(changelog_panel, "<Leave>", lambda event: canvas.itemconfig(changelog_panel, image=home))
        canvas.tag_bind(wiki_panel, "<Enter>", lambda event: canvas.itemconfig(wiki_panel, image=home_select))
        canvas.tag_bind(wiki_panel, "<Leave>", lambda event: canvas.itemconfig(wiki_panel, image=home))
        canvas.tag_bind(discord_panel, "<ButtonPress-1>",
                        lambda event: webbrowser.open('https://discord.com/invite/Kqtwa5w'))
        canvas.tag_bind(changelog_panel, "<ButtonPress-1>", lambda event: webbrowser.open(
            'https://docs.google.com/document/d/1j4UVY_1E6jqCX-sthQ467BGq67YmGrjx1I5huEmtciA/edit?usp=sharing'))
        canvas.tag_bind(wiki_panel, "<ButtonPress-1>", lambda event: webbrowser.open('http://championsashes.wikidot'
                                                                                     '.com/'))

        root.resizable(False, False)
        root.overrideredirect(True)
        root.after(10, lambda: set_appwindow(root))
        root.mainloop()


    if __name__ == '__main__':
        set_game_folder()
        main()
except Exception:
    ctypes.windll.user32.MessageBoxW(0, traceback.format_exc(), "Error", 0)
    sys.exit(0)


def kill():
    os.system("taskkill /f /im git.exe")


atexit.register(kill)
