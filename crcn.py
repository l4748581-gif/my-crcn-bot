import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

EMBED_COLOR = 0xF8F39C
FOOTER_TEXT = "Cees Rensselaer County Nation 🌟"
FOOTER_ICON = "https://cdn.discordapp.com/icons/1497481852678832158/100d02016a6cd52f74f871a3b4c95a13.webp?size=1280"
STAFF_ROLE = 1503903256076877945
CIVILIAN_ROLE = 1503604680121647214
GROUP_REQUIRED_ROLE = 1512965724329742487
HR_ROLE = 1503612022393405520
FEEDBACK_LOG_CHANNEL = 1511675078528602213
SESSION_LOG_CHANNEL = 1511679397848027207
CONCLUDE_IMAGE = "https://cdn.discordapp.com/attachments/1513671644818706472/1519545972886212658/14_20260624_223249_0013.png?ex=6a3f4477&is=6a3df2f7&hm=6749fb22b31efc39bde3f5d6c2c27c2f0abeb5592eb92c6e6dcee11239059c91&"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="?", intents=intents)

startup_messages = {}
release_times = {}
regen_times = {}
session_logs = {}

bot_status = {
    "lockdown": False,
    "revamp": False
}


async def check_bot_status(interaction: discord.Interaction) -> bool:
    if not interaction.command or interaction.command.name in ("update", "say", "dm", "conclude", "staffprofile", "cancel", "forceend"):
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


async def send_termination_embed(channel: discord.TextChannel, description: str):
    embed = discord.Embed(
        title="<:yellow_triostar:1519527667379077120> Nation, **__Conclusion__** <:yellow_triostar:1519527667379077120>",
        description=description,
        color=EMBED_COLOR
    )
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
    embed.set_image(url=CONCLUDE_IMAGE)
    await channel.send(embed=embed)


def cleanup_channel(channel_id: int):
    startup_messages.pop(channel_id, None)
    release_times.pop(channel_id, None)
    regen_times.pop(channel_id, None)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


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


@bot.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    channel_id = payload.channel_id
    if channel_id not in startup_messages:
        return

    startup_msg = startup_messages[channel_id]
    if payload.message_id != startup_msg.id:
        return

    if channel_id in release_times:
        return

    channel = bot.get_channel(channel_id)
    if channel:
        await send_termination_embed(
            channel,
            "This session has been **Terminated** automatically by the bot.\nReason: **Startup Message was Deleted.**"
        )

    cleanup_channel(channel_id)


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

        try:
            await interaction.user.send("Hey, you have reached the __required__ reactions for your session, and it is now recommended to release whenever you are ready!")
        except Exception:
            pass

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
        release_times[interaction.channel.id] = {
            "time": discord.utils.utcnow(),
            "host": interaction.user
        }

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

        host = interaction.user
        channel_id = interaction.channel.id

        async def regen_reminder():
            await asyncio.sleep(600)
            if channel_id in release_times and channel_id not in regen_times:
                try:
                    await host.send("Hey, it seems like your session link has been open for 10 minutes and its now recommended to regenerate it. If you have already regenerated it, please disregard this message and run /regen.")
                except Exception:
                    pass

        asyncio.create_task(regen_reminder())

    except Exception as e:
        print(f"[release error] {e}")
        denied_embed = discord.Embed(
            description="Command was denied.",
            color=EMBED_COLOR
        )
        denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=denied_embed, ephemeral=True)


@bot.tree.command(name="regen", description="Regenerate the session link.")
async def regen(interaction: discord.Interaction):
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

    if interaction.channel.id not in release_times:
        error_embed = discord.Embed(
            description="A release must be sent in this channel before regenerating.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        regen_times[interaction.channel.id] = discord.utils.utcnow()

        regen_embed = discord.Embed(
            title="<:yellow_triostar:1519527667379077120> Nation, **__Link Refreshed__** <:yellow_triostar:1519527667379077120>",
            description=(
                "<:yellow_dot:1519436473823269065> The current session link has been regenerated. At this time, we ask you __not__ to ping the host for re-invites and that you wait patiently for re-invites to commence."
            ),
            color=EMBED_COLOR
        )
        regen_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

        await interaction.channel.send(embed=regen_embed)

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


@bot.tree.command(name="conclude", description="Conclude a Roleplay Session!")
@app_commands.describe(notes="Any notes for the session (optional)")
async def conclude(interaction: discord.Interaction, notes: str = None):
    await interaction.response.defer(ephemeral=True)

    if not any(role.id == STAFF_ROLE for role in interaction.user.roles):
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    if interaction.channel.id not in release_times:
        error_embed = discord.Embed(
            description="A release must be sent in this channel before concluding.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        release_data = release_times[interaction.channel.id]
        start_time = release_data["time"]
        host = release_data["host"]
        end_time = discord.utils.utcnow()
        duration = end_time - start_time
        duration_minutes = duration.total_seconds() / 60
        start_str = discord.utils.format_dt(start_time, style="t")
        end_str = discord.utils.format_dt(end_time, style="t")
        notes_str = notes if notes else "No notes provided."
        logged = "Yes" if duration_minutes >= 30 else "No"

        conclude_embed = discord.Embed(
            title="<:yellow_triostar:1519527667379077120> Nation, **__Conclusion__** <:yellow_triostar:1519527667379077120>",
            description=(
                f"<:yellow_dot:1519436473823269065> {interaction.user.mention} has now **ended their session.** We hope to see you in more of our sessions! "
                f"Need to make a member report? Open a report ticket in <#1513290644683231454> providing proof. "
                f"We appreciate any feedback you leave by clicking the **button __below__**!\n\n"
                f"<:yellow_form:1519436591829881026> | Conclusion Information\n"
                f"<:yellow_arrow:1519436248920490305> Session Start Time: {start_str}\n"
                f"<:yellow_arrow:1519436248920490305> Session End Time: {end_str}\n"
                f"<:yellow_arrow:1519436248920490305> Notes: {notes_str}\n\n"
                f"**<:crcn:1515960103097077801> - __Session Cooldown of 15 minutes is now in effect.__**"
            ),
            color=EMBED_COLOR
        )
        conclude_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        conclude_embed.set_image(url=CONCLUDE_IMAGE)

        host_id = host.id
        if host_id not in session_logs:
            session_logs[host_id] = []
        session_logs[host_id].append({
            "start": start_str,
            "end": end_str,
            "duration_minutes": duration_minutes
        })

        log_channel = bot.get_channel(SESSION_LOG_CHANNEL)
        if log_channel:
            log_embed = discord.Embed(
                title="<:yellow_triostar:1519527667379077120> Nation, **__Session Log__** <:yellow_triostar:1519527667379077120>",
                description=(
                    f"**Host:** {host.mention}\n"
                    f"**Start Time:** {start_str}\n"
                    f"**End Time:** {end_str}\n"
                    f"**Were Log Entries Logged to Staff Profiles?** {logged}"
                ),
                color=EMBED_COLOR
            )
            log_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
            await log_channel.send(embed=log_embed)

        class FeedbackModal(discord.ui.Modal, title="Session Feedback"):
            rating = discord.ui.TextInput(
                label="Rate the session (1-5)",
                placeholder="Enter a number from 1 to 5",
                max_length=1
            )
            review = discord.ui.TextInput(
                label="How was the session?",
                style=discord.TextStyle.paragraph,
                placeholder="Share your thoughts...",
                max_length=1000
            )

            def __init__(self, host: discord.Member):
                super().__init__()
                self.host = host

            async def on_submit(self, modal_interaction: discord.Interaction):
                log_ch = bot.get_channel(FEEDBACK_LOG_CHANNEL)
                if log_ch:
                    log_embed = discord.Embed(
                        title="<:yellow_triostar:1519527667379077120> Nation, **__Session Feedback__** <:yellow_triostar:1519527667379077120>",
                        description=(
                            f"**Submitted By:** {modal_interaction.user.mention}\n"
                            f"**Host:** {self.host.mention}\n"
                            f"**Rating:** {self.rating.value}\n"
                            f"**Review:** {self.review.value}"
                        ),
                        color=EMBED_COLOR
                    )
                    log_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
                    await log_ch.send(embed=log_embed)

                confirm_embed = discord.Embed(
                    description="Thank you for your feedback!",
                    color=EMBED_COLOR
                )
                confirm_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
                await modal_interaction.response.send_message(embed=confirm_embed, ephemeral=True)

        class FeedbackView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Leave Feedback", style=discord.ButtonStyle.secondary)
            async def feedback_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_modal(FeedbackModal(host=host))

        await interaction.channel.send(embed=conclude_embed, view=FeedbackView())

        cleanup_channel(interaction.channel.id)

        success_embed = discord.Embed(
            description="Command was processed successfully.",
            color=EMBED_COLOR
        )
        success_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=success_embed, ephemeral=True)

    except Exception as e:
        print(f"[conclude error] {e}")
        denied_embed = discord.Embed(
            description="Command was denied.",
            color=EMBED_COLOR
        )
        denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=denied_embed, ephemeral=True)


@bot.tree.command(name="cancel", description="Cancel a Roleplay Session!")
@app_commands.describe(reason="The reason for canceling the session")
async def cancel(interaction: discord.Interaction, reason: str):
    await interaction.response.defer(ephemeral=True)

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
            description="There is no active session in this channel to cancel.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        cancel_embed = discord.Embed(
            title="<:yellow_triostar:1519527667379077120> Nation, **__Conclusion__** <:yellow_triostar:1519527667379077120>",
            description=(
                f"This session has been **Canceled** by {interaction.user.mention}.\n"
                f"Reason: **{reason}**"
            ),
            color=EMBED_COLOR
        )
        cancel_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        cancel_embed.set_image(url=CONCLUDE_IMAGE)

        await interaction.channel.send(embed=cancel_embed)

        cleanup_channel(interaction.channel.id)

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


@bot.tree.command(name="forceend", description="Force end a Roleplay Session!")
@app_commands.describe(reason="The reason for force ending the session")
async def forceend(interaction: discord.Interaction, reason: str):
    await interaction.response.defer(ephemeral=True)

    if not any(role.id == HR_ROLE for role in interaction.user.roles):
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    if interaction.channel.id not in startup_messages:
        error_embed = discord.Embed(
            description="There is no active session in this channel to force end.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        forceend_embed = discord.Embed(
            title="<:yellow_triostar:1519527667379077120> Nation, **__Conclusion__** <:yellow_triostar:1519527667379077120>",
            description=(
                f"This session has been **Force Ended** by the HR ({interaction.user.mention}).\n"
                f"Reason: **{reason}**"
            ),
            color=EMBED_COLOR
        )
        forceend_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        forceend_embed.set_image(url=CONCLUDE_IMAGE)

        await interaction.channel.send(embed=forceend_embed)

        cleanup_channel(interaction.channel.id)

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


@bot.tree.command(name="staffprofile", description="View a staff member's profile.")
@app_commands.describe(member="The staff member to view (leave empty for yourself)")
async def staffprofile(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer(ephemeral=True)

    target = member or interaction.user
    logs = session_logs.get(target.id, [])
    total_sessions = len(logs)

    profile_embed = discord.Embed(
        title="<:yellow_triostar:1519527667379077120> Nation, **__Staffing Profile__** <:yellow_triostar:1519527667379077120>",
        description=(
            f"<:yellow_dualhearts:1519436503217078382> All information about the Staff's Profile is located here.\n\n"
            f"<:yellow_arrow:1519436248920490305> Roblox User: **{target.display_name}**\n"
            f"<:yellow_arrow:1519436248920490305> User ID: **{target.id}**\n"
            f"<:yellow_arrow:1519436248920490305> Total Sessions: **{total_sessions}**"
        ),
        color=EMBED_COLOR
    )
    profile_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
    profile_embed.set_thumbnail(url=target.display_avatar.url)

    class SessionsView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="Sessions", style=discord.ButtonStyle.secondary)
        async def sessions_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if not logs:
                sessions_embed = discord.Embed(
                    description=f"**{target.display_name}** has no logged sessions.",
                    color=EMBED_COLOR
                )
                sessions_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
                await button_interaction.response.send_message(embed=sessions_embed, ephemeral=True)
                return

            desc = ""
            for i, log in enumerate(logs, 1):
                desc += f"**Session {i}**\n"
                desc += f"<:yellow_arrow:1519436248920490305> Start: {log['start']}\n"
                desc += f"<:yellow_arrow:1519436248920490305> End: {log['end']}\n\n"

            sessions_embed = discord.Embed(
                title=f"<:yellow_triostar:1519527667379077120> {target.display_name}'s Sessions <:yellow_triostar:1519527667379077120>",
                description=desc,
                color=EMBED_COLOR
            )
            sessions_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
            await button_interaction.response.send_message(embed=sessions_embed, ephemeral=True)

    await interaction.followup.send(embed=profile_embed, view=SessionsView(), ephemeral=True)


@bot.tree.command(name="say", description="Send a message as the bot.")
@app_commands.describe(
    message="The message to send",
    reply_to="The message ID to reply to (optional)"
)
async def say(interaction: discord.Interaction, message: str, reply_to: str = None):
    await interaction.response.defer(ephemeral=True)

    if not interaction.user.guild_permissions.administrator:
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        if reply_to:
            try:
                reply_msg = await interaction.channel.fetch_message(int(reply_to))
                await reply_msg.reply(message)
            except Exception:
                await interaction.channel.send(message)
        else:
            await interaction.channel.send(message)

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


@bot.tree.command(name="dm", description="DM a user or everyone in the server.")
@app_commands.describe(
    message="The message to send",
    user="The user to DM (leave empty to DM everyone)"
)
async def dm(interaction: discord.Interaction, message: str, user: discord.Member = None):
    await interaction.response.defer(ephemeral=True)

    if not interaction.user.guild_permissions.administrator:
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    try:
        dm_embed = discord.Embed(
            title=f"<:yellow_arrow:1519436248920490305> DM Sent By **{interaction.user.display_name}**",
            description=f"Message: **{message}**",
            color=EMBED_COLOR
        )
        dm_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

        if user:
            try:
                await user.send(embed=dm_embed)
                success_embed = discord.Embed(
                    description="Command was processed successfully.",
                    color=EMBED_COLOR
                )
                success_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
                await interaction.followup.send(embed=success_embed, ephemeral=True)
            except Exception:
                denied_embed = discord.Embed(
                    description=f"Could not DM {user.mention}.",
                    color=EMBED_COLOR
                )
                denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
                await interaction.followup.send(embed=denied_embed, ephemeral=True)
        else:
            failed = []
            for member in interaction.guild.members:
                if member.bot:
                    continue
                try:
                    await member.send(embed=dm_embed)
                except Exception:
                    failed.append(member.mention)

            result = "Command was processed successfully."
            if failed:
                result += f"\n\nCould not DM: {', '.join(failed)}"

            result_embed = discord.Embed(
                description=result,
                color=EMBED_COLOR
            )
            result_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
            await interaction.channel.send(embed=result_embed)

    except Exception:
        denied_embed = discord.Embed(
            description="Command was denied.",
            color=EMBED_COLOR
        )
        denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await interaction.followup.send(embed=denied_embed, ephemeral=True)


@bot.command(name="dm")
async def dm_prefix(ctx: commands.Context, target: str, *, message: str):
    if not ctx.author.guild_permissions.administrator:
        error_embed = discord.Embed(
            description="You do not have permission to use this command.",
            color=EMBED_COLOR
        )
        error_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await ctx.send(embed=error_embed)
        return

    dm_embed = discord.Embed(
        title=f"<:yellow_arrow:1519436248920490305> DM Sent By **{ctx.author.display_name}**",
        description=f"Message: **{message}**",
        color=EMBED_COLOR
    )
    dm_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)

    if target.lower() == "everyone":
        failed = []
        for member in ctx.guild.members:
            if member.bot:
                continue
            try:
                await member.send(embed=dm_embed)
            except Exception:
                failed.append(member.mention)

        result = "Command was processed successfully."
        if failed:
            result += f"\n\nCould not DM: {', '.join(failed)}"

        result_embed = discord.Embed(
            description=result,
            color=EMBED_COLOR
        )
        result_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
        await ctx.send(embed=result_embed)
    else:
        try:
            member = await commands.MemberConverter().convert(ctx, target)
            await member.send(embed=dm_embed)
            success_embed = discord.Embed(
                description="Command was processed successfully.",
                color=EMBED_COLOR
            )
            success_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
            await ctx.send(embed=success_embed)
        except Exception:
            denied_embed = discord.Embed(
                description=f"Could not DM {target}.",
                color=EMBED_COLOR
            )
            denied_embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
            await ctx.send(embed=denied_embed)


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


bot.run(os.environ["DISCORD_TOKEN"])
