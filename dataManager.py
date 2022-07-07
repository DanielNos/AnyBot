from os.path import exists
from math import floor
import json
from commands.roleGiver import RoleGiverObject

def load_config():
    if not exists("./config.json"):
        print("[ERROR] Config couldn't be found.")
        exit()
    
    config = json.load(open("./config.json", encoding="utf-8"))
    print("Config loaded.")

    return config


def load_help():
    if not exists("./commands.json"):
        print("[ERROR] Help file couldn't be found. Help command will return empty table.")
        return None
    
    help = json.load(open("./commands.json", encoding="utf-8"))
    
    # Format data
    keys = list(help.keys())
    values = list(help.values())
    commands = ""
    actions = ""

    for i in range(len(keys)):
        commands += keys[i] + "\n" + (floor(len(values[i]) / 52)) * "\n"
        actions += values[i] + "\n"

    print("Help data loaded.")
    return (commands, actions)


def save_role_givers(roleGivers: dict):
    newDict = {}

    for rg in roleGivers:
        newDict[rg] = roleGivers[rg].to_json()

    with open("./data/role_givers.json", mode="w") as file:
        file.write(json.dumps(newDict))
        file.close()

def load_role_givers():
    # Check if file exists
    if not exists("./data/role_givers.json"):
        print("[ERROR] Role givers file couldn't be found. It will be created.")
        with open("./data/role_givers.json", mode="w") as file:
            file.write("{}")
            file.close()
        return {}

    # Load file
    with open("./data/role_givers.json", mode="r") as file:
        dict = json.load(file)
        file.close()

    # Parse data
    newDict = {}

    for rg in dict:
        role_ids = []
        for id in dict[rg]["role_ids"]:
            role_ids.append(int(id))
        newDict[int(rg)] = RoleGiverObject(int(dict[rg]["message_id"]), role_ids)
    
    if len(newDict) == 0:
        print("[INFO] No role givers from previous session found.")
    
    print("Role giver data loaded.")

    return newDict