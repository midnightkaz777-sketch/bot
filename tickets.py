# ============================================================
#                         BOSS BOB
#                         TICKET SYSTEM
# ============================================================

import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import asyncio


# ============================================================
#                         CONFIG
# ============================================================

SUPPORT_CHANNEL_ID = 1542609199966453790
REPORT_CHANNEL_ID = 1542622151683866635
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

    except discord.Forbidden:
        pass


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
    async def close(self, interaction, button):

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
            f"**Ticket:** `{channel.name}`\n"
            f"**Closed by:** {interaction.user.mention}",
            discord.Color.red()
        )

        await asyncio.sleep(2)

        await channel.delete()


# ============================================================
#                    SUPPORT RESULT
# ============================================================

class SupportResult(View):

    def __init__(self):

        super().__init__(timeout=None)

    async def finish(self, interaction, result):

        if not staff_or_admin(interaction.user):

            await interaction.response.send_message(
                "❌ You don't have permission to do this.",
                ephemeral=True
            )

            return

        channel = interaction.channel
        owner = None

        if channel.topic:

            try:

                if channel.topic.startswith("ticket_owner:"):

                    owner_id = int(
                        channel.topic.split(":")[1]
                    )

                    owner = interaction.guild.get_member(
                        owner_id
                    )

            except ValueError:
                pass

        if owner:

            await send_dm(
                owner,
                "🛠️ Support Ticket Update",
                f"Your support ticket was marked as **{result}**.\n\n"
                f"👤 **Handled by:** {interaction.user.mention}",
                discord.Color.green()
            )

        await send_log(
            interaction.guild,
            "🛠️ Support Ticket Completed",
            f"**User:** {owner.mention if owner else 'Unknown'}\n"
            f"**Result:** {result}\n"
            f"**Handled by:** {interaction.user.mention}\n"
            f"**Ticket:** `{channel.name}`",
            discord.Color.green()
        )

        await interaction.response.send_message(
            f"✅ Ticket marked as **{result}**.",
            view=CloseTicket()
        )

    @discord.ui.button(
        label="Completed",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def completed(self, interaction, button):

        await self.finish(interaction, "Completed")

    @discord.ui.button(
        label="Not Completed",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def not_completed(self, interaction, button):

        await self.finish(interaction, "Not Completed")

    @discord.ui.button(
        label="Still Needs Help",
        emoji="🔄",
        style=discord.ButtonStyle.secondary
    )
    async def needs_help(self, interaction, button):

        await self.finish(interaction, "Still Needs Help")


# ============================================================
#                       REPORT RESULT
# ============================================================

class ReportResult(View):

    def __init__(self):

        super().__init__(timeout=None)

    async def finish(self, interaction, result):

        if not staff_or_admin(interaction.user):

            await interaction.response.send_message(
                "❌ You don't have permission to do this.",
                ephemeral=True
            )

            return

        channel = interaction.channel
        owner = None

        if channel.topic:

            try:

                if channel.topic.startswith("ticket_owner:"):

                    owner_id = int(
                        channel.topic.split(":")[1]
                    )

                    owner = interaction.guild.get_member(
                        owner_id
                    )

            except ValueError:
                pass

        if owner:

            await send_dm(
                owner,
                "🚨 Report Update",
                f"Your report has been reviewed.\n\n"
                f"📋 **Result:** {result}\n"
                f"👤 **Reviewed by:** {interaction.user.mention}",
                discord.Color.orange()
            )

        await send_log(
            interaction.guild,
            "🚨 Report Processed",
            f"**Reporter:** {owner.mention if owner else 'Unknown'}\n"
            f"**Result:** {result}\n"
            f"**Reviewed by:** {interaction.user.mention}\n"
            f"**Ticket:** `{channel.name}`",
            discord.Color.orange()
        )

        await interaction.response.send_message(
            f"✅ Report marked as **{result}**.",
            view=CloseTicket()
        )

    @discord.ui.button(
        label="Action Taken",
        emoji="🔨",
        style=discord.ButtonStyle.danger
    )
    async def action_taken(self, interaction, button):

        await self.finish(interaction, "Action Taken")

    @discord.ui.button(
        label="No Action",
        emoji="⚪",
        style=discord.ButtonStyle.secondary
    )
    async def no_action(self, interaction, button):

        await self.finish(interaction, "Reviewed - No Action")

    @discord.ui.button(
        label="Forwarded to Admin",
        emoji="👑",
        style=discord.ButtonStyle.primary
    )
    async def forwarded(self, interaction, button):

        await self.finish(interaction, "Forwarded to Admin")


# ============================================================
#                       ROLE SELECT
# ============================================================

class RoleSelect(Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Staff",
                value="staff",
                emoji="🛡️"
            ),

            discord.SelectOption(
                label="Administrator",
                value="administrator",
                emoji="👑"
            )

        ]

        super().__init__(
            placeholder="Choose a role to request...",
            options=options,
            custom_id="boss_bob_role_select"
        )

    async def callback(self, interaction):

        guild = interaction.guild
        user = interaction.user

        if self.values[0] == "staff":

            role = guild.get_role(STAFF_ROLE_ID)
            role_name = "Staff"

        else:

            role = guild.get_role(ADMIN_ROLE_ID)
            role_name = "Administrator"

        if not role:

            await interaction.response.send_message(
                "❌ Role not found.",
                ephemeral=True
            )

            return

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

        for role_id in (STAFF_ROLE_ID, ADMIN_ROLE_ID):

            staff_role = guild.get_role(role_id)

            if staff_role:

                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

        channel = await guild.create_text_channel(
            f"role-{user.name}",
            overwrites=overwrites,
            topic=f"ticket_owner:{user.id}"
        )

        await channel.send(
            content=user.mention,
            embed=discord.Embed(
                title="👑 Role Request",
                description=(
                    f"**Requested Role:** {role_name}\n\n"
                    "Please explain why you should receive this role.\n\n"
                    "An Administrator will review your request."
                ),
                color=discord.Color.purple()
            ),
            view=RoleApproval(
                user.id,
                role.id,
                role_name
            )
        )

        await send_dm(
            user,
            "👑 Role Request Submitted",
            f"Your **{role_name}** request has been submitted.",
            discord.Color.purple()
        )

        await send_log(
            guild,
            "👑 Role Request Created",
            f"**User:** {user.mention}\n"
            f"**Role:** {role_name}\n"
            f"**Ticket:** {channel.mention}",
            discord.Color.purple()
        )

        await interaction.response.send_message(
            f"✅ Request created: {channel.mention}",
            ephemeral=True
        )


class RolePanel(View):

    def __init__(self):

        super().__init__(timeout=None)
        self.add_item(RoleSelect())


# ============================================================
#                     ROLE APPROVAL
# ============================================================

class RoleApproval(View):

    def __init__(self, user_id, role_id, role_name):

        super().__init__(timeout=None)

        self.user_id = user_id
        self.role_id = role_id
        self.role_name = role_name

    @discord.ui.button(
        label="Approve",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def approve(self, interaction, button):

        if not administrator(interaction.user):

            await interaction.response.send_message(
                "❌ Only Administrators can approve role requests.",
                ephemeral=True
            )

            return

        member = interaction.guild.get_member(self.user_id)
        role = interaction.guild.get_role(self.role_id)

        if not member or not role:

            await interaction.response.send_message(
                "❌ Member or role not found.",
                ephemeral=True
            )

            return

        try:

            await member.add_roles(role)

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Boss Bob cannot assign this role. "
                "Make sure the bot's role is above the role.",
                ephemeral=True
            )

            return

        await send_dm(
            member,
            "✅ Role Request Approved",
            f"Your **{self.role_name}** role request was approved!\n\n"
            f"👤 **Approved by:** {interaction.user.mention}",
            discord.Color.green()
        )

        await send_log(
            interaction.guild,
            "✅ Role Request Approved",
            f"**User:** {member.mention}\n"
            f"**Role:** {self.role_name}\n"
            f"**Approved by:** {interaction.user.mention}",
            discord.Color.green()
        )

        await interaction.response.send_message(
            f"✅ {member.mention} received **{self.role_name}**.",
            view=CloseTicket()
        )

    @discord.ui.button(
        label="Deny",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def deny(self, interaction, button):

        if not administrator(interaction.user):

            await interaction.response.send_message(
                "❌ Only Administrators can deny role requests.",
                ephemeral=True
            )

            return

        member = interaction.guild.get_member(self.user_id)

        if member:

            await send_dm(
                member,
                "❌ Role Request Denied",
                f"Your **{self.role_name}** request was denied.\n\n"
                f"👤 **Reviewed by:** {interaction.user.mention}",
                discord.Color.red()
            )

        await interaction.response.send_message(
            "❌ Role request denied.",
            view=CloseTicket()
        )


# ============================================================
#                    CREATE TICKETS
# ============================================================

async def create_ticket(interaction, ticket_type):

    guild = interaction.guild
    user = interaction.user

    # Prevent multiple open tickets of the same type
    prefix = ticket_type.lower()

    for channel in guild.text_channels:

        if channel.name == f"{prefix}-{user.name}":

            await interaction.response.send_message(
                f"❌ You already have a {ticket_type.lower()} ticket: "
                f"{channel.mention}",
                ephemeral=True
            )

            return

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

    for role_id in (STAFF_ROLE_ID, ADMIN_ROLE_ID):

        role = guild.get_role(role_id)

        if role:

            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

    channel = await guild.create_text_channel(
        f"{prefix}-{user.name}",
        overwrites=overwrites,
        topic=f"ticket_owner:{user.id}"
    )

    if ticket_type == "Support":

        embed = discord.Embed(
            title="🛠️ Support Ticket",
            description=(
                f"{user.mention}\n\n"
                "Please explain your problem clearly.\n\n"
                "Include:\n"
                "• What is wrong?\n"
                "• What were you trying to do?\n"
                "• What happened?\n"
                "• Screenshots if useful.\n\n"
                "A staff member will help you."
            ),
            color=discord.Color.blurple()
        )

        view = SupportResult()

    else:

        embed = discord.Embed(
            title="🚨 Report Ticket",
            description=(
                f"{user.mention}\n\n"
                "Please provide the details of your report.\n\n"
                "Include:\n"
                "• Who are you reporting?\n"
                "• What happened?\n"
                "• When did it happen?\n"
                "• Evidence/screenshots if available.\n\n"
                "Please only submit genuine reports."
            ),
            color=discord.Color.red()
        )

        view = ReportResult()

    await channel.send(
        embed=embed,
        view=view
    )

    await send_dm(
        user,
        f"{'🛠️' if ticket_type == 'Support' else '🚨'} "
        f"{ticket_type} Ticket Submitted",
        f"Your {ticket_type.lower()} ticket has been submitted.\n\n"
        f"🎫 **Ticket:** {channel.name}",
        discord.Color.blurple()
        if ticket_type == "Support"
        else discord.Color.red()
    )

    await send_log(
        guild,
        f"🎫 {ticket_type} Ticket Created",
        f"**User:** {user.mention}\n"
        f"**Ticket:** {channel.mention}",
        discord.Color.blurple()
    )

    await interaction.response.send_message(
        f"✅ Your ticket has been created: {channel.mention}",
        ephemeral=True
    )


# ============================================================
#                       PANELS
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
    async def support(self, interaction, button):

        await create_ticket(
            interaction,
            "Support"
        )


class ReportPanel(View):

    def __init__(self):

        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Report Ticket",
        emoji="🚨",
        style=discord.ButtonStyle.danger,
        custom_id="boss_bob_report"
    )
    async def report(self, interaction, button):

        await create_ticket(
            interaction,
            "Report"
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

        for guild in self.bot.guilds:

            support = guild.get_channel(SUPPORT_CHANNEL_ID)
            report = guild.get_channel(REPORT_CHANNEL_ID)
            roles = guild.get_channel(ROLE_REQUEST_CHANNEL_ID)

            if support:

                await self.send_panel_once(
                    support,
                    "🛠️ BOSS BOB SUPPORT",
                    "Need help? Click below to create a private support ticket.",
                    SupportPanel()
                )

            if report:

                await self.send_panel_once(
                    report,
                    "🚨 BOSS BOB REPORTS",
                    "Need to report someone? Click below to create a private report ticket.",
                    ReportPanel()
                )

            if roles:

                await self.send_panel_once(
                    roles,
                    "👑 BOSS BOB ROLE REQUESTS",
                    "Select Staff or Administrator to request a role.",
                    RolePanel()
                )

        self.panels_ready = True

    async def send_panel_once(
        self,
        channel,
        title,
        description,
        view
    ):

        async for message in channel.history(limit=50):

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

    @commands.Cog.listener()
    async def on_ready(self):

        self.bot.add_view(SupportPanel())
        self.bot.add_view(ReportPanel())
        self.bot.add_view(RolePanel())
        self.bot.add_view(CloseTicket())

        await self.create_panels()


async def setup(bot):

    await bot.add_cog(Ticket(bot))
