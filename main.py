# ============================================================
#                       BOSS BOB
#                  KAZWARE BOT SYSTEM
#                         main.py
# ============================================================

import os
import traceback

import discord
from discord.ext import commands


# ============================================================
#                    ENVIRONMENT TOKEN
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
#                           BOT
# ============================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# ============================================================
#                     MODULE STATUS
# ============================================================

VERIFICATION_LOADED = False
TICKETS_LOADED = False
ROBLOX_LOADED = False
SECURITY_LOADED = False
BOOSTER_LOADED = False

verification_setup = None
send_verification_panel = None

setup_tickets = None
setup_roblox = None
initialize_security = None
initialize_booster = None


# ============================================================
#                    LOAD VERIFICATION
# ============================================================

try:
    from verification import (
        setup_verification,
        send_verification_panel
    )

    verification_setup = setup_verification
    VERIFICATION_LOADED = True

    print("✅ verification.py loaded.")

except Exception as error:
    print("⚠️ verification.py could not be loaded.")
    print(f"   {error}")
    traceback.print_exc()


# ============================================================
#                       LOAD TICKETS
# ============================================================

try:
    from tickets import setup_tickets

    TICKETS_LOADED = True

    print("✅ tickets.py loaded.")

except Exception as error:
    print("⚠️ tickets.py could not be loaded.")
    print(f"   {error}")
    traceback.print_exc()


# ============================================================
#                       LOAD ROBLOX
# ============================================================

try:
    from roblox import setup_roblox

    ROBLOX_LOADED = True

    print("✅ roblox.py loaded.")

except Exception as error:
    print("⚠️ roblox.py could not be loaded.")
    print(f"   {error}")
    traceback.print_exc()


# ============================================================
#                     LOAD SECURITY
# ============================================================

try:
    from security import initialize_security

    SECURITY_LOADED = True

    print("✅ security.py loaded.")

except Exception as error:
    print("⚠️ security.py could not be loaded.")
    print(f"   {error}")
    traceback.print_exc()


# ============================================================
#                      LOAD BOOSTER
# ============================================================

try:
    from booster import initialize_booster

    BOOSTER_LOADED = True

    print("✅ booster.py loaded.")

except Exception as error:
    print("⚠️ booster.py could not be loaded.")
    print(f"   {error}")
    traceback.print_exc()


# ============================================================
#                    SETUP ONCE
# ============================================================

SYSTEMS_STARTED = False


async def initialize_systems():
    global SYSTEMS_STARTED

    if SYSTEMS_STARTED:
        return

    SYSTEMS_STARTED = True

    print()
    print("======================================")
    print("        STARTING BOSS BOB SYSTEMS")
    print("======================================")

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    if VERIFICATION_LOADED:
        try:
            result = verification_setup(bot)

            # Support both normal functions and async functions.
            if hasattr(result, "__await__"):
                await result

            print("✅ Verification system started.")

        except Exception:
            print("❌ Verification system failed.")
            traceback.print_exc()

    else:
        print("❌ Verification system unavailable.")


    # --------------------------------------------------------
    # Tickets
    # --------------------------------------------------------

    if TICKETS_LOADED:
        try:
            result = setup_tickets(bot)

            if hasattr(result, "__await__"):
                await result

            print("✅ Ticket system started.")

        except Exception:
            print("❌ Ticket system failed.")
            traceback.print_exc()

    else:
        print("❌ Ticket system unavailable.")


    # --------------------------------------------------------
    # Roblox
    # --------------------------------------------------------

    if ROBLOX_LOADED:
        try:
            result = setup_roblox(bot)

            if hasattr(result, "__await__"):
                await result

            print("✅ Roblox system started.")

        except Exception:
            print("❌ Roblox system failed.")
            traceback.print_exc()

    else:
        print("❌ Roblox system unavailable.")


    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    if SECURITY_LOADED:
        try:
            result = initialize_security(bot)

            if hasattr(result, "__await__"):
                await result

            print("✅ Security system started.")

        except Exception:
            print("❌ Security system failed.")
            traceback.print_exc()

    else:
        print("❌ Security system unavailable.")


    # --------------------------------------------------------
    # Booster
    # --------------------------------------------------------

    if BOOSTER_LOADED:
        try:
            result = initialize_booster(bot)

            if hasattr(result, "__await__"):
                await result

            print("✅ Booster system started.")

        except Exception:
            print("❌ Booster system failed.")
            traceback.print_exc()

    else:
        print("❌ Booster system unavailable.")


    print("======================================")
    print("        BOSS BOB SYSTEMS STARTED")
    print("======================================")
    print()


# ============================================================
#                       BOT READY
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

    await initialize_systems()

    # --------------------------------------------------------
    # Verification Panel
    # --------------------------------------------------------

    if VERIFICATION_LOADED and send_verification_panel:

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

            except Exception:
                print(
                    f"❌ Verification panel error: "
                    f"{guild.name}"
                )

                traceback.print_exc()


    # --------------------------------------------------------
    # Startup Summary
    # --------------------------------------------------------

    print()
    print("======================================")
    print("          BOSS BOB SYSTEMS")
    print("======================================")

    print(
        f"Verification: "
        f"{'ONLINE' if VERIFICATION_LOADED else 'OFFLINE'}"
    )

    print(
        f"Tickets: "
        f"{'ONLINE' if TICKETS_LOADED else 'OFFLINE'}"
    )

    print(
        f"Roblox: "
        f"{'ONLINE' if ROBLOX_LOADED else 'OFFLINE'}"
    )

    print(
        f"Security: "
        f"{'ONLINE' if SECURITY_LOADED else 'OFFLINE'}"
    )

    print(
        f"Booster: "
        f"{'ONLINE' if BOOSTER_LOADED else 'OFFLINE'}"
    )

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

    # Send verification panel to new server.
    if VERIFICATION_LOADED and send_verification_panel:

        try:
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
#                     TOKEN CHECK
# ============================================================

def check_configuration():

    if not TOKEN:

        print()
        print("======================================")
        print("❌ BOSS_BOB_TOKEN IS MISSING")
        print("======================================")
        print()
        print(
            "Create a Railway environment variable named:"
        )
        print()
        print("BOSS_BOB_TOKEN")
        print()
        print(
            "Put your Boss Bob Discord bot token "
            "inside that environment variable."
        )
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
        print(
            "Check the BOSS_BOB_TOKEN environment variable."
        )
        print()

    except discord.PrivilegedIntentsRequired:

        print()
        print("❌ PRIVILEGED INTENTS ERROR")
        print()
        print(
            "Open the Discord Developer Portal "
            "and enable the required intents."
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
