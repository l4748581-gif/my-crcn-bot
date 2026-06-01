import discord
from discord.ext import commands
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

WELCOME_CHANNEL_ID = 1510849019838988409  # <-- CHANGE THIS


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


@bot.event
async def on_member_join(member):

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

    if channel is None:
        return

    # ---------------- GIVE ROLES ----------------
    role1 = member.guild.get_role(1503604680121647214)
   
    if role1:
        await member.add_roles(role1)

    # ---------------- EMBED ----------------
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
        url="https://cdn.discordapp.com/attachments/1507921885436969091/1510846001701851136/Fredoka_8.png?ex=6a1e4c7c&is=6a1cfafc&hm=9a364808d4e21155f2bc572640ec2910c47c134eb4c1a442730884ac03a1c21e"
    )

    now = datetime.now(ZoneInfo("America/Chicago"))

    embed.set_footer(
        text=f"Today at {now.strftime('%I:%M %p').lstrip('0')}"
    )

    # ---------------- SEND WELCOME (WITH PING) ----------------
    await channel.send(
        content=f"{member.mention}",
        embed=embed
    )

@bot.command(name="soon")
@commands.has_permissions(administrator=True)
async def soon(ctx):

    try:
        await ctx.message.delete()
    except:
        pass

    embed = discord.Embed(
        color=0xD4FF82
    )

    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1507921885436969091/1510973193433780234/Server_1.png?ex=6a1ec2f1&is=6a1d7171&hm=1dd30edec008b1ffbf3e2139de86f3baff25b66a85a24f3c8d6d1cc88a5d1b08"
    )

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

# ---------------- RUN BOT ----------------
bot.run(TOKEN)
