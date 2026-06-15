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

# Tracks startup message per channel: {channel_id: message}
startup_messages = {}

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

        startup_messages[interaction.channel.id] = msg

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


@bot.tree.command(name="release", description="Release a Roleplay Session!")
@app_commands.describe(
    session_link="The Roblox session link",
    failrp="Fail-RP Limit",
    peacetime="Peacetime Status",
    emergency_services="Emergency Services Status"
)
@app_commands.choices(
    failrp=[
        app_commands.Choice(name="65", value="65"),
        app_commands.Choice(name="75", value="75"),
        app_commands.Choice(name="85", value="85"),
    ],
    peacetime=[
        app_commands.Choice(name="Off", value="Off"),
        app_commands.Choice(name="Normal", value="Normal"),
        app_commands.Choice(name="Strict", value="Strict"),
    ],
    emergency_services=[
        app_commands.Choice(name="Offline", value="Offline"),
        app_commands.Choice(name="Online", value="Online"),
    ]
)
async def release(
    interaction: discord.Interaction,
    session_link: str,
    failrp: str,
    peacetime: str,
    emergency_services: str
):
    await interaction.response.defer(ephemeral=True)

    # Staff check
    if not any(role.id == STAFF_ROLE for role in interaction.user.roles):
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    # Startup check
    if interaction.channel.id not in startup_messages:
        error_embed = discord.Embed(
            description="A startup must be sent in this channel before releasing.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    # Session link validation
    if not session_link.startswith("https://www.roblox.com/share"):
        error_embed = discord.Embed(
            description="Invalid session link. The link must start with `https://www.roblox.com/share`.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        release_embed = discord.Embed(
            title="<a:green_butterflies2:1515944559551451208> Cees Rensselaer County Nation — Roleplay Released <a:green_butterflies2:1515944559551451208>",
            description=(
                f"<:green_arrow2:1515944486453383219> **{interaction.user.mention} has released their session!** Before leaving the spawn area, please follow all directions provided by the host and any co-hosts. "
                f"Additionally, all Cees Rensselaer County Nation rules and regulations remain in effect for the duration of the session.\n\n"
                f"<:green_arrow2:1515944486453383219> Session links will be refreshed a few minutes after release, so be sure to join promptly. "
                f"Re-invites will be distributed every fifteen minutes, so there is no need to request a link from the hosting team.\n\n"
                f"**Session Information:**\n"
                f"<:green_arrow:1515944469986410648> Fail-Roleplay Limit: **{failrp}**\n"
                f"<:green_arrow:1515944469986410648> Peacetime Status: **{peacetime}**\n"
                f"<:green_arrow:1515944469986410648> Emergency Services: **{emergency_services}**\n\n"
                f"__<:green_bell:1515944524474486935> Any unauthorized distribution of the session link will result in an immediate ban from the server.__"
            ),
            color=EMBED_COLOR
        )
        release_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        release_embed.set_image(url="https://cdn.discordapp.com/attachments/1500685322122694892/1516169155835854969/Copy_of_Information_20260615_145449_0000.png?ex=6a31aa0f&is=6a30588f&hm=754dd69507b9dd668b259065af4a28c00e00fe80a1787a581d1d9494d93759bd")

        startup_msg = startup_messages[interaction.channel.id]

        class SessionLinkButton(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Session Link", style=discord.ButtonStyle.secondary)
            async def session_link_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                # Check if user reacted to startup message
                reacted = False
                startup_msg_fresh = await button_interaction.channel.fetch_message(startup_msg.id)
                for r in startup_msg_fresh.reactions:
                    if str(r.emoji) == "<:green_hearteyes:1515944954910871655>":
                        async for user in r.users():
                            if user.id == button_interaction.user.id:
                                reacted = True
                                break
                    if reacted:
                        break

                if reacted:
                    link_embed = discord.Embed(
                        title="Session Link",
                        description=f"Click [here]({session_link}) to join the session.",
                        color=EMBED_COLOR
                    )
                    link_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
                    await button_interaction.response.send_message(embed=link_embed, ephemeral=True)
                else:
                    startup_link = f"https://discord.com/channels/{startup_msg.guild.id}/{startup_msg.channel.id}/{startup_msg.id}"
                    no_react_embed = discord.Embed(
                        title="Reaction Required!",
                        description=f"You must react to the [Startup Message]({startup_link}) to get access to the session link.",
                        color=EMBED_COLOR
                    )
                    no_react_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
                    await button_interaction.response.send_message(embed=no_react_embed, ephemeral=True)

        await interaction.channel.send(content="@everyone", embed=release_embed, view=SessionLinkButton())

        success_embed = discord.Embed(
            description="Command was processed successfully.",
            color=EMBED_COLOR
        )
        success_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

    except Exception:
        denied_embed = discord.Embed(
            description="Command was denied.",
            color=EMBED_COLOR
        )
        denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=denied_embed, ephemeral=True)


bot.run(os.environ["DISCORD_TOKEN"])
