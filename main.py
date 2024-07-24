import asyncio

import cloudscraper
import discord
from discord.ext import commands, tasks

from BountyPackage import Bounty, BountyBoard, PermaBounty
from StaticSearch import get_core_data, get_country_info_v3

board = BountyBoard()
scraper = cloudscraper.create_scraper()

intents = discord.Intents.default() 
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(seconds=60)
async def my_task():
  completed_bounties = board.check_bounties(scraper)
  if len(completed_bounties) > 0:
    for bounty in completed_bounties:
      board.updateCompletedBounties()
      bounty_data = bounty['Bounty Data']
      user = bounty['User']
      img = bounty['Image']
      embed=discord.Embed(
        title=f"Bounty Completed for {bounty_data[0]}!",
        color=discord.Color.green(),
        description=f"They are now available for sale for around {bounty['Price']}",
        url=bounty_data[1]
      )
      embed.set_image(url=img)
      await user.send(embed=embed)

@bot.event
async def on_ready():
    print(f'{bot.user} is ready to herd data-goats')
    my_task.start()

@bot.command()
async def info(ctx):
  embed = discord.Embed(title="Info about Commands", color=discord.Color.green())
  embed.add_field(
    name="__!bounty: Creates a Bounty__",
    value="!bounty <Shoe Name> <Size> <Amount> <Country>", inline=False
  )
  embed.add_field(
    name="__!info: Provides Command Info__",
    value="!info", inline=False
  )
  embed.add_field(
    name="__!status: Generates the user's status__",
    value="!status", inline=False
  )
  embed.add_field(
    name="__!remove: Removes a user's bounty using the bounty ID found in status__",
    value="!remove <ID>", inline=False
  )
  embed.set_footer(text="All arguments that have spaces needs quotes around them")
  await ctx.send(content=" ", embed=embed)

@bot.command()
async def admin(ctx, *args):
  if ctx.author.name == "cyber_scholar":
    if "totalWipe" in args:
      board.totalWipe()
      embed = discord.Embed(
        title = "Wipe Complete",
        color=discord.Color.green(),
      )
    elif "bountyList" in args:
      embed = discord.Embed(
        title = "Bounty List",
        color=discord.Color.green(),
        description=str(board)
      )
    else:
      embed = discord.Embed(
        title = "Admin Panel",
        color=discord.Color.green(),
      )
      embed.add_field(
        name="__Number of Completed Bounties__",
        value=board.getCompletedBounties(),
        inline=False
      )
      embed.add_field(
        name="__Current Length of Board__",
        value=board.getLength(),
        inline=False
      )
      embed.add_field(
        name="__Total Wipe Command__",
        value="!admin totalWipe",
        inline=False
      )
      embed.add_field(
        name="__Bounty List Command__",
        value="!admin bountyList",
        inline=False
      )
    await ctx.channel.send(embed=embed)

@bot.command()
async def status(ctx):
  embed = discord.Embed(
    title = f"User Panel: {ctx.author}",
    color=discord.Color.green(),
  )
  embed.add_field(
    name="__Open Bounties__",
    value=board.get_user_bounties(ctx.author),
    inline=False
  )
  await ctx.channel.send(embed=embed)

@bot.command()
async def remove(ctx, *args):
  try:
    check = board.remove_bounty_at_index(ctx.author, int(args[0]))
    title = 'No Bounties Found'
    if check:
      title = 'Bounty Removed'
  except Exception:
    title = 'Please check your arguments and try again'
  embed = discord.Embed(
    title = title,
    color=discord.Color.green(),
  )
  await ctx.channel.send(embed=embed)

@bot.command()
async def bounty(ctx, *args, result=0):
  
    def check(message):
      return ctx.author == message.author and ctx.channel == message.channel

    if len(args) < 4:
      embed = discord.Embed(title="Not Enough Arguments", color=discord.Color.green())
      await ctx.send(embed=embed)
      return
    country, currency = get_country_info_v3(scraper, args[3])
    id, slug, value, img = get_core_data(scraper, args[0], result)
    if id is None:
      embed = discord.Embed(
        title="No more matches exist", 
        color=discord.Color.green()
      )
      await ctx.channel.send(embed=embed)
    else:
      embed = discord.Embed(title="Bounty Request", color=discord.Color.green())
      embed.add_field(
        name="Name",
        value=value,
        inline=False
      )
      embed.add_field(
        name="Size",
        value=args[1],
        inline=False
      )
      embed.add_field(
        name="Price",
        value=args[2] + " " + currency,
        inline=False
      )
      embed.add_field(
        name="Confirm?",
        value="One-time Bounty (o) or Permanent Bounty (p) or No (n) or Next (x)",
        inline=False
      )
      embed.set_image(url=img)
      await ctx.channel.send(embed=embed)
      try:
        user_message = await bot.wait_for('message', check=check, timeout=60.0)
        confirm_title = "Error"
        if user_message.content == "x":
          await bounty(ctx, *args, result=result+1)
        else: 
          if user_message.content == "o":
            temp = Bounty(
              value, args[1], float(args[2]), country, currency, ctx.author, id, slug, img
            )
            board.add_bounty(temp)
            confirm_title = "Bounty Confirmed"
          elif user_message.content == "p":
            temp = PermaBounty(
              value, args[1], float(args[2]), country, currency, ctx.author, id, slug, img
            )
            board.add_bounty(temp)
            confirm_title = "Bounty Confirmed"
          elif user_message.content == "n":
            confirm_title = "Bounty Discarded"
            #break
          await ctx.send(embed=
              discord.Embed(
                title=confirm_title, 
                color=discord.Color.green())
          )
      except asyncio.TimeoutError:
        await ctx.send(embed=
          discord.Embed(
            title="You took too long to respond!", 
            color=discord.Color.green())
        )

bot.run('MTIwNjM2MDg5MjYxMDk3MzcyNg.GPzflW.gpLKVohT8tYKnOb8ZbBnIuYsiFRZXty2ayolaY')
