# votelimiter.py is a plugin for minqlx to:
# -limit what players are allowed to callvote.
# -This script does not appear to interfere with any votes (custom or not) managed my other scripts.
# created by BarelyMiSSeD on 7-29-16
#
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_voteLimiterAdmin "5" - Sets the minqlx server permisson level needed to admin the vote limiter.
qlx_voteLimiterLimit "5" - Sets the amount of votes each player is allowed to call before the end of a game/match
                            This count will carry through map changes. The built in limiter for Quake Live resets
                            on map changes.
qlx_voteLimiterTypes "1" - Enable/Disable the restricting of vote types ("1" = Enable, "0" = Disable)
qlx_voteLimiterDelay "60" - The amount of seconds a player must wait before the same type of vote may be called again.
qlx_voteLimiterExcludeAdmin "0" - Exclude admins from vote limiting? (Exclude on = 1, off = 0)
"""

import minqlx
import requests
import os
import time

VERSION = "v2.01"
VOTELIMITER_FILE = "votelimiter.txt"


class votelimiter(minqlx.Plugin):
    def __init__(self):
        # Cvars.
        self.set_cvar_once("qlx_voteLimiterAdmin", "5")
        self.set_cvar_once("qlx_voteLimiterLimit", "5")
        self.set_cvar_once("qlx_voteLimiterTypes", "1")
        self.set_cvar_once("qlx_voteLimiterDelay", "60")
        self.set_cvar_once("qlx_voteLimiterExcludeAdmin", "1")
        self.set_cvar_once("qlx_voteLimiterAllowed", "2")

        # Variable to hold the admin permission level
        self.AdminLevel = self.get_cvar("qlx_voteLimiterAdmin", int)

        # monitored server occurrences
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_hook("game_end", self.handle_end_game)

        # commands
        self.add_command(("addvote", "allowvote"), self.cmd_allow_vote, self.AdminLevel)
        self.add_command(("delvote", "deletevote"), self.cmd_delete_vote, self.AdminLevel)
        self.add_command(("reload_voteslist", "rvl"), self.load_allowed_votes, self.AdminLevel)
        self.add_command(("votelimiter", "vlv"), self.get_version, self.AdminLevel)
        self.add_command(("resetvotecount", "rvc"), self.reset_vote_data, self.AdminLevel)
        self.add_command(("listvotes", "votes", "allowedvotes"), self.cmd_list_allowed_votes)

        # Opens the allowed votes container
        self.voteLimiterAllowed = []
        # Dictionary for counting amount of votes called by a player per match (will count until a game/match ends)
        self.voteLimiterCount = {}
        # Dictionary to store the time and vote last called by a player
        self.voteLimiterVote = {}
        # Variable to hold the Exclude Admin setting
        self.excludeAdmin = self.get_cvar("qlx_voteLimiterExcludeAdmin", bool)
        # Loads the allowed votes list
        self.load_allowed_votes()

    def handle_vote_called(self, caller, vote, args):
        vote = vote.lower()
        sid = caller.steam_id
        if self.get_cvar("qlx_voteLimiterTypes", bool) and vote not in self.voteLimiterAllowed:
            minqlx.console_print("{} called vote {} {}, which is currently disabled on the server."
                                 .format(caller, vote, args))
            caller.tell("^3That vote type is not allowed on this server.\nSpeak to a server admin if this is in error")
            return minqlx.RET_STOP_ALL

        if self.excludeAdmin and self.db.get_permission(caller) >= self.AdminLevel:
            return

        if sid not in self.voteLimiterVote:
            self.voteLimiterVote[sid] = {}
        if vote not in self.voteLimiterVote[sid]:
            self.voteLimiterVote[sid]["{}".format(vote)] = vote
            self.voteLimiterVote[sid]["{}_time".format(vote)] = int(time.time())
            self.voteLimiterVote[sid]["{}_count".format(vote)] = 0

        elapsed = int(time.time()) - self.voteLimiterVote[sid]["{}_time".format(vote)]
        delay = self.get_cvar("qlx_voteLimiterDelay", int)

        if self.get_cvar("qlx_voteLimiterAllowed", int) > self.voteLimiterVote[sid]["{}_count".format(vote)]:
            self.voteLimiterVote[sid]["{}_count".format(vote)] += 1
        elif elapsed <= delay:
            caller.tell("^3You have called a {} vote, ^2{} seconds ^3before you "
                        "can call this vote again.".format(vote, delay - elapsed))
            minqlx.console_print("{} called vote {} {}, the similar vote wait period in effect. Vote denied."
                                 .format(caller, vote, args))
            return minqlx.RET_STOP_ALL
        self.voteLimiterVote[sid]["{}_time".format(vote)] = int(time.time())

        if sid in self.voteLimiterCount:
            if self.voteLimiterCount[sid] >= self.get_cvar("qlx_voteLimiterLimit", int):
                caller.tell("^3You have called your maximum number of votes.")
                caller.tell("^3Your vote count will reset at the end of a game/match.")
                return minqlx.RET_STOP_ALL
            self.voteLimiterCount[sid] += 1
        else:
            self.voteLimiterCount[sid] = 1

    def handle_end_game(self, data):
        self.reset_vote_data()

    def load_allowed_votes(self, player=None, msg=None, channel=None):
        try:
            f = open(os.path.join(self.get_cvar("fs_homepath"), VOTELIMITER_FILE), "r")
            lines = f.readlines()
            f.close()
            temp_list = []
            for vote in lines:
                if vote.startswith("#"):
                    continue
                try:
                    temp_list.append(vote.split(None, 1)[0].strip('\n'))
                except Exception as e:
                    minqlx.console_print("^1Error ^3during creating the Votes list: {}".format(e))
                    continue
            self.voteLimiterAllowed = temp_list
            if player:
                player.tell("^3The Allowed Votes list has been reloaded. ^1{}votes ^3 to see current load."
                            .format(self.get_cvar("qlx_commandPrefix")))
        except IOError as e:
            try:
                temp_list = []
                m = open(os.path.join(self.get_cvar("fs_homepath"), VOTELIMITER_FILE), "w")
                m.write("# This is a commented line because it starts with a '#'\n")
                m.write("# Enter every vote type you want allowed on its own line.\n")
                m.write("# Leave no blank lines in between allowed votes.\n")

                # The following lines add the default votes that are allowed. You can edit here,
                # but I recommend just removing the vote from the allowed list using the !rvote <vote> command.
                m.write("kick\n")
                temp_list.append("kick")
                m.write("clientkick\n")
                temp_list.append("clientkick")
                m.write("map\n")
                temp_list.append("map")
                m.write("teamsize\n")
                temp_list.append("teamsize")
                m.write("cointoss\n")
                temp_list.append("cointoss")
                m.write("shuffle\n")
                temp_list.append("shuffle")
                m.write("map_restart\n")
                temp_list.append("map_restart")
                # End default vote list

                m.close()
                self.voteLimiterAllowed = temp_list
                if player:
                    player.tell("^3No ^1Allowed Votes^3 list was found so one was created.")
            except Exception as e:
                if player:
                    player.tell("^1Error ^3reading and/or creating the Allowed Votes list: {}".format(e))
                minqlx.console_print("^1Error ^3reading and/or creating the Allowed Votes list: {}".format(e))
        except Exception as e:
            if player:
                player.tell("^1Error ^3reading the Allowed Votes list: {}".format(e))
            minqlx.console_print("^1Error ^3reading the Allowed Votes list: {}".format(e))
        return minqlx.RET_STOP_EVENT

    # votelimiter.py version checker. Thanks to iouonegirl for most of this section's code.
    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}.py" \
            .format(self.__class__.__name__)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^4Server: ^7Currently using  ^4BarelyMiSSeD^7's ^6{}^7 plugin ^1outdated^7 version"
                                  " ^6{}^7. The latest version is ^6{}"
                                  .format(self.__class__.__name__, VERSION, line.decode()))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^4Server: ^7Currently using ^4BarelyMiSSeD^7's  latest ^6{}^7 plugin version ^6{}^7."
                                  .format(self.__class__.__name__, VERSION))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    try:
                        player.tell("^4Server: ^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're"
                                    " using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                        player.tell("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                    except Exception as e:
                        minqlx.console_command("echo {}".format(e))
                return

    def get_version(self, player, msg, channel):
        self.check_version(channel=channel)

    # Add a vote to the Allowed Votes list
    def cmd_allow_vote(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^7<^2vote to allow^7>")
            return minqlx.RET_STOP_EVENT
        file = os.path.join(self.get_cvar("fs_homepath"), VOTELIMITER_FILE)
        try:
            with open(file) as test:
                pass
        except Exception as e:
            player.tell("^1Error ^3reading the Allowed Votes list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        vote = msg[1]

        # Checks to see if the vote is already in the Allowed Votes list and adds if not.
        if vote in self.voteLimiterAllowed:
            player.tell("^2{}^3 is already in the Allowed Votes list.".format(vote))
        else:
            h = open(file, "a")
            h.write(vote + "\n")
            h.close()
            self.voteLimiterAllowed.append(vote)
            player.tell("^2{}^3 has been added to the Allowed Votes list.".format(vote))

        return minqlx.RET_STOP_EVENT

    # Removes the desired vote from the Allowed Votes list
    def cmd_delete_vote(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^7<^2vote to not allow^7>")
            return minqlx.RET_STOP_EVENT
        file = os.path.join(self.get_cvar("fs_homepath"), VOTELIMITER_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Allowed Votes list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        vote = msg[1]

        # Removes the identified vote.
        for searchVote in lines:
            if searchVote.startswith("#"): continue
            if vote == searchVote.split(None, 1)[0]:
                h = open(file, "w")
                for line in lines:
                    if line[0] == "#":
                        h.write(line)
                    elif vote != line.split(None, 1)[0]:
                        h.write(line)
                h.close()
                if vote in self.voteLimiterAllowed:
                    self.voteLimiterAllowed.remove(vote)
                player.tell("^2{}^3 has been deleted from the Allowed Votes list.".format(vote))
                return minqlx.RET_STOP_EVENT

        player.tell("^2{}^3 is not in the Allowed Votes list.".format(vote))
        return minqlx.RET_STOP_EVENT

    # List votes in the Allowed Votes file
    def cmd_list_allowed_votes(self, player, msg, channel):
        if len(self.voteLimiterAllowed):
            player.tell("^5Allowed Votes List:\n{}".format(", ".join(self.voteLimiterAllowed)))
        else:
            player.tell("^5No voting is allowed on this server.")

    def reset_vote_data(self, player=None, msg=None, channel=None):
        self.voteLimiterCount.clear()
        self.voteLimiterVote.clear()
        if player:
            player.tell("^3The vote count for all players has been cleared.")
        return
