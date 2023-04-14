import sqlite3
import time
from config import new_worker_balance, cooldown

conn = sqlite3.connect('./nedobase/nedobase.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS coins
(member, coins int)""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS cooldowns
(member, work)""")


def is_enought(memberid, need):
    cursor.execute("SELECT coins FROM coins WHERE member=?", [memberid])
    s = cursor.fetchall()[0]
    if s[0] < need:
        return False
    else:
        return True


def updatemoney(memberid, coins):
    cursor.execute("SELECT coins FROM coins WHERE member=?", [memberid])
    new_balance = cursor.fetchone()[0] + int(coins)
    cursor.execute("UPDATE coins SET coins=? WHERE member=?", [new_balance, memberid])
    conn.commit()

def balance(memberid):
    cursor.execute("SELECT coins FROM coins WHERE member=?", [memberid])
    return cursor.fetchone()[0]

def is_member_exists(member):
    cursor.execute("SELECT EXISTS(SELECT member FROM coins WHERE member=?)", [member])
    coins = cursor.fetchone()[0]
    cursor.execute("SELECT EXISTS(SELECT work FROM cooldowns WHERE member=?)", [member])
    cooldowns = cursor.fetchone()[0]
    return {'coins': coins, 'cooldowns':cooldowns}

def register(member):
    cursor.execute("INSERT INTO coins VALUES (?,?)", [member, new_worker_balance])
    cursor.execute("INSERT INTO cooldowns VALUES (?, ?)", [member, round(time.time()) + cooldown['work']])
    conn.commit()

def set_cooldown(member, skill, cooldown):
    cursor.execute(f"UPDATE cooldowns SET {skill} = {round(time.time()) + cooldown} WHERE member = {member}")
    conn.commit()

def get_add_cooldowns(member):
    cursor.execute(f"SELECT * FROM cooldowns WHERE member={member}")
    return cursor.fetchone()

def get_cooldown(member, skill):
    if not is_member_exists(member)['cooldowns']:
        return 0
    
    cursor.execute(f"SELECT {skill} FROM cooldowns WHERE member={member}")
    return cursor.fetchone()[0] - round(time.time())

def is_cooldown(member, skill):
    cooldown = get_cooldown(member, skill)
    return 1 if cooldown >= 0 else 0
