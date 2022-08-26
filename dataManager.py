import json
import logger as log
from os.path import exists, isdir
from os import mkdir, remove, listdir
from shutil import copyfile
from importlib import import_module
from dataClasses import Poll, RoleGiver


logger = log.Logger("./logs/log.txt")


def import_commands(path: str, client):
    if not path.endswith("/"):
        path += "/"

    # Create package path for modules
    module_path = path.replace("/", ".").strip(".") + "."

    # Go trough all files
    for file in listdir(path):
        # Load contents of subdirectories
        if isdir(file) and not "__" in file and not file[0] == ".":
            import_commands(path + file)
        # Ignore everything except modules
        elif file == "__init__.py" or not file.endswith(".py"):
            continue
        
        # Load module
        module = import_module((module_path + file.removesuffix(".py")))
        module.load(client)



def save_json(path: str, object: dict):
    with open(path, mode="w", encoding="utf-8") as file:
        file.write(json.dumps(object, indent=4))
        file.close()


def load_config():
    if not exists("./config.json"):
        logger.log_error("Config couldn't be found.")
        exit()
    
    config = json.load(open("./config.json", encoding="utf-8"))

    return config


def load_help():
    if not exists("./command_data/help/help.json"):
        logger.log_error("Help file couldn't be found. Help command will return empty list.")
        return None
    
    help = json.load(open("./command_data/help/help.json", encoding="utf-8"))
    
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
    save_json("./data/role_givers.json", new_dict)


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


def save_polls(polls: dict, poll_ids: dict):
    # Format
    polls_dict = { }
    for key in polls.keys():
        polls_dict[key] = polls[key].to_json()

    # Save
    save_json("./data/polls.json", polls_dict)
    save_json("./data/poll_ids.json", poll_ids)


def load_polls():
    if not exists("./data/"):
        mkdir("./data/")

    # Check if polls file exists
    if not exists("./data/polls.json"):
        logger.log_error("Polls file couldn't be found. It will be created.")
        
        if not exists("./data/polls.json"):
            with open("./data/polls.json", mode="w") as file:
                file.write("{}")
                file.close()

    # Check if poll ids file exists
    if not exists("./data/poll_ids.json"):
        logger.log_error("Poll IDs file couldn't be found. It will be created.")

        if not exists("./data/poll_ids.json"):
            with open("./data/poll_ids.json", mode="w") as file:
                file.write("{}")
                file.close()
                    
    # Load polls
    polls = json.load(open("./data/polls.json", encoding="utf-8"))
    new_dict = {}

    for message_id in polls.keys():
        poll = polls[message_id]
        
        voted = []
        for user in poll["voted"]:
            voted.append(int(user))

        new_dict[int(message_id)] = Poll(poll["emojis"], poll["can_change_votes"], voted)
    
    # Load poll ids
    poll_ids = json.load(open("./data/poll_ids.json", encoding="utf-8"))

    logger.log_info("Polls data loaded.")

    return (new_dict, poll_ids)


def load_permissions(guild_id: int, paged=True):
    # Check if directory exists
    if not exists("./data/permissions/"):
        mkdir("./data/permissions/")

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
    
    if len(page.keys()) != 0:
        paged_permissions.append(page)

    return paged_permissions


def save_permissions(guild_id: int, permissions: dict):
    save_json("./data/permissions/" + str(guild_id) + ".json", permissions)


def reset_permissions(guild_id: int):
    remove("./data/permissions/" + str(guild_id) + ".json")


def load_commands():
    # Check if file exists
    if not exists("./command_data/help/commands.json"):
        logger.log_error("Commands file couldn't be found. Commands command will return empty embed.")
        return {}
    
    # Load commands
    commands = json.load(open("./command_data/help/commands.json", encoding="utf-8"))
    logger.log_info("Commands data loaded.")

    return commands


def is_production() -> bool:
    config = load_config()
    return not config["debug"]


def load_welcome_message(guild_id: int) -> str:
    # Check if directory exists
    if not exists("./data/welcome_messages/"):
        mkdir("./data/welcome_messages/")

    # Check if file exists
    if not exists("./data/welcome_messages/" + str(guild_id) + ".json"):
        return None
    
    # Load data
    message: dict = json.load(open("./data/welcome_messages/" + str(guild_id) + ".json", encoding="utf-8"))
    return message["message"]


def save_welcome_message(guild_id: int, message: str):
    # Check if directory exists
    if not exists("./data/welcome_messages/"):
        mkdir("./data/welcome_messages/")

    message_dict = {}
    message_dict["message"] = message

    # Save data
    save_json("./data/welcome_messages/" + str(guild_id) + ".json", message_dict)


def remove_welcome_message(guild_id: int):
    # Check if directory exists
    if not exists("./data/welcome_messages/"):
        mkdir("./data/welcome_messages/")
    
    # Remove it
    if exists("./data/welcome_messages/" + str(guild_id) + ".json"):
        remove("./data/welcome_messages/" + str(guild_id) + ".json")


def load_hangman_packs():
    # Load packs
    files = []
    for file in listdir("./command_data/hangman/"):
        files.append(json.load(open("./command_data/hangman/" + file)))

    # Format data
    packs = {}
    for file in files:
        packs[file["name"]] = file["expressions"]
    
    logger.log_info("Hangman data loaded.")

    return packs


def load_profile(user_id: int):
    user_id = str(user_id)

    # Check if directory exists
    if not exists("./data/user_profiles/"):
        mkdir("./data/user_profiles/")
    
    # Check if user has profile
    if not exists("./data/user_profiles/" + user_id + ".json"):
        copyfile("./default/user_profile.json", "./data/user_profiles/" + user_id + ".json")
    
    # Load profile
    profile = json.load(open("./data/user_profiles/" + user_id + ".json", encoding="utf-8"))
    return profile


def load_sounds():
    info = {}

    # Check if file exists
    if not exists("./command_data/sound_board/sounds.json"):
        logger.log_error("Couldn't find sound board metadata.")
    else:
        info = json.load(open("./command_data/sound_board/sounds.json", encoding="utf-8"))
        if len(info.keys()) == 0:
            logger.log_warning("Sound board didn't find any sounds. Check if they are registered properly.")   

    # Format data
    sounds = []
    page = {}
    count = 0
    for key in info.keys():
        if count == 15:
            count = 0
            sounds.append(page)
            page = {}

        page[key] = "./command_data/sound_board/" + info[key]

        count += 1
    
    if len(page.keys()) != 0:
        sounds.append(page)
    
    return sounds


def __add_experience(user_id: int, experience: int):
    # Load profile
    profile: dict = load_profile(user_id)
    
    # Add experience
    profile["experience"] += experience

    # Level up
    if int(profile["experience"]) >= int(profile["required experience"]):
        profile["level"] += 1

        profile["experience"] -= profile["required experience"]
        profile["required experience"] = round(profile["required experience"] * 1.1)
    
    # Save profile
    save_json("./data/user_profiles/" + str(user_id) + ".json", profile)


def add_experience(user_id: int, source: str):
    # Load profile
    profile: dict = load_profile(user_id)
    
    # Add experience
    experience = json.load(open("./command_data/user_profiles/experience.json", encoding="utf-8"))
    __add_experience(user_id, experience[source])
    
    # Save profile
    save_json("./data/user_profiles/" + str(user_id) + ".json", profile)


def add_game_record(user_id: int, game: str, won: bool):
    # Load profile
    profile = load_profile(user_id)

    # Update record
    profile["games"][game]["played"] += 1
    profile["games"][game]["won"] = int(won)

    # Save profile
    save_json("./data/user_profiles/" + str(user_id) + ".json", profile)

    # Add experience
    experience = json.load(open("./command_data/user_profiles/experience.json", encoding="utf-8"))
    __add_experience(user_id, experience[game][("win" * won) + ((not won) * "defeat")])