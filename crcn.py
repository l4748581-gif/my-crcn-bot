import discord
import os
from discord.ext import commands
from discord import app_commands

import sqlite3
import random
import asyncio
import time

TOKEN = os.getenv("DISCORD_TOKEN")

EMBED_COLOR = 0x89e6ff
STAFF_ROLE_ID = 1503903256076877945
STARTUP_TRACKER = {}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="-",
    intents=intents
)

db = sqlite3.connect(
    "economy.db"
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    cash INTEGER DEFAULT 1000,
    bank INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cooldowns (
    user_id INTEGER,
    command TEXT,
    last_used INTEGER,
    PRIMARY KEY(user_id, command)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    item TEXT,
    amount INTEGER DEFAULT 1,
    PRIMARY KEY(user_id, item)
)
""")

db.commit()

def ensure_user(user_id):

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = ?",
        (user_id,)
    )

    if cursor.fetchone() is None:

        cursor.execute(
            """
            INSERT INTO users
            (user_id, cash, bank)
            VALUES (?, ?, ?)
            """,
            (user_id, 1000, 0)
        )

        db.commit()


def get_cash(user_id):

    ensure_user(user_id)

    cursor.execute(
        "SELECT cash FROM users WHERE user_id = ?",
        (user_id,)
    )

    return cursor.fetchone()[0]


def get_bank(user_id):

    ensure_user(user_id)

    cursor.execute(
        "SELECT bank FROM users WHERE user_id = ?",
        (user_id,)
    )

    return cursor.fetchone()[0]


def add_cash(user_id, amount):

    ensure_user(user_id)

    cursor.execute(
        """
        UPDATE users
        SET cash = cash + ?
        WHERE user_id = ?
        """,
        (amount, user_id)
    )

    db.commit()


def remove_cash(user_id, amount):

    ensure_user(user_id)

    cursor.execute(
        """
        UPDATE users
        SET cash = MAX(cash - ?, 0)
        WHERE user_id = ?
        """,
        (amount, user_id)
    )

    db.commit()

COOLDOWN_HOURS = 24


def format_time(seconds):

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    return f"{hours}h {minutes}m"


def check_cooldown(user_id, command):

    cursor.execute(
        """
        SELECT last_used
        FROM cooldowns
        WHERE user_id = ?
        AND command = ?
        """,
        (user_id, command)
    )

    result = cursor.fetchone()

    if result is None:
        return False, 0

    last_used = result[0]

    now = int(time.time())

    remaining = (
        COOLDOWN_HOURS * 3600
    ) - (now - last_used)

    if remaining > 0:
        return True, remaining

    return False, 0


def set_cooldown(user_id, command):

    cursor.execute(
        """
        INSERT OR REPLACE INTO cooldowns
        (user_id, command, last_used)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            command,
            int(time.time())
        )
    )

    db.commit()

SHOP_ITEMS = {
    "Image Permissions": 2500,
    "Laptop": 5000,
    "Banned Vehicle Exempt": 10000,
    "Lottery Ticket": 500,
    "Luxury Watch": 15000
}

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands")
    print(f"Logged in as {bot.user}")

@bot.tree.command(
    name="balance",
    description="View your balance."
)
async def balance(
    interaction: discord.Interaction
):

    ensure_user(
        interaction.user.id
    )

    cash = get_cash(
        interaction.user.id
    )

    bank = get_bank(
        interaction.user.id
    )

    embed = discord.Embed(
        title="Account Balance",
        color=EMBED_COLOR
    )

    embed.add_field(
        name="Cash",
        value=f"${cash:,}",
        inline=True
    )

    embed.add_field(
        name="Bank",
        value=f"${bank:,}",
        inline=True
    )

    embed.add_field(
        name="Net Worth",
        value=f"${cash + bank:,}",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="dailyeconomy",
    description="Claim your daily reward."
)
async def dailyeconomy(
    interaction: discord.Interaction
):

    ensure_user(
        interaction.user.id
    )

    cooldown, remaining = check_cooldown(
        interaction.user.id,
        "daily"
    )

    if cooldown:

        embed = discord.Embed(
            title="Daily Cooldown",
            description=(
                f"You already claimed your daily reward.\n\n"
                f"Try again in **{format_time(remaining)}**."
            ),
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    reward = random.randint(
        750,
        1500
    )

    add_cash(
        interaction.user.id,
        reward
    )

    set_cooldown(
        interaction.user.id,
        "daily"
    )

    embed = discord.Embed(
        title="Daily Economy",
        description=(
            f"You claimed your daily economy "
            f"and received **${reward:,}**."
        ),
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="earn",
    description="Work a job and earn money."
)
async def earn(
    interaction: discord.Interaction
):

    ensure_user(
        interaction.user.id
    )

    cooldown, remaining = check_cooldown(
        interaction.user.id,
        "earn"
    )

    if cooldown:

        embed = discord.Embed(
            title="Work Cooldown",
            description=(
                f"You already worked today.\n\n"
                f"Try again in **{format_time(remaining)}**."
            ),
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    jobs = [
        "waitress",
        "police officer",
        "mechanic",
        "cashier",
        "construction worker",
        "delivery driver",
        "tow truck operator",
        "taxi driver",
        "store clerk",
        "firefighter"
    ]

    job = random.choice(
        jobs
    )

    earned = random.randint(
        200,
        1000
    )

    add_cash(
        interaction.user.id,
        earned
    )

    set_cooldown(
        interaction.user.id,
        "earn"
    )

    embed = discord.Embed(
        title="Earned Money",
        description=(
            f"You worked hard as a "
            f"**{job}** and earned "
            f"**${earned:,}**."
        ),
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="withdraw",
    description="Withdraw money from your bank."
)
@app_commands.describe(
    amount="Amount to withdraw"
)
async def withdraw(
    interaction: discord.Interaction,
    amount: int
):

    ensure_user(
        interaction.user.id
    )

    if amount <= 0:

        return await interaction.response.send_message(
            "Amount must be greater than 0.",
            ephemeral=True
        )

    bank = get_bank(
        interaction.user.id
    )

    if amount > bank:

        embed = discord.Embed(
            title="Withdrawal Failed",
            description="You don't have that much money in your bank account.",
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    cursor.execute(
        """
        UPDATE users
        SET bank = bank - ?
        WHERE user_id = ?
        """,
        (
            amount,
            interaction.user.id
        )
    )

    add_cash(
        interaction.user.id,
        amount
    )

    db.commit()

    embed = discord.Embed(
        title="Withdrawal Complete",
        description=f"You withdrew **${amount:,}** from your bank account.",
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="pay",
    description="Pay another user."
)
@app_commands.describe(
    user="User to pay",
    amount="Amount to send"
)
async def pay(
    interaction: discord.Interaction,
    user: discord.Member,
    amount: int
):

    ensure_user(
        interaction.user.id
    )

    ensure_user(
        user.id
    )

    if user.bot:

        return await interaction.response.send_message(
            "You cannot pay bots.",
            ephemeral=True
        )

    if user.id == interaction.user.id:

        return await interaction.response.send_message(
            "You cannot pay yourself.",
            ephemeral=True
        )

    if amount <= 0:

        return await interaction.response.send_message(
            "Amount must be greater than 0.",
            ephemeral=True
        )

    if get_cash(
        interaction.user.id
    ) < amount:

        embed = discord.Embed(
            title="Payment Failed",
            description="You don't have enough cash.",
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    remove_cash(
        interaction.user.id,
        amount
    )

    add_cash(
        user.id,
        amount
    )

    embed = discord.Embed(
        title="Payment Sent",
        description=(
            f"You sent **${amount:,}** "
            f"to {user.mention}."
        ),
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="shop",
    description="View the shop."
)
async def shop(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="Economy Shop",
        color=EMBED_COLOR
    )

    description = ""

    for item, price in SHOP_ITEMS.items():

        description += (
            f"**{item}** — "
            f"${price:,}\n"
        )

    embed.description = description

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="inventory",
    description="View your inventory."
)
async def inventory(
    interaction: discord.Interaction
):

    ensure_user(
        interaction.user.id
    )

    cursor.execute(
        """
        SELECT item, amount
        FROM inventory
        WHERE user_id = ?
        """,
        (
            interaction.user.id,
        )
    )

    items = cursor.fetchall()

    if not items:

        text = (
            "Your inventory is empty."
        )

    else:

        text = "\n".join(
            [
                f"• **{item}** x{amount}"
                for item, amount in items
            ]
        )

    embed = discord.Embed(
        title="Inventory",
        description=text,
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="buy",
    description="Purchase an item from the shop."
)
@app_commands.describe(
    item="Item to purchase"
)
async def buy(
    interaction: discord.Interaction,
    item: str
):

    ensure_user(
        interaction.user.id
    )

    item = item.title()

    if item not in SHOP_ITEMS:

        embed = discord.Embed(
            title="❌ Item Not Found",
            description="That item does not exist in the shop.",
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    price = SHOP_ITEMS[item]

    if get_cash(
        interaction.user.id
    ) < price:

        embed = discord.Embed(
            title="Not Enough Cash",
            description=(
                f"You need **${price:,}** "
                f"to buy **{item}**."
            ),
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    remove_cash(
        interaction.user.id,
        price
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO inventory
        (user_id, item, amount)
        VALUES (?, ?, 0)
        """,
        (
            interaction.user.id,
            item
        )
    )

    cursor.execute(
        """
        UPDATE inventory
        SET amount = amount + 1
        WHERE user_id = ?
        AND item = ?
        """,
        (
            interaction.user.id,
            item
        )
    )

    db.commit()

    embed = discord.Embed(
        title="Purchase Complete",
        description=(
            f"You bought **{item}** "
            f"for **${price:,}**."
        ),
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="rob",
    description="Attempt to rob another user."
)
@app_commands.describe(
    user="Victim"
)
async def rob(
    interaction: discord.Interaction,
    user: discord.Member
):

    ensure_user(
        interaction.user.id
    )

    ensure_user(
        user.id
    )

    if user.bot:

        return await interaction.response.send_message(
            "You cannot rob bots.",
            ephemeral=True
        )

    if user.id == interaction.user.id:

        return await interaction.response.send_message(
            "You cannot rob yourself.",
            ephemeral=True
        )

    cooldown, remaining = check_cooldown(
        interaction.user.id,
        "rob"
    )

    if cooldown:

        embed = discord.Embed(
            title="Robbery Cooldown",
            description=(
                f"You already attempted a robbery today.\n\n"
                f"Try again in **{format_time(remaining)}**."
            ),
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    success = random.randint(
        1,
        100
    ) <= 45

    if success:

        victim_cash = get_cash(
            user.id
        )

        if victim_cash <= 0:

            embed = discord.Embed(
                title="Robbery Failed",
                description=(
                    f"{user.mention} "
                    f"has no cash to steal."
                ),
                color=EMBED_COLOR
            )

            set_cooldown(
                interaction.user.id,
                "rob"
            )

            return await interaction.response.send_message(
                embed=embed
            )

        stolen = min(
            victim_cash,
            random.randint(
                250,
                1500
            )
        )

        remove_cash(
            user.id,
            stolen
        )

        add_cash(
            interaction.user.id,
            stolen
        )

        embed = discord.Embed(
            title="Robbery Successful",
            description=(
                f"You robbed {user.mention} "
                f"and stole **${stolen:,}**."
            ),
            color=EMBED_COLOR
        )

    else:

        fine = random.randint(
            250,
            1000
        )

        remove_cash(
            interaction.user.id,
            fine
        )

        embed = discord.Embed(
            title="Robbery Failed",
            description=(
                f"You were caught by the police.\n\n"
                f"You paid a fine of "
                f"**${fine:,}**."
            ),
            color=EMBED_COLOR
        )

    set_cooldown(
        interaction.user.id,
        "rob"
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="crime",
    description="Commit a crime."
)
async def crime(
    interaction: discord.Interaction
):

    ensure_user(
        interaction.user.id
    )

    cooldown, remaining = check_cooldown(
        interaction.user.id,
        "crime"
    )

    if cooldown:

        embed = discord.Embed(
            title="Crime Cooldown",
            description=(
                f"You already committed a crime today.\n\n"
                f"Try again in **{format_time(remaining)}**."
            ),
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    crimes = [
        "sold stolen electronics",
        "stole a luxury vehicle",
        "ran an ATM scam",
        "robbed a convenience store",
        "sold counterfeit goods",
        "smuggled illegal cargo"
    ]

    crime_name = random.choice(
        crimes
    )

    success = random.randint(
        1,
        100
    ) <= 55

    if success:

        payout = random.randint(
            500,
            3000
        )

        add_cash(
            interaction.user.id,
            payout
        )

        embed = discord.Embed(
            title="Crime Successful",
            description=(
                f"You successfully "
                f"**{crime_name}** "
                f"and earned "
                f"**${payout:,}**."
            ),
            color=EMBED_COLOR
        )

    else:

        fine = random.randint(
            500,
            2000
        )

        remove_cash(
            interaction.user.id,
            fine
        )

        embed = discord.Embed(
            title="Crime Failed",
            description=(
                f"You were caught by police.\n\n"
                f"You paid a fine of "
                f"**${fine:,}**."
            ),
            color=EMBED_COLOR
        )

    set_cooldown(
        interaction.user.id,
        "crime"
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="coinflip",
    description="Flip a coin and gamble your money."
)
@app_commands.describe(
    amount="Amount to bet"
)
async def coinflip(
    interaction: discord.Interaction,
    amount: int
):

    ensure_user(
        interaction.user.id
    )

    if amount <= 0:

        return await interaction.response.send_message(
            "Bet must be greater than 0.",
            ephemeral=True
        )

    if get_cash(
        interaction.user.id
    ) < amount:

        embed = discord.Embed(
            title="Not Enough Cash",
            description="You don't have enough cash for that bet.",
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    result = random.choice(
        ["Heads", "Tails"]
    )

    win = random.choice(
        [True, False]
    )

    if win:

        add_cash(
            interaction.user.id,
            amount
        )

        outcome = (
            f"The coin landed on **{result}**.\n\n"
            f"You won **${amount:,}**."
        )

        title = "Coin Flip Victory"

    else:

        remove_cash(
            interaction.user.id,
            amount
        )

        outcome = (
            f"The coin landed on **{result}**.\n\n"
            f"You lost **${amount:,}**."
        )

        title = "Coin Flip Defeat"

    embed = discord.Embed(
        title=title,
        description=outcome,
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.tree.command(
    name="blackjack",
    description="Play blackjack."
)
@app_commands.describe(
    amount="Amount to bet"
)
async def blackjack(
    interaction: discord.Interaction,
    amount: int
):

    ensure_user(
        interaction.user.id
    )

    if amount <= 0:

        return await interaction.response.send_message(
            "Bet must be greater than 0.",
            ephemeral=True
        )

    if get_cash(
        interaction.user.id
    ) < amount:

        embed = discord.Embed(
            title="Not Enough Cash",
            description="You don't have enough cash for that bet.",
            color=EMBED_COLOR
        )

        return await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    player = random.randint(
        15,
        21
    )

    dealer = random.randint(
        15,
        21
    )

    if player > dealer:

        add_cash(
            interaction.user.id,
            amount
        )

        result = (
            f"**Your Hand:** {player}\n"
            f"**Dealer Hand:** {dealer}\n\n"
            f"You won **${amount:,}**."
        )

        title = "Blackjack Victory"

    elif dealer > player:

        remove_cash(
            interaction.user.id,
            amount
        )

        result = (
            f"**Your Hand:** {player}\n"
            f"**Dealer Hand:** {dealer}\n\n"
            f"You lost **${amount:,}**."
        )

        title = "Blackjack Defeat"

    else:

        result = (
            f"**Your Hand:** {player}\n"
            f"**Dealer Hand:** {dealer}\n\n"
            f"It's a tie. Your bet was returned."
        )

        title = "Push"

    embed = discord.Embed(
        title=title,
        description=result,
        color=EMBED_COLOR
    )

    await interaction.response.send_message(
        embed=embed
    )

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):

    if amount <= 0:
        return await ctx.send(
            "Please provide a number greater than 0.",
            delete_after=5
        )

    deleted = 0

    async for message in ctx.channel.history(limit=500):

        if deleted >= amount:
            break

        if message.pinned:
            continue

        try:
            await message.delete()
            deleted += 1
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

    embed = discord.Embed(
        title="Messages Purged",
        description=f"Deleted **{deleted}** messages.",
        color=0xd4ff82
    )

    confirmation = await ctx.send(embed=embed)

    await asyncio.sleep(5)
    await confirmation.delete()

@bot.tree.command(
    name="startup",
    description="Start a server startup."
)
@app_commands.describe(
    required_reactions="Reaction goal required to continue setup"
)
async def startup(
    interaction: discord.Interaction,
    required_reactions: int
):

    role = interaction.guild.get_role(
        STAFF_ROLE_ID
    )

    if role not in interaction.user.roles:
        return await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="Cees Rensselaer County Nation — __Server Startup:__",
        description=(
            f"<:bluedot:1512943229216227449> {interaction.user.mention} is hosting a server! Before joining, please ensure your privacy settings are configured to \"__Everyone__\" so that invitations can be delivered if needed. By participating in this server, you acknowledge that you have read and agree to follow all server regulations. A follow-up notification will be sent by the host once the session is setup.\n\n"

            "<:bluearrow:1512942871492427917> We ask that all members remain patient while staff complete setup. A significant amount of preparation goes into each session to provide an organized and enjoyable roleplay experience for everyone involved.\n\n"

            f"<:bluearrow1:1512942887569195058> The session will begin once we reach {required_reactions} reactions. Upon meeting this requirement, early access information will be released and the host will continue with server release."
        ),
        color=EMBED_COLOR
    )

    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1512970170363150457/1512997548867059712/CR_2.gif?ex=6a262045&is=6a24cec5&hm=a8cc5941d7d59064cb969ab66ce451738f13f3fd49646cbdc2684aba89df841e"
    )

    embed.set_footer(
        text="Cees Rensselaer County Nation 💎",
        icon_url="https://cdn.discordapp.com/icons/1497481852678832158/fbd6f1b95a93c5efdb00e21365bda256.webp?size=1536"
    )

    await interaction.response.send_message(
    content="@everyone",
    embed=embed,
    allowed_mentions=discord.AllowedMentions(everyone=True)
)

message = await interaction.original_response()

# Ephemeral confirmation embed
confirm_embed = discord.Embed(
    description="Startup Sent.",
    color=EMBED_COLOR
)

await interaction.followup.send(
    embed=confirm_embed,
    ephemeral=True
)

    emoji = bot.get_emoji(
        1512942726499274752
    )

    if emoji:
        await message.add_reaction(
            emoji
        )

    STARTUP_TRACKER[message.id] = {
        "required": required_reactions,
        "host": interaction.user.id
    }


@bot.event
async def on_raw_reaction_add(payload):

    if payload.user_id == bot.user.id:
        return

    data = STARTUP_TRACKER.get(
        payload.message_id
    )

    if data is None:
        return

    channel = bot.get_channel(
        payload.channel_id
    )

    if channel is None:
        try:
            channel = await bot.fetch_channel(
                payload.channel_id
            )
        except:
            return

    try:
        message = await channel.fetch_message(
            payload.message_id
        )
    except:
        return

    reaction_count = 0

    for reaction in message.reactions:

        emoji_id = getattr(
            reaction.emoji,
            "id",
            None
        )

        if emoji_id == 1512942726499274752:

            reaction_count = max(
                0,
                reaction.count - 1
            )

            break

    if reaction_count < data["required"]:
        return

    host = message.guild.get_member(
        data["host"]
    )

    if host is None:
        try:
            host = await message.guild.fetch_member(
                data["host"]
            )
        except:
            return

    embed = discord.Embed(
        title="Cees Rensselaer County Nation — __Server Setup:__",
        description=(
            f"<:bluedot:1512943229216227449> {host.mention} has now begun preparing their session! Early Access members will soon be able to join using the Early Entry link once it is released. Consider boosting the server to gain access to Early Entry perks and other exclusive benefits.\n\n"

            "<:bluearrow1:1512942887569195058> Please remain patient while the host completes setup and final preparations before opening the session to participants."
        ),
        color=EMBED_COLOR
    )

    embed.set_thumbnail(
        url=host.display_avatar.url
    )

    embed.set_footer(
        text="Cees Rensselaer County Nation 💎",
        icon_url="https://cdn.discordapp.com/icons/1497481852678832158/fbd6f1b95a93c5efdb00e21365bda256.webp?size=1536"
    )

    await channel.send(
        embed=embed
    )

    STARTUP_TRACKER.pop(
        payload.message_id,
        None
    )

bot.run(TOKEN)
