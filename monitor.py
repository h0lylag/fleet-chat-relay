import os
import re
import time
from threading import Thread, Event
from tkinter import messagebox, StringVar
from typing import Optional
from config import Config
from helpers import send_to_discord, extract_eve_timestamp, unix_timestamp

monitor_thread: Optional[Thread] = None
stop_event = Event()

def get_latest_log(character_name: str) -> Optional[str]:
    """
    Retrieve the most recent Fleet log file for the specified character.
    Returns the full path to the log file if found, or None otherwise.
    """
    log_dir = os.path.expanduser(r"~\Documents\EVE\logs\Chatlogs")
    print(f"Searching logs in: {log_dir}")
    
    try:
        fleet_logs = [os.path.join(log_dir, file)
                      for file in os.listdir(log_dir) if file.startswith("Fleet_")]
    except FileNotFoundError:
        print(f"Log directory not found: {log_dir}")
        return None
    except Exception as e:
        print(f"Error accessing log directory: {e}")
        return None

    # Sort logs by modification time (most recent first)
    fleet_logs.sort(key=os.path.getmtime, reverse=True)
    
    # Prepare the regex to search for the character in the log
    pattern = re.compile(rf"Listener:\s+{re.escape(character_name.strip())}")
    for log_file in fleet_logs:
        try:
            with open(log_file, 'r', encoding='utf-16', errors='ignore') as f:
                content = f.read()
                if pattern.search(content):
                    print(f"Found log for '{character_name}': {log_file}")
                    return log_file
        except Exception as e:
            print(f"Error reading log file {log_file}: {e}")
    
    print(f"No log found for character: {character_name}")
    return None

def monitor_log_updates(log_file: str, character_name: str) -> None:
    """
    Continuously monitor the given log file for new fleet chat messages.
    For every new line, optionally prepend a relative Discord timestamp (if enabled in the config)
    and relay the message to the Discord webhook.
    """
    print(f"Monitoring log file: {log_file}")
    webhook_url = Config.user_config.get("DISCORD_WEBHOOK_URL", Config.DEFAULT_DISCORD_WEBHOOK_URL)
    try:
        with open(log_file, 'r', encoding='utf-16', errors='ignore') as f:
            # Move to the end of the file so that only new messages are relayed.
            f.seek(0, os.SEEK_END)
            while not stop_event.is_set():
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                line = line.strip()
                current_ts = unix_timestamp()
                if Config.user_config.get("DISCORD_TIMESTAMPS", Config.DEFAULT_DISCORD_TIMESTAMPS):
                    formatted_message = f'<t:{current_ts}:T> {line}'
                else:
                    formatted_message = line
                send_to_discord(formatted_message, webhook_url)
                print(f"Relayed: {formatted_message}")
    except Exception as e:
        print(f"Error monitoring log file: {e}")

def start_monitoring(character_name: str, log_file_var: StringVar) -> None:
    """
    Start (or restart) the log-monitoring thread for the specified character.
    Before tailing new messages, send an initial message indicating that relaying has begun.
    """
    global monitor_thread, stop_event

    if monitor_thread and monitor_thread.is_alive():
        stop_event.set()
        monitor_thread.join()
    
    stop_event.clear()
    log_file = get_latest_log(character_name)
    if not log_file:
        messagebox.showerror("Error", f"No log file found for character: {character_name}")
        return
    log_file_var.set(os.path.basename(log_file))

    webhook_url = Config.user_config.get("DISCORD_WEBHOOK_URL", Config.DEFAULT_DISCORD_WEBHOOK_URL)

    # Read the header of the log file to extract the Listener's name.
    listener: Optional[str] = None
    try:
        with open(log_file, 'r', encoding='utf-16', errors='ignore') as f:
            for line in f:
                if "Listener:" in line:
                    parts = line.split("Listener:")
                    if len(parts) > 1:
                        listener = parts[1].strip()
                        break
    except Exception as e:
        print(f"Error reading log header: {e}")

    if listener:
        send_to_discord(f"Relaying fleet chat for `{listener}`", webhook_url)
    
    monitor_thread = Thread(
        target=monitor_log_updates,
        args=(log_file, character_name)
    )
    monitor_thread.daemon = True
    monitor_thread.start()

def load_character_monitor(character_var: StringVar, log_file_var: StringVar) -> None:
    """
    Initiate monitoring for the selected character.
    If no valid EVE client is selected, do nothing.
    """
    character_name = character_var.get().replace("EVE - ", "").strip()
    if character_name == "No EVE clients found":
        return
    start_monitoring(character_name, log_file_var)
