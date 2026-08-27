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

# Your token is stored in an environment variable.
#
# Windows:
# BOSS_BOB_TOKEN = your Discord bot token
#
# Do NOT put the actual token in this file.

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
    intents=intents
)


# ============================================================
#                      MODULE STATUS
# ============================================================

VERIFICATION_LOADED = False
TICKETS_LOADED = False
ROBLOX_LOADED = False
SECURITY_LOADED = False
BOOSTER_LOADED = False


# ============================================================
#                    VERIFICATION SYSTEM
# ============================================================

try:

    from verification import (
        setup_verification,
        send_verification_panel
    )

    VERIFICATION_LOADED = True

except Exception as error:

    print(
        "⚠️ verification.py could not be loaded."
    )

    print(error)


# ============================================================
#                       TICKET SYSTEM
# ============================================================

try:

    from tickets import setup_tickets

    TICKETS_LOADED = True

except Exception as error:

    print(
        "⚠️ tickets.py could not be loaded."
    )

    print(error)


# ============================================================
#                       ROBLOX SYSTEM
# ============================================================

try:

    from roblox import setup_roblox

    ROBLOX_LOADED = True

except Exception as error:

    print(
        "⚠️ roblox.py could not be loaded."
    )

    print(error)


# ============================================================
#                     SECURITY SYSTEM
# ============================================================

try:

    from security import initialize_security

    SECURITY_LOADED = True

except Exception as error:

    print(
        "⚠️ security.py could not be loaded."
    )

    print(error)


# ============================================================
#                      BOOSTER SYSTEM
# ============================================================

try:

    from booster import initialize_booster

    BOOSTER_LOADED = True

except Exception as error:

    print(
        "⚠️ booster.py could not be loaded."
    )

    print(error)


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


    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    if VERIFICATION_LOADED:

        try:

            setup_verification(bot)

            print(
                "✅ Verification system loaded."
            )

        except Exception:

            print(
                "❌ Verification system failed."
            )

            traceback.print_exc()


    # --------------------------------------------------------
    # Tickets
    # --------------------------------------------------------

    if TICKETS_LOADED:

        try:

            setup_tickets(bot)

            print(
                "✅ Ticket system loaded."
            )

        except Exception:

            print(
                "❌ Ticket system failed."
            )

            traceback.print_exc()


    # --------------------------------------------------------
    # Roblox
    # --------------------------------------------------------

    if ROBLOX_LOADED:

        try:

            setup_roblox(bot)

            print(
                "✅ Roblox system loaded."
            )

        except Exception:

            print(
                "❌ Roblox system failed."
            )

            traceback.print_exc()


    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    if SECURITY_LOADED:

        try:

            initialize_security(bot)

            print(
                "✅ Security system loaded."
            )

        except Exception:

            print(
                "❌ Security system failed."
            )

            traceback.print_exc()


    # --------------------------------------------------------
    # Booster
    # --------------------------------------------------------

    if BOOSTER_LOADED:

        try:

            initialize_booster(bot)

            print(
                "✅ Booster system loaded."
            )

        except Exception:

            print(
                "❌ Booster system failed."
            )

            traceback.print_exc()


    # --------------------------------------------------------
    # Verification panel
    # --------------------------------------------------------

    if VERIFICATION_LOADED:

        for guild in bot.guilds:

            try:

                await send_verification_panel(
                    bot,
                    guild
                )

            except Exception:

                print(
                    f"❌ Verification panel error "
                    f"in {guild.name}"
                )

                traceback.print_exc()


    # --------------------------------------------------------
    # Startup summary
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

    if VERIFICATION_LOADED:

        try:

            await send_verification_panel(
                bot,
                guild
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
async def on_error(
    event,
    *args,
    **kwargs
):

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
            "Create an environment variable named:"
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
    print(
        "🟣 Starting Boss Bob..."
    )
    print()


    if not check_configuration():

        raise SystemExit(1)


    try:

        bot.run(
            TOKEN
        )


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
        print(
            "🛑 Boss Bob stopped."
        )
        print()


    except Exception:

        print()
        print(
            "❌ BOSS BOB CRASHED"
        )
        print()

        traceback.print_exc()