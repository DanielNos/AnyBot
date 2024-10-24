DEBUG = {
    "test_guilds": [794290505273966604, 793074039996416012] # To disable debug, leave this empty. NON-EMPTY TEST GUILDS DISABLE GLOBAL COMMAND SYNC!
}

BOT = {
    "command_prefix": "any   ",
    "name": "AnyBot",
    "icon": "",
    "color": 0xFBCE9D
}

AUTHOR = {
    "name": "Daniel Nos",
    "url": "https://github.com/DanielNos",
    "id": 277796227397976064
}

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "\033[0;97m%(asctime)s   \033[1;96m%(levelname)-6s \033[93m%(name)s - %(module)-18s   \033[0;97m%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "standard": {
            "format": "\033[0;97m%(asctime)s   \033[1;96m%(levelname)-6s \033[93m%(name)-15s  \033[0;97m %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose"
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/bot.log",
            "formatter": "verbose"
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
    }
}
