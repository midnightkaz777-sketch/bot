# ============================================================
#                         BOSS BOB
#                    ROBLOX UPDATE SYSTEM
# ============================================================

import discord
from discord.ext import commands, tasks
import requests


# ============================================================
#                         CONFIG
# ============================================================

# Put the Discord channel ID where Roblox updates should go
ROBLOX_UPDATE_CHANNEL_ID = 123456789012345678

# Check Roblox every 10 minutes
CHECK_INTERVAL_MINUTES = 10


# ============================================================
#                         COG
# ============================================================

class Roblox(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.last_version = None

        self.check_roblox.start()

    def cog_unload(self):

        self.check_roblox.cancel()


    # ========================================================
    #                  ROBLOX VERSION CHECK
    # ========================================================

    def get_roblox_version(self):

        try:

            response = requests.get(
                "https://clientsettings.roblox.com/v2/client-version/WindowsPlayer/channel/live",
                timeout=10
            )

            if response.status_code != 200:
                return None

            data = response.json()

            return data.get("clientVersionUpload")

        except Exception as e:

            print("Roblox check error:", e)

            return None


    # ========================================================
    #                     UPDATE CHECK
    # ========================================================

    @tasks.loop(minutes=CHECK_INTERVAL_MINUTES)
    async def check_roblox(self):

        version = self.get_roblox_version()

        if not version:
            return

        # First check — don't announce an update
        if self.last_version is None:

            self.last_version = version

            print(
                f"🎮 Roblox version: {version}"
            )

            return


        # New version detected
        if version != self.last_version:

            old_version = self.last_version

            self.last_version = version

            channel = self.bot.get_channel(
                ROBLOX_UPDATE_CHANNEL_ID
            )

            if not channel:
                print(
                    "❌ Roblox update channel not found."
                )

                return

            embed = discord.Embed(

                title="🎮 Roblox Update Detected!",

                description=(
                    "Roblox has released a new client version!\n\n"

                    f"**Previous:** `{old_version}`\n"
                    f"**New:** `{version}`\n\n"

                    "🔄 Roblox may need to be restarted "
                    "to receive the update."
                ),

                color=discord.Color.green()

            )

            embed.set_footer(
                text="Boss Bob • Roblox Updater"
            )

            await channel.send(
                embed=embed
            )

            print(
                f"🎮 Roblox update detected: {version}"
            )


    # ========================================================
    #                    WAIT UNTIL READY
    # ========================================================

    @check_roblox.before_loop
    async def before_check(self):

        await self.bot.wait_until_ready()


# ============================================================
#                         SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Roblox(bot)
    )