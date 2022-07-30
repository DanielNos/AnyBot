import json
import logger as log
from os.path import exists
from os import mkdir
from commands.roleGivers import RoleGiver
from shutil import copyfile

logger = log.Logger("./logs/log.txt")

def load_config():
    if not exists("./config.json"):
        logger.log_error("Config couldn't be found.")
        exit()
    
    config = json.load(open("./config.json", encoding="utf-8"))

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
    new_dict = {}

    for rg in roleGivers:
        new_dict[rg] = roleGivers[rg].to_json()

    # Save
    with open("./data/role_givers.json", mode="w") as file:
        file.write(json.dumps(new_dict))
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
    new_dict = {}

    for rg in dict:
        role_ids = []
        for id in dict[rg]["role_ids"]:
            role_ids.append(int(id))
        new_dict[int(rg)] = RoleGiver(int(dict[rg]["message_id"]), role_ids)
    
    if len(new_dict) == 0:
        logger.log_info("No role givers from previous session found.")
    
    logger.log_info("Role giver data loaded.")

    return new_dict


def load_test_guilds():
    config = json.load(open("./config.json", encoding="utf-8"))
    return config["test_guilds"]


def save_polls(polls: dict):
    # Save
    with open("./data/polls.json", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(polls))
        file.close()


def load_polls() -> dict:
    # Check if file exists
    if not exists("./data/polls.json"):
        logger.log_error("Polls file couldn't be found. It will be created.")
        if not exists("./data/"):
            mkdir("./data/")
            with open("./data/polls.json", mode="w") as file:
                file.write("{}")
                file.close()
        return {}
    
    # Load polls
    polls = json.load(open("./data/polls.json", encoding="utf-8"))
    new_dict = {}

    for message_id in polls.keys():
        new_dict[int(message_id)] = polls[message_id]

    logger.log_info("Polls data loaded.")

    return new_dict


def load_permissions(guild_id: int, paged=True):
    # Check if file exists
    if guild_id != None and not exists("./data/permissions/" + str(guild_id) + ".json"):
        logger.log_info("Guild " + str(guild_id) + " command permissions couldn't be found. Creating default configuration.")
        copyfile("./default/permissions.json", "./data/permissions/" + str(guild_id) + ".json")
    
    # Load data
    if guild_id != None:
        permissions: dict = json.load(open("./data/permissions/" + str(guild_id) + ".json", encoding="utf-8"))
    else:
        permissions: dict = json.load(open("./default/permissions.json", encoding="utf-8"))
    
    permissions_per_page = load_config()["permissions_per_page"]

    if not paged:
        return permissions

    # Split data to pages
    paged_permissions = []
    keys = list(permissions.keys())
    page = {}

    for i in range(1, len(keys)+1):
        page[keys[i-1]] = permissions[keys[i-1]]

        if i % permissions_per_page == 0:
            paged_permissions.append(page)
            page = {}

    return paged_permissions


def save_permissions(guild_id: int, permissions: dict):
    with open("./data/permissions/" + str(guild_id) + ".json", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(permissions, indent=4))
        file.close()