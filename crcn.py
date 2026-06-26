import os
import discord
from discord import app_commands
from discord.ext import commands

EMBED_COLOR = 0xF8F39C
FOOTER_TEXT = "Cees Rensselaer County Nation 🌟"
FOOTER_ICON = "https://cdn.discordapp.com/icons/1497481852678832158/100d02016a6cd52f74f871a3b4c95a13.webp?size=1280"
STAFF_ROLE = 1503903256076877945
CIVILIAN_ROLE = 1503604680121647214
GROUP_REQUIRED_ROLE = 1512965724329742487

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

startup_messages = {}

bot_status = {
    "lockdown": False,
    "revamp": False
}


async def check_bot_status(interaction: discord.Interaction) -> bool:
    if not interaction.command or interaction.command.name == "update":
        return True
    if bot_status["lockdown"]:
        error_embed = discord.Embed(
            title="Error",
            description="<:yellow_bell:1519436277907193976> The bot is currently on **__Lockdown__** and you may __not__ use any commands at this time.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return False
    if bot_status["revamp"]:
        error_embed = discord.Embed(
            title="Error",
            description="<:yellow_bell:1519436277907193976> Commands Disabled, **__Revamp Ongoing.__**",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return False
    return True


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="startup", description="Start a Roleplay Session!")
@app_commands.describe(reactions="The number of reactions needed to begin the session")
async def startup(interaction: discord.Interaction, reactions: int):
    await interaction.response.defer(ephemeral=True)

    if not await check_bot_status(interaction):
        return

    if not any(role.id == STAFF_ROLE for role in interaction.user.roles):
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        launch_embed = discord.Embed(
            title="<:yellow_triostar:1519527667379077120> Nation, **__Session Starting__** <:yellow_triostar:1519527667379077120>",
            description=(
                f"<:yellow_dot:1519436473823269065> {interaction.user.mention} is **hosting a roleplay Session!** Prior to joining, we highly encourage you to familiarize yourself with our **Server Regulations** and **Banned Vehicles List** both listed within the <#1512946599821574296> channel. "
                f"Ensure you have the correct privacy settings so the host can send manual invites if necessary. You will receive another notification when the session is released.\n\n"
                f"In order for Early Access to be unlocked, this message must reach **__{reactions}__** reactions."
            ),
            color=EMBED_COLOR
        )
        launch_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        launch_embed.set_image(url="https://cdn.discordapp.com/attachments/1513671644818706472/1519545970613026927/11_20260624_223249_0010.png?ex=6a3e9bb7&is=6a3d4a37&hm=6bd5a23543dd110306b669dc30c4568613ec9d41a143a96e7daaf03e2f980d03&")

        msg = await interaction.channel.send(
            content=f"<@&{CIVILIAN_ROLE}>",
            embed=launch_embed
        )

        startup_messages[interaction.channel.id] = msg

        await msg.add_reaction("🌟")

        success_embed = discord.Embed(
            description="Command was processed successfully.",
            color=EMBED_COLOR
        )
        success_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

        def check(reaction, user):
            return (
                reaction.message.id == msg.id
                and str(reaction.emoji) == "🌟"
                and not user.bot
            )

        while True:
            reaction, user = await bot.wait_for("reaction_add", check=check)
            msg = await interaction.channel.fetch_message(msg.id)
            for r in msg.reactions:
                if str(r.emoji) == "🌟":
                    total = r.count - 1
                    if total >= reactions:
                        break
            else:
                continue
            break

        setup_embed = discord.Embed(
            title="<:yellow_triostar:1519527667379077120> Nation, **__Session Setup__** <:yellow_triostar:1519527667379077120>",
            description=(
                f"<:yellow_dot:1519436473823269065> {interaction.user.mention} is now **setting up** their Roleplay Session. During this time, please do __not__ ping the host or it will lead to moderation actions."
            ),
            color=EMBED_COLOR
        )
        setup_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        setup_embed.set_image(url="https://cdn.discordapp.com/attachments/1513671644818706472/1519546154633793657/Roleplay_20260624_223345_0000.png?ex=6a3e9be3&is=6a3d4a63&hm=6e2884a290e9588175d8becb7cb3f1d022c3cca426c8bed419097048d88e72cf")
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
    failrp="Fail Roleplay Speeds",
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

    if not await check_bot_status(interaction):
        return

    if not any(role.id == STAFF_ROLE for role in interaction.user.roles):
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    if interaction.channel.id not in startup_messages:
        error_embed = discord.Embed(
            description="A startup must be sent in this channel before releasing.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    if not session_link.startswith(("https://roblox.com", "https://www.roblox.com")):
        error_embed = discord.Embed(
            description="Invalid session link. The link must start with `https://roblox.com`.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        release_embed = discord.Embed(
            title="<:yellow_triostar:1519527667379077120> Nation, **__Release__** <:yellow_triostar:1519527667379077120>",
            description=(
                f"<:yellow_dot:1519436473823269065> {interaction.user.mention} has **released their session!** Prior to leaving the dealership, ensure all of your vehicles are registered in the bot input channel, if your vehicles are not registered, you could get cited by Law Enforcement. Read all the information below to get a better understanding of the Session.\n\n"
                f"<:yellow_form:1519436591829881026> | Session Information\n"
                f"<:yellow_arrow:1519436248920490305> Fail Roleplay Speeds: **{failrp}**\n"
                f"<:yellow_arrow:1519436248920490305> Peacetime Status: **{peacetime}**\n"
                f"<:yellow_arrow:1519436248920490305> Emergency Services: **{emergency_services}**"
            ),
            color=EMBED_COLOR
        )
        release_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        release_embed.set_image(url="https://cdn.discordapp.com/attachments/1513671644818706472/1519545971183194163/12_20260624_223249_0011.png?ex=6a3e9bb7&is=6a3d4a37&hm=02ca764c966e246176a3c4fb988c5dfd0e8591331a9c25950bf1d0feecc1c0c9&")

        startup_msg = startup_messages[interaction.channel.id]

        class SessionLinkButton(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Session Link", style=discord.ButtonStyle.secondary)
            async def session_link_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                reacted = False
                startup_msg_fresh = await button_interaction.channel.fetch_message(startup_msg.id)
                for r in startup_msg_fresh.reactions:
                    if str(r.emoji) == "🌟":
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

    except Exception as e:
        print(f"[release error] {e}")
        denied_embed = discord.Embed(
            description="Command was denied.",
            color=EMBED_COLOR
        )
        denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=denied_embed, ephemeral=True)


@bot.tree.command(name="update", description="Manage bot lockdown and revamp mode.")
async def update(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        return

    class UpdateView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.update_buttons()

        def update_buttons(self):
            self.clear_items()

            lockdown_label = "Disable Lockdown" if bot_status["lockdown"] else "Enable Lockdown"
            lockdown_style = discord.ButtonStyle.danger if bot_status["lockdown"] else discord.ButtonStyle.secondary
            lockdown_btn = discord.ui.Button(label=lockdown_label, style=lockdown_style)
            lockdown_btn.callback = self.lockdown_callback
            self.add_item(lockdown_btn)

            revamp_label = "Disable Revamp Mode" if bot_status["revamp"] else "Enable Revamp Mode"
            revamp_style = discord.ButtonStyle.danger if bot_status["revamp"] else discord.ButtonStyle.secondary
            revamp_btn = discord.ui.Button(label=revamp_label, style=revamp_style)
            revamp_btn.callback = self.revamp_callback
            self.add_item(revamp_btn)

        async def lockdown_callback(self, button_interaction: discord.Interaction):
            if bot_status["lockdown"]:
                bot_status["lockdown"] = False
                desc = "<:yellow_bell:1519436277907193976> Lockdown Disabled."
            else:
                bot_status["lockdown"] = True
                bot_status["revamp"] = False
                desc = "<:yellow_bell:1519436277907193976> Lockdown Enabled."

            self.update_buttons()
            status_embed = discord.Embed(description=desc, color=EMBED_COLOR)
            status_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
            await button_interaction.response.edit_message(embed=status_embed, view=self)

        async def revamp_callback(self, button_interaction: discord.Interaction):
            if bot_status["revamp"]:
                bot_status["revamp"] = False
                desc = "<:yellow_bell:1519436277907193976> Revamp Mode Disabled."
            else:
                bot_status["revamp"] = True
                bot_status["lockdown"] = False
                desc = "<:yellow_bell:1519436277907193976> Revamp Mode Enabled."

            self.update_buttons()
            status_embed = discord.Embed(description=desc, color=EMBED_COLOR)
            status_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
            await button_interaction.response.edit_message(embed=status_embed, view=self)

    initial_embed = discord.Embed(
        description="Use the buttons below to manage bot status.",
        color=EMBED_COLOR
    )
    initial_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
    await interaction.response.send_message(embed=initial_embed, view=UpdateView(), ephemeral=True)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if "banned" in message.content.lower():
        banned_embed = discord.Embed(
            title="**__<:yellow_bell:1519436277907193976>  Banned From a Session? <:yellow_bell:1519436277907193976>__**",
            description=(
                "<:yellow_arrow:1519436248920490305> If you were banned from a Session, you'll need to fill out a **Ban Appeal**. "
                "The ban appeal is in the button below. If you were not banned, kindly disregard this message."
            ),
            color=EMBED_COLOR
        )
        banned_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

        class BanAppealView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(discord.ui.Button(
                    label="Ban Appeal Link",
                    style=discord.ButtonStyle.link,
                    url="https://docs.google.com/forms/d/e/1FAIpQLSdxRa3lO57ssTE5qgX912UxMAJVQm2uXGUThJoECSOa4c86CA/viewform?usp=sharing&ouid=114820152348130489079"
                ))

        await message.channel.send(embed=banned_embed, view=BanAppealView())

    await bot.process_commands(message)


bot.run(os.environ["DISCORD_TOKEN"])
