# votelimiter.py is a plugin for minqlx to:
# -limit what players are allowed to callvote.
# -This script does not appear to interfere with any votes (custom or not) managed my other scripts.
# created by BarelyMiSSeD on 7-29-16
# 
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_votelimiterAdmin "5" - Sets the minqlx server permisson level needed to add and remove Allowed Votes from the list.
"""

import minqlx
import os
import requests

VERSION = "v1.00"
VOTELIMITER_FILE = "votelimiter.txt"

class votelimiter(minqlx.Plugin):
    def __init__(self):
        # Cvars.
        self.set_cvar_once("qlx_votelimiterAdmin", "5")
        
        # monitored server occurrences
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        
        # commands
        self.add_command(("addvote", "allowvote", "av"), self.cmd_votelimiterAllow,
                         int(self.get_cvar("qlx_votelimiterAdmin")))
        self.add_command(("delvote", "deletevote", "dv"), self.cmd_votelimiterDelete,
                         int(self.get_cvar("qlx_votelimiterAdmin")))
        self.add_command(("voteslist", "listvotes", "votes"), self.cmd_votelimiterList,
                         int(self.get_cvar("qlx_votelimiterAdmin")))
        self.add_command(("reload_voteslist", "load_votelist", "rvl"), self.load_allowed_votes,
                         int(self.get_cvar("qlx_votelimiterAdmin")))
        self.add_command(("versionvotelimiter", "version_votelimiter", "vlv"), self.votelimiter_version,
                         int(self.get_cvar("qlx_votelimiterAdmin")))
        self.add_command("sv", self.show_vote_string, int(self.get_cvar("qlx_votelimiterAdmin")))  # Used for testing

        # Opens the allowed votes container
        self.votelimiterAllowed = []

        # Loads the allowed votes list
        self.load_allowed_votes()
        
    def handle_vote_called(self, caller, vote, args):
        vote = vote.lower()
        if vote not in self.votelimiterAllowed:
            caller.tell("^3That vote type is not allowed on this server.\nSpeak to a server admin if this is in error")
            return minqlx.RET_STOP_ALL
        
    def load_allowed_votes(self, player=None, msg=None, channel=None):
        try:
            f = open(os.path.join(self.get_cvar("fs_homepath"), VOTELIMITER_FILE), "r")
            lines = f.readlines()
            f.close()
            tempList = []
            for vote in lines:
                if vote.startswith("#"):
                    continue
                try:
                    tempList.append(vote.split(None, 1)[0].strip('\n'))
                except:
                    continue
            self.votelimiterAllowed = tempList
            if player:
                player.tell("^3The Allowed Votes list has been reloaded. ^1!listvotes ^3 to see current load.")
        except IOError as e:
            try:
                tempList = []
                m = open(os.path.join(self.get_cvar("fs_homepath"), VOTELIMITER_FILE), "w")
                m.write("# This is a commented line because it starts with a '#'\n")
                m.write("# Enter every vote type you want allowed on its own line.\n")
                m.write("# Leave no blank lines in between allowed votes.\n")
                
                # The following lines add the default votes that are allowed. You can edit here,
                # but I recommend just removing the vote from the allowed list using the !rvote <vote> command.
                m.write("kick\n")
                tempList.append("kick")
                m.write("clientkick\n")
                tempList.append("clientkick")
                m.write("map\n")
                tempList.append("map")
                m.write("teamsize\n")
                tempList.append("teamsize")
                m.write("cointoss\n")
                tempList.append("cointoss")
                m.write("shuffle\n")     
                tempList.append("shuffle")
                # End default vote list
                
                m.close()
                self.votelimiterAllowed = tempList
                if player:
                    player.tell("^3No ^1Allowed Votes^3 list was found so one was created.")
            except:
                if player:
                    player.tell("^1Error ^3reading and/or creating the Allowed Votes list: {}".format(e))
        except Exception as e:
            if player:
                player.tell("^1Error ^3reading the Allowed Votes list: {}".format(e))
        return minqlx.RET_STOP_EVENT

    # votelimiter.py version checker. Thanks to iouonegirl for most of this section's code.
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
                        minqlx.console_command("echo {}".format(e))
                return

    def votelimiter_version(self, player, msg, channel):
        self.check_version(channel=channel)
        
    # Add a vote to the Allowed Votes list
    def cmd_votelimiterAllow(self, player, msg, channel):
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
        if vote in self.votelimiterAllowed:
            player.tell("^2{}^3 is already in the Allowed Votes list.".format(vote))
        else:
            h = open(file, "a")
            h.write(vote + "\n")
            h.close()
            self.votelimiterAllowed.append(vote)
            player.tell("^2{}^3 has been added to the Allowed Votes list.".format(vote))
    
        return minqlx.RET_STOP_EVENT

    # Removes the desired vote from the Allowed Votes list
    def cmd_votelimiterDelete(self, player, msg, channel):
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
                if vote in self.votelimiterAllowed:
                    self.votelimiterAllowed.remove(vote)
                player.tell("^2{}^3 has been deleted from the Allowed Votes list.".format(vote))
                return minqlx.RET_STOP_EVENT

        player.tell("^2{}^3 is not in the Allowed Votes list.".format(vote))
        return minqlx.RET_STOP_EVENT

    # List votes in the Allowed Votes file
    def cmd_votelimiterList(self, player, msg, channel):

        file = os.path.join(self.get_cvar("fs_homepath"), VOTELIMITER_FILE)
        try:
            f = open(file, "r")
            lines = f.readlines()
            f.close()
        except Exception as e:
            player.tell("^1Error ^3reading the Allowed Votes file: {}".format(e))
            return minqlx.RET_STOP_EVENT

        displayList = "^5Allowed Votes List:\n"

        for line in lines:
            if line.startswith("#"): continue
            words = line.split(" ")
            vote = words[0].strip('\n')
            
            displayList += " ^7Vote: ^3{}\n".format(vote)

        player.tell(displayList[:-1])
        return minqlx.RET_STOP_EVENT

    def show_vote_string(self, player, msg, channel):
        player.tell("List: {}:".format(str(self.votelimiterAllowed)))
