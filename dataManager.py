import json
import logger as log
from os.path import exists
from os import mkdir
from commands.roleGivers import RoleGiver

logger = log.Logger("./logs/log.txt")

def load_config():
    if not exists("./config.json"):
        logger.log_error("Config couldn't be found.")
        exit()
    
    config = json.load(open("./config.json", encoding="utf-8"))
    logger.log_info("Config loaded.")

    return config


def load_help():
    if not exists("./commands.json"):
        logger.log_error("Help file couldn't be found. Help command will return empty table.")
        return None
    
    help = json.load(open("./commands.json", encoding="utf-8"))
    
    # Format data
    keys = list(help.keys())
    values = list(help.values())
    commands = []
    actions = []

    for i in range(len(keys)):
        commands.append(keys[i])
        actions.append(values[i])

    logger.log_info("Help data loaded.")
    return (commands, actions)


def save_role_givers(roleGivers: dict):
    # Convert class instances to objects
    newDict = {}

    for rg in roleGivers:
        newDict[rg] = roleGivers[rg].to_json()

    # Save
    with open("./data/role_givers.json", mode="w") as file:
        file.write(json.dumps(newDict))
        file.close()


def load_role_givers():
    # Check if file exists
    if not exists("./data/role_givers.json"):
        logger.log_error("Role givers file couldn't be found. It will be created.")
        if not exists("./data/"):
            mkdir("./data/")
            with open("./data/role_givers.json", mode="w") as file:
                file.write("{}")
                file.close()
        return {}

    # Load file
    with open("./data/role_givers.json", mode="r") as file:
        if file.read() == "":
            logger.log_info("No role givers from previous session found.")
            logger.log_info("Role giver data loaded.")
            file.close()
            return {}
        file.close()
    
    with open("./data/role_givers.json", mode="r") as file:
        dict = json.load(file)
        file.close()

    # Parse data
    newDict = {}

    for rg in dict:
        role_ids = []
        for id in dict[rg]["role_ids"]:
            role_ids.append(int(id))
        newDict[int(rg)] = RoleGiver(int(dict[rg]["message_id"]), role_ids)
    
    if len(newDict) == 0:
        logger.log_info("No role givers from previous session found.")
    
    logger.log_info("Role giver data loaded.")

    return newDict


def load_test_guilds():
    config = json.load(open("./config.json", encoding="utf-8"))
    return config["test_guilds"]