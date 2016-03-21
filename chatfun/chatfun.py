# chatfun.py is a plugin for minqlx to:
# -allow the server to respond to things said in the server.
# -Hopefully this livens things up a bit for players.
# created by BarelyMiSSeD on 3-5-16
#
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_chatfunAdmin "4" - Sets the minqlx permission level needed to turn the chatfun auto responses on/off in game with
                        !chatfun <on|off>. This will override the qlx_chatfunReply setting until the server is restarted.
qlx_chatfunPauseTime "5" - Sets the amount of seconds between each response from the server.
qlx_chatfunReply "1" - Turns on/off the auto responses from the server to trigger text said in normal chat.
The command !fun will display a list of commands that players can use to interact with the server.
"""

import minqlx
from threading import Timer
import random
from numbers import Number
import requests

VERSION = "v1.01"

class chatfun(minqlx.Plugin):
    def __init__(self):

        # Cvars.
        self.set_cvar_once("qlx_chatfunPauseTime", "5")
        self.set_cvar_once("qlx_chatfunReply", "1")
        self.set_cvar_once("qlx_chatfunAdmin", "4")

        self.add_hook("player_loaded", self.player_loaded)
        self.add_hook("chat", self.monitor_chat)
        self.add_command("cookie", self.cmd_cookie)
        self.add_command("stfu", self.cmd_stfu)
        self.add_command(("random", "bot", "server"), self.cmd_respond)
        self.add_command("flowers", self.cmd_flowers)
        self.add_command("lies", self.cmd_lies)
        self.add_command(("boobies", "titties", "boobs", "tits"), self.cmd_boobies)
        self.add_command("hit", self.cmd_hit, usage="|player id or player name|")
        self.add_command("kill", self.cmd_kill, usage="|player id or player name|")
        self.add_command(("beer", "beerme"), self.cmd_beer, usage="|player id or player name|")
        self.add_command("insult", self.cmd_insult, usage="|player id or player name|")
        self.add_command("chatfun", self.cmd_chat_monitor, int(self.get_cvar("qlx_chatfunAdmin")), usage="<on/off>")
        self.add_command("fun", self.cmd_fun)
        self.add_command(("chatfunversion", "chatfun_version", "cfv"), self.chatfun_version, int(self.get_cvar("qlx_chatfunAdmin")))

        self.ct = {}
        self.ct["time"] = 0

        if self.get_cvar("qlx_chatfunReply", int) == 1:
            self.enable_chat = "On"
        else:
            self.enable_chat = "Off"

    # chatfun.py version checker. Thanks to iouonegirl for most of this section's code.
    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}/{}.py".format(self.__class__.__name__, self.__class__.__name__)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^4Server: ^7Currently using  ^4BarelyMiSSeD^7's ^6{}^7 plugin ^1outdated^7 version ^6{}^7. The latest version is ^6{}".format(self.__class__.__name__, VERSION, line.decode()))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^4Server: ^7Currently using ^4BarelyMiSSeD^7's  latest ^6{}^7 plugin version ^6{}^7.".format(self.__class__.__name__, VERSION))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    try:
                        player.tell("^4Server: ^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                        player.tell("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                    except Exception as e: minqlx.console_command("echo {}".format(e))
                return

    def chatfun_version(self, player, msg, channel):
        self.check_version(channel=channel)

    @minqlx.delay(4)
    def player_loaded(self, player):
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)

    def bot_timer(self):
        self.ct["time"] = 1
        t = Timer(self.get_cvar("qlx_chatfunPauseTime", int), self.bot_stoptimer)
        t.start()

    def bot_stoptimer(self):
        self.ct["time"] = 0

    def cmd_chat_monitor(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        cmd = msg[1].lower()
        if cmd == "on":
            self.enable_chat = "On"
            channel.reply("^2Server: Chat monitoring is turned on.")
        elif cmd == "off":
            self.enable_chat = "Off"
            channel.reply("^2Server: Chat monitoring is turned off.")

    def monitor_chat(self, player, msg, channel):
        split_msg = msg.lower().split()
        if self.ct["time"] != 0 or self.enable_chat != "On":
            return
        elif "fuck" in split_msg:
            dSearch = ["fuck","you"]
            found_word = 0
            for text_word in split_msg:
                for search_word in dSearch:
                    if hash(search_word) == hash(text_word):
                        found_word += 1
            if found_word == 2:
                with open("./minqlx-plugins/fuckyou.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
                f.close()
                self.bot_timer()
            elif found_word == 1:
                with open("./minqlx-plugins/fuck.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
                f.close()
                self.bot_timer()
            else:
                return
        elif "rail" in split_msg or "railgun" in split_msg:
            dSearch = ["rail","ruined","quake","railgun"]
            found_word = 0
            for text_word in split_msg:
                for search_word in dSearch:
                    if hash(search_word) == hash(text_word):
                        found_word += 1
            if found_word == 3:
                with open("./minqlx-plugins/rail.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
                f.close()
                self.bot_timer()
            else:
                return
        elif "ouch" in split_msg:
            dSearch = ["ouch"]
            lenSearch = len(dSearch)
            found_word = 0
            for text_word in split_msg:
                for search_word in dSearch:
                    if hash(search_word) == hash(text_word):
                        found_word += 1
            if found_word == lenSearch:
                with open("./minqlx-plugins/ouch.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
                f.close()
                self.bot_timer()
            else:
                return
        elif "shit" in split_msg:
            dSearch = ["shit"]
            lenSearch = len(dSearch)
            found_word = 0
            for text_word in split_msg:
                for search_word in dSearch:
                    if hash(search_word) == hash(text_word):
                        found_word += 1
            if found_word == lenSearch:
                with open("./minqlx-plugins/shit.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
                f.close()
                self.bot_timer()
            else:
                return
        elif "gay" in split_msg:
            dSearch = ["gay"]
            lenSearch = len(dSearch)
            found_word = 0
            for text_word in split_msg:
                for search_word in dSearch:
                    if hash(search_word) == hash(text_word):
                        found_word += 1
            if found_word == lenSearch:
                with open("./minqlx-plugins/gay.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
                f.close()
                self.bot_timer()
        elif "puta" in split_msg:
            dSearch = ["puta"]
            lenSearch = len(dSearch)
            found_word = 0
            for text_word in split_msg:
                for search_word in dSearch:
                    if hash(search_word) == hash(text_word):
                        found_word += 1
            if found_word == lenSearch:
                with open("./minqlx-plugins/puta.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
                f.close()
                self.bot_timer()
            else:
                return
        else:
            return

    def cmd_fun(self, player, msg, channel):
        self.tell("^4Fun Commands:^3 !beer |id|, !insult |id|, !hit |id|, !kill |id|, !cookie, !stfu, !random, !flowers, !lies, !boobs", player)
        
    def cmd_cookie(self, player, msg, channel):
        if self.ct["time"] != 0:
           return
        else:
            with open("./minqlx-plugins/cookies.txt", "r") as f:
                self.lines = f.readlines()
            i = random.randrange(1, len(self.lines))
            channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
            f.close()
            self.bot_timer()

    def cmd_stfu(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            channel.reply("^2Server: " + "^1Fuck You ^2{}^1! ^7You can't stop my ^4POWER^1!!".format(player))
            self.bot_timer()

    def cmd_respond(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            with open("./minqlx-plugins/fun.txt", "r") as f:
                self.lines = f.readlines()
            i = random.randrange(1, len(self.lines))
            channel.reply("^2Server: " + self.lines[i].format(player).rstrip())
            f.close()
            self.bot_timer()

    def cmd_flowers(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            channel.reply("^2Server: " + "^7 Awww, ^1Flowers ^7are so thoughtful {}^7. Still no sex for you!".format(player))
            self.bot_timer()

    def cmd_lies(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            channel.reply("^2Server: " + "^1LIES?!? ^7Who is full of lies? {} ^7You should kick the liar!".format(player))
            self.bot_timer()

    def cmd_boobies(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            channel.reply("^2Server: " + "^7(^1.^7Y^1.^7)")
            self.bot_timer()

    def cmd_hit(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            if len(msg) > 1:
                try:
                    attempt = int(msg[1])
                except:
                    attempt = "name"
                if attempt == "name":
                    player_list = self.players()
                    players = []
                    for name in msg[1:]:
                        for p in self.find_player(name):
                            if p not in players:
                                players.append(p)
                    if players and len(players) == 1:
                        with open("./minqlx-plugins/hit.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(player, players[0]).rstrip())
                        f.close()
                        self.bot_timer()
                    elif players and len(players) > 1:
                        channel.reply("^2Server: " + "^3Sorry, but too many players matched your request.")
                    else:
                        channel.reply("^2Server: " + "^3Sorry, but no players matched your request.")
                else:
                    ident = int(msg[1])
                    if ident < 0 or ident >= 64:
                        return minqlx.RET_USAGE
                    try:
                        n = self.player(ident)
                    except minqlx.NonexistentPlayerError:
                        player.tell("^3No players match the client ID supplied.")
                        return
                    if n:
                        with open("./minqlx-plugins/hit.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(player, n).rstrip())
                        f.close()
                        self.bot_timer()
                    else:
                        player.tell("^3No players match the client ID supplied.")
            else:
                with open("./minqlx-plugins/hit.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format("^2The ^4S^7erver", player).rstrip())
                f.close()
                self.bot_timer()

    def cmd_kill(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            if len(msg) > 1:
                try:
                    attempt = int(msg[1])
                except:
                    attempt = "name"
                if attempt == "name":
                    player_list = self.players()
                    players = []
                    for name in msg[1:]:
                        for p in self.find_player(name):
                            if p not in players:
                                players.append(p)
                    if players and len(players) == 1:
                        with open("./minqlx-plugins/kill.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(player, players[0]).rstrip())
                        f.close()
                        self.bot_timer()
                    elif players and len(players) > 1:
                        channel.reply("^2Server: " + "^3Sorry, but too many players matched your request.")
                    else:
                        channel.reply("^2Server: " + "^3Sorry, but no players matched your request.")
                else:
                    ident = int(msg[1])
                    if ident < 0 or ident >= 64:
                        return minqlx.RET_USAGE
                    try:
                        n = self.player(ident)
                    except minqlx.NonexistentPlayerError:
                        player.tell("^3No players match the client ID supplied.")
                        return
                    if n:
                        with open("./minqlx-plugins/kill.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(player, n).rstrip())
                        f.close()
                        self.bot_timer()
                    else:
                        player.tell("^3No players match the client ID supplied.")
            else:
                with open("./minqlx-plugins/kill.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format("^2The ^4S^7erver", player).rstrip())
                f.close()
                self.bot_timer()

    def cmd_beer(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            if len(msg) > 1:
                try:
                    attempt = int(msg[1])
                except:
                    attempt = "name"
                if attempt == "name":
                    players = []
                    for name in msg[1:]:
                        for p in self.find_player(name):
                            if p not in players:
                                players.append(p)
                    if players and len(players) == 1:
                        with open("./minqlx-plugins/beer.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(player, players[0]).rstrip())
                        f.close()
                        self.bot_timer()
                    elif players and len(players) > 1:
                        channel.reply("^2Server: " + "^3Sorry, but too many players matched your request.")
                    else:
                        channel.reply("^2Server: " + "^3Sorry, but no players matched your request.")
                else:
                    ident = int(msg[1])
                    if ident < 0 or ident >= 64:
                        return minqlx.RET_USAGE
                    try:
                        n = self.player(ident)
                    except minqlx.NonexistentPlayerError:
                        player.tell("^3No players match the client ID supplied.")
                        return
                    if n:
                        with open("./minqlx-plugins/beer.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(player, n).rstrip())
                        f.close()
                        self.bot_timer()
                    else:
                        player.tell("^3No players match the client ID supplied.")
            else:
                with open("./minqlx-plugins/beer.txt", "r") as f:
                    self.lines = f.readlines()
                i = random.randrange(1, len(self.lines))
                channel.reply("^2Server: " + self.lines[i].format("^2The ^4S^7erver", player).rstrip())
                f.close()
                self.bot_timer()

    def cmd_insult(self, player, msg, channel):
        if self.ct["time"] != 0:
            return
        else:
            if len(msg) > 1:
                try:
                    attempt = int(msg[1])
                except:
                    attempt = "name"
                if attempt == "name":
                    players = []
                    for name in msg[1:]:
                        for p in self.find_player(name):
                            if p not in players:
                                players.append(p)
                    if players and len(players) == 1:
                        with open("./minqlx-plugins/insults.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(players[0]).rstrip())
                        f.close()
                        self.bot_timer()
                    elif players and len(players) > 1:
                        channel.reply("^2Server: " + "^3Sorry, but too many players matched your request.")
                    else:
                        channel.reply("^2Server: " + "^3Sorry, but no players matched your request.")
                else:
                    ident = int(msg[1])
                    if ident < 0 or ident >= 64:
                        return minqlx.RET_USAGE
                    try:
                        n = self.player(ident)
                    except minqlx.NonexistentPlayerError:
                        player.tell("^3No players match the client ID supplied.")
                        return
                    if n:
                        with open("./minqlx-plugins/insults.txt", "r") as f:
                            self.lines = f.readlines()
                        i = random.randrange(1, len(self.lines))
                        channel.reply("^2Server: " + self.lines[i].format(n).rstrip())
                        f.close()
                        self.bot_timer()
                    else:
                        player.tell("^3No players match the client ID supplied.")
            else:
                return minqlx.RET_USAGE