from random import choice
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Greedy
from config import BOT_TOKEN, BOT_PREFIX
import functions
from functions import log

# variables bl0ck
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# when connected bl0ck
@bot.event
async def on_ready():    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="на тебя!"))

    print('{0:#^60}'.format(''))
    print('{0:*^60}'.format(f'Logged in as: {bot.user.name}'))
    print('{0:*^60}'.format(bot.user.id))

    print('{0:#^60}'.format('USER STATS:'))
    print('{0:*^60}'.format('all users: {0}'.format(len(bot.users))))
    print('{0:*^60}'.format('online: {0}'.format(len(functions.get_online_members(bot)))))

    print('{0:#^60}'.format('SYNCING SLASH COMMANDS:'))
    # await bot.tree.sync() # sync local, use to clean
    for guild in bot.guilds:
        bot.tree.clear_commands(guild=guild)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print('{0:*^60}'.format(f"{guild}: {[i.name for i in synced]}")) # print name of commands on every guild
    print('{0:*^60}'.format('Done!'))
    print('{0:#^60}'.format(''))

# on_message bl0ck
@bot.event
async def on_message(message):
    log(f'{message.guild} - #{message.channel} - @{message.author}: "{functions.replace_mention(message)}"', type='message')
    return await bot.process_commands(message)

# sending all online users
@bot.hybrid_command(name='check', guild_ids=[537267521565229056])
async def check(ctx):
    '''Имена всех, кто онлайн'''
    log(f'check by {ctx.author}', type='debug')
    await ctx.reply(f'```bash\n{functions.get_online_members(bot)}```')

# randomizing winner of roulette
@bot.hybrid_command(name='roulette')
@app_commands.describe(members='Участники')
async def _roulette(ctx, members: Greedy[discord.Member]):
    '''Выбирает случайного победителя'''
    log(f'roulette by {ctx.author}: {members}', type='debug')
    if not len(members):
        return await ctx.reply("Передан пустой список")

    winner = choice(members)
    await ctx.reply(f'{winner.mention} Победил!')

# work
@bot.hybrid_command(name='work')
async def _work(ctx):
    '''Заработок nedocoins'''
    log(f'work {ctx.author}', type='debug')
    await functions.work(ctx)

# BlackJack
@bot.hybrid_command(name="bj")
@app_commands.describe(bet='Ставка nedocoins')
async def _bj(ctx, bet: int):
    '''Блекджек'''
    log(f'blackjack {ctx.author}: {bet}', type='debug')
    await functions.bj(ctx, bet)

# move people to voice channel
@bot.hybrid_command(name='move')
@app_commands.describe(members="Кого переместить")
async def _move(ctx, members: Greedy[discord.Member]):
    '''Переместить участников в свободный голосовой канал
    Нужны права доступа на перемещение участников
    '''
    log(f'move {ctx.author}: {members}', type='debug')
    await functions.move(ctx, members)

if __name__ == '__main__':
    bot.run(BOT_TOKEN)
