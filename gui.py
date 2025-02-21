import tkinter as tk
from tkinter import ttk, messagebox
from monitor import load_character_monitor, stop_event, monitor_thread
from eve import get_eve_windows, refresh_eve_clients
from config import Config

def toggle_always_on_top(root, top_var):
    root.attributes('-topmost', top_var.get())

def show_about():
    messagebox.showinfo(f"About {Config.APP_TITLE}", Config.ABOUT_TEXT)

def build_gui():
    root = tk.Tk()
    root.title(f"{Config.APP_TITLE} - {Config.VERSION}")
    root.geometry("300x180")
    root.resizable(False, False)

    # Load configuration using Config methods.
    config_data = Config.load_config()
    webhook_default = config_data.get("DISCORD_WEBHOOK_URL", Config.DEFAULT_DISCORD_WEBHOOK_URL)
    discord_ts_default = config_data.get("DISCORD_TIMESTAMPS", Config.DEFAULT_DISCORD_TIMESTAMPS)

    always_on_top = tk.BooleanVar(value=False)
    
    # Build the menu.
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    settings_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_checkbutton(
        label="Always on Top",
        variable=always_on_top,
        command=lambda: toggle_always_on_top(root, always_on_top)
    )
    menu_bar.add_command(label="About", command=lambda: show_about())
    
    # Get initial EVE client list.
    clients = get_eve_windows()
    if clients:
        initial_client = clients[0]
        combobox_state = "readonly"
    else:
        initial_client = "No EVE clients found"
        clients = [initial_client]
        combobox_state = "disabled"
    
    character_var = tk.StringVar(value=initial_client)
    log_file_var = tk.StringVar(value="None")
    
    # Frame for client selection.
    client_frame = ttk.Frame(root)
    client_frame.pack(pady=5)
    
    combobox = ttk.Combobox(
        client_frame,
        textvariable=character_var,
        values=clients,
        state=combobox_state
    )
    combobox.pack(side=tk.LEFT, padx=5)
    combobox.after(5000, refresh_eve_clients, character_var, combobox)
    
    ttk.Button(
        client_frame, 
        text="Load Character",
        command=lambda: load_character_monitor(character_var, log_file_var)
    ).pack(side=tk.LEFT, padx=5)
    
    # Log file display.
    log_frame = ttk.Frame(root)
    log_frame.pack(pady=5)
    ttk.Label(log_frame, text="Log:").grid(row=0, column=0)
    ttk.Label(log_frame, textvariable=log_file_var).grid(row=0, column=1)
    
    # Webhook row (same row, no extra space or padding).
    webhook_frame = ttk.Frame(root)
    webhook_frame.pack(anchor="w", padx=10, pady=5)
    ttk.Label(webhook_frame, text="Webhook: ").grid(row=0, column=0, padx=0, pady=0)
    webhook_var = tk.StringVar(value=webhook_default)
    ttk.Entry(webhook_frame, textvariable=webhook_var, width=30).grid(row=0, column=1, padx=0, pady=0)
    
    # Option checkboxes.
    discord_ts_var = tk.BooleanVar(value=discord_ts_default)

    ttk.Checkbutton(root, text="Discord Timestamps", variable=discord_ts_var).pack(anchor="w", padx=10, pady=2)

    def save_config():
        Config.user_config["DISCORD_WEBHOOK_URL"] = webhook_var.get()
        Config.user_config["DISCORD_TIMESTAMPS"] = discord_ts_var.get()
        Config.save_config()
    
    ttk.Button(root, text="Save Config", command=save_config).pack(pady=10)
    
    def on_close():
        stop_event.set()
        if monitor_thread and monitor_thread.is_alive():
            monitor_thread.join()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    build_gui()
