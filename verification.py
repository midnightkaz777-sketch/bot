
# ============================================================
#                 BOSS BOB - VERIFICATION
#                    CAPTCHA SYSTEM
# ============================================================

import discord
from discord.ui import View, Button, Modal, TextInput
import random
import time


# ============================================================
#                         CONFIG
# ============================================================

VERIFIED_ROLE_ID = 1542600660317638736
VERIFICATION_CHANNEL_ID = 1542592828629188608
VERIFICATION_LOG_CHANNEL_ID = 1542608047409602600


# ============================================================
#                    CAPTCHA STORAGE
# ============================================================

# user_id -> {
#     "answer": "...",
#     "created": timestamp
# }
captchas = {}

CAPTCHA_TIMEOUT = 300  # 5 minutes


# ============================================================
#                    CAPTCHA MODAL
# ============================================================

class CaptchaModal(Modal):

    def __init__(self, answer):
        super().__init__(title="🛡️ Boss Bob CAPTCHA")
        self.correct_answer = str(answer)

        self.answer_input = TextInput(
            label="Enter the CAPTCHA answer",
            placeholder="Type your answer here...",
            required=True,
            max_length=10
        )

        self.add_item(self.answer_input)

    async def on_submit(self, interaction: discord.Interaction):

        user_id = interaction.user.id

        captcha = captchas.get(user_id)

        if not captcha:
            await interaction.response.send_message(
                "❌ Your CAPTCHA expired. Click **Verify** again.",
                ephemeral=True
            )
            return

        # Expiration check
        if time.time() - captcha["created"] > CAPTCHA_TIMEOUT:

            captchas.pop(user_id, None)

            await interaction.response.send_message(
                "⌛ Your CAPTCHA expired. Click **Verify** again.",
                ephemeral=True
            )
            return

        # Check answer
        if self.answer_input.value.strip() != captcha["answer"]:

            await interaction.response.send_message(
                "❌ **Incorrect CAPTCHA.**\n"
                "Click **Verify** and try again.",
                ephemeral=True
            )
            return

        # Remove used CAPTCHA
        captchas.pop(user_id, None)

        guild = interaction.guild

        if not guild:
            await interaction.response.send_message(
                "❌ This verification can only be used inside the server.",
                ephemeral=True
            )
            return

        verified_role = guild.get_role(
            VERIFIED_ROLE_ID
        )

        if not verified_role:

            await interaction.response.send_message(
                "❌ The Verified role could not be found.",
                ephemeral=True
            )
            return

        # Already verified
        if verified_role in interaction.user.roles:

            await interaction.response.send_message(
                "✅ You are already verified!",
                ephemeral=True
            )
            return

        # Give role
        try:

            await interaction.user.add_roles(
                verified_role,
                reason="Boss Bob CAPTCHA verification"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ I can't give you the Verified role.\n\n"
                "An administrator needs to move Boss Bob's "
                "bot role above the Verified role.",
                ephemeral=True
            )
            return

        except discord.HTTPException:

            await interaction.response.send_message(
                "❌ Discord returned an error while giving you "
                "the Verified role. Please try again later.",
                ephemeral=True
            )
            return

        # Success
        await interaction.response.send_message(
            "🎉 **Verification successful!**\n\n"
            f"You received {verified_role.mention}.",
            ephemeral=True
        )

        # Log
        log_channel = guild.get_channel(
            VERIFICATION_LOG_CHANNEL_ID
        )

        if log_channel:

            embed = discord.Embed(
                title="🛡️ Verification Completed",
                description=(
                    f"**User:** {interaction.user.mention}\n"
                    f"**User ID:** `{interaction.user.id}`\n"
                    f"**Method:** CAPTCHA\n"
                    f"**Role:** {verified_role.mention}"
                ),
                color=discord.Color.green()
            )

            await log_channel.send(
                embed=embed
            )


# ============================================================
#                    VERIFICATION VIEW
# ============================================================

class VerificationView(View):

    def __init__(self):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Verify",
        emoji="🛡️",
        style=discord.ButtonStyle.success,
        custom_id="boss_bob_verify"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        guild = interaction.guild

        if not guild:
            return

        verified_role = guild.get_role(
            VERIFIED_ROLE_ID
        )

        if verified_role and verified_role in interaction.user.roles:

            await interaction.response.send_message(
                "✅ You are already verified!",
                ephemeral=True
            )
            return

        # Generate CAPTCHA
        number1 = random.randint(10, 99)
        number2 = random.randint(1, 50)

        answer = number1 + number2

        # Store CAPTCHA
        captchas[interaction.user.id] = {
            "answer": str(answer),
            "created": time.time()
        }

        modal = CaptchaModal(
            answer
        )

        # Put the actual question in the label
        modal.answer_input.label = (
            f"What is {number1} + {number2}?"
        )

        await interaction.response.send_modal(
            modal
        )


# ============================================================
#                 CREATE VERIFICATION PANEL
# ============================================================

async def send_verification_panel(bot, guild):

    channel = guild.get_channel(
        VERIFICATION_CHANNEL_ID
    )

    if not channel:

        print(
            f"❌ Verification channel not found "
            f"in {guild.name}."
        )

        return

    # Prevent duplicate panels
    async for message in channel.history(
        limit=100
    ):

        if message.author != bot.user:
            continue

        if not message.embeds:
            continue

        if (
            message.embeds[0].title
            == "🛡️ BOSS BOB VERIFICATION"
        ):

            print(
                f"✅ Verification panel already exists "
                f"in {guild.name}."
            )

            return

    # Create panel
    embed = discord.Embed(
        title="🛡️ BOSS BOB VERIFICATION",
        description=(
            "## Welcome to Kazware!\n\n"

            "Before accessing the server, you must "
            "complete a quick CAPTCHA.\n\n"

            "### 🔐 How it works\n"
            "1. Click **Verify**\n"
            "2. Solve the CAPTCHA\n"
            "3. Submit your answer\n"
            "4. Receive the **Verified** role\n\n"

            "🤖 This helps protect the server from bots."
        ),
        color=discord.Color.blurple()
    )

    await channel.send(
        embed=embed,
        view=VerificationView()
    )

    print(
        f"✅ Verification panel created "
        f"in {guild.name}."
    )


# ============================================================
#                       SETUP
# ============================================================

def setup_verification(bot):

    bot.add_view(
        VerificationView()
    )

    print(
        "🛡️ Boss Bob verification system loaded."
    )