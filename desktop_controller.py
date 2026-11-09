import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import socket
import time
import os
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parent
HAND_TRACKING = ROOT / "hand_tracking"
MOUSE_SERVER = ROOT / "mouse_controller.py"

URL = "http://localhost:8000"

http_process = None
mouse_process = None
chrome_process = None


def find_chrome():
    possible_paths = [
        Path(os.environ.get("PROGRAMFILES", "")) /
        "Google/Chrome/Application/chrome.exe",

        Path(os.environ.get("PROGRAMFILES(X86)", "")) /
        "Google/Chrome/Application/chrome.exe",

        Path(os.environ.get("LOCALAPPDATA", "")) /
        "Google/Chrome/Application/chrome.exe"
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return None


def port_is_open(port):
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except OSError:
        return False


def start_controller():
    global http_process, mouse_process, chrome_process

    if http_process or mouse_process:
        messagebox.showinfo("Controller", "Controller is already running.")
        return

    chrome = find_chrome()

    if not chrome:
        messagebox.showerror(
            "Chrome Not Found",
            "Please install Google Chrome first."
        )
        return

    if not MOUSE_SERVER.exists():
        messagebox.showerror(
            "File Missing",
            "mouse_controller.py was not found."
        )
        return

    try:
        status_label.config(text="Starting controller...", fg="orange")
        root.update()

        # Start Python mouse server
        mouse_process = subprocess.Popen(
            [sys.executable, "-u", str(MOUSE_SERVER)],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Start local web server
        http_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "http.server",
                "8000"
            ],
            cwd=str(HAND_TRACKING),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Wait for servers
        for _ in range(20):
            if port_is_open(8765) and port_is_open(8000):
                break
            time.sleep(0.5)

        if not port_is_open(8765) or not port_is_open(8000):
            raise RuntimeError(
                "Could not start the servers. Check whether ports 8000 and 8765 are already in use."
            )

        # Dedicated Chrome profile
        profile = ROOT / "chrome-controller-profile"
        profile.mkdir(exist_ok=True)

        # Open controller as a standalone Chrome app
        chrome_process = subprocess.Popen([
            chrome,
            f"--user-data-dir={profile}",
            f"--app={URL}",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-features=CalculateNativeWinOcclusion"
        ])

        status_label.config(
            text="Controller Running",
            fg="#22c55e"
        )

    except Exception as error:
        stop_controller()
        messagebox.showerror("Startup Error", str(error))


def stop_controller():
    global http_process, mouse_process, chrome_process

    for process in [chrome_process, http_process, mouse_process]:
        if process and process.poll() is None:
            try:
                process.terminate()
            except Exception:
                pass

    chrome_process = None
    http_process = None
    mouse_process = None

    status_label.config(
        text="Controller Stopped",
        fg="#ef4444"
    )


def create_desktop_shortcut():
    pythonw = Path(sys.executable).with_name("pythonw.exe")

    if not pythonw.exists():
        pythonw = Path(sys.executable)

    desktop = Path.home() / "Desktop"
    shortcut = desktop / "AI Virtual Computer Controller.lnk"

    script_path = Path(__file__).resolve()

    command = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{shortcut}')
    $Shortcut.TargetPath = '{pythonw}'
    $Shortcut.Arguments = '"{script_path}"'
    $Shortcut.WorkingDirectory = '{ROOT}'
    $Shortcut.IconLocation = "$env:SystemRoot\\System32\\shell32.dll,220"
    $Shortcut.Save()
    """

    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        messagebox.showinfo(
            "Desktop Shortcut",
            "Desktop shortcut created successfully!"
        )

    except Exception as error:
        messagebox.showerror("Shortcut Error", str(error))


def close_window():
    stop_controller()
    root.destroy()


# GUI
root = tk.Tk()
root.title("AI Virtual Computer Controller")
root.geometry("420x350")
root.resizable(False, False)
root.configure(bg="#101827")

title = tk.Label(
    root,
    text="AI Virtual Computer",
    font=("Arial", 21, "bold"),
    bg="#101827",
    fg="white"
)
title.pack(pady=(30, 5))

subtitle = tk.Label(
    root,
    text="Gesture Control System",
    font=("Arial", 11),
    bg="#101827",
    fg="#94a3b8"
)
subtitle.pack(pady=5)

status_label = tk.Label(
    root,
    text="Controller Stopped",
    font=("Arial", 12, "bold"),
    bg="#101827",
    fg="#ef4444"
)
status_label.pack(pady=20)

start_button = tk.Button(
    root,
    text="START CONTROLLER",
    command=start_controller,
    font=("Arial", 12, "bold"),
    bg="#16a34a",
    fg="white",
    activebackground="#15803d",
    width=25,
    height=2,
    relief="flat",
    cursor="hand2"
)
start_button.pack(pady=8)

stop_button = tk.Button(
    root,
    text="STOP CONTROLLER",
    command=stop_controller,
    font=("Arial", 12, "bold"),
    bg="#dc2626",
    fg="white",
    activebackground="#b91c1c",
    width=25,
    height=2,
    relief="flat",
    cursor="hand2"
)
stop_button.pack(pady=8)

shortcut_button = tk.Button(
    root,
    text="Create Desktop Icon",
    command=create_desktop_shortcut,
    font=("Arial", 10),
    bg="#334155",
    fg="white",
    width=25,
    relief="flat",
    cursor="hand2"
)
shortcut_button.pack(pady=12)

root.protocol("WM_DELETE_WINDOW", close_window)

root.mainloop()