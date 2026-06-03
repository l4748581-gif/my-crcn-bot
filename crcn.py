import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# Load token from Railway environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------------- INTENTS ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # REQUIRED for welcome event

bot = commands.Bot(command_prefix="?", intents=intents)

WELCOME_CHANNEL_ID = 1510849019838988409
ROLE_LOCK_ID = 1502773113408983271

# ---------------- STARTUP STORAGE ----------------
active_startups = []

# ---------------- READY EVENT ----------------
@bot.event
async def on_ready():
    await bot.tree.sync()

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="discord.gg/crcnation"
    )

    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )

    print(f"Logged in as {bot.user}")


# ---------------- SLASH COMMAND ----------------
@bot.tree.command(name="membercount", description="Displays the server member count.")
async def membercount(interaction: discord.Interaction):

    guild = interaction.guild

    now = datetime.now(ZoneInfo("America/Chicago"))
    time_text = now.strftime("Today at %-I:%M %p")

    embed = discord.Embed(
        title="Membercount",
        description=str(guild.member_count),
        color=0xFA474A
    )

    embed.set_footer(text=time_text)

    await interaction.response.send_message(embed=embed)


# ---------------- WELCOME EVENT ----------------
@bot.event
async def on_member_join(member):

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    if channel is None:
        return

    role1 = member.guild.get_role(ROLE_LOCK_ID)
    if role1:
        await member.add_roles(role1)

    embed = discord.Embed(
        title="<a:balloons:1510771333997264936> Welcome to CRCN '26! <a:balloons:1510771333997264936>",
        description=(
            f"> Welcome, {member.mention} to "
            f"**Cees Rensselaer County Nation**.\n\n"
            f"<:dasharrow:1510776394332770374> Before partaking in sessions, please review over "
            f"<#1497725279144120450> before attending any sessions. "
            f"To become a civilian, please verify your 'ROBLOX' account using the "
            f"'BLOXLINK' Discord application within <#1503899088188342352>."
        ),
        color=0xD4FF82
    )

    embed.set_author(
        name=str(member),
        icon_url=member.display_avatar.url
    )

    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1507921885436969091/1510846001701851136/Fredoka_8.png"
    )

    now = datetime.now(ZoneInfo("America/Chicago"))
    embed.set_footer(text=f"Today at {now.strftime('%I:%M %p').lstrip('0')}")

    await channel.send(content=f"{member.mention}", embed=embed)


# ---------------- SOON COMMAND ----------------
@bot.command(name="soon")
@commands.has_permissions(administrator=True)
async def soon(ctx):

    try:
        await ctx.message.delete()
    except:
        pass

    embed = discord.Embed(color=0xD4FF82)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1507921885436969091/1510973193433780234/Server_1.png")

    await ctx.send(embed=embed)


@soon.error
async def soon_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        try:
            await ctx.message.delete()
        except:
            pass

        msg = await ctx.send("❌ No permission.")
        await msg.delete(delay=5)


# ---------------- PD SOON COMMAND ----------------
@bot.command(name="pdsoon")
@commands.has_permissions(administrator=True)
async def pdsoon(ctx):

    try:
        await ctx.message.delete()
    except:
        pass

    embed = discord.Embed(color=0xD4FF82)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1507980572889186394/1510978702496763954/Server_2.png")

    await ctx.send(embed=embed)


@pdsoon.error
async def pdsoon_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        try:
            await ctx.message.delete()
        except:
            pass

        msg = await ctx.send("❌ No permission.")
        await msg.delete(delay=5)


# ---------------- STARTUP COMMAND ----------------
@bot.tree.command(name="startup", description="Start a roleplay session.")
@app_commands.describe(
    reactions="Reactions required before setup starts.",
    image="Optional image for the startup embed."
)
async def startup(interaction: discord.Interaction, reactions: int, image: discord.Attachment = None):

    role_id = ROLE_LOCK_ID

    if not any(r.id == role_id for r in interaction.user.roles):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    if len(active_startups) >= 2:
        await interaction.response.send_message(
            "❌ Only 2 Startups are allowed at once. End one before starting another.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="<a:beatinghearts:1510771374359318639> Cees Rensselaer County Nation — Roleplay Startup!",
        color=0xD4FF82
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1502420648327118978/1510966611463639080/Screenshot_2026-05-07_160747.png")

    msg = await interaction.channel.send(
        content=f"<@&{ROLE_LOCK_ID}>",
        embed=embed
    )

    await msg.add_reaction(bot.get_emoji(1510771397771792394))

    active_startups.append({
        "host_id": interaction.user.id,
        "message_id": msg.id,
        "required": reactions,
        "state": "startup"
    })

    await interaction.response.send_message("✅ Startup created.", ephemeral=True)


class SessionLinkView(discord.ui.View):
    def __init__(self, startup_message, release_link):
        super().__init__(timeout=None)
        self.startup_message = startup_message
        self.release_link = release_link

    @discord.ui.button(label="Session Link", style=discord.ButtonStyle.secondary)
    async def session_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        reacted = False

        for reaction in self.startup_message.reactions:
            users = [u async for u in reaction.users()]
            if interaction.user in users:
                reacted = True
                break

        if not reacted:
            await interaction.response.send_message(
                f"You have not reacted to the startup message. [React here.]({self.startup_message.jump_url})",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Click [here]({self.release_link}) to join the session.",
            ephemeral=True
        )


@bot.tree.command(name="release", description="Release a roleplay session.")
@app_commands.describe(
    link="Session join link",
    frp_input="Fail Roleplay Speed",
    pt_input="Peacetime Status",
    leo_input="LEO Status",
    hc_input="House Claiming"
)
async def release(
    interaction: discord.Interaction,
    link: str,
    frp_input: str,
    pt_input: str,
    leo_input: str,
    hc_input: str
):

    role_id = ROLE_LOCK_ID

    if not any(r.id == role_id for r in interaction.user.roles):
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    await interaction.response.send_message("✅ Session released.", ephemeral=True)

# ---------------- RUN ----------------
bot.run(TOKEN)
