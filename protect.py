# protect.py is a plugin for minqlx to:
# -protect selected players from being kicked using a callvote, if enabled
# -protect from mapvoting during an active match, if enabled
# -allow any player, even those on the protected list, to be put to spectator if the AFK vote passes, if enabled.
# created by BarelyMiSSeD on 11-10-15
# 
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_protectMapVoting  "1" - Enabling does not allow map voting during match play but does not effect map voting during warm-up. ("1" on, "0" off)
qlx_protectAfkVoting  "1" - Enabling will allow players to be voted into spectator. ("1" on, "0" off)
qlx_protectJoinMapMessage "0" - Sends join message to players if map voting protection is enabled. ("1" on, "0" off)
qlx_protectJoinAfkMessage "1" - Sends join message to players if voting players to spectator is enabled. ("1" on, "0" off)
qlx_protectPermissionLevel "5" - Sets the lowest level bot permission level to  automatically protect
qlx_protectMuteVoting "1" - Allows voting muting and unmuting of a player. ("1" on, "0" off)
qlx_protectJoinMuteVoting "1" - Sends join message to players if mute voting is enabled. ("1" on, "0" off)
qlx_protectAdminLevel "5" - Sets the minqlx server permission level needed to add/del/list the protect list, and display the protect.py version number.
qlx_protectPassLevel "5" - Sets the minqlx server permission level needed to set/unset the server join password.
qlx_protectFTS "5" - Sets the minqlx server permisson level needed to force teamsize.
qlx_protectPlayerPercForVote "26" - Percentage of players voting yes to pass the AFK vote
"""

import minqlx
import requests
import os
import codecs
import random
import time
import re

VERSION = "2.3"
PROTECT_FILE = "protect.txt"


class protect(minqlx.Plugin):
    def __init__(self):
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_hook("player_loaded", self.player_loaded)

        # Cvars.
        self.set_cvar_once("qlx_protectMapVoting", "1")
        self.set_cvar_once("qlx_protectJoinMapMessage", "0")
        self.set_cvar_once("qlx_protectAfkVoting", "1")
        self.set_cvar_once("qlx_protectJoinAfkMessage", "1")
        self.set_cvar_once("qlx_protectPermissionLevel", "5")
        self.set_cvar_once("qlx_protectMuteVoting", "1")
        self.set_cvar_once("qlx_protectJoinMuteVoting", "1")
        self.set_cvar_once("qlx_protectAdminLevel", "5")
        self.set_cvar_once("qlx_protectPassLevel", "5")
        self.set_cvar_once("qlx_protectFTS", "5")
        self.set_cvar_once("qlx_protectPlayerPercForVote", "26")

        self.protectPermission = self.get_cvar("qlx_protectPermissionLevel", int)
        self.mapProtect = self.get_cvar("qlx_protectMapVoting", bool)

        # Commands: permission level is set using some of the Cvars. See the Cvars description at the top of the file.
        self.add_command("protect", self.cmd_protect, self.get_cvar("qlx_protectAdminLevel", int))
        self.add_command(("reload_protect", "load_protect"), self.cmd_load_protects,
                         self.get_cvar("qlx_protectAdminLevel", int))
        self.add_command("setpass", self.cmd_setpass, self.get_cvar("qlx_protectPassLevel", int))
        self.add_command("unsetpass", self.cmd_unsetpass, self.get_cvar("qlx_protectPassLevel", int))
        self.add_command(("forcets", "forceteamsize"), self.teamsize_force, self.get_cvar("qlx_protectFTS", int),
                         usage="<wanted_teamsize>")
        self.add_command(("protectversion", "pv"), self.protect_version, self.get_cvar("qlx_protectAdminLevel", int))
        self.add_command("protectlist", self.cmd_protect_list, 5)  # command for testing purposes
        
        # Opens Protect list container
        self.protect = []
        self.vote_count = [0, 0, 0]
        self.found_player = []

        # Loads the protect list.
        self.cmd_load_protects()

    # protect.py version checker. Thanks to iouonegirl for most of this section's code.
    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}.py"\
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
                        minqlx.console_command("echo {}".format([e]))
                return

    def protect_version(self, player, msg, channel):
        self.check_version(channel=channel)

    # Player Join actions. Version checker and join messages.
    @minqlx.delay(4)
    def player_loaded(self, player):
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)
        if self.get_cvar("qlx_protectJoinMapMessage", bool) and self.mapProtect:
            player.tell("^3Map voting during an active match is disabled on this server.")
        if self.get_cvar("qlx_protectJoinAfkMessage", bool) and self.get_cvar("qlx_protectAfkVoting", bool):
            player.tell("^3To vote someone to ^1Spectator ^3use ^4/cv afk <client id|name>^3 or"
                        "^4/cv spectate <client id>^3.")
        if self.get_cvar("qlx_protectJoinMuteVoting", bool) and self.get_cvar("qlx_protectMuteVoting", bool):
            player.tell("^3To ^1Mute ^3someone use ^4/cv mute <client id|name>."
                        "To ^1UnMute ^3use ^4/cv unmute <client id|name>.")

    # Search for a player name match using the supplied string
    def find_player(self, args):
        def string(name):
            found_player = None
            found_count = 0
            # Remove color codes from the supplied string
            player_name = self.clean_text(name).lower()
            # search through the list of connected players for a name match
            for p in self.players():
                if player_name in self.clean_text(p.name).lower():
                    # if match is found return player
                    found_player = p
                    found_count += 1
            # if only one match was found return player, player id
            if found_count == 1:
                return found_player
            # if more than one match is found return -2
            elif found_count > 1:
                return -2
            # if no match is found return -1
            else:
                return -1

        try:
            player = self.player(int(args))
            if player is None:
                player = -3
        except minqlx.NonexistentPlayerError:
            player = -3
        except ValueError:
            player = string(" ".join(args))
        if player in [-1, -2, -3]:
            pid = player
            sid = player
        else:
            pid = player.id
            sid = player.steam_id
        return [player, sid, pid]

    def clean_text(self, text):
        return re.sub(r"\^[0-9]", "", text)

    # Handles votes called: Kick protection, Map voting rejection during active matches, AFK voting,
    # and Mute/UnMute voting.
    def handle_vote_called(self, caller, vote, args):
        try:
            # Map Voting
            vote = vote.lower()
            if vote in ["map", "nextmap", "map_restart"] and self.mapProtect and self.game.state == "in_progress":
                caller.tell("^3Map voting is not allowed during an active match")
                return minqlx.RET_STOP_ALL
            # Kick Voting
            elif vote in ["kick", "clientkick"]:
                player = self.find_player(args)
                if player[0] in [-1, -2, -3]:
                    caller.tell("^1No matching player found")
                    return minqlx.RET_STOP_ALL
                if player[1] == minqlx.owner():
                    caller.tell("^2That's my master! I won't let this vote pass.")
                    return minqlx.RET_STOP_ALL
                if self.db.has_permission(player[1], self.protectPermission):
                    caller.tell("^2That player is too important on this server and can't be kicked.")
                    return minqlx.RET_STOP_ALL
                elif player[1] in self.protect:
                    caller.tell("^3That player is in the ^1kick protect^3 list.")
                    return minqlx.RET_STOP_ALL
            # Voting people to Spectator
            elif vote in ["afk", "spectate", "spec"]:
                if not self.get_cvar("qlx_protectAfkVoting", bool):
                    caller.tell("^3Voting players to spectator is not enabled on this server.")
                    return minqlx.RET_STOP_ALL
                player = self.find_player(args)
                if player[0] in [-1, -2, -3]:
                    caller.tell("^1No matching player found")
                    return minqlx.RET_STOP_ALL
                if player[0].team == "spectator":
                    caller.tell("That player is already in the spectators.")
                    return minqlx.RET_STOP_ALL
                self.callvote_to_spec(caller, vote, self.clean_text(player[0].name), player[2])
                return minqlx.RET_STOP_ALL
            # Voting to mute people
            elif vote == "mute" or vote == "silence":
                if not self.get_cvar("qlx_protectMuteVoting", bool):
                    caller.tell("^3Voting to mute players is not enabled on this server.")
                    return minqlx.RET_STOP_ALL
                player = self.find_player(args)
                if player[0] in [-1, -2, -3]:
                    caller.tell("^1No matching player found")
                    return minqlx.RET_STOP_ALL
                if player[1] == minqlx.owner():
                    caller.tell("^2That's my master! I won't let this vote pass.")
                    return minqlx.RET_STOP_ALL
                if self.db.has_permission(player[1], self.protectPermission):
                    caller.tell("^2That player is too important on this server and can't be muted.")
                    return minqlx.RET_STOP_ALL
                name = player[0].name
                self.callvote("mute {}".format(player[2]), "Mute {}?".format(self.clean_text(name)))
                minqlx.client_command(caller.id, "vote yes")
                self.msg("{}^7 called vote ^6mute {}".format(caller.name, name))
                return minqlx.RET_STOP_ALL
            # Voting to unMute people
            elif vote == "unmute" or vote == "unsilence":
                if not self.get_cvar("qlx_protectMuteVoting", bool):
                    caller.tell("^3Voting to mute/unmute players is not enabled on this server.")
                    return minqlx.RET_STOP_ALL
                player = self.find_player(args)
                if player[0] in [-1, -2, -3]:
                    caller.tell("^1No matching player found")
                    return minqlx.RET_STOP_ALL
                if int(caller.id) == player[2]:
                    caller.tell("^3Sorry, you cannot callvote to unmute yourself.")
                    return minqlx.RET_STOP_ALL
                name = player[0].name
                self.callvote("unmute {}".format(player[2]), "UnMute {}?".format(self.clean_text(name)))
                minqlx.client_command(caller.id, "vote yes")
                self.msg("{}^7 called vote ^6unmute {}".format(caller.name, name))
                return minqlx.RET_STOP_ALL
        except Exception as e:
            minqlx.console_print("^1protect.py handle_vote_called Exception: {}".format([e]))

    @minqlx.thread
    def callvote_to_spec(self, caller, vote, player_name, player_id):
        try:
            self.callvote("put {} spec".format(player_id), "Move {} to spectate?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called vote /cv {}".format(caller.name, vote))
            voter_perc = self.get_cvar("qlx_protectPlayerPercForVote", int)
            if voter_perc > 0:
                self.vote_count[0] = 1
                self.vote_count[1] = 0
                thread_number = random.randrange(0, 10000000)
                self.vote_count[2] = thread_number
                teams = self.teams()
                voters = len(teams["red"]) + len(teams["blue"])
                time.sleep(28.7)
                if self.vote_count[2] == thread_number and self.vote_count[0] / voters * 100 >= voter_perc and\
                        self.vote_count[0] > self.vote_count[1]:
                    self.force_vote(True)
            return
        except Exception as e:
            minqlx.console_print("^1protect.py callvote_to_spec Exception: {}".format([e]))

    # Checks for a protect.txt file and loads the entries if the file exists. Creates one if it doesn't.
    def cmd_load_protects(self, player=None, msg=None, channel=None):
        try:
            f = codecs.open(os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE), "r", "utf-8")
            lines = f.readlines()
            f.close()
            temp_list = []
            for player_id in lines:
                if player_id.startswith("#"):
                    continue
                try:
                    temp_list.append(int(player_id.split(None, 1)[0].strip('\n')))
                except:
                    continue
            self.protect = temp_list
            if player:
                player.tell("^3The protect list has been reloaded. ^1!protect list ^3 to see current load.")
        except IOError:
            try:
                m = codecs.open(os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE), "w", "utf-8")
                m.write("# This is a commented line because it starts with a '#'\n")
                m.write("# Enter every protect SteamID and name on a newline, format: SteamID Name\n")
                m.write("# The NAME is for a mental reference and may contain spaces.\n")
                m.write("# NAME will be added automatically if the protection is added with a client id when the"
                        " player is connected to the server.\n")
                m.write("{} ServerOwner\n".format(minqlx.owner()))
                m.close()
                temp_list = [int(minqlx.owner())]
                self.protect = temp_list
                if player:
                    player.tell("^3No ^1Protect^3 list was found so one was created and the server owner was added.")
            except Exception as e:
                if player:
                    player.tell("^1Error ^3reading and/or creating the Protect list: {}".format([e]))
                minqlx.console_print("^1Error ^3reading and/or creating the Protect list: {}".format([e]))
        except Exception as e:
            if player:
                player.tell("^1Error ^3reading the Protect list: {}".format([e]))
            minqlx.console_print("^1protect.py cmd_load_protects Exception: {}".format([e]))
        return minqlx.RET_STOP_EVENT

    # The PROTECT command: add, del, check, and list people.
    def cmd_protect(self, player, msg, channel):
        self.exec_protect(player, msg)
        return minqlx.RET_STOP_EVENT

    @minqlx.thread
    def exec_protect(self, player, msg):
        try:
            if len(msg) < 2:
                player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7|^2name^7>")
                return

            action = msg[1].lower()
            # Executes if msg begins with "!protect list"
            if action == "list":
                player_list = self.players()
                message = ["^5Protect List:"]
                file = os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE)
                try:
                    f = codecs.open(file, "r", "utf-8")
                except FileNotFoundError:
                    player.tell("^1Error ^3opening the Protect list file")
                    minqlx.console_print("^1Error ^3opening the Protect list file")
                    return
                except Exception as e:
                    player.tell("^1Error ^3reading the Protect list file: {}".format([e]))
                    minqlx.console_print("^1Error ^3reading the Protect list file: {}".format([e]))
                    return
                lines = f.readlines()
                f.close()
                for line in lines:
                    if line.startswith("#"):
                        continue
                    line = line.split(" ")
                    sid = int(line[0].strip("\n"))
                    if sid in player_list:
                        name = self.player(sid).name
                    else:
                        name = " ".join(line[1:]).strip("\n")
                    message.append("  ^7SteamID ^1{} ^7: ^4{}".format(sid, name))
                player.tell("\n".join(message))
                return

            if len(msg) < 3:
                player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7|^2name^7>")
                return
            target_player = self.find_player(" ".join(msg[2:]))
            if target_player[0] in [-1, -2, -3]:
                name = "Name not supplied"
                try:
                    sid = int(msg[2])
                    if len(msg[2]) == 17:
                        target_player[1] = sid
                        try:
                            name = self.db.lindex("minqlx:players:{}".format(msg[2]), 0)
                        except Exception as e:
                            minqlx.console_print("^1protect exec_protect Find DB Name Exception: {}".format([e]))
                except ValueError:
                    player.tell("^1No matching player found")
                    return
            else:
                name = target_player[0].name
            # Executes if msg begins with "!protect add"
            if action == "add":
                if target_player[1] in self.protect:
                    player.tell("^2{}^3 is already in the Protect list.".format(name))
                    self.update_line(player=player, add_name=[target_player[1], name])
                    return
                file = os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE)
                try:
                    h = codecs.open(file, "a", "utf-8")
                except FileNotFoundError:
                    player.tell("^1Error ^3opening the Protect list file")
                    minqlx.console_print("^1Error ^3opening the Protect list file")
                    return
                except Exception as e:
                    player.tell("^1Error ^3reading the Protect list file: {}".format([e]))
                    minqlx.console_print("^1Error ^3reading the Protect list file: {}".format([e]))
                    return
                h.write(str(target_player[1]) + " " + str(name) + "\n")
                h.close()
                self.protect.append(target_player[1])
                player.tell("^2{}^3 has been added to the Protect list.".format(name))
                return

            # Executes if msg begins with "!protect del"
            elif action == "del":
                file = os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE)
                try:
                    f = codecs.open(file, "r", "utf-8")
                except FileNotFoundError:
                    player.tell("^1Error ^3opening the Protect list file")
                    minqlx.console_print("^1Error ^3opening the Protect list file")
                    return
                except Exception as e:
                    player.tell("^1Error ^3reading the Protect list file: {}".format([e]))
                    minqlx.console_print("^1Error ^3reading the Protect list file: {}".format([e]))
                    return
                lines = f.readlines()
                f.close()
                for search_id in lines:
                    if search_id.startswith("#"):
                        continue
                    if target_player[1] == int(search_id.split(None, 1)[0]):
                        h = codecs.open(file, "w", "utf-8")
                        for line in lines:
                            if line[0] == "#":
                                h.write(line)
                            elif target_player[1] != int(line.split(None, 1)[0]):
                                h.write(line)
                        h.close()
                        if target_player[1] in self.protect:
                            self.protect.remove(target_player[1])
                        if target_player != "Name not supplied":
                            player.tell("^2{}^3 has been deleted from the Protect list.".format(name))
                        else:
                            player.tell("^2{}^3 has been deleted from the Protect list.".format(target_player[1]))
                        return
                if target_player != "Name not supplied":
                    player.tell("^2{}^3 is not in the protect list.".format(name))
                else:
                    player.tell("^2{}^3 is not in the protect list.".format(target_player[1]))
                return

            # Executes if msg begins with "!protect check"
            elif action == "check":
                if target_player[1] in self.protect:
                    if name != "Name not supplied":
                        player.tell("^2{}^3 is in the Protect list.".format(name))
                    else:
                        player.tell("^2{}^3 is in the protect list".format(target_player[1]))
                    return
                else:
                    if name != "Name not supplied":
                        player.tell("^2{}^3 is ^1NOT^3 in the Protect list.".format(name))
                    else:
                        player.tell("^2{}^3 is ^1NOT^3 in the Protect List.".format(target_player[1]))
                    return
            else:
                player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7|^2name^7>")
                return
        except Exception as e:
            minqlx.console_print("^1protect.py cmd_protect Exception: {}".format([e]))

    # Updates the protect.txt file with a player name if one was not previously saved when player was originally added.
    def update_line(self, player=None, add_name=None):
        if len(add_name) > 1:
            try:
                file = os.path.join(self.get_cvar("fs_homepath"), PROTECT_FILE)
                try:
                    f = codecs.open(file, "r", "utf-8")
                except FileNotFoundError:
                    player.tell("^1Error ^3opening the Protect list file in update_line")
                    minqlx.console_print("^1Error ^3opening the Protect list file in update_line")
                    return minqlx.RET_STOP_EVENT
                except Exception as e:
                    player.tell("^1Error ^3reading the Protect list file in update_line: {}".format([e]))
                    minqlx.console_print("^1Error ^3reading the Protect list file in update_line: {}".format([e]))
                    return minqlx.RET_STOP_EVENT
                lines = f.readlines()
                f.close()
                player_id = str(add_name[0])
                found = False
                try:
                    h = codecs.open(file, "w", "utf-8")
                    for line in lines:
                        current = line.split()
                        if line.startswith("#"):
                            h.write(line)
                        elif player_id == current[0]:
                            h.write(player_id + " " + add_name[1] + "\n")
                            found = True
                        else:
                            h.write(line)
                    if not found:
                        h.write(player_id + " " + add_name[1] + "\n")
                    h.close()
                    return minqlx.RET_STOP_EVENT
                except FileNotFoundError:
                    player.tell("^1Error ^3opening the Protect list file for writing in update_line")
                    minqlx.console_print("^1Error ^3opening the Protect list file for writing in update_line")
                    return minqlx.RET_STOP_EVENT
                except Exception as e:
                    player.tell("^1Error ^3reading the Protect list file for writing in update_line: {}"
                                .format([e]))
                    minqlx.console_print("^1Error ^3reading the Protect list file for writing in"
                                         " update_line: {}".format([e]))
                    return minqlx.RET_STOP_EVENT
            except Exception as e:
                minqlx.console_print("^1protect.py update_line Exception: {}".format([e]))
        return minqlx.RET_STOP_EVENT

    # Command used for testing: shows the contents of the self.protect string used to protect players from being kicked.
    def cmd_protect_list(self, player, msg, channel):
        player.tell("^6List^7: {}".format("^3, ^7".join(self.protect)))
        return minqlx.RET_STOP_EVENT

    # Sets a server join password
    def cmd_setpass(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^2<password>")
            return minqlx.RET_STOP_EVENT
        minqlx.console_command("set g_password \"{}\"".format(msg[1]))
        player.tell("^3Server join password is set to ^1{}.".format(msg[1]))
        return minqlx.RET_STOP_EVENT

    # Clears the server join password
    def cmd_unsetpass(self, player, msg, channel):
        minqlx.console_command("set g_password \"\"")
        player.tell("^3Server join password has been cleared.")
        return minqlx.RET_STOP_EVENT

    # Forces the teamsize to the desired size, puts all players to spectate if teamsize is less than players in team.
    def teamsize_force(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        try:
            wanted_teamsize = int(msg[1])
        except ValueError:
            player.tell("^1Unintelligible size.")
            return minqlx.RET_STOP_EVENT
        teamsize = self.get_cvar("teamsize")
        if int(teamsize) == wanted_teamsize:
            player.tell("^4The teamsize is already {}.".format(teamsize))
            return minqlx.RET_STOP_EVENT
        teams = self.teams()
        red_teamsize = len(teams["red"])
        blue_teamsize = len(teams["blue"])
        if red_teamsize <= wanted_teamsize and blue_teamsize <= wanted_teamsize:
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7.".format(wanted_teamsize))
        else:
            for client in teams["red"]:
                client.put("spectator")
            for client in teams["blue"]:
                client.put("spectator")
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7, players were put to spectator to allow the change."
                     .format(wanted_teamsize))
        return minqlx.RET_STOP_EVENT
