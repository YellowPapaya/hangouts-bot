import hangups
from hangups import hangouts_pb2
from hangups.hangouts_pb2 import ParticipantId
import asyncio
import random
from collections import defaultdict
from datetime import datetime, tzinfo
import json
# import math
import utils

from game_2048.manager import Manager2048
from economy.manager import EconomyManager
from rpg.manager import RPGManager


class Handler:

    save_file = "data.json"
    images_folder = "images/"

    keywords = {
        "ping": "pong",
        "pong": "ping",
        "saber": "hi",
        "meep": "meep"
    }
    images = {
        "/gay": "gay.jpg",
        "/math": "math.jpg",
        "/praise": "praise.jpg",
        "/goddammit": "goddammit.jpg",
        "/heymister": "heymister.png"
    }
    game_managers = {
        "/2048": Manager2048(),
        "/rpg": RPGManager(),
        "/economy": EconomyManager(),
    }
    ignore = (
        105849946242372037157,  # odlebot
        11470746254329358783,  # saberbot
        104687919952293193271,  # Ether(chendibot)
    )
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )

    def __init__(self):
        self.commands = {
            "/help": self.help_,
            "/rename": self.rename_conv,
            "/quit": self.quit_,
            "/id": self.id_,
            "/kick": self.kick,
        }
        for command in self.commands.values():
            command.cooldown_time = 0
        help_.cooldown_time
        rename_conv.cooldown_time
        quit_.cooldown_time
        id_.cooldown_time
        kick.cooldown_time

        self.cooldowns = defaultdict(dict)

        random.seed(datetime.now())

    # utility
    async def help_(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        with open("text/help.txt", 'r') as help_text:
            bot.output_text =  help_text.read()

    async def rename_conv(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return ""
        commands = trim(clean(event.text))
        new_name = get_item_safe(commands)
        if not new_name:
            bot.output_text = "Format: /rename {name}"
        else:
            await conv.rename(new_name)

    async def id_(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            bot.output_text = user.id_[0]
        except:
            bot.output_text = "Something went wrong!"

    async def kick(self, bot, event):
        user, conv = getUserConv(bot, event)
        arg1 = event.text.lower().split()[1]
        users = conv.users
        ids = []
        kick_users = []

        try:
            for user in users:
                if arg1 in user.full_name.lower():
                    kick_users.append(user)

            if not kick_users:
                bot.output_text = "Nobody in this conversation goes by that name"
                return
            # only reason i figured this out was because of hangupsbot, so thank you so much
            # https://github.com/xmikos/hangupsbot/blob/master/hangupsbot/commands/conversations.py

            ids = [ParticipantId(gaia_id=user.id_.gaia_id, chat_id=conv.id_) for user in kick_users]

            for kick_id in ids:
                request = hangouts_pb2.RemoveUserRequest(
                    request_header=bot.client.get_request_header(),
                    participant_id=kick_id,
                    event_request_header=conv._get_event_request_header()
                )
                res = await bot.client.remove_user(request)
                conv.add_event(res.created_event)
        except:
            bot.output_text = "Yeah don't use this command lol"

    async def play_game(self, bot, event):
        game_name = clean(event.text)[0]
        manager = self.game_managers[game_name]
        user, conv = getUserConv(bot, event)
        game_text = manager.run_game(user.id_[0], event.text)
        bot.output_text = game_text
        manager.save_game()

    async def quit_(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 30):
            return

        if userIn(self.admins, user):
            bot.output_text = "Saber out!"
            save_games()
            await bot.client.disconnect()
        else:
            bot.output_text = "bro wtf u can't use that"
