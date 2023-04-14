import discord
import time
from blackjack import *
from config import pay, cooldown, multiplier, new_worker_balance

def get_online_members(bot):
    gen = bot.get_all_members()
    members = [next(gen) for i in range(len(bot.users))]
    online_members = [member.name for member in members if member.status != discord.Status.offline]
    return online_members

def replace_mention(message):
    msg = message.content
    for member in message.mentions:
        msg = msg.replace(member.mention, f'@{member}')
    return msg

def log(message: str, *, type: str):
    '''
    [MESSAGE] 2023/Mar/30 12:32:44 PIZZA #bot-commands @RIPtide#4497 ".bj 1 2 3"
    [DEBUG] 2023/Mar/30 12:31:57 work RIPtide#4497
    [DEBUG] 2023/Mar/30 12:32:44 Blackjack RIPtide#4497 Dealer Q
    '''
    date = time.strftime("%Y/%b/%d %H:%M:%S")
    print(f'[{type.upper()}] {date} {message}')
    

async def move(ctx, members):
    print(members)
    if not ctx.guild.get_role(1087990528265699349) in ctx.author.roles and not ctx.author.guild_permissions.move_members:
        return await ctx.reply(f'Недостаточно прав на исполнение команды, нужна роль "nedobot move" или права на перемещение участников')
    for member in members:
        if member.voice == None: # подключен ли к голосовому каналу
            return await ctx.reply("Невозможно переместить участника, который не находится в голосовом канале")
    channel = None
    for voice_channel in ctx.guild.voice_channels:
        if len(voice_channel.members) == 0:
            channel = voice_channel; break
        
    [await member.move_to(channel) for member in members]
    await ctx.reply('Done!', ephemeral=True)

async def bj(ctx, bet):
    if ctx.author.id in bjplayers and bjplayers[ctx.author.id].status == 'playing':
        return await ctx.reply(f'{ctx.author.mention}, Ты уже в игре!')
    # if not len(ctx.message.content.split()) > 1:
    #     return await message.channel.send(f'{message.author.mention}, введите ставку nedocoins')
    # if not message.content.split()[1].isdigit():
    #     return await message.channel.send(f'{message.author.mention}, введите ставку nedocoins')
    if not is_enought(ctx.author.id, bet):
        return await ctx.reply(f'{ctx.author.mention}, недостаточно nedocoins')
    
    bjplayers[ctx.author.id] = blackjack(ctx.author, bet)
    async def button_hit_callback(interaction):
        if ctx.author.id != interaction.user.id:
            return await interaction.response.defer()
        if interaction.user.id not in bjplayers:
            return await interaction.response.defer()
        if bjplayers[interaction.user.id].status != 'playing':
            return await interaction.response.defer()
        bjplayers[interaction.user.id].hit()
        msg = blackjack.maininfo(bjplayers[interaction.user.id])
        if bjplayers[interaction.user.id].status == 'playing': # рисовать кнопки, если после hit партия не завершена
            return await interaction.response.send_message(msg, view=bj_buttons)
        await interaction.response.send_message(msg)
    async def button_stay_callback(interaction):
        if ctx.author.id != interaction.user.id:
            return await interaction.response.defer()
        if interaction.user.id not in bjplayers:
            return await interaction.response.defer()
        if bjplayers[interaction.user.id].status != 'playing':
            return await interaction.response.defer()
        bjplayers[interaction.user.id].stay()
        await interaction.response.send_message(bjplayers[interaction.user.id].maininfo())
    
    bj_buttons = discord.ui.View()
    button_hit = discord.ui.Button(label="Hit!", style=discord.ButtonStyle.green, emoji="👊")
    button_hit.callback = button_hit_callback
    bj_buttons.add_item(button_hit)
    button_stay = discord.ui.Button(label="Stay!", style=discord.ButtonStyle.red, emoji="✋")
    button_stay.callback = button_stay_callback
    bj_buttons.add_item(button_stay)
    await ctx.reply(blackjack.maininfo(bjplayers[ctx.author.id]), view=bj_buttons)

async def work(ctx):
    member = ctx.author.id

    if not is_member_exists(member)['coins']:
        register(member)
        return await ctx.reply(f' Новый работник! Баланс: {new_worker_balance}')
    
    if is_cooldown(member, 'work'):
        cd = get_cooldown(member, 'work')
        return await ctx.reply(f'{ctx.author.mention} устал и не может работать, куладун: {cd}')
    
    updatemoney(member, pay['work'] * multiplier)
    set_cooldown(member, 'work', cooldown['work'])
    await ctx.reply(f'{ctx.author.mention} сходил на работу!(вау!) Баланс: {balance(ctx.author.id)}')
