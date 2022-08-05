import colorama
from datetime import datetime
from colorama import Fore, Style
from enum import Enum
from os.path import exists
from os import mkdir

class Level(Enum):
    Info = 0,
    Warning = 1,
    Error = 2

class Logger:
    def __init__(self, log_file_path: str):
        self.file = log_file_path
        colorama.init()

        if not exists(self.file[:self.file.rfind("/")+1]): 
            mkdir(self.file[:self.file.rfind("/")+1])
        
        if not exists(self.file):
            f = open(self.file, "w", encoding="utf-8")
            f.close()

    def log(self, message: str, level: Level = 0):
        text = []
        text.append(datetime.now().strftime("%H:%M:%S %d-%m-%Y"))

        text.append(self.__level_to_text(level))

        print(str(text[0]) + str(text[1]) + message)
        
        with open(self.file, "a", encoding="utf-8") as file:
            file.write(text[0] + self.__level_to_text(level, False) + message + "\n")
            file.close()

    def log_info(self, message: str):
        self.log(message, 0)

    def log_warning(self, message: str):
        self.log(message, 1)

    def log_error(self, message: str):
        self.log(message, 2)

    def __level_to_text(self, level: Level, colored: bool = True):
        if not colored:
            if level == 0:
                return " [INFO] "
            if level == 1:
                return " [WARNING] "
            if level == 2:
                return " [ERROR] "
        
        if level == 0:
            return Fore.WHITE + " [INFO] " + Fore.WHITE
        if level == 1:
            return Fore.YELLOW + " [WARNING] " + Fore.WHITE
        if level == 2:
            return Fore.LIGHTRED_EX + " [ERROR] " + Fore.WHITE