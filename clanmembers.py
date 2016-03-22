# clanmembers.py is a plugin for minqlx to:
# -only allow players added to the Clan Members list to wear the Clan Tag(s) added to the clan tag list.
# -This is a modified and added to version of clan.py included with the minqlx bot.
# -There is no need to load clan.py if loading this plugin but loading it won't hurt.
# created by BarelyMiSSeD on 3-11-16
#
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_clanmembersAdmin "5" - Sets the minqlx server permisson level needed to admin the Clan Members and Clan Tag list.
qlx_clanmembersTagColors "0" - If on: Tag enforcement will check for exact color matching. If off: tag colors are ignored and only the text is compared. (0 = off, 1 = on)
qlx_clanmembersLetterCase "0" - If on: Tag enforcement will check for exact case matching. If off: upper/lower case is ignored. (0 = off, 1 = on)
qlx_clanmembersCheckSteamName "1" - Checks for clan tag(s) in player's steam name and renames the player without the clan tag. (0 = off, 1 = on)
"""

import minqlx
import re
import os
import requests

_re_remove_excessive_colors = re.compile(r"(?:\^.)+(\^.)")
_tag_key = "minqlx:players:{}:clantag"

VERSION = "v1.02"

CLAN_MEMBER_FILE = "clanmembers.txt"

class clanmembers(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_clanmembersAdmin", "5")
        self.set_cvar_once("qlx_clanmembersTagColors", "0")
        self.set_cvar_once("qlx_clanmembersLetterCase", "0")
        self.set_cvar_once("qlx_clanmembersCheckSteamName", "1")

        admin = int(self.get_cvar("qlx_clanmembersAdmin"))

        self.add_hook("player_loaded", self.player_loaded)
        self.add_hook("set_configstring", self.handle_set_configstring)
        self.add_hook("userinfo", self.handle_userinfo, priority=minqlx.PRI_HIGH)
        self.add_command(("clan", "setclan"), self.cmd_clan, usage="<clan_tag>", client_cmd_perm=0)
        self.add_command(("add_clanmember", "acm"), self.cmd_addClanMember, admin)
        self.add_command(("del_clanmember", "dcm", "remove_clanmember"), self.cmd_delClanMember, admin)
        self.add_command(("listclanmembers", "list_clanmembers", "cml"), self.cmd_listClanMembers, admin)
        self.add_command(("add_clantag", "act"), self.cmd_addClanTag, admin)
        self.add_command(("del_clantag", "dct", "remove_clantag"), self.cmd_delClanTag, admin)
        self.add_command(("listclantag", "listclantags", "ctl"), self.cmd_listClanTags, admin)
        self.add_command(("reload_clanmembers", "load_clanmembers", "rlcm"), self.cmd_loadClanTag, admin)
        self.add_command(("clanmembersversion", "clanmembers_version", "cmv"), self.cmd_clanMembersVersion, admin)


        # Opens clanTag list container
        self.clanTagMembers = []
        self.clanTag = []

        # Loads the clan tag list.
        self.cmd_loadClanTag()

        self.tagEnforced = False

        #Unload the clan command if the default minqlx clan.py is loaded on the server
        self.unload_overlapping_commands()

    @minqlx.delay(1)
    def unload_overlapping_commands(self):
        try:
            clan = minqlx.Plugin._loaded_plugins['clan']
            remove_commands = set(['clan'])
            for cmd in clan.commands.copy():
                if remove_commands.intersection(cmd.name):
                    clan.remove_command(cmd.name, cmd.handler)
        except Exception as e:
            pass

    # clanmembers.py version checker. Thanks to iouonegirl for most of this section's code.
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

    def cmd_clanMembersVersion(self, player, msg, channel):
        self.check_version(channel=channel)

    #@minqlx.delay(1)
    def player_loaded(self, player):
        #If the owner connects the script only checks for updates.
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)
            #return
        if self.get_cvar("qlx_clanmembersCheckSteamName", bool):
            self.cmd_checkname(player)

    @minqlx.delay(2)
    def cmd_checkname(self, player, changed=False):
        self.tagEnforced = False
        #The clan tag being protected is checked against player's name if the player is not in the clan members list.
        if player.steam_id not in self.clanTagMembers:
            if changed:
                nameWords = str(changed["name"]).split(" ")
            else:
                nameWords = str(player).split(" ")
            colors = self.get_cvar("qlx_clanmembersTagColors", bool)
            case = self.get_cvar("qlx_clanmembersLetterCase", bool)
            slot = 0
            #Checks the player's name angainst protected tags if tag enforcement is not color or case specific.
            if not colors and not case:
                tempList = []
                tempName = []
                for word in nameWords:
                    tempName.append(self.clean_text(word).lower())
                for tags in self.clanTag:
                    tempList.append(self.clean_text(tags).lower())
                for check in tempName:
                    if check in tempList:
                        player.tell("^3Your name cannot include {} tag on in this server and you have been renamed exculding the tag.".format(check))
                        nameWords.pop(slot)
                        if len(nameWords) == 0: nameWords = ['^6Change','^6Your','^6Steam','^6Name']
                        player.name = " ".join(nameWords)
                        self.tagEnforced = True
                    slot += 1
            #Checks the player's name angainst protected tags if tag enforcement is not color specific but is case specific.
            elif not colors:
                tempList = []
                tempName = []
                for word in nameWords:
                    tempName.append(self.clean_text(word))
                for tags in self.clanTag:
                    tempList.append(self.clean_text(tags))
                for check in tempName:
                    if check in tempList:
                        player.tell("^3Your name cannot include {} tag on in this server and you have been renamed exculding the tag.".format(check))
                        nameWords.pop(slot)
                        if len(nameWords) == 0: nameWords = ['^6Change','^6Your','^6Steam','^6Name']
                        player.name = " ".join(nameWords)
                        self.tagEnforced = True
                    slot += 1
            #Checks the player's name angainst protected tags if tag enforcement is not case specific but is color specific.
            elif not case:
                tempList = []
                tempName = []
                for word in nameWords:
                    tempName.append(word.lower())
                for tags in self.clanTag:
                    tempList.append(tags.lower())
                for check in tempName:
                    if check in tempList:
                        player.tell("^3Your name cannot include {} tag on in this server and you have been renamed exculding the tag.".format(check))
                        nameWords.pop(slot)
                        if len(nameWords) == 0: nameWords = ['^6Change','^6Your','^6Steam','^6Name']
                        player.name = " ".join(nameWords)
                        self.tagEnforced = True
                    slot += 1
            #Checks the player's name angainst protected tags if tag enforcement is case and color specific.
            elif cleanTag in self.clanTag or tag in self.clanTag:
                for check in nameWords:
                    if check in self.clanTag:
                        player.tell("^3Your name cannot include {} tag on in this server and you have been renamed exculding the tag.".format(check))
                        nameWords.pop(slot)
                        if len(nameWords) == 0: nameWords = ['^6Change','^6Your','^6Steam','^6Name']
                        player.name = " ".join(nameWords)
                        self.tagEnforced = True
                    slot += 1

    def handle_userinfo(self, player, changed):
        # Make sure we're not doing anything if our script set the name.
        if self.tagEnforced:
            self.tagEnforced = False
            return minqlx.RET_STOP_EVENT

        if "name" in changed and self.get_cvar("qlx_clanmembersCheckSteamName", bool):
            self.cmd_checkname(player, changed)

    def handle_set_configstring(self, index, value):
        # The engine strips cn and xcn, so we can safely append it
        # without having to worry about duplicate entries.
        if not value: # Player disconnected?
            return
        elif 529 <= index < 529 + 64:
            try:
                player = self.player(index - 529)
            except minqlx.NonexistentPlayerError:
                return
            if not player:
                # This happens when someone connects, but the player
                # has yet to be properly initialized. We can safely
                # skip it because the clan will be set later.
                return
            tag_key = _tag_key.format(player.steam_id)
            if tag_key in self.db:
                return value + "\\cn\\{0}\\xcn\\{0}".format(self.db[tag_key])

    def cmd_clan(self, player, msg, channel):
        index = 529 + player.id
        tag_key = _tag_key.format(player.steam_id)
        
        if len(msg) < 2:
            if tag_key in self.db:
                del self.db[tag_key]
                cs = minqlx.parse_variables(minqlx.get_configstring(index), ordered=True)
                del cs["cn"]
                del cs["xcn"]
                new_cs = "".join(["\\{}\\{}".format(key, cs[key]) for key in cs]).lstrip("\\")
                minqlx.set_configstring(index, new_cs)
                player.tell("^3The clan tag has been cleared.")
            else:
                player.tell("^3Usage to set a clan tag: ^6{} <clan_tag>".format(msg[0]))
            return minqlx.RET_STOP_EVENT

        cleanTag = self.clean_text(msg[1])
        if len(cleanTag) > 5:
            player.tell("^3The clan tag can only be at most 5 characters long, excluding colors.")
            return minqlx.RET_STOP_EVENT

        tag = self.clean_tag(msg[1])

        #The clan tag being added is checked if the player is not in the clan members list.
        if player.steam_id not in self.clanTagMembers:
            colors = self.get_cvar("qlx_clanmembersTagColors", bool)
            case = self.get_cvar("qlx_clanmembersLetterCase", bool)
            #Checks the tag if tag enforcement is not color or case specific.
            if not colors and not case:
                tempList = []
                for tags in self.clanTag:
                    tempList.append(self.clean_text(tags).lower())
                if cleanTag.lower() in tempList:
                    player.tell("^3You must be added to the clan members list to put that tag on in this server.")
                    return minqlx.RET_STOP_EVENT
            #Checks the tag if tag enforcement is not color specific but is case specific.
            elif not colors:
                tempList = []
                for tags in self.clanTag:
                    tempList.append(self.clean_text(tags))
                if cleanTag in tempList:
                    player.tell("^3You must be added to the clan members list to put that tag on in this server.")
                    return minqlx.RET_STOP_EVENT
            #Checks the tag if tag enforcement is not case specific but is color specific.
            elif not case:
                tempList = []
                for tags in self.clanTag:
                    tempList.append(tags.lower())
                if tag.lower() in tempList:
                    player.tell("^3You must be added to the clan members list to put that tag on in this server.")
                    return minqlx.RET_STOP_EVENT
            #Checks the tag if tag enforcement is case and color specific.
            elif cleanTag in self.clanTag or tag in self.clanTag:
                player.tell("^3You must be added to the clan members list to put that tag on in this server.")
                return minqlx.RET_STOP_EVENT
        
        # If the player already has a clan, we need to edit the current
        # configstring. We can't just append cn and xcn.
        cs = minqlx.parse_variables(minqlx.get_configstring(index), ordered=True)
        cs["xcn"] = tag
        cs["cn"] = tag
        new_cs = "".join(["\\{}\\{}".format(key, cs[key]) for key in cs])
        minqlx.set_configstring(index, new_cs)
        self.db[tag_key] = tag
        self.msg("{} changed clan tag to {}".format(player, tag))
        return minqlx.RET_STOP_EVENT

    def clean_tag(self, tag):
        """Removes excessive colors and only keeps the one that matters."""
        def sub_func(match):
            return match.group(1)

        return _re_remove_excessive_colors.sub(sub_func, tag)

    def cmd_loadClanTag(self, player=None, msg=None, channel=None):
        try:
            f = open(os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE), "r")
            lines = f.readlines()
            f.close()
            tempList = []
            tempTag = []
            tempClean = []
            for id in lines:
                if id.startswith("#"): continue
                elif id.startswith("C"):
                    tags = id.split(" ")
                    count = len(tags) - 1
                    while count > 0:
                        tempTag.append(tags[count].strip("\n"))
                        tempClean.append(self.clean_text(tags[count].strip("\n")))
                        count -= 1
                    self.clanTag = tempTag
                    continue
                try:
                    tempList.append(int(id.split(None, 1)[0].strip('\n')))
                except:
                    continue
            self.clanTagMembers = tempList
            if player:
                player.tell("^3The clan tag list has been reloaded. ^1!clantag_list ^3 to see current load.")
        except IOError as e:
            try:
                m = open(os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE), "w")
                m.write("# This is a commented line because it starts with a '#'\n")
                m.write("# Enter every protect SteamID and name on a newline, format: SteamID Name\n")
                m.write("# The NAME is for a mental reference and may contain spaces.\n")
                m.write("# NAME will be added automatically if the clan tag member is added with a client id when the player is connected to the server.\n")
                m.write("ClanTag(s):\n")
                m.write("{} ServerOwner\n".format(minqlx.owner()))
                m.close()
                tempList = []
                tempList.append(int(minqlx.owner()))
                self.clanTagMembers = tempList
                if player:
                    player.tell("^3No ^1Clan Tag^3 list was found so one was created and the server owner was added.\n"
                                "Use !addtag to add your clan's tag. !acm to add clantag members.")
            except:
                if player:
                    player.tell("^1Error ^3reading and/or creating the Clan Tag list: {}".format(e))
        except Exception as e:
            if player:
                player.tell("^1Error ^3reading the Clan Tag list: {}".format(e))
        return minqlx.RET_STOP_EVENT

    def cmd_addClanMember(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=^7<^2player id^7|^2steam id^7> <^2name^7>")
            return minqlx.RET_STOP_EVENT
        target_player = False
        file = os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE)
        try:
            with open(file) as test:
                pass
        except Exception as e:
            player.tell("^1Error ^3reading the Clan Members list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        # Checks to see if client_id or steam_id was used
        try:
            id = int(msg[1])
            if 0 <= id <= 63:
                try:
                    target_player = self.player(id)
                except minqlx.NonexistentPlayerError:
                    player.tell("^3There is no player using that client ID. Please check the client ID and try again.")
                    return minqlx.RET_STOP_EVENT
                if not target_player:
                    player.tell("^3There is no player using that client ID. Please check the client ID and try again.")
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

        # Checks to see if the player is already on the Clan Members list and adds if not.
        if id in self.clanTagMembers:
            player.tell("^2{}^3 is already in the Clan Member list.".format(target_player))
            return minqlx.RET_STOP_EVENT

        h = open(file, "a")
        h.write(str(id) + " " + str(target_player) + "\n")
        h.close()
        self.clanTagMembers.append(id)
        player.tell("^2{}^3 has been added to the Clan Member list.".format(target_player))

        return minqlx.RET_STOP_EVENT

    # Removes the desired player from the Clan Members list
    def cmd_delClanMember(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=<^2player id^7|^2steam id^7>")
            return minqlx.RET_STOP_EVENT

        # Opens the Clan Members list file.
        file = os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Clan Member list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        target_player = False

        # Checks to see if client_id or steam_id was used
        try:
            id = int(msg[1])
            if 0 <= id <= 63:
                try:
                    target_player = self.player(id)
                except minqlx.NonexistentPlayerError:
                    player.tell("^3There is no player using that client ID. Please check the client ID and try again.")
                    return minqlx.RET_STOP_EVENT
                if not target_player:
                    player.tell("^3There is no player using that client ID. Please check the client ID and try again.")
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
            if searchID.startswith("#") or searchID.startswith("C"): continue
            if id == int(searchID.split(None, 1)[0]):
                h = open(file, "w")
                for line in lines:
                    if line[0] == "#" or line[0] == "C":
                        h.write(line)
                    elif id != int(line.split(None, 1)[0]):
                        h.write(line)
                h.close()
                if id in self.clanTagMembers:
                    self.clanTagMembers.remove(id)
                player.tell("^2{}^3 has been deleted from the Clan Member list.".format(messageName))
                return minqlx.RET_STOP_EVENT

        player.tell("^2{}^3 is not on the Clan Member list.".format(messageName))
        return minqlx.RET_STOP_EVENT

    # List players in the Clan Members file
    def cmd_listClanMembers(self, player, msg, channel):
        player_list = self.players()
        if not player_list:
            player.tell("There are no players connected at the moment.")

        file = os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Clan Member file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        list = "^5Clan Member List:\n"

        for line in lines:
            if line.startswith("#") or line.startswith("C"): continue
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

    def cmd_addClanTag(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=<^2clan_tag^7>")
            return minqlx.RET_STOP_EVENT

        if len(self.clean_text(msg[1])) > 5:
            player.tell("^3The clan tag can only be at most 5 characters long, excluding colors.")
            return minqlx.RET_STOP_EVENT 

        file = os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Clan Members file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        tag = msg[1]

        # Checks to see if the clan tag is already in the list and adds if not.
        if tag in self.clanTag:
            player.tell("^2{}^3 is already in the Clan Tag list.".format(tag))
            return minqlx.RET_STOP_EVENT

        # Adds the new clan tag.
        self.clanTag.append(tag)
        h = open(file, "w")
        for line in lines:
            if line[0] == "C":
                h.write("ClanTag(s): " + " ".join(self.clanTag) + "\n")
            else:
                h.write(line)
        h.close()

        player.tell("^2{}^3 has been added to the Clan Tag list.".format(tag))
        return minqlx.RET_STOP_EVENT

    # Removes the desired clan tag from the list
    def cmd_delClanTag(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7=<^2clan_tag^7>")
            return minqlx.RET_STOP_EVENT

        file = os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Clan Member list file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        tag = msg[1]

        # Checks to see if the clan tag is already in the list.
        if tag not in self.clanTag:
            player.tell("^2{}^3 is not in the Clan Tag list.".format(tag))
            return minqlx.RET_STOP_EVENT

        # Removes the clan tag.
        self.clanTag.remove(tag)
        h = open(file, "w")
        for line in lines:
            if line[0] == "C":
                h.write("ClanTag(s): " + " ".join(self.clanTag) + "\n")
            else:
                h.write(line)
        h.close()

        player.tell("^2{}^3 has been removed from the Clan Tag list.".format(tag))
        return minqlx.RET_STOP_EVENT

    # List Clan Tags in Clan Member file
    def cmd_listClanTags(self, player, msg, channel):
        
        file = os.path.join(self.get_cvar("fs_homepath"), CLAN_MEMBER_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Clan Member file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        list = "^5Clan Tag List^7: "

        for line in lines:
            if line.startswith("#"): continue
            elif line.startswith("C"):
                list += " ".join(line.split(" ")[1:]).strip("\n")

        player.tell(list)
        return minqlx.RET_STOP_EVENT