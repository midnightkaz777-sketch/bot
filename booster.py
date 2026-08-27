# ============================================================
#                       BOSS BOB
#                    BOOSTER SYSTEM
#                       booster.py
# ============================================================

import discord


# ============================================================
#                         CONFIG
# ============================================================

# Role given to anyone who boosts the server.
BOOSTER_ROLE_ID = 1542600972432441455

# Optional channel where boost logs are sent.
BOOSTER_LOG_CHANNEL_ID = 1542637574680477746


# ============================================================
#                     BOOSTER SETUP
# ============================================================

def setup_booster(bot):

    print(
        "🚀 Boss Bob booster system loaded."
    )


# ============================================================
#                    BOOST EVENT
# ============================================================

async def handle_boost(
    member
):

    guild = member.guild

    booster_role = guild.get_role(
        BOOSTER_ROLE_ID
    )

    if not booster_role:

        print(
            "❌ Booster role could not be found."
        )

        return


    # --------------------------------------------------------
    # Give Booster role
    # --------------------------------------------------------

    if booster_role not in member.roles:

        try:

            await member.add_roles(
                booster_role,
                reason="Server boost"
            )

            print(
                f"🚀 Booster role given to {member}"
            )

        except discord.Forbidden:

            print(
                "❌ Boss Bob cannot give the Booster role."
            )

            print(
                "Move Boss Bob's bot role above "
                "the Booster role."
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Discord error giving Booster role: "
                f"{error}"
            )

            return


    # --------------------------------------------------------
    # Send boost log
    # --------------------------------------------------------

    log_channel = guild.get_channel(
        BOOSTER_LOG_CHANNEL_ID
    )

    if not log_channel:
        return


    embed = discord.Embed(
        title="🚀 New Server Booster!",
        description=(
            f"**Booster:** {member.mention}\n"
            f"**User ID:** `{member.id}`\n\n"
            f"🎉 Thank you for boosting **{guild.name}**!\n"
            f"🏆 Booster role: {booster_role.mention}"
        ),
        color=discord.Color.purple()
    )

    await log_channel.send(
        embed=embed
    )


# ============================================================
#                 REGISTER BOOST LISTENER
# ============================================================

def register_booster_listener(bot):

    @bot.listen("on_member_update")
    async def boss_bob_booster_listener(
        before,
        after
    ):

        # Detect a new server boost
        if (
            before.premium_since is None
            and after.premium_since is not None
        ):

            try:

                await handle_boost(
                    after
                )

            except Exception as error:

                print(
                    f"❌ Booster system error: {error}"
                )


# ============================================================
#                         STARTUP
# ============================================================

def initialize_booster(bot):

    setup_booster(bot)

    register_booster_listener(bot)