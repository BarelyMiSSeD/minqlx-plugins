# inviteonly.py is a plugin for minqlx to:
# -only allow players added to the invoteonly list to play on the server, if enabled
# created by BarelyMiSSeD on 2-24-16
#
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_inviteonlyAdmin "5" - Sets the minqlx server permisson level needed to add and remove someone from the invite only list.
qlx_invoteonlyAllowSpectator "0" - Set to "1" to allow spectators to remain on the server indefiniltely even when not on the invite only list.
qlx_inviteonlySpectatorTime "3" - Sets the amount of time (in minutes) a player can be a spectaror before being kicked if not on the invite only list.
                    Set qlx_invoteonlyAllowSpectator and qlx_inviteonlySpectatorTime to "0" to kick players immediately.
change notes: Added !aio and !dio commands for adding and deleting from the inviteonly list.
"""



import minqlx
import re
import threading
import requests
import datetime
import os

VERSION = "v1.04"
INVITEONLY_FILE = "inviteonly.txt"

class inviteonly(minqlx.Plugin):
    def __init__(self):
        # Cvars.
        self.set_cvar_once("qlx_inviteonlyAdmin", "5")
        self.set_cvar_once("qlx_invoteonlyAllowSpectator", "0")
        self.set_cvar_once("qlx_inviteonlySpectatorTime", "3")

        # monitored server occurrences
        self.add_hook("player_loaded", self.player_loaded)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("player_disconnect", self.handle_player_disconnect)

        # set script variable values
        self.allowSpec = int(self.get_cvar("qlx_invoteonlyAllowSpectator"))
        self.spectateTime = int(self.get_cvar("qlx_inviteonlySpectatorTime"))
        self.adminLevel = int(self.get_cvar("qlx_inviteonlyAdmin"))

        # commands
        self.add_command(("addinviteonly", "add_inviteonly", "aio"), self.cmd_inviteOnlyAdd, self.adminLevel)
        self.add_command(("delinviteonly", "del_inviteonly", "dio"), self.cmd_inviteOnlyDelete, self.adminLevel)
        self.add_command(("listinviteonly", "list_inviteonly", "iol"), self.cmd_inviteOnlyList, self.adminLevel)
        self.add_command(("reload_inviteonly", "load_inviteonly", "rlio"), self.cmd_loadInvites, self.adminLevel)
        self.add_command(("versioninviteonly", "version_inviteonly", "iov"), self.cmd_inviteOnlyVersion, self.adminLevel)
        self.add_command("iolist", self.cmd_IOList, 5) # command for testing purposes

        # Opens Invite Only list container
        self.inviteonly = []
        self.notOnIOList = []
        self.NotInvited = {}

        # Loads Invite Only list
        self.cmd_loadInvites()

    # inviteonly.py version checker. Thanks to iouonegirl for most of this section's code.
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

    def cmd_inviteOnlyVersion(self, player, msg, channel):
        self.check_version(channel=channel)

    # Command for testing: shows the contents of the self.inviteonly string used to allow only invited player to play.
    def cmd_IOList(self, player, msg, channel):
        player.tell("List: " + str(self.inviteonly))
        player.tell("NotOnIOList: " + str(self.notOnIOList))
        player.tell("Length: " + str(len(self.notOnIOList)))
        player.tell("{} {} {}".format(self.allowSpec, self.spectateTime, self.adminLevel))
        if self.spectateTime:
            player.tell("SpectateTime")
        if self.allowSpec:
            player.tell("AllowSpec")
        return minqlx.RET_STOP_EVENT

    # Checks the invite only list when a player connects to see if they are allowed to play on the server.
    def player_loaded(self, player):
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)
            return
        id = int(player.steam_id)
        if id not in self.inviteonly:
            if self.allowSpec:
                player.tell("^2Server^7: ^3You are not on the Invited Player list for this server. "
                            "Speak to a server admin to be added to the list or you will only be able to spectate.")
            elif self.spectateTime:
                player.tell("^2Server^7: ^3You are not on the Invited Player list for this server. "
                            "Speak to a server admin to be added to the list or you will be kicked in ^1{}^3 minute(s).".format(self.spectateTime))
                player.center_print("^2Server^7: ^3You are not on the Invited Player list for this server. "
                            "Speak to a server admin to be added to the list or you will be kicked in ^1{}^3 minute(s).".format(self.spectateTime))
                self.notOnIOList.append(id)
                name = player.clean_name
                timeJoined = str(id) + "time"
                now = datetime.datetime.now()
                self.NotInvited[str(id)] = name
                self.NotInvited[timeJoined] = now

                # Timer to kick uninvited player
                checkIOL = threading.Timer(10, self.check_nonInvite)
                checkIOL.start()
            else:
                player.tempban()
                self.msg("^2Server^7: ^4{} ^3is not on the Invite Only list and was kicked from the server.".format(player))

    def check_nonInvite(self):
        if len(self.notOnIOList) > 0:
            teams = self.teams()
            for id in self.notOnIOList:
                for client in teams["spectator"]:
                    if id == client.steam_id:
                        timeJoined = str(id) + "time"
                        now = datetime.datetime.now()
                        if (now - self.NotInvited[timeJoined]).total_seconds() >= (self.spectateTime * 60):
                            client.tempban()
                            self.msg("^2Server^7: ^4{} ^3is not on the Invite Only list and was kicked from the server.".format(client))
                            self.notOnIOList.remove(id)

            if len(self.notOnIOList) > 0:
                checkIOL = threading.Timer(10, self.check_nonInvite)
                checkIOL.start()
        else:
            self.NotInvited.clear()

    def handle_player_disconnect(self, player, reason):
        if player.steam_id in self.notOnIOList:
            self.notOnIOList.remove(player.steam_id)

    def handle_team_switch(self, player, old, new):
        if player.steam_id not in self.inviteonly and new in ['red', 'blue']:
            player.put("spectator")
            player.center_print("^2Server^7: ^6You are not on the Invite Only list of allowed players for this server. Speak to a server admin.")
            player.tell("^2Server^7: ^6You are not on the Invite Only list of allowed players for this server. Speak to a server admin.")
            if self.allowSpec:
                player.tell("^2Server^7: ^6Feel free to continue spectating.")
            else:
                player.tell("^2Server^7: ^6You will be kicked soon if an admin does not add you to the Invite Only list.")

    # Checks for a inviteonly.txt file and loads the entries if the file exists. Creates one if it doesn't.
    def cmd_loadInvites(self, player=None, msg=None, channel=None):
        try:
            f = open(os.path.join(self.get_cvar("fs_homepath"), INVITEONLY_FILE), "r")
            lines = f.readlines()
            f.close()
            tempList = []
            for id in lines:
                if id.startswith("#"): continue
                try:
                    tempList.append(int(id.split(None, 1)[0].strip('\n')))
                except:
                    continue
            self.inviteonly = tempList
        except IOError as e:
            try:
                m = open(os.path.join(self.get_cvar("fs_homepath"), INVITEONLY_FILE), "w")
                m.write("# This is a commented line because it starts with a '#'\n")
                m.write("# Enter every invite only SteamID and name on a newline, format: SteamID Name\n")
                m.write("# The NAME is for a mental reference and may contain spaces but is required.\n")
                m.write("# NAME will be added automatically if the invite only entry is added with a client id when the player is connected to the server.\n")
                m.write("{} ServerOwner\n".format(minqlx.owner()))
                m.close()
                tempList = []
                tempList.append(int(minqlx.owner()))
                self.inviteonly = tempList
                if player:
                    player.tell("^3No ^1Invite Only^3 list was found so one was created and the server owner was added.")
            except:
                if player:
                    player.tell("^1Error ^3reading and/or creating the Invite Only list: {}".format(e))
        except Exception as e:
            if player:
                player.tell("^1Error ^3reading the Invite Only list: {}".format(e))

    def cmd_inviteOnlyAdd(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^7<^2player id^7|^2steam id^7> <^2name^7>")
            return minqlx.RET_STOP_EVENT
        target_player = False
        file = os.path.join(self.get_cvar("fs_homepath"), INVITEONLY_FILE)
        try:
            with open(file) as test:
                pass
        except Exception as e:
            player.tell("^1Error ^3reading the Invite Only list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        # Checks to see if client_id or steam_id was used
        try:
            id = int(msg[1])
            if 0 <= id <= 63:
                try:
                    target_player = self.player(id)
                except minqlx.NonexistentPlayerError:
                    player.tell("^3There is no one on the server using that Client ID.")
                    return minqlx.RET_STOP_EVENT
                if not target_player:
                    player.tell("^3There is no one on the server using that Client ID.")
                    return minqlx.RET_STOP_EVENT
                id = int(target_player.steam_id)
            elif len(msg) < 3 or id < 0:
                player.tell("^3usage^7=^7<^2player id^7|^2steam id^7> <^2name^7>")
                return minqlx.RET_STOP_EVENT
            elif len(str(id)) != 17:
                player.tell("^3The STEAM ID given needs to be 17 digits in length.")
                return minqlx.RET_STOP_EVENT
        except ValueError:
            player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
            return minqlx.RET_STOP_EVENT

        if not target_player:
            target_player = " ".join(msg[2:])

        # Checks to see if the player is already on the Invite Only list and adds if not.
        if id in self.inviteonly:
            player.tell("^2{}^3 is already in the Invite Only list.".format(target_player))
            return minqlx.RET_STOP_EVENT

        h = open(file, "a")
        h.write(str(id) + " " + str(target_player) + "\n")
        h.close()
        self.inviteonly.append(id)
        player.tell("^2{}^3 has been added to the Invite Only list.".format(target_player))

        if id in self.notOnIOList:
            self.notOnIOList.remove(id)
            player_list = self.players()
            for p in player_list:
                if id == p.steam_id:
                    minqlx.console_command("tell {} ^3You have been added to the Invited Player list for this server. Enjoy your game!".format(p.id))
                    return minqlx.RET_STOP_EVENT

        return minqlx.RET_STOP_EVENT

    # Removes the desired player from the invite only list
    def cmd_inviteOnlyDelete(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=<^2player id^7|^2steam id^7>")
            return minqlx.RET_STOP_EVENT

        # Opens the invite only list file.
        file = os.path.join(self.get_cvar("fs_homepath"), INVITEONLY_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Invite Only list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        target_player = False

        # Checks to see if client_id or steam_id was used
        try:
            id = int(msg[1])
            if 0 <= id <= 63:
                try:
                    target_player = self.player(id)
                except minqlx.NonexistentPlayerError:
                    player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                    return minqlx.RET_STOP_EVENT
                if not target_player:
                    player.tell("^3There is no one on the server using that Client ID.")
                    return minqlx.RET_STOP_EVENT
                id = int(target_player.steam_id)
            elif id < 0:
                player.tell("^3usage^7=^7<^2player id^7|^2steam id^7> <^2name^7>")
                return minqlx.RET_STOP_EVENT
            elif len(str(id)) != 17:
                player.tell("^3The STEAM ID given needs to be 17 digits in length.")
                return minqlx.RET_STOP_EVENT
        except ValueError:
            player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
            return minqlx.RET_STOP_EVENT

        if target_player:
            messageName = target_player
        else:
            messageName = str(id)

        # Removes the identified player.
        for searchID in lines:
            if searchID.startswith("#"): continue
            if id == int(searchID.split(None, 1)[0]):
                h = open(file, "w")
                for line in lines:
                    if line[0] == "#":
                        h.write(line)
                    elif id != int(line.split(None, 1)[0]):
                        h.write(line)
                h.close()
                if id in self.inviteonly:
                    self.inviteonly.remove(id)
                player.tell("^2{}^3 has been deleted from the Invite Only list.".format(messageName))
                return minqlx.RET_STOP_EVENT

        player.tell("^2{}^3 is not on the Invite Only list.".format(messageName))
        return minqlx.RET_STOP_EVENT

    # List players in the invite only file
    def cmd_inviteOnlyList(self, player, msg, channel):
        player_list = self.players()
        if not player_list:
            player.tell("There are no players connected at the moment.")

        file = os.path.join(self.get_cvar("fs_homepath"), INVITEONLY_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Invite Only list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        list = "^5Invite Only List:\n"

        for line in lines:
            if line.startswith("#"): continue
            foundName = False
            words = line.split(" ")
            id = words[0]
            for p in player_list:
                if int(id) == p.steam_id:
                    foundName = p.name
            if not foundName:
                foundName = " ".join(words[1:]).strip("\n")

            if foundName:
                list += " ^7SteamID ^1{} ^7: ^3{}\n".format(id, foundName)
            else:
                list += " ^7SteamID ^1{} ^7: ^3No Name saved\n".format(id)

        player.tell(list[:-1])
        return minqlx.RET_STOP_EVENT