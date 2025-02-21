import json
import os
import sys

class Config:
    APP_TITLE = "Fleet Chat Relay"
    VERSION = "0.0.1"
    ABOUT_TEXT = (
        f"{APP_TITLE} v{VERSION}\n\n"
        "A simple tool for EVE Online to relay fleet chat messages to Discord.\n\n"
        "Made by h0ly lag"
    )
    CONFIG_FILE_PATH = os.path.join(os.path.dirname(sys.argv[0]), "fleet-chat-relay.json")

    DISCORD_WEBHOOK_NAME = "Fleet Chat Relay"
    DISCORD_WEBHOOK_AVATAR = "https://i.imgur.com/a5sNnRi.gif"
    
    # Default configuration values
    DEFAULT_DISCORD_WEBHOOK_URL = (
        "https://discord.com/api/webhooks/000000000000000000/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    DEFAULT_DISCORD_TIMESTAMPS = True

    # This dict will hold the current user configuration.
    user_config = {
        "DISCORD_WEBHOOK_URL": DEFAULT_DISCORD_WEBHOOK_URL,
        "DISCORD_TIMESTAMPS": DEFAULT_DISCORD_TIMESTAMPS,
    }
    
    @classmethod
    def load_config(cls) -> dict:
        """
        Load configuration from fleet-chat-relay.json (if it exists) and update user_config.
        Returns the updated configuration dictionary.
        """
        if os.path.exists(Config.CONFIG_FILE_PATH):
            try:
                with open(Config.CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls.user_config.update(data)
            except Exception as e:
                print("Error loading config:", e)
        return cls.user_config

    @classmethod
    def save_config(cls) -> None:
        """
        Save the current user_config dictionary to fleet-chat-relay.json.
        """
        try:
            with open(Config.CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(cls.user_config, f, indent=4)
        except Exception as e:
            print("Error saving config:", e)

# Load the configuration when the module is imported.
Config.load_config()
