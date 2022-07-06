from os.path import exists
from math import floor
import json
from commands.roleGiver import RoleGiverObject

def load_help():
    if not exists("./commands.json"):
        print("[ERROR] Help file couldn't be found. Help command will return empty table.")
        return None
    
    help = json.load(open("./commands.json", encoding="utf-8"))
    keys = list(help.keys())
    values = list(help.values())
    commands = ""
    actions = ""

    for i in range(len(keys)):
        commands += keys[i] + "\n" + (floor(len(values[i]) / 52)) * "\n"
        actions += values[i] + "\n"

    print("Help loaded.")
    return (commands, actions)

def load_config():
    if not exists("./config.json"):
        print("[ERROR] Config couldn't be found.")
        exit()
    
    config = json.load(open("./config.json", encoding="utf-8"))
    print("Config loaded.")

    return config

def save_role_givers(roleGivers: dict):
    newDict = {}

    for rg in roleGivers:
        newDict[rg] = roleGivers[rg].to_json()

    with open("./data/role_givers.json", mode="w") as file:
        file.write(json.dumps(newDict))
        file.close()

def load_role_givers():
    if not exists("./data/role_givers.json"):
        print("[ERROR] Role givers file couldn't be found.")
        return

    with open("./data/role_givers.json", mode="r") as file:
        dict = json.load(file)
        file.close()

    newDict = {}

    for rg in dict:
        role_ids = []
        for id in dict[rg]["role_ids"]:
            role_ids.append(int(id))
        newDict[int(rg)] = RoleGiverObject(int(dict[rg]["message_id"]), role_ids)
    
    print("Role giver data loaded.")

    return newDict