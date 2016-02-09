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
"""

import minqlx
import re
import threading

class protect(minqlx.Plugin):
    def __init__(self):
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("player_loaded", self.player_loaded)
        self.add_command("protect", self.cmd_protect, 4, usage="add|del|check|list <player id|steam id>")
        self.add_command("unsetpass", self.cmd_unsetpass, 5)
        self.add_command(("forcets", "forceteamsize"), self.teamsize_force, 4, usage="<wanted_teamsize>")

        # Cvars.
        self.set_cvar_once("qlx_protectMapVoting", "1")
        self.set_cvar_once("qlx_protectJoinMapMessage", "1")
        self.set_cvar_once("qlx_protectAfkVoting", "1")
        self.set_cvar_once("qlx_protectJoinAfkMessage", "1")
        self.set_cvar_once("qlx_protectPermissionLevel", "5")

        self.protectPermission = self.get_cvar("qlx_protectPermissionLevel")

        try:
            list = open(self.get_cvar("fs_homepath") + "/protect.txt").readlines()
            self.protect = []
            for i in range(len(list)):
                self.protect.append(int(list[i].strip('\n')))
        except:
            self.protect = []

    @minqlx.delay(4)
    def player_loaded(self, player):
        if self.get_cvar("qlx_protectJoinMapMessage", bool) and self.get_cvar("qlx_protectMapVoting", int) == 1:
            player.tell("^3Map voting during an active match is disabled on this server.")
        if self.get_cvar("qlx_protectJoinAfkMessage", bool) and  self.get_cvar("qlx_protectAfkVoting", int) == 1:
                player.tell("^3To vote someone to ^1Spectator ^3use ^4/cv afk <client id>^3 or"
                            "^4/cv spectate <client id>^3. Use ^4/players^3 in console to get client IDs.")

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

            self.callvote("put {} spec".format(player_id), "Move {} to the spectators?".format(player_name))
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL

    def cmd_protect(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7>")
            return minqlx.RET_STOP_EVENT

        file = self.get_cvar("fs_homepath") + "/protect.txt"
        try:
            with open(file) as test:
                pass
        except:
            m = open(file, "w+")
            m.close()
        action = msg[1].lower()
        target_player = None
        if action == "add":
            if len(msg) < 3: return minqlx.RET_USAGE
            try:
                id = int(msg[2])
                if 0 <= id <= 63:
                    target_player = self.player(id)
                    id = target_player.steam_id
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            except minqlx.NonexistentPlayerError:
                player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            f = open(file, "r")
            g = f.readlines()
            f.close()
            if id in self.protect:
                if not target_player:
                    player.tell("^2{}^3 is already in the Protect list.".format(target_player))
                else:
                    player.tell("^2{}^3 is already in the Protect list.".format(msg[2]))
                return minqlx.RET_STOP_EVENT

            h = open(file, "a")
            h.write(str(id) + "\n")
            h.close()
            self.protect.append(id)
            if target_player:
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
                    id = target_player.steam_id
            except ValueError:
                player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            except minqlx.NonexistentPlayerError:
                player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                return minqlx.RET_STOP_EVENT
            found_word = 0
            f = open(file, "r")
            g = f.readlines()
            f.close()
            for search_id in g:
                if int(id) == int(search_id):
                    found_word += 1
                if found_word == 1:
                    h = open(file, "w")
                    for line in g:
                        if int(id) != int(line):
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
                        id = target_player.steam_id
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
            for id in self.protect:
                replace = ""
                for p in player_list:
                    if id == p.steam_id:
                        replace = p.name
                if len(replace) >= 1:
                    list += "  ^7SteamID ^1{} ^7: {}\n".format(id, replace)
                else:
                    list += "  ^7SteamID ^1{} ^7: ^3Player not connected\n".format(id)
            player.tell(list[:-1])
            return minqlx.RET_STOP_EVENT
        else:
            player.tell("^3usage^7=^2add^7|^2del^7|^2check^7|^2list ^7<^2player id^7|^2steam id^7>")
            return minqlx.RET_STOP_EVENT

    def cmd_unsetpass(self, player, msg, channel):
        minqlx.console_command('set g_password ""')
        player.tell("^1Server password is unset.")

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
