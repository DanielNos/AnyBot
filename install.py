import os, platform


# MODULES
print("Installing modules...")

python = "py"
if platform.system() == "Linux":
    python = "python3"

for module in ["nextcord", "colorama", "emoji", "PyNaCl", "discord-emoji"]:
    os.system(python + " -m pip install " + module)

# LIBRARIES
print("Installing libraries...")

os.system("sudo apt install ffmpeg")

print("Bot is ready. Run main.py to start it.")