# minqlx - A Quake Live server administrator bot.
# Copyright (C) 2015 Mino <mino@minomino.org>

# minqlx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# minqlx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.


# Modified by Thomas Jones on 27/01/2016 - thomas@tomtecsolutions.com
# commlink.py, a plugin for minqlx to enable inter-server communication functionality.
# This plugin is released to everyone, for any purpose. It comes with no warranty, no guarantee it works, it's released AS IS.
# You can modify everything, except for lines 1-4 and the !tomtec_versions code. Please make it better :D

#Modified by OrbitaL on 9/19/2019 changed irc server

# Modified by BarelyMiSSeD on 10/6/2019: (only team games modifications)
# added - !status (responds with the player status of the other servers)
# added - !need <num> (tells other server that num of players is needed on the requesting server)
# 12/6/2022: added checking for self.game in places it is used before executing further code

"""

    Set the following cvars:
        qlx_commlinkIdentity                        - Set this cvar in your server.cfg, it needs to be the same for all your servers. If someone's using the same identity, there'll be crosstalk across the servers.
            No Default. This cvar MUST be set.
        qlx_commlinkServerName                      - Make this a 12 character or less identifier that will appear when messages from the server appear on other servers in the same identity group.
            Default: Server-XXXX (where X = random number)
        qlx_enableConnectDisconnectMessages         - Enables the 'Player connected.' and 'Player disconnected.' messages in CommLink.
            Default: 1
        qlx_enableCommlinkMessages                  - Enables CommLink message reception for all players. If this is set to 0, players have to manually enable CommLink with the !commlink command.
            Default: 1

"""

import minqlx
import threading
import asyncio
import random
import time
import re
import urllib.request

TEAM_BASED_GAMETYPES = ("ca", "ctf", "ft", "tdm", "ictf", "wipeout", "dom", "ad", "1f", "har")


class commlink(minqlx.Plugin):
    def __init__(self):
        if not self.get_cvar("qlx_commlinkIdentity"):
            self.msg("^1Error: ^7Please set your ^4qlx_commlinkIdentity^7 cvar in your server.cfg.")
            minqlx.unload_plugin("commlink")
            return
                     
        self.add_hook("unload", self.handle_unload)
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_LOWEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect, priority=minqlx.PRI_LOWEST)
        self.add_hook("game_countdown", self.game_countdown)
        
        self.set_cvar_once("qlx_commlinkServerName", "Server-{}".format(random.randint(1000, 9999)))
        self.set_cvar_once("qlx_enableConnectDisconnectMessages", "1")
        self.set_cvar_once("qlx_enableCommlinkMessages", "1")

        self.server = "irc.quakenet.org"
        self.identity = ("#" + self.get_cvar("qlx_commlinkIdentity"))
        self.clientName = self.get_cvar("qlx_commlinkServerName")

        self.add_command(("world", "say_world"), self.send_commlink_message, priority=minqlx.PRI_LOWEST, usage="<message>")
        self.add_command("tomtec_versions", self.cmd_showversion)
        self.add_command("commlink", self.cmd_toggle_commlink)
        self.add_command("status", self.server_status)
        self.add_command("need", self.need_player, usage="<number>")
        
        self.irc = SimpleAsyncIrc(self.server, self.clientName, self.handle_msg, self.handle_perform, self.handle_raw)
        self.irc.start()
        self.logger.info("Connecting to {}...".format(self.server))
        self.msg("Connecting to ^3CommLink^7 server...")

        self.plugin_version = "1.5.pew"
        self.status_request = False
        self.server_ip = ""
        self.server_port = self.get_cvar("net_port")
        self.set_ip()

    @minqlx.delay(0.5)
    def set_ip(self):
        res = urllib.request.urlopen("http://checkip.amazonaws.com/").read()
        ip = "{}".format(res)
        ip = re.sub("[b']", "", ip)
        self.server_ip = ip[0:-2]

    def game_countdown(self):
        if self.game and self.game.type_short == "duel":
            self.msg("^3CommLink^7 message reception has been disabled during your Duel.")
            
    def cmd_toggle_commlink(self, player, msg, channel):
        flag = self.db.get_flag(player, "commlink:enabled", default=(self.get_cvar("qlx_enableCommlinkMessages", bool)))
        self.db.set_flag(player, "commlink:enabled", not flag)
        if flag:
            word = "disabled"
        else:
            word = "enabled"
        player.tell("^3CommLink^7 notices have been ^4{}^7.".format(word))
        return minqlx.RET_STOP_ALL
    
    def handle_unload(self, plugin):
        if plugin == self.__class__.__name__ and self.irc and self.irc.is_alive():
            self.irc.quit("CommLink plugin unloaded.")
            self.irc.stop()

    def handle_player_connect(self, player):
        if self.irc and self.get_cvar("qlx_enableConnectDisconnectMessages", bool):
            if str(player.steam_id)[0] == "9":
                return
            self.irc.msg(self.identity, self.translate_colors("{} connected.".format(player.name)))

    def handle_player_disconnect(self, player, reason):
        if reason and reason[-1] not in ("?", "!", "."):
            reason = reason + "."
        
        if self.irc and self.get_cvar("qlx_enableConnectDisconnectMessages", bool):
            if str(player.steam_id)[0] == "9": return
            self.irc.msg(self.identity, self.translate_colors("{} {}".format(player.name, reason)))
        
    def handle_msg(self, irc, user, channel, msg):
        def broadcast_commlink(pm):
            if pm[0].startswith("Duel-") or pm[0].startswith("Free-") and pm[1].startswith("Spec-"):
                if not self.status_request:
                    return
                self.unset_server_status()
                pm[0] = "^3{}".format(pm[0])
                pm[1] = "^6{}".format(pm[1])
                pm[2] = "^5/connect {}".format(pm[2])
            elif pm[0].startswith("Red-") and pm[1].startswith("Blue-") and pm[2].startswith("Spec-"):
                if not self.status_request:
                    return
                self.unset_server_status()
                pm[0] = "^1{}".format(pm[0])
                pm[1] = "^4{}".format(pm[1])
                pm[2] = "^6{}".format(pm[2])
                pm[3] = "^5/connect {}".format(pm[3])
            minqlx.console_print("[CommLink] ^5{}^7:^3 {}".format(user[0], " ".join(pm)))
            duelers = self.teams()["free"]
            for p in self.players():
                if self.game and self.game.type_short == "duel" and p in duelers and self.game.state != "warmup":
                    continue
                if self.db.get_flag(p, "commlink:enabled", default=(self.get_cvar("qlx_enableCommlinkMessages", bool))):
                    p.tell("[CommLink] ^4{}^7:^3 {}".format(user[0], " ".join(pm)))

        if not msg:
            return
        if msg[0] == 'request_status':
            status = self.get_status_msg()
            self.irc.msg(self.identity, "{} {}:{}".format(status, self.server_ip, self.server_port))
        else:
            broadcast_commlink(msg)

    def handle_perform(self, irc):
        self.logger.info("Connected to CommLink!".format(self.server))
        self.msg("Connected to ^3CommLink^7.")
        irc.join(self.identity)

    def send_commlink_message(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        text = "^7<{}> ^3{} ".format(player.name, " ".join(msg[1:]))
        self.irc.msg(self.identity, self.translate_colors(text))
        player.tell("Message sent via ^3CommLink^7.")

    def get_status_msg(self):
        teams = self.teams()
        free = len(teams["free"])
        red = len(teams["red"])
        blue = len(teams["blue"])
        spec = len(teams["spectator"])
        if self.game:
            if self.game.type_short == "duel":
                status = "^3Duel-{}, ^6Spec-{}".format(free, spec)
            elif self.game.type_short in TEAM_BASED_GAMETYPES:
                status = "^1Red-{}, ^4Blue-{}, ^6Spec-{}".format(red, blue, spec)
            else:
                status = "^3Free-{}, ^6Spec-{}".format(free, spec)
            return status

    def server_status(self, player, msg, channel):
        self.query_status()

    @minqlx.thread
    def query_status(self):
        free = self.teams()["free"]
        status = self.get_status_msg()
        minqlx.console_print("[CommLink] ^5{}^7: {}".format(self.clientName, status))
        if self.game:
            for p in self.players():
                if self.game.type_short == "duel" and p in free and self.game.state != "warmup":
                    continue
                if self.db.get_flag(p, "commlink:enabled", default=(self.get_cvar("qlx_enableCommlinkMessages", bool))):
                    p.tell("[CommLink] ^4{}^7: {}".format(self.clientName, status))
            self.status_request = True
            self.irc.msg(self.identity, "request_status")

    @minqlx.delay(1.5)
    def unset_server_status(self):
        self.status_request = False

    def need_player(self, player, msg, channel):
        if len(msg) > 1:
            try:
                needed = int(msg[1])
            except:
                player.tell("^1You must include a number")
                return minqlx.RET_STOP_ALL
        else:
            needed = 1
        player.tell("^6Sent player request to other servers")
        status = self.get_status_msg()
        self.irc.msg(self.identity, "Need {} player{} here: {} /connect {}:{}"
                     .format(needed, "s" if needed > 1 else "", status, self.server_ip, self.server_port))
         
    def handle_raw(self, irc, msg):
        split_msg = msg.split()
        if len(split_msg) > 1 and split_msg[1] == "433":
            irc.nick(irc.nickname + "_")

    @classmethod
    def translate_colors(cls, text):
        return cls.clean_text(text)

    def cmd_showversion(self, player, msg, channel):
        channel.reply("^4commlink.py^7 - version {}, by Thomas Jones, ^1O^7rbitaL, & Barely^4MiSSeD.".format(self.plugin_version))


# ====================================================================
#                        COMMLINK CHANNEL
# ====================================================================

class IrcChannel(minqlx.AbstractChannel):
    name = "irc"

    def __init__(self, irc, recipient):
        self.irc = irc
        self.recipient = recipient

    def __repr__(self):
        return "{} {}".format(str(self), self.recipient)

    def reply(self, msg):
        for line in msg.split("\n"):
            self.irc.msg(self.recipient, irc.translate_colors(line))

# ====================================================================
#                        SIMPLE ASYNC IRC
# ====================================================================

re_msg = re.compile(r"^:([^ ]+) PRIVMSG ([^ ]+) :(.*)$")
re_user = re.compile(r"^(.+)!(.+)@(.+)$")

class SimpleAsyncIrc(threading.Thread):
    def __init__(self, address, nickname, msg_handler, perform_handler, raw_handler=None, stop_event=threading.Event()):
        split_addr = address.split(":")
        self.host = split_addr[0]
        self.port = int(split_addr[1]) if len(split_addr) > 1 else 6667
        self.nickname = nickname
        self.msg_handler = msg_handler
        self.perform_handler = perform_handler
        self.raw_handler = raw_handler
        self.stop_event = stop_event
        self.reader = None
        self.writer = None
        self.server_options = {}
        super().__init__()

        self._lock = threading.Lock()
        self._old_nickname = self.nickname

    def run(self):
        loop = asyncio.new_event_loop()
        logger = minqlx.get_logger("irc")
        asyncio.set_event_loop(loop)
        while not self.stop_event.is_set():
            try:
                loop.run_until_complete(self.connect())
            except Exception:
                minqlx.log_exception()
            
            # Disconnected. Try reconnecting in 30 seconds.
            logger.info("Disconnected from CommLink. Reconnecting in 30 seconds...")
            minqlx.CHAT_CHANNEL.reply("Disconnected from ^3CommLink^7. Reconnecting in 30 seconds...")
            time.sleep(30)
        loop.close()

    def stop(self):
        self.stop_event.set()

    def write(self, msg):
        if self.writer:
            with self._lock:
                self.writer.write(msg.encode(errors="ignore"))

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from asyncio.open_connection(self.host, self.port)
        self.write("NICK {0}\r\nUSER {0} 0 * :{0}\r\n".format(self.nickname))
        
        while not self.stop_event.is_set():
            line = yield from self.reader.readline()
            if not line:
                break
            line = line.decode("utf-8", errors="ignore").rstrip()
            if line:
                yield from self.parse_data(line)

        self.write("QUIT Quit by user.\r\n")
        self.writer.close()

    @asyncio.coroutine
    def parse_data(self, msg):
        split_msg = msg.split()
        if len(split_msg) > 1 and split_msg[0] == "PING":
            self.pong(split_msg[1].lstrip(":"))
        elif len(split_msg) > 3 and split_msg[1] == "PRIVMSG":
            r = re_msg.match(msg)
            user = re_user.match(r.group(1)).groups()
            channel = user[0] if self.nickname == r.group(2) else r.group(2)
            self.msg_handler(self, user, channel, r.group(3).split())
        elif len(split_msg) > 2 and split_msg[1] == "NICK":
            user = re_user.match(split_msg[0][1:])
            if user and user.group(1) == self.nickname:
                self.nickname = split_msg[2][1:]
        elif split_msg[1] == "005":
            for option in split_msg[3:-1]:
                opt_pair = option.split("=", 1)
                if len(opt_pair) == 1:
                    self.server_options[opt_pair[0]] = ""
                else:
                    self.server_options[opt_pair[0]] = opt_pair[1]
        elif len(split_msg) > 1 and split_msg[1] == "433":
            self.nickname = self._old_nickname
        # Stuff to do after we get the MOTD.
        elif re.match(r":[^ ]+ (376|422) .+", msg):
            self.perform_handler(self)

        # If we have a raw handler, let it do its stuff now.
        if self.raw_handler:
            self.raw_handler(self, msg)

    def msg(self, recipient, msg):
        self.write("PRIVMSG {} :{}\r\n".format(recipient, msg))

    def nick(self, nick):
        with self._lock:
            self._old_nickname = self.nickname
            self.nickname = nick
        self.write("NICK {}\r\n".format(nick))

    def join(self, channels):
        self.write("JOIN {}\r\n".format(channels))

    def part(self, channels):
        self.write("PART {}\r\n".format(channels))

    def mode(self, what, mode):
        self.write("MODE {} {}\r\n".format(what, mode))

    def kick(self, channel, nick, reason):
        self.write("KICK {} {}:{}\r\n".format(channel, nick, reason))

    def quit(self, reason):
        self.write("QUIT :{}\r\n".format(reason))

    def pong(self, n):
        self.write("PONG :{}\r\n".format(n))
