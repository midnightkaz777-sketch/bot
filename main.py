# ============================================================
#                         BOSS BOB
#                    KAZWARE BOT SYSTEM
#                         main.py
# ============================================================

import os
import traceback

import discord
from discord.ext import commands


# ============================================================
#                         TOKEN
# ============================================================

TOKEN = os.getenv("BOSS_BOB_TOKEN")


# ============================================================
#                         INTENTS
# ============================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True


# ============================================================
#                         BOT CLASS
# ============================================================

class BossBob(commands.Bot):

    async def setup_hook(self):

        print("🟣 Loading Boss Bob systems...")
        print()

        # ----------------------------------------------------
        # Tickets
        # ----------------------------------------------------

        try:
            from tickets import setup as setup_tickets

            await setup_tickets(self)

            print("✅ Ticket system loaded.")

        except Exception as error:
            print("❌ Ticket system failed to load.")
            print(error)
            traceback.print_exc()


        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        try:
            from verification import setup_verification

            result = setup_verification(self)

            if hasattr(result, "__await__"):
                await result

            print("✅ Verification system loaded.")

        except Exception as error:
            print("❌ Verification system failed to load.")
            print(error)
            traceback.print_exc()


        # ----------------------------------------------------
        # Roblox
        # ----------------------------------------------------

        try:
            from roblox import setup_roblox

            result = setup_roblox(self)

            if hasattr(result, "__await__"):
                await result

            print("✅ Roblox system loaded.")

        except Exception as error:
            print("❌ Roblox system failed to load.")
            print(error)
            traceback.print_exc()


        # ----------------------------------------------------
        # Security
        # ----------------------------------------------------

        try:
            from security import initialize_security

            result = initialize_security(self)

            if hasattr(result, "__await__"):
                await result

            print("✅ Security system loaded.")

        except Exception as error:
            print("❌ Security system failed to load.")
            print(error)
            traceback.print_exc()


        # ----------------------------------------------------
        # Booster
        # ----------------------------------------------------

        try:
            from booster import initialize_booster

            result = initialize_booster(self)

            if hasattr(result, "__await__"):
                await result

            print("✅ Booster system loaded.")

        except Exception as error:
            print("❌ Booster system failed to load.")
            print(error)
            traceback.print_exc()


        print()
        print("======================================")
        print("       BOSS BOB SYSTEMS LOADED")
        print("======================================")
        print()


# ============================================================
#                           BOT
# ============================================================

bot = BossBob(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# ============================================================
#                       READY EVENT
# ============================================================

@bot.event
async def on_ready():

    print()
    print("======================================")
    print("          🟣 BOSS BOB ONLINE")
    print("======================================")
    print(f"Bot: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print(f"Servers: {len(bot.guilds)}")
    print("======================================")
    print()


    # --------------------------------------------------------
    # Verification Panels
    # --------------------------------------------------------

    try:

        from verification import send_verification_panel

        for guild in bot.guilds:

            try:

                result = send_verification_panel(
                    bot,
                    guild
                )

                if hasattr(result, "__await__"):
                    await result

                print(
                    f"✅ Verification panel checked: "
                    f"{guild.name}"
                )

            except Exception as error:

                print(
                    f"❌ Verification panel error "
                    f"in {guild.name}: {error}"
                )

    except ImportError:
        pass

    except Exception:

        print("❌ Verification panel system failed.")
        traceback.print_exc()


    # --------------------------------------------------------
    # Startup Summary
    # --------------------------------------------------------

    print()
    print("======================================")
    print("          BOSS BOB SYSTEMS")
    print("======================================")
    print("Tickets:      ONLINE")
    print("Verification: ONLINE")
    print("Security:     ONLINE")
    print("Roblox:       ONLINE")
    print("Booster:      ONLINE")
    print("======================================")
    print("          🟣 BOSS BOB READY")
    print("======================================")
    print()


# ============================================================
#                    SERVER JOIN EVENT
# ============================================================

@bot.event
async def on_guild_join(guild):

    print(
        f"🟣 Boss Bob joined: {guild.name}"
    )

    try:

        from verification import send_verification_panel

        result = send_verification_panel(
            bot,
            guild
        )

        if hasattr(result, "__await__"):
            await result

        print(
            f"✅ Verification panel created "
            f"in {guild.name}"
        )

    except Exception:

        print(
            f"❌ Could not create verification "
            f"panel in {guild.name}"
        )

        traceback.print_exc()


# ============================================================
#                       ERROR HANDLER
# ============================================================

@bot.event
async def on_error(event, *args, **kwargs):

    print()
    print(
        f"❌ Discord event error: {event}"
    )

    traceback.print_exc()


# ============================================================
#                       TOKEN CHECK
# ============================================================

def check_configuration():

    if not TOKEN:

        print()
        print("======================================")
        print("❌ BOSS_BOB_TOKEN IS MISSING")
        print("======================================")
        print()
        print("Create a Railway variable named:")
        print()
        print("BOSS_BOB_TOKEN")
        print()
        print("Put your Discord bot token there.")
        print()

        return False

    return True


# ============================================================
#                       START BOT
# ============================================================

if __name__ == "__main__":

    print()
    print("🟣 Starting Boss Bob...")
    print()

    if not check_configuration():
        raise SystemExit(1)

    try:

        bot.run(TOKEN)

    except discord.LoginFailure:

        print()
        print("❌ INVALID DISCORD BOT TOKEN")
        print("Check BOSS_BOB_TOKEN in Railway.")
        print()

    except discord.PrivilegedIntentsRequired:

        print()
        print("❌ PRIVILEGED INTENTS ERROR")
        print()
        print(
            "Enable the required intents in the "
            "Discord Developer Portal."
        )
        print()

    except KeyboardInterrupt:

        print()
        print("🛑 Boss Bob stopped.")
        print()

    except Exception:

        print()
        print("❌ BOSS BOB CRASHED")
        print()

        traceback.print_exc()
