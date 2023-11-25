#!/usr/bin/env python3

import os
import sys
import signal
import json
import psutil
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import random

blocked_sites_file = "/Users/charlieholtz/workspace/dev/block/blocked_sites.json"
blocked_apps_file = "/Users/charlieholtz/workspace/dev/block/blocked_apps.json"

def load_list(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_list(file, list):
    with open(file, 'w') as f:
        json.dump(list, f)

def open_file(file):
    subprocess.call(['open', file])

hosts_path = "/etc/hosts"
redirect = "127.0.0.1"
backup_hosts_path = "/etc/hosts.bak"

def block_sites():
    blocked_sites = load_list(blocked_sites_file)

    with open(hosts_path, 'r+') as file:
        content = file.read()
        for site in blocked_sites:
            if site not in content:
                file.write(redirect + " " + site + "\n")

def unblock_sites():
    blocked_sites = load_list(blocked_sites_file)

    with open(hosts_path, 'r') as file:
        lines = file.readlines()
    with open(hosts_path, 'w') as file:
        for line in lines:
            if not any(site in line for site in blocked_sites):
                file.write(line)

def quit_apps(app_list):
    for app_name in app_list:
        os.system(f"osascript -e 'quit app \"{app_name}\"'")

def signal_handler(sig, frame):
    print("Unblocking sites and exiting...")
    unblock_sites()
    sys.exit(0)

def is_any_app_running(app_list):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in app_list:
            return True
    return False


def stop_blocking(root):
    root.quit()  # close the GUI


def main():
    # Load blocked sites and apps from files
    blocked_sites = load_list(blocked_sites_file)
    blocked_apps = load_list(blocked_apps_file)


    # Backup hosts file
    os.system(f"cp {hosts_path} {backup_hosts_path}")

    # Block sites
    block_sites()

    # Handle SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    # Create a simple GUI
    root = tk.Tk()
    root.title("Charlie Zen Mode")

    label = tk.Label(root, text="Blocking active. Press 'Stop' to unblock.")
    label.pack()

    print("Blocking active. Press Ctrl+C to stop.")

    stop_button = tk.Button(root, text="Stop", command=lambda: stop_blocking(root))
    stop_button.pack()

    # Add Listbox to display blocked sites
    blocked_sites_listbox = tk.Listbox(root)
    blocked_sites_listbox.pack()
    for site in blocked_sites:
        blocked_sites_listbox.insert(tk.END, site)

    # Add Listbox to display blocked apps
    blocked_apps_listbox = tk.Listbox(root)
    blocked_apps_listbox.pack()
    for app in blocked_apps:
        blocked_apps_listbox.insert(tk.END, app)

    # Add button to open blocked_sites.json
    edit_sites_button = tk.Button(root, text="Edit blocked sites", command=lambda: open_file(blocked_sites_file))
    edit_sites_button.pack()

    edit_apps_button = tk.Button(root, text="Edit blocked apps", command=lambda: open_file(blocked_apps_file))
    edit_apps_button.pack()

    # Quit specific apps in a separate thread
    def schedule_quit_apps():
        quit_apps(blocked_apps)
        root.after(1000, schedule_quit_apps)  # schedule again after 1000ms

    root.after(1000, schedule_quit_apps)  # initial scheduling

    # Save blocked sites and apps to files when the GUI is closed
    def on_close():
        save_list(blocked_sites_file, blocked_sites)
        save_list(blocked_apps_file, blocked_apps)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()

if __name__ == "__main__":
    main()
