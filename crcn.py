EMBED_COLOR = 0xF2D096
FOOTER_TEXT = "Cees Rensselaer County Nation™"
FOOTER_ICON = "https://cdn.discordapp.com/icons/1497481852678832158/c754ad9d295cc7febb5939bb51f4c78b.webp?size=1536"
STAFF_ROLE = 1503903256076877945
CIVILIAN_ROLE = 1503604680121647214

import discord
from discord import app_commands
from discord.ext import commands


@bot.tree.command(name="startup", description="Send a server launch announcement.")
@app_commands.describe(reactions="The number of reactions needed to begin the session")
async def startup(interaction: discord.Interaction, reactions: int):
    await interaction.response.defer(ephemeral=True)

    launch_embed = discord.Embed(
        title="<a:blue_heartballoons:1515000669726314578> Cees Rensselaaer County Nation - Server Launch <a:blue_heartballoons:1515000669726314578>",
        description=(
            f"<:bluedot:1515001393675632793> **{interaction.user.mention} is launching a server!** Before joining, please ensure your privacy settings are configured to \"Everyone\" so that invitations can be sent if needed. "
            f"By participating in this session, you acknowledge that you have read and agree to follow all server regulations. "
            f"A follow-up notification will be sent by the host once the session is released.\n\n"
            f"<:bluearrow:1515000950371123384> We ask that all members remain patient while staff complete setup. "
            f"A significant amount of preparation goes into each session to provide an organized and enjoyable roleplay experience for everyone involved.\n\n"
            f"<:bluearrow1:1515000970445062244> The session will begin once we reach **{reactions}+** reactions. "
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
                total = r.count - 1  # subtract the bot's reaction
                if total >= reactions:
                    break
        else:
            continue
        break

    setup_embed = discord.Embed(
        title="<a:blue_heartballoons:1515000669726314578> Cees Rensselaer County Nation - Server Setup <a:blue_heartballoons:1515000669726314578>",
        description=(
            f"<:bluedot:1515001393675632793> **{interaction.user.mention} has started preparing their session!** Early Access members will soon be able to join using the Early Entry link once it is released. "
            f"Consider boosting the server to gain access to Early Entry perks and other exclusive benefits.\n\n"
            f"<:bluearrow:1515000950371123384> Please remain patient while the host completes setup and final preparations before releasing the session to participants."
        ),
        color=EMBED_COLOR
    )
    setup_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

    await interaction.channel.send(embed=setup_embed)
