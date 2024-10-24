from __future__ import annotations

import os

from discord import Intents
from dotenv import load_dotenv

from Classes.Core.Bot import RentARaBot
################################################################################

load_dotenv()

################################################################################
    
bot = RentARaBot(
    description="Rent-A-Ra Bot!",
    intents=Intents.all(),
    debug_guilds=(
        None
        if os.getenv("DEBUG") == "False"
        else [
            955933227372122173, 
            1098708733284061278
        ]
    )
)

################################################################################

for filename in os.listdir("Cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"Cogs.{filename[:-3]}")

################################################################################

# if os.getenv("DEBUG") == "True":
#     token = os.getenv("DEBUG_TOKEN")
# else:
token = os.getenv("DISCORD_TOKEN")
    
bot.run(token)

################################################################################
