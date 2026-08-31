# ============================================================
#                         BOSS BOB
#                    ROBLOX UPDATE SYSTEM
# ============================================================

import json
import os

import aiohttp
import discord
from discord.ext import commands, tasks


# ============================================================
#                         CONFIG
# ============================================================

# Discord channel where Roblox updates should be announced
ROBLOX_UPDATE_CHANNEL_ID = 1542637457495957666

# Check Roblox every 10 minutes
CHECK_INTERVAL_MINUTES = 10

# File used to remember the last Roblox version
VERSION_FILE = "roblox_version.json"

# Roblox Windows live client endpoint
ROBLOX_VERSION_URL = (
    "https://clientsettings.roblox.com/"
    "v2/client-version/WindowsPlayer/channel/live"
)


# ============================================================
#                         COG
# ============================================================

class Roblox(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.last_version = self.load_version()

        self.check_roblox.start()


    # ========================================================
    #                         UNLOAD
    # ========================================================

    def cog_unload(self):

        self.check_roblox.cancel()


    # ========================================================
    #                    LOAD SAVED VERSION
    # ========================================================

    def load_version(self):

        if not os.path.exists(VERSION_FILE):
            return None

        try:

            with open(
                VERSION_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                return data.get("version")

        except Exception as e:

            print(
                f"❌ Could not load Roblox version: {e}"
            )

            return None


    # ========================================================
    #                    SAVE VERSION
    # ========================================================

    def save_version(self, version):

        try:

            with open(
                VERSION_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    {
                        "version": version
                    },
                    file,
                    indent=4
                )

        except Exception as e:

            print(
                f"❌ Could not save Roblox version: {e}"
            )


    # ========================================================
    #                  GET ROBLOX VERSION
    # ========================================================

    async def get_roblox_version(self):

        try:

            timeout = aiohttp.ClientTimeout(
                total=15
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    ROBLOX_VERSION_URL
                ) as response:

                    if response.status != 200:

                        print(
                            "⚠️ Roblox API returned "
                            f"HTTP {response.status}"
                        )

                        return None

                    data = await response.json()

                    return data.get(
                        "clientVersionUpload"
                    )

        except aiohttp.ClientError as e:

            print(
                f"⚠️ Roblox connection error: {e}"
            )

            return None

        except Exception as e:

            print(
                f"❌ Roblox check error: {e}"
            )

            return None


    # ========================================================
    #                    UPDATE CHECK
    # ========================================================

    @tasks.loop(
        minutes=CHECK_INTERVAL_MINUTES
    )
    async def check_roblox(self):

        version = await self.get_roblox_version()

        # Roblox API failed
        if not version:

            print(
                "⚠️ Could not get Roblox version."
            )

            return


        # ====================================================
        # FIRST RUN
        # ====================================================

        if self.last_version is None:

            self.last_version = version

            self.save_version(version)

            print(
                "🎮 Roblox version initialized:"
            )

            print(
                f"   {version}"
            )

            return


        # ====================================================
        # NO UPDATE
        # ====================================================

        if version == self.last_version:

            print(
                f"✅ Roblox unchanged: {version}"
            )

            return


        # ====================================================
        # UPDATE DETECTED
        # ====================================================

        old_version = self.last_version

        self.last_version = version

        self.save_version(version)


        # ====================================================
        # FIND DISCORD CHANNEL
        # ====================================================

        channel = self.bot.get_channel(
            ROBLOX_UPDATE_CHANNEL_ID
        )

        if channel is None:

            print(
                "❌ Roblox update channel not found."
            )

            return


        # ====================================================
        # CREATE EMBED
        # ====================================================

        embed = discord.Embed(

            title="🎮 Roblox Update Detected!",

            description=(
                "Roblox has released a new "
                "Windows client version!\n\n"

                f"**Previous Version:**\n"
                f"`{old_version}`\n\n"

                f"**New Version:**\n"
                f"`{version}`\n\n"

                "🔄 **Roblox may need to be restarted "
                "to receive the update.**"
            ),

            color=discord.Color.green()
        )


        embed.set_footer(
            text="Boss Bob • Roblox Update System"
        )


        # ====================================================
        # SEND MESSAGE
        # ====================================================

        try:

            await channel.send(
                embed=embed
            )

            print(
                "🎮 Roblox update detected!"
            )

            print(
                f"   Old: {old_version}"
            )

            print(
                f"   New: {version}"
            )

        except discord.Forbidden:

            print(
                "❌ Boss Bob does not have permission "
                "to send messages in the Roblox update channel."
            )

        except discord.HTTPException as e:

            print(
                f"❌ Discord error while sending update: {e}"
            )


    # ========================================================
    #                    WAIT UNTIL READY
    # ========================================================

    @check_roblox.before_loop
    async def before_check(self):

        await self.bot.wait_until_ready()

        print(
            "🎮 Roblox update checker is ready!"
        )

        if self.last_version:

            print(
                f"💾 Saved Roblox version: "
                f"{self.last_version}"
            )

        else:

            print(
                "ℹ️ No saved Roblox version found."
            )


# ============================================================
#                         SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Roblox(bot)
    )
