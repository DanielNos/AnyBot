BOT = {
    "name": "NosBot",
    "icon": "https://cdn.discordapp.com/app-icons/990276313287888896/f4fa1fc1207e7430a510ed6b367da042.png",
    "color": 0xFBCE9D
}

AUTHOR = {
    "name": "Daniel Nos",
    "url": "https://github.com/DanielNos"
}

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "\033[0;97m%(asctime)s   \033[1;96m%(levelname)-6s \033[93m%(asctime)s   \033[1;97m%(module)-10s   \033[0;97m%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "standard": {
            "format": "\033[0;97m%(asctime)s   \033[1;96m%(levelname)-6s \033[93m%(name)-15s  \033[0;97m %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "chat": {
            "format": "\033[0;97m%(asctime)s   \033[1;92mCHAT   \033[93m%(name)-15s   \033[0;97m%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/nosbot.log",
            "formatter": "verbose"
        },
        "chatConsole": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "chat"
        },
        "chatFile": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/chat.log",
            "formatter": "chat"
        },
    },
    "loggers": {
        "bot": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "discord": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "chat": {
            "handlers": ["chatConsole", "chatFile"],
            "level": "INFO",
            "propagate": False
        },
    }
}