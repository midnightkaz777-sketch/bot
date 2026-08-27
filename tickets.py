# ============================================================
#                         BOSS BOB
#                    COMPLETE TICKET SYSTEM
# ============================================================

import asyncio
import discord
from discord.ext import commands
from discord.ui import View, Button, Select


# ============================================================
#                         CONFIG
# ============================================================

SUPPORT_CHANNEL_ID = 1542609199966453790

# Report panel removed.
# Reports are handled through Support.

ROLE_REQUEST_CHANNEL_ID = 1542609148909322282

TICKETS_LOG_CHANNEL_ID = 1542608080116785172

STAFF_ROLE_ID = 1542600297048711168
ADMIN_ROLE_ID = 1542600054819393597


# ============================================================
#                         HELPERS
# ============================================================

def staff_or_admin(member):

    if member.guild_permissions.administrator:
        return True

    return any(
        role.id in (STAFF_ROLE_ID, ADMIN_ROLE_ID)
        for role in member.roles
    )


def administrator(member):

    if member.guild_permissions.administrator:
        return True

    return any(
        role.id == ADMIN_ROLE_ID
        for role in member.roles
    )


async def send_log(guild, title, description, color):

    channel = guild.get_channel(TICKETS_LOG_CHANNEL_ID)

    if not channel:
        print(
            f"⚠️ Logs channel not found: "
            f"{TICKETS_LOG_CHANNEL_ID}"
        )
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    await channel.send(embed=embed)


async def send_dm(member, title, description, color):

    try:

        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        await member.send(embed=embed)

        return True

    except discord.Forbidden:

        print(
            f"⚠️ Could not DM {member}."
        )

        return False

    except Exception as error:

        print(
            f"⚠️ DM error: {error}"
        )

        return False


# ============================================================
#                       CLOSE TICKET
# ============================================================

class CloseTicket(View):

    def __init__(self):

        super().__init__(timeout=None)


    @discord.ui.button(
        label="Close Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="boss_bob_close_ticket"
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not staff_or_admin(interaction.user):

            await interaction.response.send_message(
                "❌ You don't have permission to close this ticket.",
                ephemeral=True
            )

            return

        channel = interaction.channel

        await interaction.response.send_message(
            "🔒 Closing ticket...",
            ephemeral=True
        )

        await send_log(
            interaction.guild,
            "🔒 Ticket Closed",
            (
                f"**Ticket:** `{channel.name}`\n"
                f"**Closed by:** {interaction.user.mention}"
            ),
            discord.Color.red()
        )

        await asyncio.sleep(2)

        try:

            await channel.delete(
                reason=f"Ticket closed by {interaction.user}"
            )

        except discord.NotFound:
            pass

        except discord.Forbidden:

            print(
                f"❌ Cannot delete ticket channel "
                f"{channel.name}"
            )


# ============================================================
#                    SUPPORT TICKET
# ============================================================

class SupportView(View):

    def __init__(self):

        super().__init__(timeout=None)


    @discord.ui.button(
        label="Close Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="boss_bob_support_close"
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not staff_or_admin(interaction.user):

            await interaction.response.send_message(
                "❌ You don't have permission to close this ticket.",
                ephemeral=True
            )

            return

        channel = interaction.channel

        owner = None

        if channel.topic:

            try:

                if channel.topic.startswith(
                    "ticket_owner:"
                ):

                    owner_id = int(
                        channel.topic.split(":")[1]
                    )

                    owner = interaction.guild.get_member(
                        owner_id
                    )

            except (ValueError, IndexError):

                pass

        if owner:

            await send_dm(
                owner,
                "🛠️ Support Ticket Closed",
                (
                    "Your support ticket has been closed.\n\n"
                    f"**Closed by:** "
                    f"{interaction.user.mention}"
                ),
                discord.Color.red()
            )

        await send_log(
            interaction.guild,
            "🛠️ Support Ticket Closed",
            (
                f"**User:** "
                f"{owner.mention if owner else 'Unknown'}\n"
                f"**Closed by:** "
                f"{interaction.user.mention}\n"
                f"**Ticket:** `{channel.name}`"
            ),
            discord.Color.red()
        )

        await interaction.response.send_message(
            "🔒 Closing ticket...",
            ephemeral=True
        )

        await asyncio.sleep(2)

        try:

            await channel.delete(
                reason="Support ticket closed"
            )

        except discord.Forbidden:

            pass


# ============================================================
#                    ROLE REQUEST SELECT
# ============================================================

class RoleSelect(Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Staff",
                value="staff",
                emoji="🛡️",
                description="Request the Staff role"
            ),

            discord.SelectOption(
                label="Administrator",
                value="administrator",
                emoji="👑",
                description="Request the Administrator role"
            )

        ]

        super().__init__(
            placeholder="Choose a role to request...",
            options=options,
            custom_id="boss_bob_role_select"
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild
        user = interaction.user

        # ----------------------------------------------------
        # Determine role
        # ----------------------------------------------------

        if self.values[0] == "staff":

            role = guild.get_role(
                STAFF_ROLE_ID
            )

            role_name = "Staff"

        else:

            role = guild.get_role(
                ADMIN_ROLE_ID
            )

            role_name = "Administrator"


        if not role:

            await interaction.response.send_message(
                f"❌ The **{role_name}** role could not be found.",
                ephemeral=True
            )

            return


        # ----------------------------------------------------
        # Prevent duplicate role requests
        # ----------------------------------------------------

        for channel in guild.text_channels:

            if (
                channel.topic
                == f"role_request:{user.id}"
            ):

                await interaction.response.send_message(
                    (
                        "❌ You already have an open "
                        "role request: "
                        f"{channel.mention}"
                    ),
                    ephemeral=True
                )

                return


        # ----------------------------------------------------
        # Private ticket permissions
        # ----------------------------------------------------

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
        }


        # Staff can see it
        staff_role = guild.get_role(
            STAFF_ROLE_ID
        )

        if staff_role:

            overwrites[staff_role] = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            )


        # Admin can see it
        admin_role = guild.get_role(
            ADMIN_ROLE_ID
        )

        if admin_role:

            overwrites[admin_role] = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            )


        # ----------------------------------------------------
        # Create request ticket
        # ----------------------------------------------------

        channel = await guild.create_text_channel(
            f"role-{user.name}",
            overwrites=overwrites,
            topic=f"role_request:{user.id}"
        )


        # ----------------------------------------------------
        # Private ticket message
        # ----------------------------------------------------

        embed = discord.Embed(
            title="👑 Role Request",
            description=(
                f"{user.mention}\n\n"
                f"**Requested Role:** {role_name}\n\n"
                "Please explain why you should receive "
                "this role.\n\n"
                "An administrator will review your "
                "request.\n\n"
                "⚠️ Approval is handled in the "
                "staff logs channel."
            ),
            color=discord.Color.purple()
        )

        await channel.send(
            content=user.mention,
            embed=embed,
            view=RoleTicketView()
        )


        # ----------------------------------------------------
        # DM requester
        # ----------------------------------------------------

        await send_dm(
            user,
            "📨 Role Request Submitted",
            (
                f"Your request for the **{role_name}** "
                "role has been submitted.\n\n"
                "An administrator will review it."
            ),
            discord.Color.purple()
        )


        # ----------------------------------------------------
        # Logs channel
        # ----------------------------------------------------

        logs_channel = guild.get_channel(
            TICKETS_LOG_CHANNEL_ID
        )


        if not logs_channel:

            print(
                "❌ Logs channel not found!"
            )

        else:

            log_embed = discord.Embed(
                title="👑 NEW ROLE REQUEST",
                description=(
                    f"**User:** {user.mention}\n"
                    f"**User ID:** `{user.id}`\n"
                    f"**Requested Role:** `{role_name}`\n"
                    f"**Ticket:** {channel.mention}\n\n"
                    "An Administrator must review "
                    "this request."
                ),
                color=discord.Color.purple()
            )

            log_embed.set_footer(
                text="Boss Bob • Role Request System"
            )

            await logs_channel.send(
                embed=log_embed,
                view=RoleApproval(
                    user_id=user.id,
                    role_id=role.id,
                    role_name=role_name,
                    ticket_channel_id=channel.id
                )
            )


        # ----------------------------------------------------
        # Log
        # ----------------------------------------------------

        await send_log(
            guild,
            "👑 Role Request Created",
            (
                f"**User:** {user.mention}\n"
                f"**Role:** {role_name}\n"
                f"**Ticket:** {channel.mention}"
            ),
            discord.Color.purple()
        )


        # ----------------------------------------------------
        # User confirmation
        # ----------------------------------------------------

        await interaction.response.send_message(
            (
                f"✅ Your **{role_name}** request has "
                "been submitted!\n\n"
                "An administrator will review it."
            ),
            ephemeral=True
        )


# ============================================================
#                    ROLE TICKET VIEW
# ============================================================

class RoleTicketView(View):

    def __init__(self):

        super().__init__(timeout=None)


    @discord.ui.button(
        label="Close Request",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="boss_bob_role_close"
    )
    async def close_request(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not staff_or_admin(interaction.user):

            await interaction.response.send_message(
                "❌ You don't have permission to close this request.",
                ephemeral=True
            )

            return

        channel = interaction.channel

        await interaction.response.send_message(
            "🔒 Closing request...",
            ephemeral=True
        )

        await asyncio.sleep(1)

        try:

            await channel.delete(
                reason="Role request manually closed"
            )

        except discord.Forbidden:

            pass


# ============================================================
#                    ROLE REQUEST PANEL
# ============================================================

class RolePanel(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            RoleSelect()
        )


# ============================================================
#                    ROLE APPROVAL SYSTEM
# ============================================================

class RoleApproval(View):

    def __init__(
        self,
        user_id,
        role_id,
        role_name,
        ticket_channel_id
    ):

        super().__init__(timeout=None)

        self.user_id = user_id
        self.role_id = role_id
        self.role_name = role_name
        self.ticket_channel_id = ticket_channel_id


    # ========================================================
    #                         APPROVE
    # ========================================================

    @discord.ui.button(
        label="Approve",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="boss_bob_role_approve"
    )
    async def approve(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not administrator(interaction.user):

            await interaction.response.send_message(
                "❌ Only Administrators can approve role requests.",
                ephemeral=True
            )

            return

        guild = interaction.guild

        member = guild.get_member(
            self.user_id
        )

        role = guild.get_role(
            self.role_id
        )


        if not member:

            await interaction.response.send_message(
                "❌ The requested member could not be found.",
                ephemeral=True
            )

            return


        if not role:

            await interaction.response.send_message(
                "❌ The requested role could not be found.",
                ephemeral=True
            )

            return


        # ----------------------------------------------------
        # Check role hierarchy
        # ----------------------------------------------------

        if role >= guild.me.top_role:

            await interaction.response.send_message(
                (
                    "❌ I cannot give this role because "
                    "my bot role is not above it."
                ),
                ephemeral=True
            )

            return


        # ----------------------------------------------------
        # Give role
        # ----------------------------------------------------

        try:

            await member.add_roles(
                role,
                reason=(
                    f"Role request approved by "
                    f"{interaction.user}"
                )
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                (
                    "❌ Discord denied the role change.\n"
                    "Make sure my bot's role is above "
                    "the requested role."
                ),
                ephemeral=True
            )

            return


        # ----------------------------------------------------
        # DM requester
        # ----------------------------------------------------

        await send_dm(
            member,
            "✅ Role Request Approved",
            (
                f"Your **{self.role_name}** role request "
                "has been approved!\n\n"
                f"**Approved by:** "
                f"{interaction.user.mention}\n\n"
                "The role has been added to your account."
            ),
            discord.Color.green()
        )


        # ----------------------------------------------------
        # Update logs
        # ----------------------------------------------------

        embed = discord.Embed(
            title="✅ ROLE REQUEST APPROVED",
            description=(
                f"**User:** {member.mention}\n"
                f"**Role:** `{self.role_name}`\n"
                f"**Approved by:** "
                f"{interaction.user.mention}\n\n"
                "The role has been assigned."
            ),
            color=discord.Color.green()
        )

        embed.set_footer(
            text="Boss Bob • Role Request System"
        )


        for item in self.children:

            item.disabled = True


        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


        # ----------------------------------------------------
        # Close request ticket
        # ----------------------------------------------------

        ticket_channel = guild.get_channel(
            self.ticket_channel_id
        )

        if ticket_channel:

            try:

                await ticket_channel.send(
                    embed=discord.Embed(
                        title="✅ Request Approved",
                        description=(
                            f"Your **{self.role_name}** request "
                            "was approved.\n\n"
                            "This ticket will now close."
                        ),
                        color=discord.Color.green()
                    )
                )

                await asyncio.sleep(2)

                await ticket_channel.delete(
                    reason="Role request approved"
                )

            except discord.Forbidden:

                pass


    # ========================================================
    #                           DENY
    # ========================================================

    @discord.ui.button(
        label="Deny",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="boss_bob_role_deny"
    )
    async def deny(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not administrator(interaction.user):

            await interaction.response.send_message(
                "❌ Only Administrators can deny role requests.",
                ephemeral=True
            )

            return


        guild = interaction.guild

        member = guild.get_member(
            self.user_id
        )


        # ----------------------------------------------------
        # DM requester
        # ----------------------------------------------------

        if member:

            await send_dm(
                member,
                "❌ Role Request Denied",
                (
                    f"Your **{self.role_name}** role request "
                    "has been denied.\n\n"
                    f"**Reviewed by:** "
                    f"{interaction.user.mention}"
                ),
                discord.Color.red()
            )


        # ----------------------------------------------------
        # Update logs
        # ----------------------------------------------------

        embed = discord.Embed(
            title="❌ ROLE REQUEST DENIED",
            description=(
                f"**User:** "
                f"{member.mention if member else self.user_id}\n"
                f"**Role:** `{self.role_name}`\n"
                f"**Denied by:** "
                f"{interaction.user.mention}\n\n"
                "The role was not assigned."
            ),
            color=discord.Color.red()
        )

        embed.set_footer(
            text="Boss Bob • Role Request System"
        )


        for item in self.children:

            item.disabled = True


        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


        # ----------------------------------------------------
        # Close request ticket
        # ----------------------------------------------------

        ticket_channel = guild.get_channel(
            self.ticket_channel_id
        )

        if ticket_channel:

            try:

                await ticket_channel.send(
                    embed=discord.Embed(
                        title="❌ Request Denied",
                        description=(
                            f"Your **{self.role_name}** request "
                            "was denied.\n\n"
                            "This ticket will now close."
                        ),
                        color=discord.Color.red()
                    )
                )

                await asyncio.sleep(2)

                await ticket_channel.delete(
                    reason="Role request denied"
                )

            except discord.Forbidden:

                pass


# ============================================================
#                    CREATE SUPPORT TICKET
# ============================================================

async def create_support_ticket(
    interaction: discord.Interaction
):

    guild = interaction.guild
    user = interaction.user


    # --------------------------------------------------------
    # Prevent duplicate ticket
    # --------------------------------------------------------

    for channel in guild.text_channels:

        if channel.topic == f"ticket_owner:{user.id}":

            await interaction.response.send_message(
                (
                    "❌ You already have an open "
                    f"ticket: {channel.mention}"
                ),
                ephemeral=True
            )

            return


    # --------------------------------------------------------
    # Permissions
    # --------------------------------------------------------

    overwrites = {

        guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

        user:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
    }


    for role_id in (
        STAFF_ROLE_ID,
        ADMIN_ROLE_ID
    ):

        role = guild.get_role(
            role_id
        )

        if role:

            overwrites[role] = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            )


    # --------------------------------------------------------
    # Create channel
    # --------------------------------------------------------

    channel = await guild.create_text_channel(
        f"support-{user.name}",
        overwrites=overwrites,
        topic=f"ticket_owner:{user.id}"
    )


    # --------------------------------------------------------
    # Ticket message
    # --------------------------------------------------------

    embed = discord.Embed(
        title="🛠️ BOSS BOB SUPPORT",
        description=(
            f"Welcome {user.mention}!\n\n"
            "Please explain your problem clearly.\n\n"
            "**Include:**\n"
            "• What is wrong?\n"
            "• What were you trying to do?\n"
            "• What happened?\n"
            "• Screenshots if useful.\n\n"
            "A staff member will help you."
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(
        text="Boss Bob • Support System"
    )


    await channel.send(
        content=user.mention,
        embed=embed,
        view=SupportView()
    )


    # --------------------------------------------------------
    # DM user
    # --------------------------------------------------------

    await send_dm(
        user,
        "🛠️ Support Ticket Created",
        (
            "Your support ticket has been created.\n\n"
            f"🎫 **Ticket:** {channel.name}"
        ),
        discord.Color.blurple()
    )


    # --------------------------------------------------------
    # Logs
    # --------------------------------------------------------

    await send_log(
        guild,
        "🎫 Support Ticket Created",
        (
            f"**User:** {user.mention}\n"
            f"**Ticket:** {channel.mention}"
        ),
        discord.Color.blurple()
    )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    await interaction.response.send_message(
        f"✅ Your support ticket has been created: {channel.mention}",
        ephemeral=True
    )


# ============================================================
#                    SUPPORT PANEL
# ============================================================

class SupportPanel(View):

    def __init__(self):

        super().__init__(timeout=None)


    @discord.ui.button(
        label="Create Support Ticket",
        emoji="🛠️",
        style=discord.ButtonStyle.primary,
        custom_id="boss_bob_support"
    )
    async def support(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await create_support_ticket(
            interaction
        )


# ============================================================
#                    TICKET COG
# ============================================================

class Ticket(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.panels_ready = False


    async def create_panels(self):

        if self.panels_ready:
            return


        print("🎫 Creating ticket panels...")


        for guild in self.bot.guilds:

            # ------------------------------------------------
            # Support panel
            # ------------------------------------------------

            support = guild.get_channel(
                SUPPORT_CHANNEL_ID
            )

            if support:

                await self.send_panel_once(
                    support,
                    "🛠️ BOSS BOB SUPPORT",
                    (
                        "Need help?\n\n"
                        "Click the button below to create "
                        "a private support ticket.\n\n"
                        "Reports should also be submitted "
                        "through Support."
                    ),
                    SupportPanel()
                )

                print(
                    f"✅ Support panel ready in "
                    f"{guild.name}"
                )

            else:

                print(
                    f"❌ Support channel not found in "
                    f"{guild.name}: "
                    f"{SUPPORT_CHANNEL_ID}"
                )


            # ------------------------------------------------
            # Role request panel
            # ------------------------------------------------

            roles = guild.get_channel(
                ROLE_REQUEST_CHANNEL_ID
            )

            if roles:

                await self.send_panel_once(
                    roles,
                    "👑 BOSS BOB ROLE REQUESTS",
                    (
                        "Need a Staff or Administrator role?\n\n"
                        "Select the role you want to request "
                        "below.\n\n"
                        "Your request will be reviewed by "
                        "an Administrator."
                    ),
                    RolePanel()
                )

                print(
                    f"✅ Role panel ready in "
                    f"{guild.name}"
                )

            else:

                print(
                    f"❌ Role request channel not found "
                    f"in {guild.name}: "
                    f"{ROLE_REQUEST_CHANNEL_ID}"
                )


        self.panels_ready = True

        print("🎫 Ticket panels finished.")


    async def send_panel_once(
        self,
        channel,
        title,
        description,
        view
    ):

        try:

            async for message in channel.history(
                limit=50
            ):

                if (
                    message.author == self.bot.user
                    and message.embeds
                    and message.embeds[0].title == title
                ):

                    return


            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blurple()
            )


            await channel.send(
                embed=embed,
                view=view
            )

        except discord.Forbidden:

            print(
                f"❌ Missing permissions in "
                f"#{channel.name}"
            )

        except Exception as error:

            print(
                f"❌ Could not create panel in "
                f"#{channel.name}: {error}"
            )


    @commands.Cog.listener()
    async def on_ready(self):

        # ----------------------------------------------------
        # Persistent views
        # ----------------------------------------------------

        self.bot.add_view(
            SupportPanel()
        )

        self.bot.add_view(
            RolePanel()
        )

        self.bot.add_view(
            RoleTicketView()
        )

        self.bot.add_view(
            SupportView()
        )

        # ----------------------------------------------------
        # Create panels
        # ----------------------------------------------------

        await self.create_panels()


# ============================================================
#                         SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Ticket(bot)
    )
