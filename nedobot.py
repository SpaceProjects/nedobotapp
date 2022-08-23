from random import choice
from math import ceil
import discord
import sqlite3
import time
import db
import requests


# api bl0ck
DISCORD_BOT_TOKEN = '611508921919733780'


# variables bl0ck
client = discord.Client()
allmembers = []
onlinemembers = []
conn = sqlite3.connect('nedobase.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS info
(member, level int, exp int, expnlvl int, coins int)""")
db.connect('nedobase.db', 'cooldown', '(member, work)')
starting = '.'
bjplayers = []
cards = ('A', 'K', 'Q', 'J', 10, 9, 8, 7, 6, 5, 4, 3, 2)
cooldown = {'work': 10, }
pay = {'work': 20, }
multiplier = 1
timer = 3600

# when connected bl0ck
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="на тебя!"))
    await epicgames_parse()


def get_all_users():
    allmembers.clear()
    for guild in client.guilds:
        for member in guild.members:
            allmembers.append(member)


def get_online_users():
    onlinemembers.clear()
    for guild in client.guilds:
        for member in guild.members:
            if (member.status != discord.Status.offline) and (member.name not in onlinemembers) and not (member.bot):
                onlinemembers.append(str(member.name))


def roulette(firstpart, secondpart):
    participant = firstpart, secondpart
    winner = choice(participant)
    return winner


def replace_mention(message):
    num_of_ment = len(message.mentions)
    msg = str(message.content)
    for i in range(0, num_of_ment):
        msg = msg.replace(message.mentions[i].mention, '@' + message.mentions[i].name)
    return msg


def is_enought(memberid, need):
    cursor.execute("SELECT coins FROM info WHERE member=?", [memberid])
    s = cursor.fetchall()[0]
    if s[0] < need:
        return False
    else:
        return True


def updatemoney(memberid, coins):
    cursor.execute("SELECT coins FROM info WHERE member=?", [memberid])
    s = cursor.fetchone()[0] + int(coins)
    cursor.execute("UPDATE info SET coins=? WHERE member=?", [s, memberid])
    conn.commit()


def balance(memberid):
    cursor.execute("SELECT coins FROM info WHERE member=?", [memberid])
    return cursor.fetchone()[0]


async def epicgames_parse(timenextstart=(time.time()), lastdata=[]):
  r = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=ru&country=RU&allowCountries=RU")
#   print(timenextstart, lastdata)
  # по кулдауну
  if time.time() > timenextstart:
    timenextstart += timer
    # парс элементов
    currentdata = []
    msg = 'EPIC GAMES INFO:\n'
    for el in r.json()['data']['Catalog']['searchStore']['elements']:
      title = el['title']
      date = el['effectiveDate'][0:-8] 
      if date.startswith("2022-08"):
        currentdata.append(title)
        msg += f'Начиная с {date[0:10]} начнется раздача {title} \n'

    if lastdata != currentdata:
      print('not equal')
      lastdata = currentdata
      for guild in client.guilds:
        if guild.id == 537267521565229056:
          for channel in guild.channels:
            if channel.id == 609703612150448128:
              await channel.send(msg)
    await epicgames_parse(timenextstart, lastdata)


# minigames block
# BlackJack
class blackjack():
    def __init__(self, id, name, bet=0):
        self.id = id
        self.name = str(name)
        self.bet = int(bet)
        self.hand = []
        self.sum = 0
        self.dealer_hand = []
        self.dealer_sum = 0
        self.status = 'playing'
        updatemoney(self.id, (self.bet * -1))
        [self.getcard() for i in range(2)]
        [self.dealer_getcard() for i in range(2)]
        self.epicwin()

    def what_is_value_of_card(self, card):
        if card in ('A', 'Q', 'K', 'J'):
            if card == 'A':
                if (self.sum + 11) > 21:
                    return 1
                else:
                    return 11
            else:
                return 10
        else:
            return card

    def checkMySum(self):
        self.sum = 0
        for i in self.hand:
            if i == 'A':
                pass
            elif i in ('Q', 'K', 'J'):
                self.sum += 10
            else:
                self.sum += i
        for i in self.hand:
            if i == 'A':
                if self.sum + 11 > 21:
                    self.sum += 1
                else:
                    self.sum += 11

    def checkDealerSum(self):
        self.dealer_sum = 0
        for i in self.dealer_hand:
            if i == 'A':
                pass
            elif i in ('Q', 'K', 'J'):
                self.dealer_sum += 10
            else:
                self.dealer_sum += i
        for i in self.dealer_hand:
            if i == 'A':
                if self.dealer_sum + 11 > 21:
                    self.dealer_sum += 1
                else:
                    self.dealer_sum += 11

    # getting cards
    def getcard(self):
        card = choice(cards)
        self.hand.append(card)
        self.checkMySum()

    def dealer_getcard(self):
        card = choice(cards)
        self.dealer_hand.append(card)
        print(f'{self.name}\'s Dealer got {card}')  # ---удали это
        self.checkDealerSum()

    # main return
    def maininfo(self):
        self.whowin()
        print(f'status: {self.status}\n')  # --
        if self.status == 'tie':
            updatemoney(self.id, self.bet)
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum}.```\
{self.name}, Это ничья!'
        elif self.status == 'win':
            updatemoney(self.id, int(self.bet * 2))
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum}.```\
{self.name} выиграл {self.bet} nedocoins!'
        elif self.status == 'lose':
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum},```{self.name}, Ты проиграл!`'
        elif self.status == 'epic-win':
            updatemoney(self.id, ceil(self.bet * 2.5))
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum}.```\
{self.name} выиграл {ceil(self.bet*1.5)} nedocoins!'
        else:
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}\n\
Карты диллера: [{str(self.dealer_hand[0])}, ?], сумма: {self.what_is_value_of_card(self.dealer_hand[0])},```\
Взять ещё карту или достаточно? (напиши "h" или "s")'

    # win types
    def whowin(self):
        if self.status == 'playing':
            if self.dealer_sum > 21:
                self.status = 'win'
            elif self.sum > 21:
                self.status = 'lose'
            elif len(self.hand) >= 5:
                self.status = 'win'
            elif len(self.dealer_hand) >= 5:
                self.status = 'lose'

    def epicwin(self):
        if self.sum == self.dealer_sum == 21:
            self.status = 'tie'
        elif self.sum == 21:
            self.status = 'epic-win'

    # to-do defs
    def hit(self):
        self.getcard()

    def stay(self):
        self.whowin()
        if self.status != 'playing':
            return
        elif self.sum == self.dealer_sum > 17:
            self.status = 'tie'
        elif self.sum < self.dealer_sum:
            self.status = 'lose'
        else:
            self.dealer_getcard()
            self.stay()
###


# on_message bl0ck
@client.event
async def on_message(message):
    # when any message sent
    if message.__init__:
        # printing bot messages
        if message.author == client.user:
            if len(message.mentions) > 0:
                msg = replace_mention(message)
                print('[Bot]: ' + msg + '\n -----')
            else:
                print('[Bot]: ' + message.content + '\n -----')
        # printing messages from users
        elif len(message.mentions) > 0:
            msg = replace_mention(message)
            print('[Message in {4}/{3}: {2}] {0} : {1}, \n ----------'.format(message.author.name, msg, time.strftime('[%H:%M:%S]'), message.channel, message.guild))
        else:
            print('[Message in {4}/{3}: {2}] {0} : {1}, \n ----------'.format(message.author.name, message.content, time.strftime('[%H:%M:%S]'), message.channel, message.guild))

    # hello function
    if message.content.startswith('{starting}привет'.format(starting=starting)):
        print('[Command]: Привет!')
        msg = 'Привет, {0.author.mention}'.format(message)
        await message.channel.send(msg)
    # sending all online users
    elif message.content.startswith('{starting}check'.format(starting=starting)):
        print('[Command]: Check!')
        get_online_users()
        await message.channel.send('```bash\n{0}```'.format(onlinemembers))
    # randomizing winner of roulette
    elif message.content.startswith('{starting}roulette'.format(starting=starting)):
        mesment = message.mentions
        if (len(mesment) == 0) or (message.author == mesment[-1]):
            return
        print('[Command]: roulette')
        winner = roulette(message.author, message.mentions[-1])
        await message.channel.send('{0.mention} Победил!'.format(winner))
    # work
    elif message.content.startswith(f'{starting}work'):
        cursor.execute("SELECT EXISTS(SELECT member FROM info WHERE member=?)", [message.author.id])
        dbmembercheck = cursor.fetchone()[0]
        print('[COMMAND]: work')
        if (dbmembercheck != 1):
            cursor.execute("INSERT INTO info VALUES (?,?,?,?,?)", [message.author.id, 1, 0, 20, 100])
            conn.commit()
            cursor.execute("SELECT coins FROM info WHERE member=?", [message.author.id])
            coins = cursor.fetchone()
            db.insert('cooldown', '({0}, {1})'.format(message.author.id, time.time() + cooldown['work']))
            await message.channel.send(message.author.mention + ' Новый работник! Баланс: ' + str(coins[0]))
        elif db.select('cooldown', 'work', 'member', '{0}'.format(message.author.id)) <= round(time.time()):
            cursor.execute("SELECT coins FROM info WHERE member=?", [message.author.id])
            coins = cursor.fetchone()[0] + (pay['work'] * multiplier)
            cursor.execute("UPDATE info SET coins=? WHERE member=?", [coins, message.author.id])
            conn.commit()
            db.update('cooldown', 'member', message.author.id, 'work', '{0}'.format(round(time.time()) + cooldown['work']))
            await message.channel.send(message.author.mention + ' сходил на работу!(вау!) Баланс: ' + str(coins))
        else:
            await message.channel.send(message.author.mention + 'устал и не может работать, куладун: ' + str((db.select('cooldown', 'work', 'member', message.author.id)) - round(time.time())))
    # help
    elif message.content.startswith(f'{starting}help'):
        await message.channel.send('```\n\
Префикс всех команд это "."\n\
-----\n\
Список комманд:\n\
привет - приветственное сообщение;\n\
check - имена всех, кто онлайн;\n\
roulette @mention - выбирает случайного победителя\n\
work - заработок nedocoins\n\
bj [ставка] - Блекджек\n\
заточится? - "да" или "нет"(чаще нет)\n\
-----```')
    # random yes or no
    elif message.content.startswith(f'{starting}заточится?'):
        msg = choice('Да!', 'нет', 'Да, но Нет!', 'Нет!')
        await message.channel.send(msg)

    # BlackJack
    if message.content.startswith(f'{starting}bj'):
        for i in bjplayers:
            if (str(i.name) == str(message.author)) and (i.status == 'playing'):
                await message.channel.send(f'{message.author.mention}, Ты уже в игре!')
                return
            elif i.status != 'playing':
                bjplayers.remove(i)
        if len(message.content.split()) > 1 and message.content.split()[1].isdigit():
            bet = int(message.content.split()[1])
            if is_enought(message.author.id, bet):
                message.author = blackjack(message.author.id, message.author, bet)
                bjplayers.append(message.author)
                await message.channel.send(blackjack.maininfo(message.author))
            else:
                await message.channel.send(f'{message.author.mention}, недостаточно nedocoins')
        else:
            await message.channel.send(f'{message.author.mention}, введите ставку nedocoins')
    elif message.content.startswith('h'):
        for i in bjplayers:
            if str(i.name) == str(message.author) and (i.status == 'playing'):
                i.hit()
                await message.channel.send(i.maininfo())
    elif message.content.startswith('s'):
        for i in bjplayers:
            if str(i.name) == str(message.author) and (i.status == 'playing'):
                i.stay()
                await message.channel.send(i.maininfo())

if __name__ == '__main__':
    client.run('NjExNTA4OTIxOTE5NzMzNzgw.XVU2EA.QXHq1ikXc9fSpzZmkV7bXob-W7Q')
