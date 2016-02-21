# protect.py is a plugin for minqlx to:
# -protect selected players from being kicked using a callvote, if enabled
# -protect from mapvoting during an active match, if enabled
# -allow any player, even those on the protected list, to be put to spectator if the AFK vote passes, if enabled.
# created by BarelyMiSSeD on 11-10-15
# 
"""
Set these cvars:
qlx_protectMapVoting  - Enabling does not allow map voting during match play but does not effect map voting during warm-up
qlx_protectAfkVoting  - Enabling will allow players to be voted into spectator
qlx_protectJoinMapMessage - Sends join message to players if map voting protection is enabled
qlx_protectJoinAfkMessage - Sends join message to players if voting players to spectator is enabled
qlx_protectPermissionLevel - Sets the lowest level bot permission level to  automatically protect
qlx_protectMuteVoting - Allows muting and unmuting of a player.
qlx_protectJoinMuteVoting - Sends join message to players if mute voting is enabled.
"""

import minqlx
import re
import threading
import requests

VERSION = "v1.02"

class protect(minqlx.Plugin):
    def __init__(self):
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("player_loaded", self.player_loaded)
        self.add_command("protect", self.cmd_protect, 4, usage="add|del|check|list <player id|steam id> |name|")
        self.add_command("setpass", self.cmd_setpass, 5)
        self.add_command("unsetpass", self.cmd_unsetpass, 5)
        self.add_command(("forcets", "forceteamsize"), self.teamsize_force, 4, usage="<wanted_teamsize>")
        self.add_command("protectlist", self.cmd_protectList, 5)
        self.add_command("protectfile", self.cmd_protectReadFile, 5)

        # Cvars.
        self.set_cvar_once("qlx_protectMapVoting", "1")
        self.set_cvar_once("qlx_protectJoinMapMessage", "1")
        self.set_cvar_once("qlx_protectAfkVoting", "1")
        self.set_cvar_once("qlx_protectJoinAfkMessage", "1")
        self.set_cvar_once("qlx_protectPermissionLevel", "5")
        self.set_cvar_once("qlx_protectMuteVoting", "1")
        self.set_cvar_once("qlx_protectJoinMuteVoting", "1")

        self.protectPermission = self.get_cvar("qlx_protectPermissionLevel")

        try:
            list = open(self.get_cvar("fs_homepath") + "/protect.txt").readlines()
            self.protect = []
            for i in list:
                self.protect.append(int(i.split(None, 1)[0].strip('\n')))
        except:
            self.protect = []

    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}.py".format(self.__class__.__name__)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^7Currently using  BarelyMiSSeD's ^6{}^7 plugin ^1outdated^7 version ^6{}^7.".format(self.__class__.__name__, VERSION))
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^7Currently using BarelyMiSSeD's  latest ^6{}^7 plugin version ^6{}^7.".format(self.__class__.__name__, VERSION))
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    #time.sleep(15)
                    try:
                        player.tell("^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                    except Exception as e: minqlx.console_command("echo {}".format(e))
                return

    @minqlx.delay(4)
    def player_loaded(self, player):
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)
        if self.get_cvar("qlx_protectJoinMapMessage", bool) and self.get_cvar("qlx_protectMapVoting", bool):
            player.tell("^3Map voting during an active match is disabled on this server.")
        if self.get_cvar("qlx_protectJoinAfkMessage", bool) and  self.get_cvar("qlx_protectAfkVoting", bool) or self.get_cvar("qlx_protectJoinMuteVoting", bool) and  self.get_cvar("qlx_protectMuteVoting", bool):
                if self.get_cvar("qlx_protectJoinAfkMessage", bool) and self.get_cvar("qlx_protectJoinMuteVoting", bool):
                    player.tell("^3To vote someone to ^1Spectator ^3use ^4/cv afk <client id>^3 or"
                            "^4/cv spectate <client id>^3. To ^1Mute ^3someone use ^4/cv mute <client id>^3."
                            "To ^1UnMute ^3use ^4/cv unmute <client id>^3. Use ^4/players^3 in console to get client IDs.")
                elif self.get_cvar("qlx_protectJoinAfkMessage", bool):
                    player.tell("^3To vote someone to ^1Spectator ^3use ^4/cv afk <client id>^3 or"
                            "^4/cv spectate <client id>^3. Use ^4/players^3 in console to get client IDs.")
                elif self.get_cvar("qlx_protectJoinMuteVoting", bool):
                    player.tell("^3To ^1Mute ^3someone use ^4/cv mute <client id>."
                            "To ^1UnMute ^3use ^4/cv unmute <client id>. Use ^4/players^3 in console to get client IDs.")

    def handle_vote_called(self, caller, vote, args):
        if vote.lower() == "kick" or vote.lower() == "clientkick":
            try:
                client_id = int(args)
                target_player = self.player(client_id)
            except ValueError:
                target_player = self.player(args)
            ident = target_player.steam_id
            perm = self.db.get_permission(ident)
            if ident == minqlx.owner():
                caller.tell("^2That's my master! I won't let this vote pass.")
                return minqlx.RET_STOP_ALL
            elif int(perm) >= int(self.protectPermission):
                caller.tell("^2That player is too important on this server and can't be kicked.")
                return minqlx.RET_STOP_ALL
            elif ident in self.protect:
                caller.tell("^3That player is in the ^1kick protect^3 list.")
                return minqlx.RET_STOP_ALL
        elif vote.lower() == "map" and self.get_cvar("qlx_protectMapVoting", int) == 1:
            if self.game.state == "in_progress":
                caller.tell("^3Map voting is not allowed during an active match")
                return minqlx.RET_STOP_ALL
        elif vote.lower() == "spectate" or vote.lower() == "afk":
            if self.get_cvar("qlx_protectAfkVoting", int) == 0:
                caller.tell("^3Voting players to spectator is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL

            if self.player(int(args)).team == "spectator":
                caller.tell("That player is already in the spectators.")
                return minqlx.RET_STOP_ALL
            self.callvote("put {} spec".format(player_id), "Move {} to spectate?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL
        elif vote.lower() == "mute" or vote.lower() == "silence":
            if self.get_cvar("qlx_protectMuteVoting", int) == 0:
                caller.tell("^3Voting to mute players is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL
            ident = self.player(int(args)).steam_id
            perm = self.db.get_permission(ident)
            if ident == minqlx.owner():
                caller.tell("^2That's my master! I won't let this vote pass.")
                return minqlx.RET_STOP_ALL
            elif int(perm) >= int(self.protectPermission):
                caller.tell("^2That player is too important on this server and can't be muted.")
                return minqlx.RET_STOP_ALL
            self.callvote("mute {}".format(player_id), "Mute {}?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL
        elif vote.lower() == "unmute" or vote.lower() == "unsilence":
            if self.get_cvar("qlx_protectMuteVoting", int) == 0:
                caller.tell("^3Voting to mute/unmute players is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL
            if int(caller.id) == int(player_id):
                caller.tell("^3Sorry, you cannot callvote to unmute yourself.")
                return minqlx.RET_STOP_ALL
            self.callvote("unmute {}".format(player_id), "UnMute {}?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL

    def cmd_protect(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
            return minqlx.RET_STOP_EVENT

        file = self.get_cvar("fs_homepath") + "/protect.txt"
        try:
            with open(file) as test:
                pass
        except:
            m = open(file, "w+")
            m.close()
        action = msg[1].lower()
        target_player = False
        if action == "add":
            if len(msg) < 3:
                player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
                return minqlx.RET_STOP_EVENT
            try:
                id = int(msg[2])
                if 0 <= id <= 63:
                    target_player = self.player(id)
                    id = int(target_player.steam_id)
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            except minqlx.NonexistentPlayerError:
                player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            if len(str(id)) != 17:
                player.tell("^3The STEAM ID given needs to be 17 digits in length.")
                return minqlx.RET_STOP_EVENT

            if id in self.protect:
                if target_player:
                    player.tell("^2{}^3 is already in the Protect list.".format(target_player))
                    message = "{} {}".format(id, target_player).split()
                else:
                    player.tell("^2{}^3 is already in the Protect list.".format(msg[2]))
                    message = msg[2:]
                self.updateLine(player, message)
                return minqlx.RET_STOP_EVENT

            if not target_player:
                target_player = "Name not supplied"

            h = open(file, "a")
            h.write(str(id) + " " + str(target_player) + "\n")
            h.close()
            self.protect.append(id)
            if target_player != "Name not supplied":
                player.tell("^2{}^3 has been added to the Protect list.".format(target_player))
            else:
                player.tell("^2{}^3 has been added to the Protect list.".format(id))
            return minqlx.RET_STOP_EVENT

        elif action == "del":
            if len(msg) < 3: return minqlx.RET_USAGE
            try:
                id = int(msg[2])
                if 0 <= id <= 63:
                    target_player = self.player(id)
                    id = int(target_player.steam_id)
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            except minqlx.NonexistentPlayerError:
                player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            f = open(file, "r")
            lines = f.readlines()
            f.close()
            for search_id in lines:
                if id == int(search_id.split(None, 1)[0]):
                    h = open(file, "w")
                    for line in lines:
                        if id != int(line.split(None, 1)[0]):
                            h.write(line)
                    h.close()
                    if id in self.protect:
                        self.protect.remove(id)
                    if target_player:
                        player.tell("^2{}^3 has been deleted from the Protect list.".format(target_player))
                    else:
                        player.tell("^2{}^3 has been deleted from the Protect list.".format(id))
                    return minqlx.RET_STOP_EVENT
            if target_player:
                player.tell("^2{}^3 is not in the protect list.".format(target_player))
            else:
                player.tell("^2{}^3 is not in the protect list.".format(id))
            return minqlx.RET_STOP_EVENT

        elif action == "check":
            if len(msg) < 3: return minqlx.RET_USAGE
            try:
                id = int(msg[2])
                if 0 <= id <= 63:
                    target_player = self.player(id)
                    if target_player:
                        id = int(target_player.steam_id)
                    else:
                        player.tell("^3That client ID is not on the server.")
                        return minqlx.RET_STOP_EVENT
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            except minqlx.NonexistentPlayerError:
                player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            if id in self.protect:
                if target_player:
                    player.tell("^2{}^3 is in the Protect list.".format(target_player))
                else:
                    player.tell("^2{}^3 is in the protect list".format(id))
                return minqlx.RET_STOP_EVENT
            else:
                if target_player:
                    player.tell("^2{}^3 is ^1NOT^3 in the Protect list.".format(target_player))
                else:
                    player.tell("^2{}^3 is ^1NOT^3 in the Protect List.".format(id))
                return minqlx.RET_STOP_EVENT

        elif action == "list":
            player_list = self.players()
            if not player_list:
                player.tell("There are no players connected at the moment.")
            list = "^7Protect List:\n"
            f = open(file, "r")
            g = f.readlines()
            f.close()
            for line in g:
                count = 1
                foundName = "None"
                foundID = False
                for word in line.split():
                    if count == 1:
                        id = word
                        count += 1
                        for p in player_list:
                            if int(id) == p.steam_id:
                                foundName = p.name
                                foundID = True
                    elif count == 2 and not foundID:
                        foundName = word
                        count += 1
                    elif count > 2 and not foundID:
                        foundName = foundName + " " + word
                if foundName == "None":
                    list += "  ^7SteamID ^1{} ^7: ^3No Name saved : ^3Player not connected\n".format(id)
                elif foundID:
                    list += "  ^7SteamID ^1{} ^7: ^3{}\n".format(id, foundName)
                else:
                    list += "  ^7SteamID ^1{} ^7: ^3{} : ^3Player not connected\n".format(id, foundName)

            player.tell(list[:-1])
            return minqlx.RET_STOP_EVENT
        else:
            player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7> |name|")
            return minqlx.RET_STOP_EVENT

    def updateLine(self, player, message):
        if len(message) > 1:
            file = self.get_cvar("fs_homepath") + "/protect.txt"
            f = open(file, "r")
            lines = f.readlines()
            f.close()
            id = int(message[0])
            for checkID in lines:
                check = checkID.split()
                if id == int(check[0]) and len(check) == 1:
                    h = open(file, "w")
                    for line in lines:
                        if id == int(line.split(None, 1)[0]):
                            save = ""
                            for word in message:
                                save += word + " "
                            save += "\n"
                            h.write(save)
                        else:
                            h.write(line)
                    h.close()
                    return

    def cmd_protectList(self, player, msg, channel):
        player.tell("List: " + str(self.protect))

    def cmd_protectReadFile(self, player, msg, channel):
        f = open(self.get_cvar("fs_homepath") + "/protect.txt", "r").readlines()
        num = 1
        for line in f:
            words = line.split()
            part1 = words[0]
            part2 = ""
            player.tell("length: {}".format(len(words)))
            if len(words) > 2:
                count = 0
                for word in words:
                    if count > 0:
                        part2 += " " + word
                    count += 1
            elif len(words) > 1:
                part2 = words[1]
            #for word in line.split():
            #    if count == 1:
            #        part1 = word
            #        count += 1
            #    else:
            #        part2 += " " + word
            player.tell("^3Line {}: Steam ID - {} :: Name - {}".format(num, part1, part2))
            num += 1

    def cmd_setpass(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^2<password>")
            return minqlx.RET_STOP_EVENT

        password = str(msg[1])
        minqlx.console_command("set g_password {}".format(password))
        player.tell("^3Server password is set to ^1{}.".format(password))

    def cmd_unsetpass(self, player, msg, channel):
        minqlx.console_command('set g_password ""')
        player.tell("^3Server password is unset.")

    def teamsize_force(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            wanted_teamsize = int(msg[1])
        except ValueError:
            player.tell("^7Unintelligible size.")
            return minqlx.RET_STOP_EVENT

        teams = self.teams()
        teamsize = self.get_cvar("teamsize")
        if int(teamsize) == wanted_teamsize:
            player.tell("^4The teamsize is already {}.".format(teamsize))
            return minqlx.RET_STOP_EVENT

        red_teamsize = len(teams["red"])
        blue_teamsize = len(teams["blue"])
        if int(red_teamsize) <= wanted_teamsize and int(blue_teamsize) <= wanted_teamsize:
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7.".format(wanted_teamsize))
        else:
            for player in teams["red"]:
                player.put("spectator")
            for player in teams["blue"]:
                player.put("spectator")
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7, players were put to spectator to allow the change.".format(wanted_teamsize))
        return minqlx.RET_STOP_EVENT