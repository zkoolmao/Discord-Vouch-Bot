import json, nextcord
from nextcord.ext import commands
from modules.console import Logger

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents, help_command=None)
vouches = []

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching,name="vouches"), status=nextcord.Status.idle)
    load_vouches()
    Logger.info(f"Logged in as {bot.user}")

with open("./data/config.json") as f:
    config = json.load(f)

def save_vouches():
    with open("./data/vouches.json", 'w') as file:
        json.dump(vouches, file)

def load_vouches():
    global vouches
    try:
        with open("./data/vouches.json", 'r') as file:
            vouches = json.load(file)
    except FileNotFoundError:
        Logger.error(f"Couldn't find the JSON file, starting with empty vouches.")

@bot.slash_command(name="vouch", description="Vouch for our server.")
async def vouch(ctx, user: nextcord.Member, stars: int, *, message: str):
    if ctx.channel.id != config["channelID"]:
        embed = nextcord.Embed(title="🤡 Fail!", description=f"> You can't vouch in this channel, please go to <#{config["channelID"]}>", color=nextcord.Colour.red())
        Logger.error(f"{ctx.user} tried vouching in the wrong channel.")
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    if user == ctx.user:
        embed = nextcord.Embed(title="🤡 Fail!", description="> You can't vouch for yourself.", color=nextcord.Colour.red())
        Logger.error(f"{ctx.user} tried vouching for themselves.")
        await ctx.send(embed=embed, ephemeral=True)
        return

    if user.id not in config["allowedUsers"]:
        embed = nextcord.Embed(title="🤡 Fail!", description="> You can only vouch for the owners.", color=nextcord.Colour.red())
        Logger.error(f"{ctx.user} tried vouching for a different person.")
        await ctx.send(embed=embed, ephemeral=True)
        return

    if stars < 1 or stars > 5:
        embed = nextcord.Embed(title="🤡 Fail!", description="> You can choose between 1 star and 5 stars.", color=nextcord.Colour.red())
        Logger.error(f"{ctx.user} tried choosing a different amount of stars.")
        await ctx.send(embed=embed, ephemeral=True)
        return

    vouch_id = len(vouches) + 1
    vouches.append({'id': vouch_id, 'vouched_by': ctx.user.display_name, 'vouched_user': user.display_name, 'stars': stars, 'message': message})
    save_vouches()

    embed = nextcord.Embed(title=f"Vouch #{vouch_id}", description=f"Stars: {'⭐' * stars}", color=nextcord.Colour.green())
    embed.add_field(name="Vouched by:", value=vouches[-1]['vouched_by'], inline=True)
    embed.add_field(name="User vouched:", value=vouches[-1]['vouched_user'], inline=True)
    embed.add_field(name="Message:", value=vouches[-1]['message'], inline=True)
    await ctx.send(embed=embed)
    Logger.info(f"{vouches[-1]['vouched_by']} successfully vouched for {vouches[-1]['vouched_user']} with message {vouches[-1]['message']}.")

@bot.slash_command(name="restore_vouches", description="Restore all vouches from JSON file")
async def restore_vouches(ctx):
    await ctx.send(f"> Restoring vouches to <#{config["restoreChannel"]}>, please wait.")
    channel = bot.get_channel(config["restoreChannel"])
    
    load_vouches()
    for vouch in vouches:
        embed = nextcord.Embed(title=f"Restored Vouch #{int(vouch['id'])}", description=f"Stars: {'⭐' * int(vouch['stars'])}", color=nextcord.Colour.green())
        embed.add_field(name="Vouched by:", value=vouch['vouched_by'], inline=True)
        embed.add_field(name="User vouched:", value=vouch['vouched_user'], inline=True)
        embed.add_field(name="Message:", value=vouch['message'], inline=True)
        await channel.send(embed=embed)
        Logger.info(f"Successfully restored vouch #{vouch['id']} by {vouch['vouched_by']} for {vouch['vouched_user']} with message {vouch['message']}.")

@bot.slash_command(name="total_vouches", description="Get the total count of vouches.")
async def total_vouches(ctx):
    total_count = len(vouches)
    embed = nextcord.Embed(title="Total Vouches", description=f"The total count of our vouches is: {total_count}", color=nextcord.Colour.green())
    await ctx.send(embed=embed, ephemeral=True)

bot.run(config["botToken"])