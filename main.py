import atexit
import sys
import os
import os.path
import tkinter.ttk
from tkinter import filedialog, messagebox
import shutil
from pathlib import Path
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
import glob
import webbrowser
import threading
import git

if getattr(sys, 'frozen', False):
        gpath = os.path.dirname(sys.executable)
elif __file__:
        gpath = os.path.dirname(__file__)
git_path = gpath + r"\data\Git\bin\git.exe"
print(git_path)
git.refresh(path=git_path)

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20

os.system("taskkill /f /im  DarkSoulsIII.exe")


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

"""
Creates (if it doesn't exist) and reads the location of the game folder.
"""
Path("C:/ProgramData/AshesLauncher").mkdir(parents=True, exist_ok=True)
Path("C:/ProgramData/AshesLauncher/settings.txt").touch(exist_ok=True)
settings_file = open(r"C:/ProgramData/AshesLauncher/settings.txt", "r")
dir_path = settings_file.read()
settings_file.close()


def onObjectClick(event):
    os.system("taskkill /f /im git.exe")
    sys.exit(0)


def main():
    root = tkinter.Tk()
    title_icon = tkinter.PhotoImage(file=resource_path('icon.png'))
    root.wm_title("Champion's Ashes")
    root.geometry('1280x720+320+180')
    root.iconphoto(True, title_icon)

    def disabled_folder():
        if os.path.isdir(dir_path + "/disabled") is True:
            files = glob.iglob(os.path.join(dir_path + "/disabled"))
            for file in files:
                if os.path.isfile(file):
                    shutil.copy(file, dir_path)

    def play_vanilla(event):
        if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
            messagebox.showerror("AshesLauncher", "Please select Game folder.")
            browse()
        else:
            vanilla()

    def play_ashes(event):
        if os.path.isfile(dir_path + "/DarkSoulsIII.exe") is False:
            messagebox.showinfo("AshesLauncher", "Please select Game folder.")
            browse()
        else:
            ashes()

    def vanilla():
        delete()
        disabled_folder()
        webbrowser.open('steam://rungameid/374320')

    class CloneProgress(git.RemoteProgress):
        def update(self, op_code, cur_count, max_count=None, message=''):
            canvas.itemconfig('proglines', state='normal')
            x = cur_count * 864 // max_count
            canvas.coords('progress', 150, 605, 150 + x, 620)
            print(self._cur_line)

    def install():
        git.Repo.clone_from("https://github.com/SirHalvard/Champions-Ashes",
                            dir_path + "/AshesLauncher/Ashes", depth=1, progress=CloneProgress())
        webbrowser.open('steam://rungameid/374320')

    def update():
        repo = git.Repo(dir_path + "/AshesLauncher/Ashes")
        repo.remotes.origin.pull(progress=CloneProgress())
        webbrowser.open('steam://rungameid/374320')

    def ashes():
        if os.path.isdir(dir_path + "/AshesLauncher/Ashes/.git") is False:
            Path(dir_path + "/AshesLauncher/Ashes").mkdir(parents=True, exist_ok=True)
            s = threading.Thread(target=install)
            s.setDaemon(True)
            s.start()
        else:
            s = threading.Thread(target=update)
            s.setDaemon(True)
            s.start()

    def delete():
        if os.path.isfile(dir_path + "/dinput8.dll"):
            os.remove(dir_path + "/dinput8.dll")
        if os.path.isfile(dir_path + "/modengine.ini"):
            os.remove(dir_path + "/modengine.ini")

    def browse():
        settings_file = open(r"C:/ProgramData/AshesLauncher/settings.txt", "w")
        global dir_path
        dir_path = filedialog.askdirectory()
        settings_file.write(dir_path)
        settings_file.close()

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

    def mod_enabled(event):
        canvas.itemconfig(mod_button, image=enabled)
        canvas.tag_bind(mod_button, "<ButtonPress-1>", mod_disabled)
        canvas.tag_bind(mod_button, "<Enter>", lambda event: canvas.itemconfig(mod_button, image=enabled_select))
        canvas.tag_bind(mod_button, "<Leave>", lambda event: canvas.itemconfig(mod_button, image=enabled))
        canvas.tag_bind(play_button, "<ButtonPress-1>", play_ashes)

    canvas = tkinter.Canvas(width=1280, height=720, bg='black', highlightthickness=0)
    canvas.pack(expand=tkinter.YES, fill=tkinter.BOTH)

    """IMAGE PATHS"""
    cross_pic = tkinter.PhotoImage(file=resource_path('cross.png'))
    hold_pic = tkinter.PhotoImage(file=resource_path('hold.png'))
    bg = tkinter.PhotoImage(file=resource_path('bg.png'))
    panel = tkinter.PhotoImage(file=resource_path('panel.png'))
    play = tkinter.PhotoImage(file=resource_path('play.png'))
    play_select = tkinter.PhotoImage(file=resource_path('play_select.png'))
    enabled = tkinter.PhotoImage(file=resource_path('enabled.png'))
    enabled_select = tkinter.PhotoImage(file=resource_path('enabled_select.png'))
    disabled = tkinter.PhotoImage(file=resource_path('disabled.png'))
    disabled_select = tkinter.PhotoImage(file=resource_path('disabled_select.png'))
    logo = tkinter.PhotoImage(file=resource_path('logo.png'))

    """IMAGES"""
    canvas.create_image(0, 0, image=bg, anchor=tkinter.NW)
    canvas.create_image(0, 0, image=panel, anchor=tkinter.NW)
    canvas.create_image(0, -50, image=logo, anchor=tkinter.NW)
    hold = canvas.create_image(0, 0, image=hold_pic, anchor=tkinter.NW)
    cross = canvas.create_image(1220, 15, image=cross_pic, anchor=tkinter.NW)
    canvas.create_rectangle(150, 603, 1014, 605, fill='#bc9a4c', width=0, tags='proglines', state='hidden')
    canvas.create_rectangle(150, 620, 1014, 622, fill='#bc9a4c', width=0, tags='proglines', state='hidden')
    canvas.create_rectangle(0, 0, 0, 0, fill='#ebd7aa', width=0, state='hidden', tags=['progress', 'proglines'])
    play_button = canvas.create_image(1280, 570, image=play, anchor=tkinter.NE)
    mod_button = canvas.create_image(1280, 573, image=disabled, anchor=tkinter.SE)
    canvas.create_rectangle(0, 55, 1280, 58, fill='#ddcc9d', width=0)

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

    root.resizable(False, False)
    root.overrideredirect(True)
    root.after(10, lambda: set_appwindow(root))
    root.mainloop()


if __name__ == '__main__':
    main()


def kill():
    os.system("taskkill /f /im  git.exe")


atexit.register(kill)
