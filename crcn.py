import os
import discord
from discord import app_commands
from discord.ext import commands

EMBED_COLOR = 0x5f8575
FOOTER_TEXT = "Cees Rensselaer County Nation™"
FOOTER_ICON = "https://cdn.discordapp.com/icons/1497481852678832158/ab48dbd460758c87d47fb069cbfbc3e1.webp?size=1280"
STAFF_ROLE = 1503903256076877945
CIVILIAN_ROLE = 1503604680121647214

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="startup", description="Start a Roleplay Session!")
@app_commands.describe(reactions="The number of reactions needed to begin the session")
async def startup(interaction: discord.Interaction, reactions: int):
    await interaction.response.defer(ephemeral=True)

    try:
        launch_embed = discord.Embed(
            title="<a:green_butterflies2:1515944559551451208> Cees Rensselaaer County Nation - Roleplay Startup <a:green_butterflies2:1515944559551451208>",
            description=(
                f"<:green_dot:1515944734017978409> **{interaction.user.mention} is hosting a session!** Before joining, please ensure your privacy settings are configured to \"Everyone\" so that invitations can be sent if needed. "
                f"By participating in this session, you acknowledge that you have read and agree to follow all server regulations. "
                f"A follow-up notification will be sent by the host once the session is released.\n\n"
                f"<:green_arrow2:1515944486453383219> We ask that all members remain patient while staff complete setup. "
                f"A significant amount of preparation goes into each session to provide an organized and enjoyable roleplay experience for everyone involved.\n\n"
                f"<:green_reply1:1516105094129647668> The session will begin once we reach **{reactions}+** reactions. "
                f"Upon meeting this requirement, early access information will be released and the host will continue with releasing."
            ),
            color=EMBED_COLOR
        )
        launch_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        launch_embed.set_image(url="https://cdn.discordapp.com/attachments/1500685322122694892/1516156503130902528/Copy_of_Information_20260615_140429_0000.png?ex=6a319e47&is=6a304cc7&hm=f1ad2a2240ffc8d5331eb905f212b0d23eb2549e261b446c91fe50a2fc859553")

        msg = await interaction.channel.send(
            content=f"<@&{CIVILIAN_ROLE}>",
            embed=launch_embed
        )

        await msg.add_reaction("<:green_hearteyes:1515944954910871655>")

        success_embed = discord.Embed(
            description="Command was processed successfully.",
            color=EMBED_COLOR
        )
        success_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

        def check(reaction, user):
            return (
                reaction.message.id == msg.id
                and str(reaction.emoji) == "<:green_hearteyes:1515944954910871655>"
                and not user.bot
            )

        while True:
            reaction, user = await bot.wait_for("reaction_add", check=check)
            msg = await interaction.channel.fetch_message(msg.id)
            for r in msg.reactions:
                if str(r.emoji) == "<:green_hearteyes:1515944954910871655>":
                    total = r.count - 1
                    if total >= reactions:
                        break
            else:
                continue
            break

        setup_embed = discord.Embed(
            title="<a:green_butterflies2:1515944559551451208> Cees Rensselaer County Nation - Roleplay Setup <a:green_butterflies2:1515944559551451208>",
            description=(
                f"<:green_dot:1515944734017978409> **{interaction.user.mention} has started preparing their session!** Early Access members will soon be able to join using the Early Entry link once it is released. "
                f"Consider boosting the server to gain access to Early Entry perks and other exclusive benefits.\n\n"
                f"<:green_reply1:1516105094129647668> Please remain patient while the host completes setup and final preparations before releasing the session to participants."
            ),
            color=EMBED_COLOR
        )
        setup_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        setup_embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.channel.send(embed=setup_embed)

    except Exception:
        denied_embed = discord.Embed(
            description="Command was denied.",
            color=EMBED_COLOR
        )
        denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=denied_embed, ephemeral=True)

bot.run(os.environ["DISCORD_TOKEN"])
