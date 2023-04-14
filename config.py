import os
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_PREFIX = os.environ.get('BOT_PREFIX') or '.'

cooldown = {'work': 10, }
pay = {'work': 20, }
multiplier = 1
new_worker_balance = 100