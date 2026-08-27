# ============================================================
#                       BOSS BOB
#                     SECURITY SYSTEM
#                       security.py
# ============================================================

import discord


# ============================================================
#                         CONFIG
# ============================================================

# The channel Boss Bob should protect.
SECURITY_CHANNEL_ID = 1542602684081770526

# Your Discord user ID.
# Boss Bob will NEVER ban this account.
OWNER_USER_ID = 1542599719753097386

# Channel where security actions are logged.
SECURITY_LOG_CHANNEL_ID = 1542608047409602600


# ============================================================
#                    SECURITY SETUP
# ============================================================

def setup_security(bot):

    print(
        "🛡️ Boss Bob security system loaded."
    )


# ============================================================
#                     MESSAGE CHECK
# ============================================================

async def security_message_check(
    bot,
    message
):

    # Ignore DMs
    if not message.guild:
        return

    # Ignore bots
    if message.author.bot:
        return

    # Only monitor the configured channel
    if message.channel.id != SECURITY_CHANNEL_ID:
        return

    # Ignore the owner
    if message.author.id == OWNER_USER_ID:

        print(
            f"🛡️ Owner ignored: {message.author}"
        )

        return

    member = message.author

    # --------------------------------------------------------
    # Delete the message first
    # --------------------------------------------------------

    try:

        await message.delete()

    except discord.NotFound:
        pass

    except discord.Forbidden:

        print(
            "❌ Boss Bob cannot delete messages "
            "in the security channel."
        )

    except discord.HTTPException:

        print(
            "❌ Discord error while deleting "
            "security message."
        )


    # --------------------------------------------------------
    # Ban the user
    # --------------------------------------------------------

    try:

        await member.ban(
            reason="Message sent in protected security channel."
        )

        print(
            f"🚫 Banned {member} "
            f"for messaging in the security channel."
        )

    except discord.Forbidden:

        print(
            f"❌ Boss Bob cannot ban {member}."
        )

        return

    except discord.HTTPException:

        print(
            f"❌ Discord error while banning {member}."
        )

        return


    # --------------------------------------------------------
    # Security log
    # --------------------------------------------------------

    log_channel = message.guild.get_channel(
        SECURITY_LOG_CHANNEL_ID
    )

    if not log_channel:
        return


    embed = discord.Embed(
        title="🚨 Security Action",
        description=(
            f"**User:** {member.mention}\n"
            f"**Username:** `{member}`\n"
            f"**User ID:** `{member.id}`\n\n"
            f"**Channel:** {message.channel.mention}\n"
            f"**Action:** 🔨 Banned\n"
            f"**Reason:** Message sent in protected channel."
        ),
        color=discord.Color.red()
    )

    await log_channel.send(
        embed=embed
    )


# ============================================================
#                 REGISTER MESSAGE LISTENER
# ============================================================

def register_security_listener(bot):

    @bot.listen("on_message")
    async def boss_bob_security_listener(
        message
    ):

        try:

            await security_message_check(
                bot,
                message
            )

        except Exception as error:

            print(
                f"❌ Security system error: {error}"
            )


# ============================================================
#                         STARTUP
# ============================================================

def initialize_security(bot):

    setup_security(bot)

    register_security_listener(bot)