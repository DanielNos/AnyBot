import os, platform


# LIBRARIES
print("Installing libraries...")

for lib in ["python3-pip", "ffmpeg"]:
    os.system("sudo apt install " + lib)

# MODULES
print("Installing modules...")

os.system("sudo apt install python3-pip")

python = "py"
if platform.system() == "Linux":
    python = "python3"

for module in ["nextcord", "colorama", "emoji", "PyNaCl", "discord-emoji", "pypng"]:
    os.system(python + " -m pip install " + module)

print("Bot is ready. Run main.py to start it.")