# votelimiter.py is a plugin for minqlx to:
# -limit what players are allowed to callvote.
# -This script does not appear to interfere with any votes (custom or not) managed my other scripts.
# created by BarelyMiSSeD on 7-29-16
#
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_voteLimiterAdmin "5"        // Sets the minqlx server permisson level needed to admin the vote limiter.
qlx_voteLimiterLimit "5"        // Sets the amount of votes each player is allowed to call before game/match end
                                //   This count will carry through map changes.
                                //   The built in limiter for Quake Live resets on map changes.
qlx_voteLimiterTypes "1"        // Enable/Disable the restricting of vote types ("1" = Enable, "0" = Disable)
qlx_voteLimiterDelay "30"       // The amount of seconds a player must wait before again calling the same type of vote.
qlx_voteLimiterExcludeAdmin "1" // Exclude admins from vote limiting? (Exclude on = 1, off = 0)
"""

import minqlx
import os
import time
import re

VERSION = "2.03"
VOTELIMITER_FILE = "votelimiter.txt"


class votelimiter(minqlx.Plugin):
    def __init__(self):
        # Cvars.
        self.set_cvar_once("qlx_voteLimiterAdmin", "5")
        self.set_cvar_once("qlx_voteLimiterLimit", "5")
        self.set_cvar_once("qlx_voteLimiterTypes", "1")
        self.set_cvar_once("qlx_voteLimiterDelay", "30")
        self.set_cvar_once("qlx_voteLimiterExcludeAdmin", "1")
        self.set_cvar_once("qlx_voteLimiterAllowed", "2")

        # monitored server occurrences
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGHEST)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("game_end", self.handle_end_game)
        self.add_hook("player_disconnect", self.handle_player_disconnect)

        # Variable to hold the admin permission level
        self.AdminLevel = self.get_cvar("qlx_voteLimiterAdmin", int)

        # commands
        self.add_command(("addvote", "allowvote"), self.cmd_allow_vote, self.AdminLevel)
        self.add_command(("delvote", "deletevote"), self.cmd_delete_vote, self.AdminLevel)
        self.add_command(("reload_voteslist", "rvl"), self.load_allowed_votes, self.AdminLevel)
        self.add_command(("votelimiter", "vlv"), self.get_version, self.AdminLevel)
        self.add_command(("resetvotecount", "rvc"), self.reset_vote_data, self.AdminLevel)
        self.add_command(("listvotes", "votes", "allowedvotes"), self.cmd_list_allowed_votes)
        self.add_command("votelimiter_voteban", self.votelimiter_voteban, self.AdminLevel)
        self.add_command("unvoteban", self.unvoteban, self.AdminLevel)
        self.add_command("addvoteban", self.addvoteban, self.AdminLevel)
        self.add_command("votebanlist", self.vote_ban_list, self.AdminLevel)

        # Opens the allowed votes container
        self.voteLimiterAllowed = []
        # Dictionary for counting amount of votes called by a player per match (will count until a game/match ends)
        self.voteLimiterCount = {}
        # Dictionary to store the time and vote last called by a player
        self.voteLimiterVote = {}
        # Loads the allowed votes list
        self.load_allowed_votes()
        # Holds Steam ID of player who called a vote
        self.steam_id = "0"
        # Holds player names that have been vote banned through callvote
        self.vote_banned = []

    def handle_vote_called(self, caller, vote, args):
        if caller.id in self.vote_banned:
            caller.tell("^1You have had your voting privileges removed by a server callvote."
                        " Your vote will not be allowed.")
            minqlx.console_print("^3Player ^6{} ^7tried calling a vote while on the votelimiter voteban list."
                                 " Vote was denied.".format(caller))
            return minqlx.RET_STOP_ALL

        vote = vote.lower()
        sid = caller.steam_id

        if vote == "voteban":
            try:
                player = self.player(int(args))
                player_id = player.id
            except ValueError:
                player, player_id = self.find_player(args)
                if player_id == -1:
                    if player == 0:
                        caller.tell("^1Too Many players matched your player name")
                    else:
                        caller.tell("^1No player matching that name found")
                    return minqlx.RET_STOP_ALL
            except Exception as e:
                if type(e).__name__ == "NonexistentPlayerError":
                    caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                    return minqlx.RET_STOP_ALL
                minqlx.console_print("^3Exception during vote call attempt^7: ^1{} ^7: ^4{}"
                                     .format(type(e).__name__, e.args))
                return minqlx.RET_STOP_ALL

            if self.db.get_permission(player) >= self.AdminLevel and\
                    self.db.get_permission(player) >= self.db.get_permission(caller):
                caller.tell("^3That player is a server admin and can't have their voting privileges suspended.")
                minqlx.console_print("Votelimiter voteban attempted for player {}."
                                     " Vote denied due to admin permission level.".format(player))
                return minqlx.RET_STOP_ALL

            self.callvote("qlx {}votelimiter_voteban {}".format(self.get_cvar("qlx_commandPrefix"), player_id),
                          "Ban {} from calling votes on the server?".format(player))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called vote /cv {} {}".format(caller.name, vote, args))
            return minqlx.RET_STOP_ALL

        if self.get_cvar("qlx_voteLimiterTypes", bool) and vote not in self.voteLimiterAllowed:
            minqlx.console_print("{} called vote {} {}, which is currently disabled on the server."
                                 .format(caller, vote, args))
            caller.tell("^3That vote type is not allowed on this server.\nSpeak to a server admin if this is in error")
            return minqlx.RET_STOP_ALL

        if self.get_cvar("qlx_voteLimiterExcludeAdmin", bool) and self.db.get_permission(caller) >= self.AdminLevel:
            return

        if sid not in self.voteLimiterVote:
            self.voteLimiterVote[sid] = {}

        if vote not in self.voteLimiterVote[sid]:
            self.voteLimiterVote[sid]["{}".format(vote)] = vote
            self.voteLimiterVote[sid]["{}_time".format(vote)] = int(time.time())
            self.voteLimiterVote[sid]["{}_count".format(vote)] = 0

        elapsed = int(time.time()) - self.voteLimiterVote[sid]["{}_time".format(vote)]
        delay = self.get_cvar("qlx_voteLimiterDelay", int)

        if sid in self.voteLimiterCount:
            self.voteLimiterCount[sid] += 1
            if self.voteLimiterCount[sid] >= self.get_cvar("qlx_voteLimiterLimit", int):
                caller.tell("^3You have called your maximum number of votes.\n"
                            "^3Your vote count will reset at the end of a game/match.")
                return minqlx.RET_STOP_ALL
        else:
            self.voteLimiterCount[sid] = 1

        if self.get_cvar("qlx_voteLimiterAllowed", int) > self.voteLimiterVote[sid]["{}_count".format(vote)]:
            self.voteLimiterVote[sid]["{}_count".format(vote)] += 1
        elif elapsed <= delay:
            caller.tell("^3You have called a {} type of vote, ^2{} seconds ^3before you "
                        "can call this type of vote again.".format(vote, delay - elapsed))
            return minqlx.RET_STOP_ALL
        self.steam_id = sid
        self.voteLimiterVote[sid]["{}_time".format(vote)] = int(time.time())

    def handle_vote_ended(self, votes, vote, args, passed):
        self.voteLimiterVote[self.steam_id]["{}_time".format(vote.lower())] = int(time.time())

    def handle_end_game(self, data):
        self.reset_vote_data()

    def handle_player_disconnect(self, player, reason):
        if player.id in self.vote_banned:
            self.vote_banned.remove(player.id)

    # Search for a player name match using the supplied string
    def find_player(self, name):
        found_player = None
        found_count = 0
        # Remove color codes from the supplied string
        player_name = re.sub(r"\^[0-9]", "", name).lower()
        # search through the list of connected players for a name match
        for player in self.players():
            if player_name in re.sub(r"\^[0-9]", "", player.name).lower():
                # if match is found return player, player id
                found_player = player
                found_count += 1
        # if only one match was found return player, player id
        if found_count == 1:
            return found_player, int(str([found_player]).split(":")[0].split("(")[1])
        # if more than one match is found return 0, -1
        elif found_count > 1:
            return 0, -1
        # if no match is found return -1, -1
        else:
            return -1, -1

    def votelimiter_voteban(self, player, msg, channel):
        try:
            if int(msg[1]) not in self.vote_banned:
                self.vote_banned.append(int(msg[1]))
        except Exception as e:
            minqlx.console_print("Error adding player ID to votelimiter voteban: {} : {}"
                                 .format(type(e).__name__, e.args))

    def unvoteban(self, player, msg, channel):
        try:
            if int(msg[1]) in self.vote_banned:
                self.vote_banned.remove(int(msg[1]))
                player.tell("^6Player ^4{} ^6has been removed from the votelimiter voteban list^7."
                            .format(self.player(int(msg[1]))))
        except:
            player.tell("^3Usage^7: {}unvoteban <player id>".format(self.get_cvar("qlx_commandPrefix")))
        return minqlx.RET_STOP_ALL

    def vote_ban_list(self, player=None, msg=None, channel=None):
        banned = []
        populated = False
        for pid in self.vote_banned:
            populated = True
            banned.append("^7(^4{}^7)^2{}".format(pid, self.player(pid)))
        if populated:
            if player:
                player.tell("^3Current Voting Bans^7: {}".format(", ".join(banned)))
            else:
                minqlx.console_print("^3Current Voting Bans^7: {}".format(", ".join(banned)))
        else:
            if player:
                player.tell("^3The votelimiter voteban list is empty^7.")
            else:
                minqlx.console_print("^3The votelimiter voteban list is empty^7.")
        return minqlx.RET_STOP_ALL

    def addvoteban(self, player, msg, channel):
        try:
            if int(msg[1]) not in self.vote_banned:
                self.vote_banned.append(int(msg[1]))
                player.tell("^6Player ^4{} ^6has been added to the votelimiter voteban list^7."
                            .format(self.player(int(msg[1]))))
        except:
            player.tell("^3Usage^7: {}addvoteban <player id>".format(self.get_cvar("qlx_commandPrefix")))
        return minqlx.RET_STOP_ALL

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

    def get_version(self, player, msg, channel):
        player.tell("^4The server is using ^5{} ^4version ^1{}".format(self.__class__.__name__, VERSION))

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
