# This plugin is a modification of minqlx's fun.py
# https://github.com/MinoMino/minqlx

# Created by BarelyMiSSeD
# https://github.com/BarelyMiSSeD

# You are free to modify this plugin
# This plugin comes with no warranty or guarantee

"""
This is my replacement for the minqlx fun.py so if you use this file make sure not to load fun.py

This plugin plays sounds for players on the Quake Live server
It plays the sounds included in fun.py and some from other workshop item sound packs.

This can limit sound spamming to the server.
It only allows one sound to be played at a time and each user is limited in the frequency they can play sounds.
If you desire no restriction then set both of the 2 following cvars to "0".
The default qlx_funSoundDelay setting will require 5 seconds from the start of any sound
before another sound can be played by anyone.
The default qlx_funPlayerSoundRepeat setting will require 30 seconds from the start of a player called sound before
that player can call another sound.

To set the time required between any sound add this line to your server.cfg and edit the "5":
set qlx_funSoundDelay "5"

To set the time a player has to wait after playing a sound add this like to your server.cfg and edit the "30":
set qlx_funPlayerSoundRepeat "30"

#Play Join Sound when players connect (set to "path/file" like below example to play sound)
 (*** Disable the MOTD sound to use this with set qlx_motdSound "0" ****)
set qlx_funJoinSound "sound/feedback/welcome_02.wav"

#Play Join Sound even if players have sounds disabled
set qlx_funJoinSoundForEveryone "0"

#Play Join Sound on every map change (set to "1" to play join sound every map change)
set qlx_funJoinSoundEveryMap "0"

#Join sound path/file
set qlx_funJoinSound "sound/feedback/welcome_02.wav"

These extra workshop items need to be loaded on the server for it to work correctly if all sound packs are enabled:
(put the workshop item numbers in your workshop.txt file)
#Prestige Worldwide Soundhonks
585892371
#Funny Sounds Pack for Minqlx
620087103
#Duke Nukem Voice Sound Pack for minqlx
572453229
#Warp Sounds for Quake Live
1250689005
#West Coast Crew Sound
908031086

The minqlx 'workshop' plugin needs to be loaded and the required workshop
items added to the set qlx_workshopReferences line
(This example shows only these required workshop items):
set qlx_workshopReferences "585892371, 620087103, 572453229, 1250689005, 908031086"
(Only include the sound pack workshop item numbers that you decide to enable on the server)
(The Default sounds use sounds already available as part of the Quake Live install)

Soundpacks:
1) The Default soundpack uses sounds that are already included in the Quake Live install.
2) The Prestige Worldwide Soundhonks soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=585892371
3) The Funny Sounds Pack for Minqlx can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=620087103
4) The Duke Nukem Voice Sound Pack for minqlx soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=572453229
5) The Warp Sounds for Quake Live soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=1250689005
6) The West Coast Crew Sound soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=908031086

The soundpacks are all enabled by default. Which soundpacks are enabled can be set.
set qlx_funEnableSoundPacks "63" : Enables all sound packs.
****** How to set which sound packs are enabled ******
Add the values for each sound pack listed below and set that value to the
 qlx_funEnableSoundPacks in the same location as the rest of your minqlx cvar's.

 ****Sound Pack Values****
                               Default:  1
         Prestige Worldwide Soundhonks:  2
          Funny Sounds Pack for Minqlx:  4
Duke Nukem Voice Sound Pack for minqlx:  8
            Warp Sounds for Quake Live:  16
                 West Coast Crew Sound:  32

   Duke Nukem Soundpack Disabled Example: set qlx_funEnableSoundPacks "55"

When a player issues the !listsounds command it wil list all of the sounds available on the server with
 the sounds displayed in a tabbed format to help enable the redability of the sounds without requiring
  the use of pages or exessie scrolling. Only the soundpacks that are enabled will be shown. Any disabled
   soundpacks will not be displayed and will not be searchable.

If !listsounds is issued with a search term it will search for sounds that contain that term and display
 each enabled soundpack and the sounds found in them.

Example: !listsounds yeah would list all the sound phrases containing 'yeah'
and would print this to the player's console (assuming all sound packs are enabled):

SOUNDS: Type these words/phrases in normal chat to play a sound on the server.
Default
haha yeah haha hahaha yeah yeah hahaha yeahhh
Prestige Worldwide Soundhonks
No Matches
Funny Sounds Pack for Minqlx
No Matches
Duke Nukem Voice Sound Pack for minqlx
No Matches
Warp Sounds for Quake Live
No Matches
West Coast Crew Sound
No Matches
4 SOUNDS: Type these words/phrases in normal chat to play a sound on the server.

If !listsounds is issued with a sound pack limiting value it will only search that soundpack for sounds.
!listsounds #Default would only list the sounds in the Default soundpack, if it is enabled.

Example: '!listsounds #Default yeah' would list all the sounds containing 'yeah' but limit that search to
just the Default sounds and produce the following output:

SOUNDS: Type these words/phrases in normal chat to play a sound on the server.
Default
haha yeah haha hahaha yeah yeah hahaha yeahhh
4 SOUNDS: Type these words/phrases in normal chat to play a sound on the server.

"""

import minqlx
import random
import time
import re

from minqlx.database import Redis

VERSION = 3.4
TRIGGERS_LOCATION = "minqlx:myFun:addedTriggers:{}"
PLAYERS_SOUNDS = "minqlx:players:{0}:flags:myFun:{1}"
DISABLED_SOUNDS = "minqlx:myFun:disabled:{}"


class myFun(minqlx.Plugin):
    database = Redis

    def __init__(self):
        super().__init__()

        # Let players with perm level 5 play sounds after the "qlx_funSoundDelay" timeout (no player time restriction)
        self.set_cvar_once("qlx_funUnrestrictAdmin", "0")
        # Delay between sounds being played
        self.set_cvar_once("qlx_funSoundDelay", "5")
        # **** Used for limiting players spamming sounds. ****
        #  Amount of seconds player has to wait before allowed to play another sound
        self.set_cvar_once("qlx_funPlayerSoundRepeat", "30")
        # Keep muted players from playing sounds
        self.set_cvar_once("qlx_funDisableMutedPlayers", "1")
        # Enable/Disable sound pack files
        self.set_cvar_once("qlx_funEnableSoundPacks", "63")
        # Join sound path/file ("0" disables sound)
        self.set_cvar_once("qlx_funJoinSound", "0")
        # Play Join Sound even if players have sounds disabled
        self.set_cvar_once("qlx_funJoinSoundForEveryone", "0")
        # Play Join Sound on every map change
        self.set_cvar_once("qlx_funJoinSoundEveryMap", "0")

        self.add_hook("chat", self.handle_chat)
        self.add_hook("server_command", self.handle_server_command)
        self.add_hook("player_disconnect", self.player_disconnect)
        self.add_hook("player_loaded", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)
        self.add_command("cookies", self.cmd_cookies)
        self.add_command(("getsounds", "listsounds", "listsound"), self.cmd_list_sounds)
        self.add_command(("myfun", "fun"), self.cmd_help)
        self.add_command(("off", "soundoff"), self.cmd_sound_off, client_cmd_perm=0)
        self.add_command(("on", "soundon"), self.cmd_sound_on, client_cmd_perm=0)
        self.add_command(("offlist", "soundofflist"), self.cmd_sound_off_list, client_cmd_perm=0)
        self.add_command("playsound", self.cmd_sound, 3)
        self.add_command("disablesound", self.cmd_disable_sound, client_cmd_perm=5, usage="<sound trigger>")
        self.add_command("enablesound", self.cmd_enable_sound, client_cmd_perm=5, usage="<sound trigger>")
        self.add_command(("listdisabledsounds", "listdisabled"), self.cmd_list_disabled, client_cmd_perm=5)
        self.add_command(("reenablesounds", "reloadsounds"), self.enable_sound_packs, 5)
        self.add_command("addtrigger", self.add_trigger, 5)
        self.add_command("deltrigger", self.del_trigger, 5)
        self.add_command("listtriggers", self.list_triggers, 3)

        # variable to show when a sound has been played
        self.played = False
        # variable to store the sound to be called
        self.soundFile = ""
        # variable to store the sound trigger
        self.trigger = ""
        # stores time of last sound play
        self.last_sound = None
        # stores state of sound trigger find
        self.Found_Sound = False
        # Dictionary used to store player sound call times.
        self.sound_limiting = {}
        # List to store steam ids of muted players
        self.muted_players = []
        # List to store the enable/disabled status of the soundpacks
        self.Enabled_SoundPacks = [0,0,0,0,0,0]
        # set the desired sound packs to enabled
        self.enable_sound_packs()
        # List of soundpack names
        self.soundPacks = ["Default Quake Live Sounds", "Prestige Worldwide Soundhonks", "Funny Sounds Pack for Minqlx",
                           "Duke Nukem Voice Sound Pack for minqlx", "Warp Sounds for Quake Live",
                           "West Coast Crew Sound"]
        # List of soundpack categories (used to narrow search results in !listsounds)
        self.categories = ["#Default", "#Prestige", "#Funny", "#Duke", "#Warp", "#West"]
        # List for storing soundpack dictionaries
        self.soundDictionaries = []
        # List for storing the lists of sounds
        self.soundLists = []
        self.sound_list_count = 0
        self.help_msg = []
        # populate the list with empty dictionaries
        dicts = 0
        while dicts < len(self.Enabled_SoundPacks):
            self.soundDictionaries.append({})
            self.soundLists.append([])
            dicts += 1
        # populate the dictionaries and sound lists with the enabled soundpacks
        self.populate_dicts()
        # Welcome sound played list
        self.playedWelcome = []

    def enable_sound_packs(self, player=None, msg=None, channel=None):
        packs = self.get_cvar("qlx_funEnableSoundPacks", int)
        binary = bin(packs)[2:]
        length = len(str(binary))
        count = 0
        
        # save the packs value's binary representation to the slots in self.Enabled_SoundPacks
        # to identify the enabled sound packs
        while length > 0:
            self.Enabled_SoundPacks[count] = int(binary[length - 1])
            count += 1
            length -= 1

        # If this command was issued by a user them notify the user of the enables soundpacks
        #  and reload the soundpack dictionaries
        if player:
            sound_packs = []
            count = 0
            while count < len(self.Enabled_SoundPacks):
                if self.Enabled_SoundPacks[count]:
                    sound_packs.append(self.soundPacks[count])
                count += 1
            player.tell("Enabled Sound Packs are: ^3{}".format(", ".join(sound_packs)))
            dicts = 0
            while dicts < len(self.Enabled_SoundPacks):
                self.soundDictionaries[dicts].clear()
                self.soundLists[dicts] = []
                dicts += 1
            self.populate_dicts()
            player.tell("Completed Sound Pack reload.")
            return minqlx.RET_STOP_ALL

    @minqlx.delay(2)
    def handle_player_loaded(self, player):
        if self.get_cvar("qlx_motdSound") != "0" or self.get_cvar("qlx_funJoinSound") == "0":
            return
        # plays the join sound for a connecting player if qlx_funJoinSound is set and qlx_motdSound is not set
        # join sound can be played for everyone even if sounds are disabled if qlx_funJoinSoundForEveryone is enabled
        # join sound will play every map load for already connected players if qlx_funJoinSoundEveryMap is enabled
        welcome_sound = self.get_cvar("qlx_funJoinSound")
        if welcome_sound and player.steam_id not in self.playedWelcome and\
                (self.get_cvar("qlx_funJoinSoundForEveryone", bool) or
                 self.db.get_flag(player, "essentials:sounds_enabled", default=True)):
            super().play_sound(welcome_sound, player)
            if not self.get_cvar("qlx_funJoinSoundEveryMap", bool):
                self.playedWelcome.append(player.steam_id)

    # Remove stored information for disconnecting players
    def player_disconnect(self, player, reason):
        try:
            del self.sound_limiting[player.steam_id]
        except:
            pass
        try:
            self.muted_players.remove(player.steam_id)
        except:
            pass
        try:
            self.playedWelcome.remove(player.steam_id)
        except:
            pass

    # stores the mute status of a player when muted or un-muted
    def handle_server_command(self, player, cmd):
        if "has been muted" in cmd:
            cmd_string = cmd.split()
            cmd_len = len(cmd_string)
            name_length = cmd_len - 4
            name = " ".join(cmd_string[1:name_length]).strip('"')
            muted = self.find_player(name)
            steam_id = muted[0].steam_id
            if steam_id not in self.muted_players:
                self.muted_players.append(steam_id)
        elif "has been unmuted" in cmd:
            cmd_string = cmd.split()
            cmd_len = len(cmd_string)
            name_length = cmd_len - 4
            name = " ".join(cmd_string[1:name_length]).strip('"')
            muted = self.find_player(name)
            steam_id = muted[0].steam_id
            try:
                self.muted_players.remove(steam_id)
            except:
                pass

    # Monitors the chat messages of players to process the sound triggers
    @minqlx.thread
    def handle_chat(self, player, msg, channel):
        # don't process the chat if it was in the wrong channel or the player is muted or has sounds turned off
        if channel != "chat" or player.steam_id in self.muted_players or\
                not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            return

        # find the sound trigger for this sound (sets self.trigger, self.soundFile, self.Found_Sound)
        self.find_sound_trigger(self.clean_text(msg))
        if self.Found_Sound:
            # stop sound processing if the player has this sound trigger turned off
            if self.db.get(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)):
                return
            # check sound delay time
            delay_time = self.check_time(player)
            if delay_time:
                # if admins have no delay time restriction then PASS
                if self.get_cvar("qlx_funUnrestrictAdmin", bool) and self.db.get_permission(player.steam_id) == 5:
                    pass
                # otherwise, impose the delay time wait and stop sound trigger processing
                else:
                    player.tell("^3You played a sound recently. {} seconds timeout remaining."
                                .format(delay_time))
                    return
            # check to see if a sound has been played
            if not self.last_sound:
                pass
            # Make sure the last sound played was not within the sound delay limit
            elif time.time() - self.last_sound < self.get_cvar("qlx_funSoundDelay", int):
                player.tell("^3A sound has been played in last {} seconds. Try again after the timeout."
                            .format(self.get_cvar("qlx_funSoundDelay")))
                return
            # call the play sound function
            self.play_sound(self.soundFile)

        # If the sound played record the time with the player's steam id (for delay_time processing)
        if self.played:
            self.sound_limiting[player.steam_id] = time.time()
        # unset self.played so it can be checked again the next time a sound trigger is typed
        self.played = False

    # Compares the msg with the sound triggers to determine if there is a match
    def find_sound_trigger(self, msg):
        msg_lower = msg.lower()
        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                for key in self.soundDictionaries[sound_dict]:
                    # if sound trigger matches set self.trigger to the trigger,
                    #  self.soundFile to the location of the sound
                    #  self.Found_Sound to True to indicate the trigger match
                    #  (required because of running check in a thread)
                    if self.soundDictionaries[sound_dict][key][0].match(msg_lower):
                        self.trigger = key
                        self.soundFile = self.soundDictionaries[sound_dict][key][1]
                        self.Found_Sound = True
                        return
                    # if custom sound triggers have been added for the sound being examined
                    #  it searches through the stored triggers for a match
                    if self.db.exists(TRIGGERS_LOCATION.format(self.soundDictionaries[sound_dict][key][1])):
                        for trigger in self.db.lrange(TRIGGERS_LOCATION.format(self.soundDictionaries[sound_dict][key][1]), 0, -1):
                            if trigger == msg_lower:
                                self.trigger = key
                                self.soundFile = self.soundDictionaries[sound_dict][key][1]
                                self.Found_Sound = True
                                return
            sound_dict += 1

        self.Found_Sound = False
        return

    def add_trigger(self, player, msg, channel):
        if len(msg) < 3:
            player.tell("^3usage^7: ^1!addtrigger ^7<^2default trigger^7> ^1= ^7<^4added trigger^7>")
            return minqlx.RET_STOP_ALL
        msg_lower = [x.lower() for x in msg]
        split = 0
        count = 0
        for item in msg_lower[1:]:
            count += 1
            if item == "=":
                split = count
                break
        if split == 0:
            player.tell("^7You MUST include a ^1= ^7sign in to separate the default trigger from the desired trigger.")
            player.tell("^3usage^7: ^1{}addtrigger ^7<^2default trigger^7> ^1= ^7<^4added trigger^7>"
                        .format(self.get_cvar("qlx_commandPrefix")))
        else:
            trigger = " ".join(msg_lower[1:split])
            add_trigger = " ".join(msg_lower[split + 1:])
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.exists(TRIGGERS_LOCATION.format(found_path)):
                    for existing_trigger in self.db.lrange(TRIGGERS_LOCATION.format(found_path), 0, -1):
                        if existing_trigger == add_trigger:
                            player.tell("^3This trigger already exists")
                            return minqlx.RET_STOP_ALL
                self.db.rpush(TRIGGERS_LOCATION.format(found_path), add_trigger)
                player.tell("^3The sound trigger ^4{0} ^3has been added to the trigger list for ^2{1}."
                            .format(add_trigger, trigger))
            else:
                player.tell("^3usage^7: ^1{}addtrigger ^7<^2default trigger^7> ^1= ^7<^4added trigger^7>"
                            .format(self.get_cvar("qlx_commandPrefix")))
        return minqlx.RET_STOP_ALL

    def del_trigger(self, player, msg, channel):
        if len(msg) < 3:
            player.tell("^3usage^7: ^1!deltrigger ^7<^2default trigger^7> ^1= ^7<^4delete trigger^7>")
            return minqlx.RET_STOP_ALL
        msg_lower = [x.lower() for x in msg]
        split = 0
        count = 0
        for item in msg_lower[1:]:
            count += 1
            if item == "=":
                split = count
                break
        if split == 0:
            player.tell("^7You MUST include a ^1= ^7sign in to separate the default trigger from the desired trigger.")
            player.tell("^3usage^7: ^1{}deltrigger ^7<^2default trigger^7> ^1= ^7<^4del trigger^7>"
                        .format(self.get_cvar("qlx_commandPrefix")))
        else:
            trigger = " ".join(msg_lower[1:split])
            del_trigger = " ".join(msg_lower[split + 1:])
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.exists(TRIGGERS_LOCATION.format(found_path)):
                    self.db.lrem(TRIGGERS_LOCATION.format(found_path), 0, del_trigger)
                    player.tell("^3The sound trigger ^4{0} ^3has been deleted from the trigger list for ^2{1}."
                                .format(del_trigger, trigger))
                else:
                    player.tell("^3There are no custom triggers saved for ^4{}".format(trigger))
            else:
                player.tell("^3usage^7: ^1{}deltrigger ^7<^2default trigger^7> ^1= ^7<^4del trigger^7>"
                            .format(self.get_cvar("qlx_commandPrefix")))
        return minqlx.RET_STOP_ALL

    def list_triggers(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3usage^7: ^1!listtriggers ^7<^2default trigger^7>")
            return minqlx.RET_STOP_ALL
        msg_lower = [x.lower() for x in msg]
        trigger = " ".join(msg_lower[1:])
        found_path = self.find_sound_path(trigger)
        if found_path:
            if self.db.exists(TRIGGERS_LOCATION.format(found_path)):
                if self.db.llen(TRIGGERS_LOCATION.format(found_path)) == 0:
                    player.tell("^3There are no custom triggers saved for ^4{}".format(trigger))
                    return minqlx.RET_STOP_ALL
                else:
                    triggers = self.db.lrange(TRIGGERS_LOCATION.format(found_path), 0, -1)
                    self.msg("^3The custom sound triggers for ^4{0}^7: ^2{1}".format(trigger, ", ".join(triggers)))
                    return
            else:
                player.tell("^3There are no custom triggers saved for ^4{}".format(trigger))
        else:
            player.tell("^3There are no custom sound triggers for ^2{}^7.".format(trigger))
        return minqlx.RET_STOP_ALL

    # players can turn off individual sounds for only themselves
    @minqlx.thread
    def cmd_sound_off(self, player, msg, channel):
        if len(msg) < 2:
            if self.soundFile != "":
                if self.db.get(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)):
                    player.tell("^3The sound ^4{0} ^3is already disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(self.trigger, self.get_cvar("qlx_commandPrefix")))
                else:
                    self.db.set(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile), 1)
                    if self.trigger == "":
                        self.find_sound_trigger(self.soundFile)
                    player.tell("^3The sound ^4{0} ^3has been disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(self.trigger, self.get_cvar("qlx_commandPrefix")))
            else:
                player.tell("^1{0}off <sound call> ^7use ^6{0}listsounds #help ^7to find triggers"
                            .format(self.get_cvar("qlx_commandPrefix")))

        else:
            trigger = " ".join(msg[1:]).lower()
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.get(PLAYERS_SOUNDS.format(player.steam_id, found_path)):
                    player.tell("^3The sound ^4{0} ^3is already disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(trigger, self.get_cvar("qlx_commandPrefix")))
                else:
                    self.db.set(PLAYERS_SOUNDS.format(player.steam_id, found_path), 1)
                    player.tell("^3The sound ^4{0} ^3has been disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(trigger, self.get_cvar("qlx_commandPrefix")))
            else:
                player.tell("^3usage: ^1{0}off <sound call> ^7use ^1{0}listsounds #help ^7to find triggers"
                            .format(self.get_cvar("qlx_commandPrefix")))
        return

    # players can re-enable sounds that they previously disabled for themselves
    @minqlx.thread
    def cmd_sound_on(self, player, msg, channel):
        if len(msg) < 2:
            if self.soundFile != "":
                if self.trigger == "":
                    self.find_sound_trigger(self.soundFile)
                if self.db.get(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)):
                    del self.db[PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)]
                    player.tell("^3The sound ^4{0} ^3has been enabled. Use ^1{1}off ^4{0} ^3to disable."
                                .format(self.trigger, self.get_cvar("qlx_commandPrefix")))
                else:
                    player.tell("^3The sound ^4{0} ^3is not disabled. Use ^1{1}off ^4{0} ^3to disable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(self.trigger, self.get_cvar("qlx_commandPrefix")))
            else:
                player.tell("^1{0}on <sound call> ^7use ^1{0}listsounds #help ^7to find triggers"
                            .format(self.get_cvar("qlx_commandPrefix")))

        else:
            trigger = " ".join(msg[1:]).lower()
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.get(PLAYERS_SOUNDS.format(player.steam_id, found_path)):
                    del self.db[PLAYERS_SOUNDS.format(player.steam_id, found_path)]
                    player.tell("^3The sound ^4{0} ^3has been enabled. Use ^1{1}off ^4{0} ^3to disable."
                                .format(trigger, self.get_cvar("qlx_commandPrefix")))
                else:
                    player.tell("^3The sound ^4{0} ^3is not disabled. Use ^1{1}off ^4{0} ^3to disable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(trigger, self.get_cvar("qlx_commandPrefix")))
            else:
                player.tell("^3usage: ^1{0}on <sound call> ^7use ^1{0}listsounds #help ^7to find triggers"
                            .format(self.get_cvar("qlx_commandPrefix")))
        return

    # return the path to the supplied sound trigger
    def find_sound_path(self, trigger):
        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                for key in self.soundDictionaries[sound_dict]:
                    if key == trigger:
                        return self.soundDictionaries[sound_dict][key][1]
            sound_dict += 1

        return False

    # return the sound trigger for the sound at the supplied path
    def sound_trigger(self, path):
        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                for key in self.soundDictionaries[sound_dict]:
                    if self.soundDictionaries[sound_dict][key][1] == path:
                        return key
            sound_dict += 1

        return None

    # list the disabled sound to the requesting player
    def cmd_sound_off_list(self, player, msg, channel):
        disabled_key = "minqlx:players:{0}:flags:myFun".format(player.steam_id)
        sound_list = []
        count = 0
        list = self.db.keys(disabled_key + ":*")
        for key in list:
            trigger = self.sound_trigger(key.split(":")[-1])
            sound_list.append(trigger)
            count += 1
            if (count % 3) == 0:
                sound_list.append("\n")

        player.tell("^3You have ^4{0} ^3sounds disabled: ^1{1}".format(count, "^7, ^1".join(sound_list)))
        return

    # disable the specified sound on the server
    def cmd_disable_sound(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        trigger = " ".join(msg[1:]).lower()
        sound_dict, key, found_path = self.find_sound_info(trigger)
        if found_path:
            if self.db.get(DISABLED_SOUNDS.format(key)):
                player.tell("^3The sound ^4{} ^3is already disabled. ^1{1}listdisabled ^3to see the disabled sounds."
                            .format(key, self.get_cvar("qlx_commandPrefix")))
            else:
                self.db.set(DISABLED_SOUNDS.format(key), 1)
                del self.soundDictionaries[sound_dict][key]
                slot = 0
                while slot < len(self.Enabled_SoundPacks):
                    if self.Enabled_SoundPacks[slot] and key in self.soundLists[slot]:
                        self.soundLists[slot].remove(key)
                    slot += 1

                player.tell("^3The sound ^4{} ^3is now disabled.".format(key, self.get_cvar("qlx_commandPrefix")))

        else:
            player.tell("^3Invalid sound trigger. Use ^1{}listsounds ^7<^1search string^7>"
                        " ^3to find the correct sound trigger.".format(self.get_cvar("qlx_commandPrefix")))
        return minqlx.RET_STOP_ALL

    # enable the specified sound on the server
    def cmd_enable_sound(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        trigger = " ".join(msg[1:]).lower()
        try:
            if self.db.exists(DISABLED_SOUNDS.format(trigger)):
                del self.db[DISABLED_SOUNDS.format(trigger)]
                player.tell("^3The sound will be enabled on next list reload. Use ^1{0}reloadsounds ^3or the ^4{1}"
                            " ^3sound list will be reloaded next time the server is restarted or myFun.py is reloaded."
                            .format(self.get_cvar("qlx_commandPrefix"), trigger))
            else:
                player.tell("^3The sound ^4{0} ^3is not disabled. ^1{1}listdisabled ^3to see the disabled sounds."
                            .format(trigger, self.get_cvar("qlx_commandPrefix")))
        except Exception as e:
            player.tell("^3The sound ^4{0} ^3is not disabled. ^1{1}listdisabled ^3to see the disabled sounds."
                        .format(trigger, self.get_cvar("qlx_commandPrefix")))
            minqlx.console_print("^1Enable sound exception:: {}".format(e))
        return minqlx.RET_STOP_ALL

    # list the sounds disabled on the server for the requesting player
    def cmd_list_disabled(self, player, msg, channel):
        sound_list = []
        count = 0
        for key in self.db.keys("minqlx:myFun:disabled:*"):
            trigger = key.split(":")[-1]
            sound_list.append(trigger)
            count += 1
            if (count % 3) == 0:
                sound_list.append("\n")
        player.tell("^3There are ^4{0} ^3sound(s) disabled on the server:\n^1{1}".format(count, "^7, ^1".join(sound_list)))
        return minqlx.RET_STOP_ALL

    # return the sound dictionary number, the sound trigger (key), and the sound path for the supplied sound trigger
    def find_sound_info(self, msg):
        msg_lower = msg.lower()

        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                for key in self.soundDictionaries[sound_dict]:
                    if self.soundDictionaries[sound_dict][key][0].match(msg_lower):
                        return sound_dict, key, self.soundDictionaries[sound_dict][key][1]
            sound_dict += 1

        return False

    # play the sound at the supplied path
    def cmd_sound(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("Include a path/sound to play.")
            return minqlx.RET_STOP_ALL

        if "console" != channel and not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            player.tell("Your sounds are disabled. Use ^6{}sounds^7 to enable them again."
                .format(self.get_cvar("qlx_commandPrefix")))
            return minqlx.RET_STOP_ALL

        # Play locally to validate.
        if "console" != channel and not super().play_sound(msg[1], player):
            player.tell("Invalid sound.")
            return minqlx.RET_STOP_ALL

        if "console" == channel:
            minqlx.console_print("^1Playing sound^7: ^4{}".format(msg[1]))

        self.play_sound(msg[1])

        return minqlx.RET_STOP_ALL

    # plays the supplied sound for the players on the server (if the player has the sound(s) enabled)
    def play_sound(self, path):
        self.played = True

        self.last_sound = time.time()
        for p in self.players():
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True) and \
                    not self.db.get(PLAYERS_SOUNDS.format(p.steam_id, path)):
                super().play_sound(path, p)

    # populates the sound list that is used to list the available sounds on the server
    @minqlx.thread
    def populate_sound_lists(self):
        # remove dictionary entries for sounds disabled on the server
        for key in self.db.keys("minqlx:myFun:disabled:*"):
            if self.db[key]:
                sound_dict = 0
                trigger = key.split(":")[-1]
                while sound_dict < len(self.Enabled_SoundPacks):
                    if self.Enabled_SoundPacks[sound_dict]:
                        self.soundDictionaries[sound_dict].pop(trigger, None)
                    sound_dict += 1

        self.sound_list_count = 0
        self.help_msg = []
        slot = 0
        while slot < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[slot]:
                self.soundLists[slot] = []
                self.sound_list_count += 1
                self.help_msg.append(self.categories[slot])
                for key in self.soundDictionaries[slot]:
                    self.soundLists[slot].append(key)
                self.soundLists[slot].sort()
            slot += 1

    def cmd_cookies(self, player, msg, channel):
        x = random.randint(0, 100)
        if not x:
            channel.reply("^6♥ ^7Here you go, {}. I baked these just for you! ^6♥".format(player))
        elif x == 1:
            channel.reply("What, you thought ^6you^7 would get cookies from me, {}? Hah, think again.".format(player))
        elif x < 50:
            channel.reply("For me? Thank you, {}!".format(player))
        else:
            channel.reply("I'm out of cookies right now, {}. Sorry!".format(player))

    def check_time(self, player):
        if self.get_cvar("qlx_funUnrestrictAdmin", bool) and self.db.get_permission(player.steam_id) == 5:
            return False
        try:
            saved_time = self.sound_limiting[player.steam_id]
            play_time = time.time() - saved_time
            if play_time > self.get_cvar("qlx_funPlayerSoundRepeat", int):
                return False
            else:
                return int(self.get_cvar("qlx_funPlayerSoundRepeat", int) - play_time)
        except KeyError:
            return False

    # list the command usage for !listsounds
    def cmd_help(self, player, msg=None, channel=None):
        player.tell("^1myFun Version {0}\n"
                    "^6{1}myFun ^3to quickly pull up this help menu.\n"
                    "^6{1}listsounds ^3shows all sounds\n^6{1}listsounds #sound-pack ^3 to see just one sound"
                    " pack\n^6{1}listsounds #sound-pack search-term ^3to see sounds in that sound pack that"
                    " have the search term\n^6{0}listsounds search-term ^3to search all sound packs for sounds"
                    " with that search term\n^2EXAMPLES^7:\n^6{1}listsounds #Default ^3 will display all"
                    " ^4Default Quake Live Sounds\n^6{1}lsitsounds #Default yeah ^3 will search ^4#Default"
                    " ^3for sounds containing ^4yeah\n^6{1}listsounds yeah ^3 will search all the sound packs"
                    " for sounds containing ^4yeah\n^3Search terms can be multiple words\n"
                    "^3Valid sound-pack are ^2{2}\n^6{1}sounds ^3to disable^7/^3enable all sound playing for yourself."
                    "\n ^6{1}off^7/^6{1}on trigger ^3to disable^7/^3enable a specific sound\n^6{1}offlist ^3to see a"
                    " list of sounds you have disabled."
                    .format(VERSION, self.get_cvar("qlx_commandPrefix"), "^7/^2".join(self.help_msg)))
        return

    # list the available sounds to the requesting player
    @minqlx.thread
    def cmd_list_sounds(self, player, msg, channel):
        sounds = ["^4SOUNDS^7: ^3Type these words/phrases in normal chat to play a sound on the server.\n"]

        count = 0
        category = None
        search = None
        if len(msg) == 2:
            if msg[1].startswith("#"):
                category = msg[1]
            else:
                search = msg[1]
        elif len(msg) > 2:
            if msg[1].startswith("#"):
                category = msg[1]
                search = " ".join(msg[2:])
            else:
                search = " ".join(msg[1:])

        if category:
            category = category.lower()
            if category == "#help":
                self.cmd_help(player)
                return
            elif any(s.lower() == category for s in self.help_msg):
                category_num = -1
                cat_num = 0
                while cat_num < len(self.categories):
                    if re.compile(self.categories[cat_num].lower()).match(category):
                        category_num = cat_num
                    cat_num += 1

                if -1 < category_num < len(self.Enabled_SoundPacks):
                    sounds_line = ""
                    sounds.append("^4" + self.soundPacks[category_num] + "\n")
                    for item in self.soundLists[category_num]:
                        if search and search not in item:
                            continue
                        add_sound, status = self.line_up(sounds_line, item)
                        if status == 1:
                            sounds.append("^1" + sounds_line + "\n")
                            sounds_line = add_sound
                        elif status == 2:
                            sounds_line += add_sound
                            sounds.append("^1" + sounds_line + "\n")
                            sounds_line = ""
                        else:
                            sounds_line += add_sound
                        count += 1
                    if len(sounds_line):
                        sounds.append("^1" + sounds_line + "\n")

                if count == 0:
                    sounds.append("^3No Matches\n")
            else:
                if self.sound_list_count == 1:
                    player.tell("^3INVALID ^2Category ^7given. Valid category is ^2" + "^7, ^2".join(self.help_msg))
                else:
                    player.tell("^3INVALID ^2Category ^7given. Valid categories are ^2" + "^7, ^2".join(self.help_msg))
                return

        else:
            slot = 0
            while slot < len(self.Enabled_SoundPacks):
                sounds_line = ""
                if self.Enabled_SoundPacks[slot]:
                    found = 0
                    sounds.append("^4" + self.soundPacks[slot] + "\n")
                    for item in self.soundLists[slot]:
                        if search and search not in item:
                            continue
                        add_sound, status = self.line_up(sounds_line, item)
                        if status == 1:
                            sounds.append("^1" + sounds_line + "\n")
                            sounds_line = add_sound
                        elif status == 2:
                            sounds_line += add_sound
                            sounds.append("^1" + sounds_line + "\n")
                            sounds_line = ""
                        else:
                            sounds_line += add_sound
                        count += 1
                        found += 1
                    if len(sounds_line):
                        sounds.append("^1" + sounds_line + "\n")
                    if found == 0:
                        sounds.append("^3No Matches\n")
                slot += 1

            if count == 0:
                player.tell("^4Server^7: No sounds contain the search string ^1{}^7.".format(search))
                return

            if self.sound_list_count > 1 and not category and not search:
                sounds.append("^3Type ^4{}listsounds #help ^3 to get instructions on narrowing your search results.\n"
                              .format(self.get_cvar("qlx_commandPrefix")))
            elif not search:
                sounds.append("^3Add a search string to further narrow results:\n^2{0}listsounds ^7<^2category^7>"
                              " <^2search string^7>".format(self.get_cvar("qlx_commandPrefix")))

        sounds.append("^2{} ^4SOUNDS^7: ^3Type these words/phrases in normal chat to trigger a sound on the server.\n"
                      .format(count))

        if "console" == channel:
            for line in sounds:
                minqlx.console_print(line.strip())
        else:
            player.tell("".join(sounds))
        return

    # puts the list of sounds in a column style format for easier reading
    def line_up(self, sound_line, add_sound):
        length = len(sound_line)
        # 0 = add to line, 1 = add to new line, 2 = add current sound and start new line
        status = 0
        if length + len(add_sound) > 78:
            append = add_sound
            status = 1
        elif length == 0:
            append = add_sound
        elif length < 16:
            append = " " * (18 - length) + add_sound
        elif length < 36:
            append = " " * (38 - length) + add_sound
        elif length < 56:
            append = " " * (58 - length) + add_sound
        elif length < 76:
            append = " " * (78 - length) + add_sound
            status = 2
        else:
            append = add_sound
            status = 1
        return append, status

    # These are the sounds available on the server put into the dictionaries used to search for a sound trigger match
    #  when processing normal chat messages
    @minqlx.thread
    def populate_dicts(self):
        if self.Enabled_SoundPacks[0]:
            self.soundDictionaries[0]["hahaha yeah"] = [re.compile(r"^haha(?:ha)?,? yeah?\W?$"), "sound/player/lucy/taunt.wav"]
            self.soundDictionaries[0]["haha yeah haha"] = [re.compile(r"^haha(?:ha)?,? yeah?,? haha\W?$"), "sound/player/biker/taunt.wav"]
            self.soundDictionaries[0]["yeah hahaha"] = [re.compile(r"^yeah?,? haha(?:ha)\W?$"), "sound/player/razor/taunt.wav"]
            self.soundDictionaries[0]["duahahaha"] = [re.compile(r"^duahaha(?:ha)?\W?$"), "sound/player/keel/taunt.wav"]
            self.soundDictionaries[0]["hahaha"] = [re.compile(r"^hahaha"), "sound/player/santa/taunt.wav"]
            self.soundDictionaries[0]["glhf"] = [re.compile(r"^(?:gl ?hf\W?)|(?:hf\W?)|(?:gl hf\W?)"), "sound/vo/crash_new/39_01.wav"]
            self.soundDictionaries[0]["f3"] = [re.compile(r"^((?:(?:press )?f3)|ready|ready up)$\W?"), "sound/vo/crash_new/36_04.wav"]
            self.soundDictionaries[0]["holy shit"] = [re.compile(r"holy shit"), "sound/vo_female/holy_shit"]
            self.soundDictionaries[0]["welcome to quake live"] = [re.compile(r"^welcome to (?:ql|quake live)\W?$"), "sound/vo_evil/welcome"]
            self.soundDictionaries[0]["go"] = [re.compile(r"^go\W?$"), "sound/vo/go"]
            self.soundDictionaries[0]["beep boop"] = [re.compile(r"^beep boop\W?$"), "sound/player/tankjr/taunt.wav"]
            self.soundDictionaries[0]["you win"] = [re.compile(r"^you win\W?$"), "sound/vo_female/you_win.wav"]
            self.soundDictionaries[0]["you lose"] = [re.compile(r"^you lose\W?$"), "sound/vo/you_lose.wav"]
            self.soundDictionaries[0]["impressive"] = [re.compile(r"impressive"), "sound/vo_female/impressive1.wav"]
            self.soundDictionaries[0]["excellent"] = [re.compile(r"excellent"), "sound/vo_evil/excellent1.wav"]
            self.soundDictionaries[0]["denied"] = [re.compile(r"^denied\W?$"), "sound/vo/denied"]
            self.soundDictionaries[0]["balls out"] = [re.compile(r"^ball'?s out\W?$"), "sound/vo_female/balls_out"]
            self.soundDictionaries[0]["one"] = [re.compile(r"^one\W?$"), "sound/vo_female/one"]
            self.soundDictionaries[0]["two"] = [re.compile(r"^two\W?$"), "sound/vo_female/two"]
            self.soundDictionaries[0]["three"] = [re.compile(r"^three\W?$"), "sound/vo_female/three"]
            self.soundDictionaries[0]["fight"] = [re.compile(r"^fight\W?$"), "sound/vo_evil/fight"]
            self.soundDictionaries[0]["gauntlet"] = [re.compile(r"^gauntlet\W?$"), "sound/vo_evil/gauntlet"]
            self.soundDictionaries[0]["humiliation"] = [re.compile(r"^humiliation\W?$"), "sound/vo_evil/humiliation1"]
            self.soundDictionaries[0]["perfect"] = [re.compile(r"^perfect\W?$"), "sound/vo_evil/perfect"]
            self.soundDictionaries[0]["wah wah wah wah"] = [re.compile(r"^wa+h wa+h wa+h wa+h\W?$"), "sound/misc/yousuck"]
            self.soundDictionaries[0]["ah ah ah ah"] = [re.compile(r"^a+h a+h a+h\W?$"), "sound/player/slash/taunt.wav"]
            self.soundDictionaries[0]["oink"] = [re.compile(r"^oink\W?$"), "sound/player/sorlag/pain50_1.wav"]
            self.soundDictionaries[0]["argh"] = [re.compile(r"^a+rgh\W?$"), "sound/player/doom/taunt.wav"]
            self.soundDictionaries[0]["hah haha"] = [re.compile(r"^hah haha\W?$"), "sound/player/hunter/taunt.wav"]
            self.soundDictionaries[0]["woohoo"] = [re.compile(r"^woo+hoo+\W?$"), "sound/player/janet/taunt.wav"]
            self.soundDictionaries[0]["quake live"] = [re.compile(r"^(?:ql|quake live)\W?$"), "sound/vo_female/quake_live"]
            self.soundDictionaries[0]["chaching"] = [re.compile(r"(?:\$|€|£|chaching)"), "sound/misc/chaching"]
            self.soundDictionaries[0]["uh ah"] = [re.compile(r"^uh ah$"), "sound/player/mynx/taunt.wav"]
            self.soundDictionaries[0]["oohwee"] = [re.compile(r"^ooh+wee\W?$"), "sound/player/anarki/taunt.wav"]
            self.soundDictionaries[0]["erah"] = [re.compile(r"^erah\W?$"), "sound/player/bitterman/taunt.wav"]
            self.soundDictionaries[0]["yeahhh"] = [re.compile(r"^yeahhh\W?$"), "sound/player/major/taunt.wav"]
            self.soundDictionaries[0]["scream"] = [re.compile(r"^scream\W?$"), "sound/player/bones/taunt.wav"]
            self.soundDictionaries[0]["salute"] = [re.compile(r"^salute\W?$"), "sound/player/sarge/taunt.wav"]
            self.soundDictionaries[0]["squish"] = [re.compile(r"^squish\W?$"), "sound/player/orbb/taunt.wav"]
            self.soundDictionaries[0]["oh god"] = [re.compile(r"^oh god\W?$"), "sound/player/ranger/taunt.wav"]
            self.soundDictionaries[0]["snarl"] = [re.compile(r"^snarl\W?$"), "sound/player/sorlag/taunt.wav"]

        if self.Enabled_SoundPacks[1]:
            self.soundDictionaries[1]["assholes"] = [re.compile(r"^assholes\W?$"), "soundbank/assholes.ogg"]
            self.soundDictionaries[1]["assshafter"] = [re.compile(r"^(?:assshafter|asshafter|ass shafter)\W?$"), "soundbank/assshafterloud.ogg"]
            self.soundDictionaries[1]["babydoll"] = [re.compile(r"^babydoll\W?$"), "soundbank/babydoll.ogg"]
            self.soundDictionaries[1]["barelymissed"] = [re.compile(r"^(?:barelymissed|barely)\W?$"), "soundbank/barelymissed.ogg"]
            self.soundDictionaries[1]["belly"] = [re.compile(r"^belly\W?$"), "soundbank/belly.ogg"]
            self.soundDictionaries[1]["bitch"] = [re.compile(r"^bitch\W?$"), "soundbank/bitch.ogg"]
            self.soundDictionaries[1]["blud"] = [re.compile(r"^(?:dtblud|blud)\W?$"), "soundbank/dtblud.ogg"]
            self.soundDictionaries[1]["boats"] = [re.compile(r"^boats\W?$"), "soundbank/boats.ogg"]
            self.soundDictionaries[1]["bobg"] = [re.compile(r"^(?:bobg|bob)\W?$"), "soundbank/bobg.ogg"]
            self.soundDictionaries[1]["bogdog"] = [re.compile(r"^bogdog\W?$"), "soundbank/bogdog.ogg"]
            self.soundDictionaries[1]["boom"] = [re.compile(r"^boom\W?$"), "soundbank/boom.ogg"]
            self.soundDictionaries[1]["boom2"] = [re.compile(r"^boom2\W?$"), "soundbank/boom2.ogg"]
            self.soundDictionaries[1]["buk"] = [re.compile(r"^(?:buk|ibbukn)\W?$"), "soundbank/buk.ogg"]
            self.soundDictionaries[1]["bullshit"] = [re.compile(r"^(?:bullshit|bull shit|bs)\W?$"), "soundbank/bullshit.ogg"]
            self.soundDictionaries[1]["butthole"] = [re.compile(r"^butthole\W?$"), "soundbank/butthole.ogg"]
            self.soundDictionaries[1]["buttsex"] = [re.compile(r"^buttsex\W?$"), "soundbank/buttsex.ogg"]
            self.soundDictionaries[1]["cheeks"] = [re.compile(r"^cheeks\W?$"), "soundbank/cheeks.ogg"]
            self.soundDictionaries[1]["cocksucker"] = [re.compile(r"^(?:cocksucker|cs)\W?$"), "soundbank/cocksucker.ogg"]
            self.soundDictionaries[1]["conquer"] = [re.compile(r"^conquer\W?$"), "soundbank/conquer.ogg"]
            self.soundDictionaries[1]["countdown"] = [re.compile(r"^countdown\W?$"), "soundbank/countdown.ogg"]
            self.soundDictionaries[1]["cum"] = [re.compile(r"^cum\W?$"), "soundbank/cum.ogg"]
            self.soundDictionaries[1]["cumming"] = [re.compile(r"^cumming\W?$"), "soundbank/cumming.ogg"]
            self.soundDictionaries[1]["cunt"] = [re.compile(r"^cunt\W?$"), "soundbank/cunt.ogg"]
            self.soundDictionaries[1]["dirkfunk"] = [re.compile(r"^(?:dirkfunk|dirk)\W?$"), "soundbank/dirkfunk.ogg"]
            self.soundDictionaries[1]["disappointment"] = [re.compile(r"^disappointment\W?$"), "soundbank/disappointment.ogg"]
            self.soundDictionaries[1]["doomsday"] = [re.compile(r"^(?:doom(sday)?)\W?$"), "soundbank/doom.ogg"]
            self.soundDictionaries[1]["drumset"] = [re.compile(r"^drumset\W?$"), "soundbank/drumset.ogg"]
            self.soundDictionaries[1]["eat"] = [re.compile(r"^eat\W?$"), "soundbank/eat.ogg"]
            self.soundDictionaries[1]["eat me"] = [re.compile(r"^(?:eatme|eat me|byte me)\W?$"), "soundbank/eatme.ogg"]
            self.soundDictionaries[1]["fag"] = [re.compile(r"^(?:fag|homo|homosexual)\W?$"), "soundbank/fag.ogg"]
            self.soundDictionaries[1]["fingerass"] = [re.compile(r"^fingerass\W?$"), "soundbank/fingerass.ogg"]
            self.soundDictionaries[1]["flash"] = [re.compile(r"^(?:flashsoul|flash)\W?$"), "soundbank/flash.ogg"]
            self.soundDictionaries[1]["fuckface"] = [re.compile(r"^fuckface\W?$"), "soundbank/fuckface.ogg"]
            self.soundDictionaries[1]["fuckyou"] = [re.compile(r"^fuckyou\W?$"), "soundbank/fuckyou.ogg"]
            self.soundDictionaries[1]["get emm"] = [re.compile(r"^(?:getem+|get em+)\W?$"), "soundbank/getemm.ogg"]
            self.soundDictionaries[1]["gonads"] = [re.compile(r"^(?:gonads|nads)\W?$"), "soundbank/gonads.ogg"]
            self.soundDictionaries[1]["gtfo"] = [re.compile(r"^gtfo\W?$"), "soundbank/gtfo.ogg"]
            self.soundDictionaries[1]["hug it out"] = [re.compile(r"^hug it out\W?$"), "soundbank/hugitout.ogg"]
            self.soundDictionaries[1]["idiot"] = [re.compile(r"^(?:idiot|andycreep|d3phx|gladiat0r)\W?$"), "soundbank/idiot.ogg"]
            self.soundDictionaries[1]["idiot2"] = [re.compile(r"^idiot2\W?$"), "soundbank/idiot2.ogg"]
            self.soundDictionaries[1]["it?'s time"] = [re.compile(r"^it'?s time\W?$"), "soundbank/itstime.ogg"]
            self.soundDictionaries[1]["jeopardy"] = [re.compile(r"^jeopardy\W?$"), "soundbank/jeopardy.ogg"]
            self.soundDictionaries[1]["jerk off"] = [re.compile(r"^(?:jerk off|jerkoff)\W?$"), "soundbank/jerkoff.ogg"]
            self.soundDictionaries[1]["killo"] = [re.compile(r"^killo\W?$"), "soundbank/killo.ogg"]
            self.soundDictionaries[1]["knocked"] = [re.compile(r"^knocked\W?$"), "soundbank/knocked.ogg"]
            self.soundDictionaries[1]["ld3"] = [re.compile(r"^(?:die|ld3)\W?$"), "soundbank/ld3.ogg"]
            self.soundDictionaries[1]["liquidswords"] = [re.compile(r"^(?:liquidswords|liquid)\W?$"), "soundbank/liquid.ogg"]
            self.soundDictionaries[1]["massacre"] = [re.compile(r"^massacre\W?$"), "soundbank/massacre.ogg"]
            self.soundDictionaries[1]["mixer"] = [re.compile(r"^mixer\W?$"), "soundbank/mixer.ogg"]
            self.soundDictionaries[1]["mjman"] = [re.compile(r"^(?:mjman|marijuanaman)\W?$"), "soundbank/mjman.ogg"]
            self.soundDictionaries[1]["mmmm"] = [re.compile(r"^mmmm\W?$"), "soundbank/mmmm.ogg"]
            self.soundDictionaries[1]["monty"] = [re.compile(r"^monty\W?$"), "soundbank/monty.ogg"]
            self.soundDictionaries[1]["n8"] = [re.compile(r"^(?:n8|_n8)\W?$"), "soundbank/n8.ogg"]
            self.soundDictionaries[1]["nikon"] = [re.compile(r"^(?:nikon|niko|nikonguru)\W?$"), "soundbank/nikon.ogg"]
            self.soundDictionaries[1]["nina"] = [re.compile(r"^nina\W?$"), "soundbank/nina.ogg"]
            self.soundDictionaries[1]["nthreem"] = [re.compile(r"^nthreem\W?$"), "sound/vo_female/impressive1.wav"]
            self.soundDictionaries[1]["olhip"] = [re.compile(r"^(?:olhip|hip)\W?$"), "soundbank/hip.ogg"]
            self.soundDictionaries[1]["organic"] = [re.compile(r"^(?:organic|org)\W?$"), "soundbank/organic.ogg"]
            self.soundDictionaries[1]["paintball"] = [re.compile(r"^paintball\W?$"), "soundbank/paintball.ogg"]
            self.soundDictionaries[1]["pigfucker"] = [re.compile(r"^(?:pigfucker|pig fucker|pf)\W?$"), "soundbank/pigfer.ogg"]
            self.soundDictionaries[1]["popeye"] = [re.compile(r"^popeye\W?$"), "soundbank/popeye.ogg"]
            self.soundDictionaries[1]["rosie"] = [re.compile(r"^rosie\W?$"), "soundbank/rosie.ogg"]
            self.soundDictionaries[1]["seaweed"] = [re.compile(r"^seaweed\W?$"), "soundbank/seaweed.ogg"]
            self.soundDictionaries[1]["shit"] = [re.compile(r"^shit\W?$"), "soundbank/shit.ogg"]
            self.soundDictionaries[1]["sit"] = [re.compile(r"(^sit\W?$| sit | sit$)"), "soundbank/sit.ogg"]
            self.soundDictionaries[1]["soulianis"] = [re.compile(r"^(?:soulianis|soul)\W?$"), "soundbank/soulianis.ogg"]
            self.soundDictionaries[1]["spam"] = [re.compile(r"^spam\W?$"), "soundbank/spam3.ogg"]
            self.soundDictionaries[1]["stalin"] = [re.compile(r"^stalin\W?$"), "soundbank/ussr.ogg"]
            self.soundDictionaries[1]["stfu"] = [re.compile(r"^stfu\W?$"), "soundbank/stfu.ogg"]
            self.soundDictionaries[1]["suck a dick"] = [re.compile(r"^suck a dick\W?$"), "soundbank/suckadick.ogg"]
            self.soundDictionaries[1]["suckit"] = [re.compile(r"^suckit\W?$"), "soundbank/suckit.ogg"]
            self.soundDictionaries[1]["suck my dick"] = [re.compile(r"^suck my dick\W?$"), "soundbank/suckmydick.ogg"]
            self.soundDictionaries[1]["teapot"] = [re.compile(r"^teapot\W?$"), "soundbank/teapot.ogg"]
            self.soundDictionaries[1]["thank god"] = [re.compile(r"^(?:thankgod|thank god)\W?$"), "soundbank/thankgod.ogg"]
            self.soundDictionaries[1]["traxion"] = [re.compile(r"^traxion\W?$"), "soundbank/traxion.ogg"]
            self.soundDictionaries[1]["trixy"] = [re.compile(r"^trixy\W?$"), "soundbank/trixy.ogg"]
            self.soundDictionaries[1]["twoon"] = [re.compile(r"^(?:twoon|2pows)\W?$"), "soundbank/twoon.ogg"]
            self.soundDictionaries[1]["ty"] = [re.compile(r"^(?:ty|thanks|thank you)\W?$"), "soundbank/thankyou.ogg"]
            self.soundDictionaries[1]["venny"] = [re.compile(r"^venny\W?$"), "soundbank/venny.ogg"]
            self.soundDictionaries[1]["viewaskewer"] = [re.compile(r"^(?:viewaskewer|view)\W?$"), "soundbank/view.ogg"]
            self.soundDictionaries[1]["what's that"] = [re.compile(r"^what'?s that\W?$"), "soundbank/whatsthat.ogg"]
            self.soundDictionaries[1]["who are you"] = [re.compile(r"^who are you\W?$"), "soundbank/whoareyou.ogg"]

        if self.Enabled_SoundPacks[2]:
            self.soundDictionaries[2]["007"] = [re.compile(r"^007\W?$"), "sound/funnysounds/007.ogg"]
            self.soundDictionaries[2]["A Scratch"] = [re.compile(r"^(?:(just )?(a )?scratch)\W?$"), "sound/funnysounds/AScratch.ogg"]
            self.soundDictionaries[2]["adams family"] = [re.compile(r"^(?:adams ?family)\W?$"), "sound/funnysounds/adamsfamily.ogg"]
            self.soundDictionaries[2]["All The Things"] = [re.compile(r"^all the things\W?$"), "sound/funnysounds/AllTheThings.ogg"]
            self.soundDictionaries[2]["allahuakbar"] = [re.compile(r"^allahuakbar\W?$"), "sound/funnysounds/allahuakbar.ogg"]
            self.soundDictionaries[2]["allstar"] = [re.compile(r"^allstar\W?$"), "sound/funnysounds/allstar.ogg"]
            self.soundDictionaries[2]["Amazing"] = [re.compile(r"^amazing\W?$"), "sound/funnysounds/Amazing.ogg"]
            self.soundDictionaries[2]["Ameno"] = [re.compile(r"^ameno\W?$"), "sound/funnysounds/Ameno.ogg"]
            self.soundDictionaries[2]["America"] = [re.compile(r"^america\W?$"), "sound/funnysounds/America.ogg"]
            self.soundDictionaries[2]["Amerika"] = [re.compile(r"^amerika\W?$"), "sound/funnysounds/Amerika.ogg"]
            self.soundDictionaries[2]["And Nothing Else"] = [re.compile(r"^and nothing else\W?$"), "sound/funnysounds/AndNothingElse.ogg"]
            self.soundDictionaries[2]["Animals"] = [re.compile(r"^animals\W?$"), "sound/funnysounds/Animals.ogg"]
            self.soundDictionaries[2]["asskicking"] = [re.compile(r"^asskicking\W?$"), "sound/funnysounds/asskicking.ogg"]
            self.soundDictionaries[2]["ave"] = [re.compile(r"^ave\W?$"), "sound/funnysounds/ave.ogg"]
            self.soundDictionaries[2]["baby baby"] = [re.compile(r"^baby baby\W?$"), "sound/funnysounds/babybaby.ogg"]
            self.soundDictionaries[2]["baby evil"] = [re.compile(r"^baby evil\W?$"), "sound/funnysounds/babyevillaugh.ogg"]
            self.soundDictionaries[2]["baby laughing"] = [re.compile(r"^(?:babylaughing|baby laughing)\W?$"), "sound/funnysounds/babylaughing.ogg"]
            self.soundDictionaries[2]["bad boys"] = [re.compile(r"^bad boys\W?$"), "sound/funnysounds/badboys.ogg"]
            self.soundDictionaries[2]["Banana Boat"] = [re.compile(r"^banana boat\W?$"), "sound/funnysounds/BananaBoatSong.ogg"]
            self.soundDictionaries[2]["benny hill"] = [re.compile(r"^benny hill\W?$"), "sound/funnysounds/bennyhill.ogg"]
            self.soundDictionaries[2]["benzin"] = [re.compile(r"^benzin\W?$"), "sound/funnysounds/benzin.ogg"]
            self.soundDictionaries[2]["blue wins"] = [re.compile(r"^blue ?wins\W?$"), "sound/funnysounds/bluewins.ogg"]
            self.soundDictionaries[2]["bonkers"] = [re.compile(r"^bonkers\W?$"), "sound/funnysounds/bonkers.ogg"]
            self.soundDictionaries[2]["boom headshot"] = [re.compile(r"^boom headshot\W?$"), "sound/funnysounds/boomheadshot.ogg"]
            self.soundDictionaries[2]["booo"] = [re.compile(r"^booo?\W?$"), "sound/funnysounds/booo.ogg"]
            self.soundDictionaries[2]["boring"] = [re.compile(r"^boring\W?$"), "sound/funnysounds/boring.ogg"]
            self.soundDictionaries[2]["boze"] = [re.compile(r"^boze\W?$"), "sound/funnysounds/boze.ogg"]
            self.soundDictionaries[2]["bright side of life"] = [re.compile(r"^(?:bright ?side ?of ?life)\W?$"), "sound/funnysounds/brightsideoflife.ogg"]
            self.soundDictionaries[2]["buckdich"] = [re.compile(r"^buckdich\W?$"), "sound/funnysounds/buckdich.ogg"]
            self.soundDictionaries[2]["bullshitter"] = [re.compile(r"^bullshitter\W?$"), "sound/funnysounds/bullshitter.ogg"]
            self.soundDictionaries[2]["burns burns"] = [re.compile(r"^burns burns\W?$"), "sound/funnysounds/burnsburns.ogg"]
            self.soundDictionaries[2]["camel toe"] = [re.compile(r"^camel toe\W?$"), "sound/funnysounds/cameltoe.ogg"]
            self.soundDictionaries[2]["can't touch this"] = [re.compile(r"^can'?t touch this\W?$"), "sound/funnysounds/canttouchthis.ogg"]
            self.soundDictionaries[2]["cccp"] = [re.compile(r"^(?:cccp|ussr)\W?$"), "sound/funnysounds/cccp.ogg"]
            self.soundDictionaries[2]["champions"] = [re.compile(r"^champions\W?$"), "sound/funnysounds/champions.ogg"]
            self.soundDictionaries[2]["chicken"] = [re.compile(r"^chicken\W?$"), "sound/funnysounds/chicken.ogg"]
            self.soundDictionaries[2]["chocolate rain"] = [re.compile(r"^chocolate rain\W?$"), "sound/funnysounds/chocolaterain.ogg"]
            self.soundDictionaries[2]["coin"] = [re.compile(r"^coin\W?$"), "sound/funnysounds/coin.ogg"]
            self.soundDictionaries[2]["come"] = [re.compile(r"^come\W?$"), "sound/funnysounds/come.ogg"]
            self.soundDictionaries[2]["Come With Me Now"] = [re.compile(r"^come with me now\W?$"), "sound/funnysounds/ComeWithMeNow.ogg"]
            self.soundDictionaries[2]["Count down"] = [re.compile(r"^count down\W?$"), "sound/funnysounds/Countdown.ogg"]
            self.soundDictionaries[2]["cowards"] = [re.compile(r"^cowards\W?$"), "sound/funnysounds/cowards.ogg"]
            self.soundDictionaries[2]["crazy"] = [re.compile(r"^crazy\W?$"), "sound/funnysounds/crazy.ogg"]
            self.soundDictionaries[2]["damnit"] = [re.compile(r"^damnit\W?$"), "sound/funnysounds/damnit.ogg"]
            self.soundDictionaries[2]["Danger Zone"] = [re.compile(r"^danger zone\W?$"), "sound/funnysounds/DangerZone.ogg"]
            self.soundDictionaries[2]["dead soon"] = [re.compile(r"^(?:deadsoon|dead soon)\W?$"), "sound/funnysounds/deadsoon.ogg"]
            self.soundDictionaries[2]["defeated"] = [re.compile(r"^defeated\W?$"), "sound/funnysounds/defeated.ogg"]
            self.soundDictionaries[2]["devil"] = [re.compile(r"^devil\W?$"), "sound/funnysounds/devil.ogg"]
            self.soundDictionaries[2]["doesn't love you"] = [re.compile(r"^doesn'?t love you\W?$"), "sound/funnysounds/doesntloveyou.ogg"]
            self.soundDictionaries[2]["du bist"] = [re.compile(r"^du bist\W?$"), "sound/funnysounds/dubist.ogg"]
            self.soundDictionaries[2]["du hast"] = [re.compile(r"^du hast\W?$"), "sound/funnysounds/duhast.ogg"]
            self.soundDictionaries[2]["dumb ways"] = [re.compile(r"^dumb ways\W?$"), "sound/funnysounds/dumbways.ogg"]
            self.soundDictionaries[2]["Eat Pussy"] = [re.compile(r"^eat pussy\W?$"), "sound/funnysounds/EatPussy.ogg"]
            self.soundDictionaries[2]["education"] = [re.compile(r"^education\W?$"), "sound/funnysounds/education.ogg"]
            self.soundDictionaries[2]["einschrei"] = [re.compile(r"^einschrei\W?$"), "sound/funnysounds/einschrei.ogg"]
            self.soundDictionaries[2]["Eins Zwei"] = [re.compile(r"^eins zwei\W?$"), "sound/funnysounds/EinsZwei.ogg"]
            self.soundDictionaries[2]["electro"] = [re.compile(r"^electro\W?$"), "sound/funnysounds/electro.ogg"]
            self.soundDictionaries[2]["elementary"] = [re.compile(r"^elementary\W?$"), "sound/funnysounds/elementary.ogg"]
            self.soundDictionaries[2]["engel"] = [re.compile(r"^engel\W?$"), "sound/funnysounds/engel.ogg"]
            self.soundDictionaries[2]["erstwenn"] = [re.compile(r"^erstwenn\W?$"), "sound/funnysounds/erstwenn.ogg"]
            self.soundDictionaries[2]["exit light"] = [re.compile(r"^(?:exit ?light)\W?$"), "sound/funnysounds/exitlight.ogg"]
            self.soundDictionaries[2]["faint"] = [re.compile(r"^faint\W?$"), "sound/funnysounds/faint.ogg"]
            self.soundDictionaries[2]["fatality"] = [re.compile(r"^fatality\W?$"), "sound/funnysounds/fatality.ogg"]
            self.soundDictionaries[2]["Feel Good"] = [re.compile(r"^feel good\W?$"), "sound/funnysounds/FeelGood.ogg"]
            self.soundDictionaries[2]["flesh wound"] = [re.compile(r"^flesh wound\W?$"), "sound/funnysounds/fleshwound.ogg"]
            self.soundDictionaries[2]["for you"] = [re.compile(r"^for you\W?$"), "sound/funnysounds/foryou.ogg"]
            self.soundDictionaries[2]["freestyler"] = [re.compile(r"^freestyler\W?$"), "sound/funnysounds/freestyler.ogg"]
            self.soundDictionaries[2]["fuckfuck"] = [re.compile(r"^fuckfuck\W?$"), "sound/funnysounds/fuckfuck.ogg"]
            self.soundDictionaries[2]["fucking burger"] = [re.compile(r"^fucking burger\W?$"), "sound/funnysounds/fuckingburger.ogg"]
            self.soundDictionaries[2]["fucking kids"] = [re.compile(r"^fucking kids\W?$"), "sound/funnysounds/fuckingkids.ogg"]
            self.soundDictionaries[2]["gangnam"] = [re.compile(r"^gangnam\W?$"), "sound/funnysounds/gangnam.ogg"]
            self.soundDictionaries[2]["ganjaman"] = [re.compile(r"^ganjaman\W?$"), "sound/funnysounds/ganjaman.ogg"]
            self.soundDictionaries[2]["gay"] = [re.compile(r"^gay\W?$"), "sound/funnysounds/gay.ogg"]
            self.soundDictionaries[2]["get crowbar"] = [re.compile(r"^get crowbar\W?$"), "sound/funnysounds/getcrowbar.ogg"]
            self.soundDictionaries[2]["get out the way"] = [re.compile(r"^get out the way\W?$"), "sound/funnysounds/getouttheway.ogg"]
            self.soundDictionaries[2]["ghostbusters"] = [re.compile(r"^ghostbusters\W?$"), "sound/funnysounds/ghostbusters.ogg"]
            self.soundDictionaries[2]["girl look"] = [re.compile(r"^girl look\W?$"), "sound/funnysounds/girllook.ogg"]
            self.soundDictionaries[2]["girly"] = [re.compile(r"^girly\W?$"), "sound/funnysounds/girly.ogg"]
            self.soundDictionaries[2]["gnr guitar"] = [re.compile(r"^gnr guitar\W?$"), "sound/funnysounds/gnrguitar.ogg"]
            self.soundDictionaries[2]["goddamn right"] = [re.compile(r"^goddamn right\W?$"), "sound/funnysounds/goddamnright.ogg"]
            self.soundDictionaries[2]["goodbye andrea"] = [re.compile(r"^goodbye andrea\W?$"), "sound/funnysounds/goodbyeandrea.ogg"]
            self.soundDictionaries[2]["goodbye sarah"] = [re.compile(r"^goodbye sarah\W?$"), "sound/funnysounds/goodbyesarah.ogg"]
            self.soundDictionaries[2]["gotcha"] = [re.compile(r"^gotcha\W?$"), "sound/funnysounds/gotcha.ogg"]
            self.soundDictionaries[2]["hakunamatata"] = [re.compile(r"^hakunamatata\W?$"), "sound/funnysounds/hakunamatata.ogg"]
            self.soundDictionaries[2]["hammertime"] = [re.compile(r"^hammertime\W?$"), "sound/funnysounds/hammertime.ogg"]
            self.soundDictionaries[2]["hello"] = [re.compile(r"^hello\W?$"), "sound/funnysounds/hello.ogg"]
            self.soundDictionaries[2]["hellstestern"] = [re.compile(r"^hellstestern\W?$"), "sound/funnysounds/hellstestern.ogg"]
            self.soundDictionaries[2]["holy"] = [re.compile(r"^holy\W?$"), "sound/funnysounds/holy.ogg"]
            self.soundDictionaries[2]["hoppereiter"] = [re.compile(r"^hoppereiter\W?$"), "sound/funnysounds/hoppereiter.ogg"]
            self.soundDictionaries[2]["how are you"] = [re.compile(r"^how are you\W?$"), "sound/funnysounds/howareyou.ogg"]
            self.soundDictionaries[2]["hush"] = [re.compile(r"^hush\W?$"), "sound/funnysounds/hush.ogg"]
            self.soundDictionaries[2]["i bet"] = [re.compile(r"^(?:i ?bet)\W?$"), "sound/funnysounds/ibet.ogg"]
            self.soundDictionaries[2]["i can't believe"] = [re.compile(r"^i can'?t believe\W?$"), "sound/funnysounds/icantbelieve.ogg"]
            self.soundDictionaries[2]["ichtuedieweh"] = [re.compile(r"^ichtuedieweh\W?$"), "sound/funnysounds/ichtuedieweh.ogg"]
            self.soundDictionaries[2]["i do parkour"] = [re.compile(r"^i do parkour\W?$"), "sound/funnysounds/idoparkour.ogg"]
            self.soundDictionaries[2]["i hate all"] = [re.compile(r"^i hate all\W?$"), "sound/funnysounds/ihateall.ogg"]
            self.soundDictionaries[2]["ill be back"] = [re.compile(r"^i'?ll be back\W?$"), "sound/funnysounds/beback.ogg"]
            self.soundDictionaries[2]["imperial"] = [re.compile(r"^imperial\W?$"), "sound/funnysounds/imperial.ogg"]
            self.soundDictionaries[2]["i'm sexy"] = [re.compile(r"^i'?m sexy\W?$"), "sound/funnysounds/imsexy.ogg"]
            self.soundDictionaries[2]["i'm your father"] = [re.compile(r"^i'?m your father\W?$"), "sound/funnysounds/imyourfather.ogg"]
            self.soundDictionaries[2]["incoming"] = [re.compile(r"^incoming\W?$"), "sound/funnysounds/incoming.ogg"]
            self.soundDictionaries[2]["indiana jones"] = [re.compile(r"^indiana jones\W?$"), "sound/funnysounds/indianajones.ogg"]
            self.soundDictionaries[2]["in your head zombie"] = [re.compile(r"^in your head zombie\W?$"), "sound/funnysounds/inyourheadzombie.ogg"]
            self.soundDictionaries[2]["i see assholes"] = [re.compile(r"^i see assholes\W?$"), "sound/funnysounds/iseeassholes.ogg"]
            self.soundDictionaries[2]["i see dead people"] = [re.compile(r"^i see dead people\W?$"), "sound/funnysounds/iseedeadpeople.ogg"]
            self.soundDictionaries[2]["it's my life"] = [re.compile(r"^it'?s my life\W?$"), "sound/funnysounds/itsmylife.ogg"]
            self.soundDictionaries[2]["it's not"] = [re.compile(r"^it'?s not\W?$"), "sound/funnysounds/itsnot.ogg"]
            self.soundDictionaries[2]["jackpot"] = [re.compile(r"^jackpot\W?$"), "sound/funnysounds/jackpot.ogg"]
            self.soundDictionaries[2]["jesus"] = [re.compile(r"^jesus\W?$"), "sound/funnysounds/jesus.ogg"]
            self.soundDictionaries[2]["Jesus Oh"] = [re.compile(r"^jesus Oh\W?$"), "sound/funnysounds/JesusOh.ogg"]
            self.soundDictionaries[2]["john cena"] = [re.compile(r"^(?:john ?cena)\W?$"), "sound/funnysounds/johncena.ogg"]
            self.soundDictionaries[2]["jump motherfucker"] = [re.compile(r"^jump motherfucker\W?$"), "sound/funnysounds/jumpmotherfucker.ogg"]
            self.soundDictionaries[2]["just do it"] = [re.compile(r"^just do it\W?$"), "sound/funnysounds/justdoit.ogg"]
            self.soundDictionaries[2]["kamehameha"] = [re.compile(r"^kamehameha\W?$"), "sound/funnysounds/kamehameha.ogg"]
            self.soundDictionaries[2]["keep on fighting"] = [re.compile(r"^keep on fighting\W?$"), "sound/funnysounds/keeponfighting.ogg"]
            self.soundDictionaries[2]["keep your shirt on"] = [re.compile(r"^keep your shirt on\W?$"), "sound/funnysounds/keepyourshirton.ogg"]
            self.soundDictionaries[2]["Knocked Down"] = [re.compile(r"^knocked down\W?$"), "sound/funnysounds/KnockedDown.ogg"]
            self.soundDictionaries[2]["kommtdiesonne"] = [re.compile(r"^kommtdiesonne\W?$"), "sound/funnysounds/kommtdiesonne.ogg"]
            self.soundDictionaries[2]["kung fu"] = [re.compile(r"^(?:kung ?fu)\W?$"), "sound/funnysounds/kungfu.ogg"]
            self.soundDictionaries[2]["lately"] = [re.compile(r"^lately\W?$"), "sound/funnysounds/lately.ogg"]
            self.soundDictionaries[2]["Legitness"] = [re.compile(r"^legitness\W?$"), "sound/funnysounds/Legitness.ogg"]
            self.soundDictionaries[2]["let's get ready"] = [re.compile(r"^let'?s get ready\W?$"), "sound/funnysounds/letsgetready.ogg"]
            self.soundDictionaries[2]["let's put a smile"] = [re.compile(r"^let'?s put a smile\W?$"), "sound/funnysounds/letsputasmile.ogg"]
            self.soundDictionaries[2]["lights out"] = [re.compile(r"^lights out\W?$"), "sound/funnysounds/lightsout.ogg"]
            self.soundDictionaries[2]["lion king"] = [re.compile(r"^lion king\W?$"), "sound/funnysounds/lionking.ogg"]
            self.soundDictionaries[2]["live to win"] = [re.compile(r"^live to win\W?$"), "sound/funnysounds/livetowin.ogg"]
            self.soundDictionaries[2]["losing my religion"] = [re.compile(r"^losing my religion\W?$"), "sound/funnysounds/losingmyreligion.ogg"]
            self.soundDictionaries[2]["love me"] = [re.compile(r"^(?:love ?me)\W?$"), "sound/funnysounds/loveme.ogg"]
            self.soundDictionaries[2]["low"] = [re.compile(r"^low\W?$"), "sound/funnysounds/low.ogg"]
            self.soundDictionaries[2]["luck"] = [re.compile(r"^luck\W?$"), "sound/funnysounds/luck.ogg"]
            self.soundDictionaries[2]["lust"] = [re.compile(r"^lust\W?$"), "sound/funnysounds/lust.ogg"]
            self.soundDictionaries[2]["mahnamahna"] = [re.compile(r"^mahnamahna\W?$"), "sound/funnysounds/mahnamahna.ogg"]
            self.soundDictionaries[2]["mario"] = [re.compile(r"^mario\W?$"), "sound/funnysounds/mario.ogg"]
            self.soundDictionaries[2]["Me"] = [re.compile(r"^me\W?$"), "sound/funnysounds/Me.ogg"]
            self.soundDictionaries[2]["meinland"] = [re.compile(r"^meinland\W?$"), "sound/funnysounds/meinland.ogg"]
            self.soundDictionaries[2]["message"] = [re.compile(r"^message\W?$"), "sound/funnysounds/message.ogg"]
            self.soundDictionaries[2]["mimimi"] = [re.compile(r"^mimimi\W?$"), "sound/funnysounds/mimimi.ogg"]
            self.soundDictionaries[2]["mission"] = [re.compile(r"^mission\W?$"), "sound/funnysounds/mission.ogg"]
            self.soundDictionaries[2]["moan"] = [re.compile(r"^moan\W?$"), "sound/funnysounds/moan.ogg"]
            self.soundDictionaries[2]["mortal kombat"] = [re.compile(r"^mortal kombat\W?$"), "sound/funnysounds/mortalkombat.ogg"]
            self.soundDictionaries[2]["move ass"] = [re.compile(r"^move ass\W?$"), "sound/funnysounds/moveass.ogg"]
            self.soundDictionaries[2]["muppet opening"] = [re.compile(r"^muppet opening\W?$"), "sound/funnysounds/muppetopening.ogg"]
            self.soundDictionaries[2]["my little pony"] = [re.compile(r"^my little pony\W?$"), "sound/funnysounds/mylittlepony.ogg"]
            self.soundDictionaries[2]["my name"] = [re.compile(r"^my name\W?$"), "sound/funnysounds/myname.ogg"]
            self.soundDictionaries[2]["never seen"] = [re.compile(r"^never seen\W?$"), "sound/funnysounds/neverseen.ogg"]
            self.soundDictionaries[2]["nightmare"] = [re.compile(r"^nightmare\W?$"), "sound/funnysounds/nightmare.ogg"]
            self.soundDictionaries[2]["nobody likes you"] = [re.compile(r"^nobody likes you\W?$"), "sound/funnysounds/nobodylikesyou.ogg"]
            self.soundDictionaries[2]["nonie"] = [re.compile(r"^nonie\W?$"), "sound/funnysounds/nonie.ogg"]
            self.soundDictionaries[2]["nooo"] = [re.compile(r"^nooo+\W?$"), "sound/funnysounds/nooo.ogg"]
            self.soundDictionaries[2]["no time for loosers"] = [re.compile(r"^no time for loosers\W?$"), "sound/funnysounds/notimeforloosers.ogg"]
            self.soundDictionaries[2]["numanuma"] = [re.compile(r"^numanuma\W?$"), "sound/funnysounds/numanuma.ogg"]
            self.soundDictionaries[2]["nyancat"] = [re.compile(r"^nyancat\W?$"), "sound/funnysounds/nyancat.ogg"]
            self.soundDictionaries[2]["o fuck"] = [re.compile(r"^o fuck\W?$"), "sound/funnysounds/ofuck.ogg"]
            self.soundDictionaries[2]["oh my god"] = [re.compile(r"^oh my god\W?$"), "sound/funnysounds/ohmygod.ogg"]
            self.soundDictionaries[2]["Oh My Gosh"] = [re.compile(r"^oh my gosh\W?$"), "sound/funnysounds/OhMyGosh.ogg"]
            self.soundDictionaries[2]["ohnedich"] = [re.compile(r"^ohnedich\W?$"), "sound/funnysounds/ohnedich.ogg"]
            self.soundDictionaries[2]["oh no"] = [re.compile(r"^oh no\W?$"), "sound/funnysounds/ohno.ogg"]
            self.soundDictionaries[2]["oh noe"] = [re.compile(r"^oh noe\W?$"), "sound/funnysounds/ohnoe.ogg"]
            self.soundDictionaries[2]["pacman"] = [re.compile(r"^pacman\W?$"), "sound/funnysounds/pacman.ogg"]
            self.soundDictionaries[2]["pick me up"] = [re.compile(r"^pick me up\W?$"), "sound/funnysounds/pickmeup.ogg"]
            self.soundDictionaries[2]["pikachu"] = [re.compile(r"^pikachu\W?$"), "sound/funnysounds/pikachu.ogg"]
            self.soundDictionaries[2]["pinkiepie"] = [re.compile(r"^pinkiepie\W?$"), "sound/funnysounds/pinkiepie.ogg"]
            self.soundDictionaries[2]["Pink Panther"] = [re.compile(r"^pink panther\W?$"), "sound/funnysounds/PinkPanther.ogg"]
            self.soundDictionaries[2]["pipe"] = [re.compile(r"^pipe\W?$"), "sound/funnysounds/pipe.ogg"]
            self.soundDictionaries[2]["piss me off"] = [re.compile(r"^piss me off\W?$"), "sound/funnysounds/pissmeoff.ogg"]
            self.soundDictionaries[2]["play a game"] = [re.compile(r"^play a game\W?$"), "sound/funnysounds/playagame.ogg"]
            self.soundDictionaries[2]["pooping"] = [re.compile(r"^pooping\W?$"), "sound/funnysounds/pooping.ogg"]
            self.soundDictionaries[2]["powerpuff"] = [re.compile(r"^powerpuff\W?$"), "sound/funnysounds/powerpuff.ogg"]
            self.soundDictionaries[2]["radioactive"] = [re.compile(r"^radioactive\W?$"), "sound/funnysounds/radioactive.ogg"]
            self.soundDictionaries[2]["rammsteinriff"] = [re.compile(r"^rammsteinriff\W?$"), "sound/funnysounds/rammsteinriff.ogg"]
            self.soundDictionaries[2]["red wins"] = [re.compile(r"^red ?wins\W?$"), "sound/funnysounds/redwins.ogg"]
            self.soundDictionaries[2]["renegade"] = [re.compile(r"^renegade\W?$"), "sound/funnysounds/renegade.ogg"]
            self.soundDictionaries[2]["retard"] = [re.compile(r"^retard\W?$"), "sound/funnysounds/Retard.ogg"]
            self.soundDictionaries[2]["rocky"] = [re.compile(r"^rocky\W?$"), "sound/funnysounds/rocky"]
            self.soundDictionaries[2]["rock you guitar"] = [re.compile(r"^rock ?you ?guitar\W?$"), "sound/funnysounds/rockyouguitar.ogg"]
            self.soundDictionaries[2]["sail"] = [re.compile(r"^sail\W?$"), "sound/funnysounds/sail.ogg"]
            self.soundDictionaries[2]["Salil"] = [re.compile(r"^salil\W?$"), "sound/funnysounds/Salil.ogg"]
            self.soundDictionaries[2]["samba"] = [re.compile(r"^samba\W?$"), "sound/funnysounds/samba.ogg"]
            self.soundDictionaries[2]["sandstorm"] = [re.compile(r"^sandstorm\W?$"), "sound/funnysounds/sandstorm.ogg"]
            self.soundDictionaries[2]["saymyname"] = [re.compile(r"^saymyname\W?$"), "sound/funnysounds/saymyname.ogg"]
            self.soundDictionaries[2]["scatman"] = [re.compile(r"^scatman\W?$"), "sound/funnysounds/scatman.ogg"]
            self.soundDictionaries[2]["sell you all"] = [re.compile(r"^sell you all\W?$"), "sound/funnysounds/sellyouall.ogg"]
            self.soundDictionaries[2]["sense of humor"] = [re.compile(r"^sense of humor\W?$"), "sound/funnysounds/senseofhumor.ogg"]
            self.soundDictionaries[2]["shakesenora"] = [re.compile(r"^shakesenora\W?$"), "sound/funnysounds/shakesenora.ogg"]
            self.soundDictionaries[2]["shut the fuck up"] = [re.compile(r"^shut the fuck up\W?$"), "sound/funnysounds/shutthefuckup.ogg"]
            self.soundDictionaries[2]["shut your fucking mouth"] = [re.compile(r"^shut your fucking mouth\W?$"), "sound/funnysounds/shutyourfuckingmouth.ogg"]
            self.soundDictionaries[2]["silence"] = [re.compile(r"^silence\W?$"), "sound/funnysounds/silence.ogg"]
            self.soundDictionaries[2]["Skeet Skeet"] = [re.compile(r"^(?:(all )?skeet skeet)\W?$"), "sound/funnysounds/AllSkeetSkeet.ogg"]
            self.soundDictionaries[2]["smooth criminal"] = [re.compile(r"^smooth criminal\W?$"), "sound/funnysounds/smoothcriminal.ogg"]
            self.soundDictionaries[2]["socobatevira"] = [re.compile(r"^socobatevira\W?$"), "sound/funnysounds/socobatevira.ogg"]
            self.soundDictionaries[2]["socobatevira end"] = [re.compile(r"^socobatevira end\W?$"), "sound/funnysounds/socobateviraend.ogg"]
            self.soundDictionaries[2]["socobatevira fast"] = [re.compile(r"^socobatevira fast\W?$"), "sound/funnysounds/socobatevirafast.ogg"]
            self.soundDictionaries[2]["socobatevira slow"] = [re.compile(r"^socobatevira slow\W?$"), "sound/funnysounds/socobateviraslow.ogg"]
            self.soundDictionaries[2]["sogivemereason"] = [re.compile(r"^sogivemereason\W?$"), "sound/funnysounds/sogivemereason.ogg"]
            self.soundDictionaries[2]["so stupid"] = [re.compile(r"^so stupid\W?$"), "sound/funnysounds/sostupid.ogg"]
            self.soundDictionaries[2]["Space Jam"] = [re.compile(r"^space jam\W?$"), "sound/funnysounds/SpaceJam.ogg"]
            self.soundDictionaries[2]["space unicorn"] = [re.compile(r"^space unicorn\W?$"), "sound/funnysounds/spaceunicorn.ogg"]
            self.soundDictionaries[2]["spierdalaj"] = [re.compile(r"^spierdalaj\W?$"), "sound/funnysounds/spierdalaj.ogg"]
            self.soundDictionaries[2]["stamp on"] = [re.compile(r"^stamp on\W?$"), "sound/funnysounds/stampon.ogg"]
            self.soundDictionaries[2]["star wars"] = [re.compile(r"^star wars\W?$"), "sound/funnysounds/starwars.ogg"]
            self.soundDictionaries[2]["stayin alive"] = [re.compile(r"^stayin alive\W?$"), "sound/funnysounds/stayinalive.ogg"]
            self.soundDictionaries[2]["stoning"] = [re.compile(r"^stoning\W?$"), "sound/funnysounds/stoning.ogg"]
            self.soundDictionaries[2]["stop"] = [re.compile(r"^stop\W?$"), "sound/funnysounds/Stop.ogg"]
            self.soundDictionaries[2]["story"] = [re.compile(r"^story\W?$"), "sound/funnysounds/story.ogg"]
            self.soundDictionaries[2]["surprise"] = [re.compile(r"^surprise\W?$"), "sound/funnysounds/surprise.ogg"]
            self.soundDictionaries[2]["swedish chef"] = [re.compile(r"^swedish chef\W?$"), "sound/funnysounds/swedishchef.ogg"]
            self.soundDictionaries[2]["sweet dreams"] = [re.compile(r"^sweet dreams\W?$"), "sound/funnysounds/sweetdreams.ogg"]
            self.soundDictionaries[2]["take me down"] = [re.compile(r"^take me down\W?$"), "sound/funnysounds/takemedown.ogg"]
            self.soundDictionaries[2]["talk scotish"] = [re.compile(r"^talk scotish\W?$"), "sound/funnysounds/talkscotish.ogg"]
            self.soundDictionaries[2]["teamwork"] = [re.compile(r"^teamwork\W?$"), "sound/funnysounds/teamwork.ogg"]
            self.soundDictionaries[2]["technology"] = [re.compile(r"^technology\W?$"), "sound/funnysounds/technology.ogg"]
            self.soundDictionaries[2]["this is sparta"] = [re.compile(r"^this is sparta\W?$"), "sound/funnysounds/thisissparta.ogg"]
            self.soundDictionaries[2]["thunderstruck"] = [re.compile(r"^thunderstruck\W?$"), "sound/funnysounds/thunderstruck.ogg"]
            self.soundDictionaries[2]["to church"] = [re.compile(r"^to church\W?$"), "sound/funnysounds/tochurch.ogg"]
            self.soundDictionaries[2]["tsunami"] = [re.compile(r"^tsunami\W?$"), "sound/funnysounds/tsunami.ogg"]
            self.soundDictionaries[2]["tuturu"] = [re.compile(r"^tuturu\W?$"), "sound/funnysounds/tuturu.ogg"]
            self.soundDictionaries[2]["tututu"] = [re.compile(r"^tututu\W?$"), "sound/funnysounds/tututu.ogg"]
            self.soundDictionaries[2]["unbelievable"] = [re.compile(r"^unbelievable\W?$"), "sound/funnysounds/unbelievable.ogg"]
            self.soundDictionaries[2]["undderhaifisch"] = [re.compile(r"^undderhaifisch\W?$"), "sound/funnysounds/undderhaifisch.ogg"]
            self.soundDictionaries[2]["up town girl"] = [re.compile(r"^up town girl\W?$"), "sound/funnysounds/uptowngirl.ogg"]
            self.soundDictionaries[2]["valkyries"] = [re.compile(r"^valkyries\W?$"), "sound/funnysounds/valkyries.ogg"]
            self.soundDictionaries[2]["wahwahwah"] = [re.compile(r"(?:wahwahwah|(dc)?mattic)"), "sound/funnysounds/wahwahwah.ogg"]
            self.soundDictionaries[2]["want you"] = [re.compile(r"^want you\W?$"), "sound/funnysounds/wantyou.ogg"]
            self.soundDictionaries[2]["wazzup"] = [re.compile(r"^wazzup\W?$"), "sound/funnysounds/wazzup.ogg"]
            self.soundDictionaries[2]["wehmirohweh"] = [re.compile(r"^wehmirohweh\W?$"), "sound/funnysounds/wehmirohweh.ogg"]
            self.soundDictionaries[2]["what is love"] = [re.compile(r"^what is love\W?$"), "sound/funnysounds/whatislove.ogg"]
            self.soundDictionaries[2]["when angels"] = [re.compile(r"^when angels\W?$"), "sound/funnysounds/whenangels.ogg"]
            self.soundDictionaries[2]["where are you"] = [re.compile(r"^where are you\W?$"), "sound/funnysounds/whereareyou.ogg"]
            self.soundDictionaries[2]["whistle"] = [re.compile(r"^whistle\W?$"), "sound/funnysounds/whistle.ogg"]
            self.soundDictionaries[2]["why mad"] = [re.compile(r"^why mad\W?$"), "sound/funnysounds/whymad.ogg"]
            self.soundDictionaries[2]["Will Be Singing"] = [re.compile(r"^will be singing\W?$"), "sound/funnysounds/WillBeSinging.ogg"]
            self.soundDictionaries[2]["wimbaway"] = [re.compile(r"^wimbaway\W?$"), "sound/funnysounds/wimbaway.ogg"]
            self.soundDictionaries[2]["windows"] = [re.compile(r"^windows\W?$"), "sound/funnysounds/windows.ogg"]
            self.soundDictionaries[2]["would you like"] = [re.compile(r"^would you like\W?$"), "sound/funnysounds/wouldyoulike.ogg"]
            self.soundDictionaries[2]["wtf"] = [re.compile(r"^wtf\W?$"), "sound/funnysounds/wtf.ogg"]
            self.soundDictionaries[2]["yeee"] = [re.compile(r"^yeee\W?$"), "sound/funnysounds/yeee.ogg"]
            self.soundDictionaries[2]["yes master"] = [re.compile(r"^yes master\W?$"), "sound/funnysounds/yesmaster.ogg"]
            self.soundDictionaries[2]["yhehehe"] = [re.compile(r"^yhehehe\W?$"), "sound/funnysounds/yhehehe.ogg"]
            self.soundDictionaries[2]["ymca"] = [re.compile(r"^ymca\W?$"), "sound/funnysounds/ymca.ogg"]
            self.soundDictionaries[2]["you"] = [re.compile(r"^you\W?$"), "sound/funnysounds/You.ogg"]
            self.soundDictionaries[2]["you are a cunt"] = [re.compile(r"^you are a cunt\W?$"), "sound/funnysounds/cunt.ogg"]
            self.soundDictionaries[2]["you fucked my wife"] = [re.compile(r"^(you fucked )?my wife\W?$"), "sound/funnysounds/youfuckedmywife.ogg"]
            self.soundDictionaries[2]["You Realise"] = [re.compile(r"^you realise\W?$"), "sound/funnysounds/YouRealise.ogg"]

        if self.Enabled_SoundPacks[3]:
            self.soundDictionaries[3]["my ride"] = [re.compile(r"^my ride\W?$"), "sound/duke/2ride06.wav"]
            self.soundDictionaries[3]["abort"] = [re.compile(r"^abort\W?$"), "sound/duke/abort01.wav"]
            self.soundDictionaries[3]["ahhh"] = [re.compile(r"^ahhh\W?$"), "sound/duke/ahh04.wav"]
            self.soundDictionaries[3]["much better"] = [re.compile(r"^much better\W?$"), "sound/duke/ahmuch03.wav"]
            self.soundDictionaries[3]["aisle4"] = [re.compile(r"^aisle 4\W?$"), "sound/duke/aisle402.wav"]
            self.soundDictionaries[3]["a mess"] = [re.compile(r"^a mess\W?$"), "sound/duke/amess06.wav"]
            self.soundDictionaries[3]["annoying"] = [re.compile(r"^annoying\W?$"), "sound/duke/annoy03.wav"]
            self.soundDictionaries[3]["bitchin"] = [re.compile(r"^bitchin\W?$"), "sound/duke/bitchn04.wav"]
            self.soundDictionaries[3]["blow it out"] = [re.compile(r"^blow it out\W?$"), "sound/duke/blowit01.wav"]
            self.soundDictionaries[3]["booby trap"] = [re.compile(r"^booby trap\W?$"), "sound/duke/booby04.wav"]
            self.soundDictionaries[3]["bookem"] = [re.compile(r"^bookem\W?$"), "sound/duke/bookem03.wav"]
            self.soundDictionaries[3]["born to be wild"] = [re.compile(r"^born to be wild\W?$"), "sound/duke/born01.wav"]
            self.soundDictionaries[3]["chew gum"] = [re.compile(r"^chew gum\W?$"), "sound/duke/chew05.wav"]
            self.soundDictionaries[3]["come on"] = [re.compile(r"^come on\W?$"), "sound/duke/comeon02.wav"]
            self.soundDictionaries[3]["the con"] = [re.compile(r"^the con\W?$"), "sound/duke/con03.wav"]
            self.soundDictionaries[3]["cool"] = [re.compile(r"^cool\W?$"), "sound/duke/cool01.wav"]
            self.soundDictionaries[3]["not crying"] = [re.compile(r"^not crying\W?$"), "sound/duke/cry01.wav"]
            self.soundDictionaries[3]["daamn"] = [re.compile(r"^daa?mn\W?$"), "sound/duke/damn03.wav"]
            self.soundDictionaries[3]["damit"] = [re.compile(r"^damit\W?$"), "sound/duke/damnit04.wav"]
            self.soundDictionaries[3]["dance"] = [re.compile(r"^dance\W?$"), "sound/duke/dance01.wav"]
            self.soundDictionaries[3]["diesob"] = [re.compile(r"^diesob\W?$"), "sound/duke/diesob03.wav"]
            self.soundDictionaries[3]["doomed"] = [re.compile(r"^doomed\W?$"), "sound/duke/doomed16.wav"]
            self.soundDictionaries[3]["eyye"] = [re.compile(r"^eyye\W?$"), "sound/duke/dscrem38.wav"]
            self.soundDictionaries[3]["duke nukem"] = [re.compile(r"^duke nukem\W?$"), "sound/duke/duknuk14.wav"]
            self.soundDictionaries[3]["no way"] = [re.compile(r"^no way\W?$"), "sound/duke/eat08.wav"]
            self.soundDictionaries[3]["eat shit"] = [re.compile(r"^eat shit\W?$"), "sound/duke/eatsht01.wav"]
            self.soundDictionaries[3]["escape"] = [re.compile(r"^escape\W?$"), "sound/duke/escape01.wav"]
            self.soundDictionaries[3]["face ass"] = [re.compile(r"^face ass\W?$"), "sound/duke/face01.wav"]
            self.soundDictionaries[3]["a force"] = [re.compile(r"^a force\W?$"), "sound/duke/force01.wav"]
            self.soundDictionaries[3]["get that crap"] = [re.compile(r"^get that crap\W?$"), "sound/duke/getcrap1.wav"]
            self.soundDictionaries[3]["get some"] = [re.compile(r"^get some\W?$"), "sound/duke/getsom1a.wav"]
            self.soundDictionaries[3]["game over"] = [re.compile(r"^game over\W?$"), "sound/duke/gmeovr05.wav"]
            self.soundDictionaries[3]["gotta hurt"] = [re.compile(r"^gotta hurt\W?$"), "sound/duke/gothrt01.wav"]
            self.soundDictionaries[3]["groovy"] = [re.compile(r"^groovy\W?$"), "sound/duke/groovy02.wav"]
            self.soundDictionaries[3]["you guys suck"] = [re.compile(r"^you guys suck\W?$"), "sound/duke/guysuk01.wav"]
            self.soundDictionaries[3]["hail king"] = [re.compile(r"^hail king\W?$"), "sound/duke/hail01.wav"]
            self.soundDictionaries[3]["shit happens"] = [re.compile(r"^shit happens\W?$"), "sound/duke/happen01.wav"]
            self.soundDictionaries[3]["holy cow"] = [re.compile(r"^holy cow\W?$"), "sound/duke/holycw01.wav"]
            self.soundDictionaries[3]["holy shit"] = [re.compile(r"^holy shit\W?$"), "sound/duke/holysh02.wav"]
            self.soundDictionaries[3]["im good"] = [re.compile(r"^im good\W?$"), "sound/duke/imgood12.wav"]
            self.soundDictionaries[3]["independence"] = [re.compile(r"^independence\W?$"), "sound/duke/indpnc01.wav"]
            self.soundDictionaries[3]["in hell"] = [re.compile(r"^in ?hell\W?$"), "sound/duke/inhell01.wav"]
            self.soundDictionaries[3]["going in"] = [re.compile(r"^going ?in\W?$"), "sound/duke/introc.wav"]
            self.soundDictionaries[3]["dr jones"] = [re.compile(r"^dr jones\W?$"), "sound/duke/jones04.wav"]
            self.soundDictionaries[3]["kick your ass"] = [re.compile(r"^(kick )?your ass\W?$"), "sound/duke/kick01-i.wav"]
            self.soundDictionaries[3]["ktit"] = [re.compile(r"^ktit\W?$"), "sound/duke/ktitx.wav"]
            self.soundDictionaries[3]["let god"] = [re.compile(r"^let god\W?$"), "sound/duke/letgod01.wav"]
            self.soundDictionaries[3]["let's rock"] = [re.compile(r"^let'?s rock\W?$"), "sound/duke/letsrk03.wav"]
            self.soundDictionaries[3]["lookin' good"] = [re.compile(r"^lookin'? good\W?$"), "sound/duke/lookin01.wav"]
            self.soundDictionaries[3]["make my day"] = [re.compile(r"^make my day\W?$"), "sound/duke/makeday1.wav"]
            self.soundDictionaries[3]["midevil"] = [re.compile(r"^midevil\W?$"), "sound/duke/mdevl01.wav"]
            self.soundDictionaries[3]["my meat"] = [re.compile(r"^my meat\W?$"), "sound/duke/meat04-n.wav"]
            self.soundDictionaries[3]["no time"] = [re.compile(r"^no time\W?$"), "sound/duke/myself3a.wav"]
            self.soundDictionaries[3]["i needed that"] = [re.compile(r"^i needed that\W?$"), "sound/duke/needed03.wav"]
            self.soundDictionaries[3]["nobody"] = [re.compile(r"^nobody\W?$"), "sound/duke/nobody01.wav"]
            self.soundDictionaries[3]["only one"] = [re.compile(r"^only one\W?$"), "sound/duke/onlyon03.wav"]
            self.soundDictionaries[3]["my kinda party"] = [re.compile(r"^my kinda party\W?$"), "sound/duke/party03.wav"]
            self.soundDictionaries[3]["gonna pay"] = [re.compile(r"^gonna pay\W?$"), "sound/duke/pay02.wav"]
            self.soundDictionaries[3]["pisses me off"] = [re.compile(r"^pisses me off\W?$"), "sound/duke/pisses01.wav"]
            self.soundDictionaries[3]["pissin me off"] = [re.compile(r"^pissin me off\W?$"), "sound/duke/pissin01.wav"]
            self.soundDictionaries[3]["postal"] = [re.compile(r"^postal\W?$"), "sound/duke/postal01.wav"]
            self.soundDictionaries[3]["aint afraid"] = [re.compile(r"^aint ?afraid\W?$"), "sound/duke/quake06.wav"]
            self.soundDictionaries[3]["r and r"] = [re.compile(r"^r and r\W?$"), "sound/duke/r&r01.wav"]
            self.soundDictionaries[3]["ready for action"] = [re.compile(r"^ready for action\W?$"), "sound/duke/ready2a.wav"]
            self.soundDictionaries[3]["rip your head off"] = [re.compile(r"^rip your head off\W?$"), "sound/duke/rip01.wav"]
            self.soundDictionaries[3]["rip em"] = [re.compile(r"^rip em\W?$"), "sound/duke/ripem08.wav"]
            self.soundDictionaries[3]["rockin"] = [re.compile(r"^rockin\W?$"), "sound/duke/rockin02.wav"]
            self.soundDictionaries[3]["shake it"] = [re.compile(r"^shake ?it\W?$"), "sound/duke/shake2a.wav"]
            self.soundDictionaries[3]["slacker"] = [re.compile(r"^slacker\W?$"), "sound/duke/slacker1.wav"]
            self.soundDictionaries[3]["smack dab"] = [re.compile(r"^smack dab\W?$"), "sound/duke/smack02.wav"]
            self.soundDictionaries[3]["so help me"] = [re.compile(r"^so help me\W?$"), "sound/duke/sohelp02.wav"]
            self.soundDictionaries[3]["suck it down"] = [re.compile(r"^suck it down\W?$"), "sound/duke/sukit01.wav"]
            self.soundDictionaries[3]["terminated"] = [re.compile(r"^terminated\W?$"), "sound/duke/termin01.wav"]
            self.soundDictionaries[3]["this sucks"] = [re.compile(r"^this sucks\W?$"), "sound/duke/thsuk13a.wav"]
            self.soundDictionaries[3]["vacation"] = [re.compile(r"^vacation\W?$"), "sound/duke/vacatn01.wav"]
            self.soundDictionaries[3]["christmas"] = [re.compile(r"^christmas\W?$"), "sound/duke/waitin03.wav"]
            self.soundDictionaries[3]["wants some"] = [re.compile(r"^wants some\W?$"), "sound/duke/wansom4a.wav"]
            self.soundDictionaries[3]["you and me"] = [re.compile(r"^you and me\W?$"), "sound/duke/whipyu01.wav"]
            self.soundDictionaries[3]["where"] = [re.compile(r"^where\W?$"), "sound/duke/whrsit05.wav"]
            self.soundDictionaries[3]["yippie kai yay"] = [re.compile(r"^yippie kai yay\W?$"), "sound/duke/yippie01.wav"]
            self.soundDictionaries[3]["bottle of jack"] = [re.compile(r"^bottle of jack\W?$"), "sound/duke/yohoho01.wav"]
            self.soundDictionaries[3]["long walk"] = [re.compile(r"^long walk\W?$"), "sound/duke/yohoho09.wav"]

        if self.Enabled_SoundPacks[4]:
            self.soundDictionaries[4]["aiming"] = [re.compile(r"^aiming\W?$"), "sound/warp/aiming.ogg"]
            self.soundDictionaries[4]["always open cat"] = [re.compile(r"^always open\W?$"), "sound/warp/always_open.ogg"]
            self.soundDictionaries[4]["thanks for the advice"] = [re.compile(r"^thanks for the advice\W?$"), "sound/warp/ash_advice.ogg"]
            self.soundDictionaries[4]["angry cat"] = [re.compile(r"^angry cat\W?$"), "sound/warp/angry_cat.ogg"]
            self.soundDictionaries[4]["appreciate"] = [re.compile(r"^appreciate\W?$"), "sound/warp/ash_appreciate.ogg"]
            self.soundDictionaries[4]["looking forward to it"] = [re.compile(r"^looking forward to it\W?$"), "sound/warp/ash_lookingforwardtoit.ogg"]
            self.soundDictionaries[4]["make me"] = [re.compile(r"^make me\W?$"), "sound/warp/ash_makeme.ogg"]
            self.soundDictionaries[4]["pessimist"] = [re.compile(r"^pessimist\W?$"), "sound/warp/ash_pessimist.ogg"]
            self.soundDictionaries[4]["shoot me now"] = [re.compile(r"^shoot me now\W?$"), "sound/warp/ash_shootmenow.ogg"]
            self.soundDictionaries[4]["shoot on sight"] = [re.compile(r"^shoot on sight\W?$"), "sound/warp/ash_shootonsight.ogg"]
            self.soundDictionaries[4]["won't happen again"] = [re.compile(r"^won'?t happen again\W?$"), "sound/warp/ash_wonthappenagain.ogg"]
            self.soundDictionaries[4]["attractive"] = [re.compile(r"^attractive\W?$"), "sound/warp/attractive.ogg"]
            self.soundDictionaries[4]["awesome"] = [re.compile(r"^awesome\W?$"), "sound/warp/awesome.ogg"]
            self.soundDictionaries[4]["awkward"] = [re.compile(r"^awkward\W?$"), "sound/warp/awkward.ogg"]
            self.soundDictionaries[4]["bad feeling"] = [re.compile(r"^bad feeling\W?$"), "sound/warp/badfeeling.ogg"]
            self.soundDictionaries[4]["bad idea"] = [re.compile(r"^bad idea\W?$"), "sound/warp/badidea.ogg"]
            self.soundDictionaries[4]["ballbag"] = [re.compile(r"^ballbag\W?$"), "sound/warp/ballbag.ogg"]
            self.soundDictionaries[4]["bburp"] = [re.compile(r"^bburp\W?$"), "sound/warp/bburp.ogg"]
            self.soundDictionaries[4]["bburpp"] = [re.compile(r"^bburpp\W?$"), "sound/warp/bburpp.ogg"]
            self.soundDictionaries[4]["believe"] = [re.compile(r"^believe\W?$"), "sound/warp/believe.ogg"]
            self.soundDictionaries[4]["bend me over"] = [re.compile(r"^bend me over\W?$"), "sound/warp/bend_me_over.ogg"]
            self.soundDictionaries[4]["big leagues"] = [re.compile(r"^big leagues\W?$"), "sound/warp/bigleagues.ogg"]
            self.soundDictionaries[4]["bike horn"] = [re.compile(r"^bike horn\W?$"), "sound/warp/bike_horn.ogg"]
            self.soundDictionaries[4]["bj"] = [re.compile(r"^bj\W?$"), "sound/warp/bj.ogg"]
            self.soundDictionaries[4]["kill you with my brain"] = [re.compile(r"^kill you with my brain\W?$"), "sound/warp/brain.ogg"]
            self.soundDictionaries[4]["bravery"] = [re.compile(r"^bravery\W?$"), "sound/warp/bravery.ogg"]
            self.soundDictionaries[4]["broke"] = [re.compile(r"^broke\W?$"), "sound/warp/broke.ogg"]
            self.soundDictionaries[4]["space bugs"] = [re.compile(r"^space bugs\W?$"), "sound/warp/bugs.ogg"]
            self.soundDictionaries[4]["bunk"] = [re.compile(r"^bunk\W?$"), "sound/warp/bunk.ogg"]
            self.soundDictionaries[4]["burp"] = [re.compile(r"^burp\W?$"), "sound/warp/burp.ogg"]
            self.soundDictionaries[4]["burpp"] = [re.compile(r"^burpp\W?$"), "sound/warp/burpp.ogg"]
            self.soundDictionaries[4]["cover your butt"] = [re.compile(r"^cover your butt\W?$"), "sound/warp/butt.ogg"]
            self.soundDictionaries[4]["came out"] = [re.compile(r"^came out\W?$"), "sound/warp/cameout.ogg"]
            self.soundDictionaries[4]["anybody care"] = [re.compile(r"^anybody care\W?$"), "sound/warp/care.ogg"]
            self.soundDictionaries[4]["catch"] = [re.compile(r"^catch\W?$"), "sound/warp/catch.ogg"]
            self.soundDictionaries[4]["castrate"] = [re.compile(r"^castrate\W?$"), "sound/warp/castrate.ogg"]
            self.soundDictionaries[4]["cat scream"] = [re.compile(r"^cat scream\W?$"), "sound/warp/cat_scream.ogg"]
            self.soundDictionaries[4]["hello2"] = [re.compile(r"^hello2\W?$"), "sound/warp/coach_hello.ogg"]
            self.soundDictionaries[4]["corny"] = [re.compile(r"^corny\W?$"), "sound/warp/corny.ogg"]
            self.soundDictionaries[4]["cock push ups"] = [re.compile(r"^(?:(cock )?push ups)\W?$"), "sound/warp/cockpushups.ogg"]
            self.soundDictionaries[4]["code"] = [re.compile(r"^code\W?$"), "sound/warp/code.ogg"]
            self.soundDictionaries[4]["cold"] = [re.compile(r"^cold\W?$"), "sound/warp/cold.ogg"]
            self.soundDictionaries[4]["college student"] = [re.compile(r"^college student\W?$"), "sound/warp/college.ogg"]
            self.soundDictionaries[4]["crush your enemies"] = [re.compile(r"^(?:crush( your enemies)?|conana(palooza)?)\W?$"), "sound/warp/conana.ogg"]
            self.soundDictionaries[4]["confident"] = [re.compile(r"^confident\W?$"), "sound/warp/confident.ogg"]
            self.soundDictionaries[4]["cooperation"] = [re.compile(r"^cooperation\W?$"), "sound/warp/cooperation.ogg"]
            self.soundDictionaries[4]["cow dick"] = [re.compile(r"^cow dick\W?$"), "sound/warp/cowdick.ogg"]
            self.soundDictionaries[4]["go crazy"] = [re.compile(r"^go crazy\W?$"), "sound/warp/crazy.ogg"]
            self.soundDictionaries[4]["crowded"] = [re.compile(r"^crowded\W?$"), "sound/warp/crowded.ogg"]
            self.soundDictionaries[4]["dance off"] = [re.compile(r"^dance off\W?$"), "sound/warp/danceoff.ogg"]
            self.soundDictionaries[4]["dead"] = [re.compile(r"^dead\W?$"), "sound/warp/dead.ogg"]
            self.soundDictionaries[4]["dead guy"] = [re.compile(r"^dead guy\W?$"), "sound/warp/deadguy.ogg"]
            self.soundDictionaries[4]["dick message"] = [re.compile(r"^dick message\W?$"), "sound/warp/dickmessage.ogg"]
            self.soundDictionaries[4]["dick slip"] = [re.compile(r"^dick slip\W?$"), "sound/warp/dick_slip.ogg"]
            self.soundDictionaries[4]["dink bag"] = [re.compile(r"^dink bag\W?$"), "sound/warp/dinkbag.ogg"]
            self.soundDictionaries[4]["dirty"] = [re.compile(r"^dirty\W?$"), "sound/warp/dirty.ogg"]
            self.soundDictionaries[4]["do as you're told"] = [re.compile(r"^do as you'?re told\W?$"), "sound/warp/doasyouretold.ogg"]
            self.soundDictionaries[4]["what have we done"] = [re.compile(r"^what have we done\W?$"), "sound/warp/done.ogg"]
            self.soundDictionaries[4]["done for the day"] = [re.compile(r"^(?:done( for the)?( day)?)\W?$"), "sound/warp/done_for_the_day.ogg"]
            self.soundDictionaries[4]["done it"] = [re.compile(r"^done it\W?$"), "sound/warp/doneit.ogg"]
            self.soundDictionaries[4]["do now"] = [re.compile(r"^do now\W?$"), "sound/warp/donow.ogg"]
            self.soundDictionaries[4]["don't like vaginas"] = [re.compile(r"^don'?t like vaginas\W?$"), "sound/warp/dontlikevaginas.ogg"]
            self.soundDictionaries[4]["drawing"] = [re.compile(r"^drawing\W?$"), "sound/warp/drawing.ogg"]
            self.soundDictionaries[4]["eat it"] = [re.compile(r"^eat it\W?$"), "sound/warp/eat_it.ogg"]
            self.soundDictionaries[4]["eat my grenade"] = [re.compile(r"^(?:(eat my )?grenade)\W?$"), "sound/warp/eatmygrenade.ogg"]
            self.soundDictionaries[4]["eat my"] = [re.compile(r"^eat my\W?$"), "sound/warp/eatmytits.ogg"]
            self.soundDictionaries[4]["electricity"] = [re.compile(r"^electricity\W?$"), "sound/warp/electricity.ogg"]
            self.soundDictionaries[4]["enima"] = [re.compile(r"^enima\W?$"), "sound/warp/enima.ogg"]
            self.soundDictionaries[4]["face"] = [re.compile(r"^face\W?$"), "sound/warp/face.ogg"]
            self.soundDictionaries[4]["face2"] = [re.compile(r"^face2\W?$"), "sound/warp/face2.ogg"]
            self.soundDictionaries[4]["fart"] = [re.compile(r"^fart\W?$"), "sound/warp/fart.ogg"]
            self.soundDictionaries[4]["fartt"] = [re.compile(r"^fartt\W?$"), "sound/warp/fartt.ogg"]
            self.soundDictionaries[4]["farttt"] = [re.compile(r"^farttt\W?$"), "sound/warp/farttt.ogg"]
            self.soundDictionaries[4]["ffart"] = [re.compile(r"^ffart\W?$"), "sound/warp/ffart.ogg"]
            self.soundDictionaries[4]["ffartt"] = [re.compile(r"^ffartt\W?$"), "sound/warp/ffartt.ogg"]
            self.soundDictionaries[4]["ffarttt"] = [re.compile(r"^ffarttt\W?$"), "sound/warp/ffarttt.ogg"]
            self.soundDictionaries[4]["fffartt"] = [re.compile(r"^fffartt\W?$"), "sound/warp/fffartt.ogg"]
            self.soundDictionaries[4]["fffarttt"] = [re.compile(r"^fffarttt\W?$"), "sound/warp/fffarttt.ogg"]
            self.soundDictionaries[4]["not fair"] = [re.compile(r"^not fair\W?$"), "sound/warp/fair.ogg"]
            self.soundDictionaries[4]["falcon pawnch"] = [re.compile(r"^falcon pawnch\W?$"), "sound/warp/falcon_pawnch.ogg"]
            self.soundDictionaries[4]["fall"] = [re.compile(r"^fall\W?$"), "sound/warp/fall.ogg"]
            self.soundDictionaries[4]["favor"] = [re.compile(r"^favor\W?$"), "sound/warp/favor.ogg"]
            self.soundDictionaries[4]["feel"] = [re.compile(r"^feel\W?$"), "sound/warp/feel.ogg"]
            self.soundDictionaries[4]["feels"] = [re.compile(r"^feels\W?$"), "sound/warp/feels.ogg"]
            self.soundDictionaries[4]["something wrong"] = [re.compile(r"^something wrong\??\W?$"), "sound/warp/femaleshepherd_somethingwrong.ogg"]
            self.soundDictionaries[4]["suspense"] = [re.compile(r"^suspense\W?$"), "sound/warp/femaleshepherd_suspense.ogg"]
            self.soundDictionaries[4]["fog horn"] = [re.compile(r"^fog horn\W?$"), "sound/warp/fog_horn.ogg"]
            self.soundDictionaries[4]["found them"] = [re.compile(r"^found them\W?$"), "sound/warp/found_them.ogg"]
            self.soundDictionaries[4]["fuku"] = [re.compile(r"^fuku\W?$"), "sound/warp/fuku.ogg"]
            self.soundDictionaries[4]["fuck me"] = [re.compile(r"^fuck me\W?$"), "sound/warp/fuck_me.ogg"]
            self.soundDictionaries[4]["fuck ugly"] = [re.compile(r"^fuck ugly\W?$"), "sound/warp/fuck_ugly.ogg"]
            self.soundDictionaries[4]["awaiting orders"] = [re.compile(r"^awaiting orders\W?$"), "sound/warp/garrus_awaitingorders.ogg"]
            self.soundDictionaries[4]["got your back"] = [re.compile(r"^got your back\W?$"), "sound/warp/garrus_gotyourback.ogg"]
            self.soundDictionaries[4]["keep moving"] = [re.compile(r"^keep moving\W?$"), "sound/warp/garrus_keepmoving.ogg"]
            self.soundDictionaries[4]["nice work"] = [re.compile(r"^nice work\W?$"), "sound/warp/garrus_nicework.ogg"]
            self.soundDictionaries[4]["get away cat"] = [re.compile(r"^(?:(get away )?cat)\W?$"), "sound/warp/getawaycat.ogg"]
            self.soundDictionaries[4]["get off"] = [re.compile(r"^get off\W?$"), "sound/warp/getoff.ogg"]
            self.soundDictionaries[4]["wasting my time"] = [re.compile(r"^wasting my time\W?$"), "sound/warp/glados_wasting.ogg"]
            self.soundDictionaries[4]["just go crazy"] = [re.compile(r"^just go crazy\W?$"), "sound/warp/go_crazy.ogg"]
            self.soundDictionaries[4]["grows"] = [re.compile(r"^grows\W?$"), "sound/warp/grows.ogg"]
            self.soundDictionaries[4]["ha ha"] = [re.compile(r"^ha ha\W?$"), "sound/warp/haha.ogg"]
            self.soundDictionaries[4]["heroics"] = [re.compile(r"^heroics\W?$"), "sound/warp/heroics.ogg"]
            self.soundDictionaries[4]["hop"] = [re.compile(r"^hop\W?$"), "sound/warp/hop.ogg"]
            self.soundDictionaries[4]["horrible"] = [re.compile(r"^horrible\W?$"), "sound/warp/horrible.ogg"]
            self.soundDictionaries[4]["huge vagina"] = [re.compile(r"^huge vagina\W?$"), "sound/warp/hugevagina.ogg"]
            self.soundDictionaries[4]["hunting"] = [re.compile(r"^hunting\W?$"), "sound/warp/hunting.ogg"]
            self.soundDictionaries[4]["i am the law"] = [re.compile(r"^i am the law\W?$"), "sound/warp/iamthelaw.ogg"]
            self.soundDictionaries[4]["implied"] = [re.compile(r"^implied\W?$"), "sound/warp/implied.ogg"]
            self.soundDictionaries[4]["i died"] = [re.compile(r"^i died\W?$"), "sound/warp/i_died.ogg"]
            self.soundDictionaries[4]["i farted"] = [re.compile(r"^i farted\W?$"), "sound/warp/i_farted.ogg"]
            self.soundDictionaries[4]["i don't trust you"] = [re.compile(r"^(?:(i don'?t )?trust you|leaf(green)?)\W?$"), "sound/warp/idonttrustyou.ogg"]
            self.soundDictionaries[4]["i have a plan"] = [re.compile(r"^i have a plan\W?$"), "sound/warp/ihaveaplan.ogg"]
            self.soundDictionaries[4]["i like you"] = [re.compile(r"^i like you\W?$"), "sound/warp/ilikeyou.ogg"]
            self.soundDictionaries[4]["intensify"] = [re.compile(r"^intensify\W?"), "sound/warp/intensify.ogg"]
            self.soundDictionaries[4]["in the ass"] = [re.compile(r"^in ?the ?ass\W?"), "sound/warp/intheass.ogg"]
            self.soundDictionaries[4]["i will eat"] = [re.compile(r"^i will eat( your)?\W?$"), "sound/warp/iwilleatyour.ogg"]
            self.soundDictionaries[4]["jail"] = [re.compile(r"^jail\W?$"), "sound/warp/jail.ogg"]
            self.soundDictionaries[4]["jump pad"] = [re.compile(r"^jump pad\W?$"), "sound/warp/jump_pad.ogg"]
            self.soundDictionaries[4]["just the tip"] = [re.compile(r"^(?:just the tip|tippy(touch)?)\W?$"), "sound/warp/just_the_tip.ogg"]
            self.soundDictionaries[4]["kevin bacon"] = [re.compile(r"^kevin bacon\W?$"), "sound/warp/kevinbacon.ogg"]
            self.soundDictionaries[4]["kill"] = [re.compile(r"^kill\W?$"), "sound/warp/kill.ogg"]
            self.soundDictionaries[4]["kizuna"] = [re.compile(r"^kizuna\W?$"), "sound/warp/kizuna.ogg"]
            self.soundDictionaries[4]["need to kill"] = [re.compile(r"^need to kill\W?$"), "sound/warp/krogan_kill.ogg"]
            self.soundDictionaries[4]["ladybug"] = [re.compile(r"^ladybug\W?$"), "sound/warp/ladybug.ogg"]
            self.soundDictionaries[4]["legend"] = [re.compile(r"^(?:legend|ere(?:bux)?)\W?$"), "sound/warp/legend.ogg"]
            self.soundDictionaries[4]["lego maniac"] = [re.compile(r"^(?:lego maniac|zach|stukey)\W?$"), "sound/warp/lego_maniac.ogg"]
            self.soundDictionaries[4]["human relationships"] = [re.compile(r"^human relationships?\W?$"), "sound/warp/liara_humanrelationships.ogg"]
            self.soundDictionaries[4]["incredible"] = [re.compile(r"^incredible\W?$"), "sound/warp/liara_incredible.ogg"]
            self.soundDictionaries[4]["never happened"] = [re.compile(r"^never happened\W?$"), "sound/warp/liara_neverhappened.ogg"]
            self.soundDictionaries[4]["lick me"] = [re.compile(r"^lick me\W?$"), "sound/warp/lick_me.ogg"]
            self.soundDictionaries[4]["like this thing"] = [re.compile(r"^like this thing\W?$"), "sound/warp/like.ogg"]
            self.soundDictionaries[4]["wasn't listening"] = [re.compile(r"^wasn'?t listening\W?$"), "sound/warp/listening.ogg"]
            self.soundDictionaries[4]["listen up"] = [re.compile(r"^listen( up)?\W?$"), "sound/warp/listenup.ogg"]
            self.soundDictionaries[4]["look fine"] = [re.compile(r"^look fine\W?$"), "sound/warp/lookfine.ogg"]
            self.soundDictionaries[4]["lovely"] = [re.compile(r"^lovely\W?$"), "sound/warp/lovely.ogg"]
            self.soundDictionaries[4]["your luck"] = [re.compile(r"^your luck\W?$"), "sound/warp/luck.ogg"]
            self.soundDictionaries[4]["maggot"] = [re.compile(r"^maggot\W?$"), "sound/warp/maggot.ogg"]
            self.soundDictionaries[4]["like an idiot"] = [re.compile(r"^like an idiot\W?$"), "sound/warp/makes_you_look_like_idiot.ogg"]
            self.soundDictionaries[4]["this beat"] = [re.compile(r"^this beat\W?$"), "sound/warp/marg_tongue.ogg"]
            self.soundDictionaries[4]["killed with math"] = [re.compile(r"^(killed )?(with )?math\W?$"), "sound/warp/math.ogg"]
            self.soundDictionaries[4]["me me me"] = [re.compile(r"^me me(?: me)?\W?$"), "sound/warp/mememe.ogg"]
            self.soundDictionaries[4]["metaphor"] = [re.compile(r"^metaphor\W?$"), "sound/warp/metaphor.ogg"]
            self.soundDictionaries[4]["misdirection"] = [re.compile(r"^misdirection\W?$"), "sound/warp/misdirection.ogg"]
            self.soundDictionaries[4]["nobody move"] = [re.compile(r"^nobody move\W?$"), "sound/warp/move.ogg"]
            self.soundDictionaries[4]["my friends"] = [re.compile(r"^my friends\W?$"), "sound/warp/my_friends.ogg"]
            self.soundDictionaries[4]["mwahaha"] = [re.compile(r"^mwahaha\W?$"), "sound/warp/mwahaha.ogg"]
            self.soundDictionaries[4]["my gun's bigger"] = [re.compile(r"^my gun'?s bigger\W?$"), "sound/warp/mygunsbigger.ogg"]
            self.soundDictionaries[4]["nades"] = [re.compile(r"^nades\W?$"), "sound/warp/nades.ogg"]
            self.soundDictionaries[4]["never look back"] = [re.compile(r"^(?:never look back|muddy(?:creek)?)\W?$"), "sound/warp/neverlookback.ogg"]
            self.soundDictionaries[4]["nonono"] = [re.compile(r"^no( )?no( )?no\W?$"), "sound/warp/nonono.ogg"]
            self.soundDictionaries[4]["nutsack"] = [re.compile(r"^nutsack\W?$"), "sound/warp/nutsack.ogg"]
            self.soundDictionaries[4]["my god"] = [re.compile(r"^my god\W?$"), "sound/warp/oh_my_god.ogg"]
            self.soundDictionaries[4]["on me"] = [re.compile(r"^on me\W?$"), "sound/warp/onme.ogg"]
            self.soundDictionaries[4]["on my mom"] = [re.compile(r"^(?:on my mom)\W?|\( ͡° ͜ʖ ͡°\)$"), "sound/warp/onmymom.ogg"]
            self.soundDictionaries[4]["ow what the"] = [re.compile(r"^(ow )?what the\W?"), "sound/warp/owwhatthe.ogg"]
            self.soundDictionaries[4]["pain in the ass"] = [re.compile(r"^pain in the ass\W?$"), "sound/warp/pain.ogg"]
            self.soundDictionaries[4]["pan out"] = [re.compile(r"^pan out\W?$"), "sound/warp/panout.ogg"]
            self.soundDictionaries[4]["pee bad"] = [re.compile(r"^pee bad\W?$"), "sound/warp/pee_bad.ogg"]
            self.soundDictionaries[4]["pee myself"] = [re.compile(r"^pee myself\W?$"), "sound/warp/pee_myself.ogg"]
            self.soundDictionaries[4]["petty"] = [re.compile(r"^petty\W?$"), "sound/warp/petty.ogg"]
            self.soundDictionaries[4]["pie intro"] = [re.compile(r"^pie intro\W?$"), "sound/warp/pie_intro4.ogg"]
            self.soundDictionaries[4]["pile of shit"] = [re.compile(r"^pile( of shit)?\W?$"), "sound/warp/pile.ogg"]
            self.soundDictionaries[4]["pizza time"] = [re.compile(r"^pizza time\W?$"), "sound/warp/pizza_time.ogg"]
            self.soundDictionaries[4]["plasma"] = [re.compile(r"^(?:(respect )?(the )?plasma)\W?"), "sound/warp/plasma.ogg"]
            self.soundDictionaries[4]["plus back"] = [re.compile(r"^plus back\W?$"), "sound/warp/plus_back.ogg"]
            self.soundDictionaries[4]["poop myself"] = [re.compile(r"^poop myself\W?$"), "sound/warp/poop_myself.ogg"]
            self.soundDictionaries[4]["good point"] = [re.compile(r"^good point\W?$"), "sound/warp/point.ogg"]
            self.soundDictionaries[4]["quarter"] = [re.compile(r"^quarter\W?$"), "sound/warp/quarter.ogg"]
            self.soundDictionaries[4]["question"] = [re.compile(r"^question\W?$"), "sound/warp/question.ogg"]
            self.soundDictionaries[4]["rage"] = [re.compile(r"^rage\W?$"), "sound/warp/rage.ogg"]
            self.soundDictionaries[4]["real me"] = [re.compile(r"^real me\W?$"), "sound/warp/realme.ogg"]
            self.soundDictionaries[4]["roll with"] = [re.compile(r"^roll with\W?$"), "sound/warp/roll_with.ogg"]
            self.soundDictionaries[4]["no longer require"] = [re.compile(r"^no longer require\W?$"), "sound/warp/require.ogg"]
            self.soundDictionaries[4]["ready for this"] = [re.compile(r"^ready for this\W?$"), "sound/warp/rochelle_ready.ogg"]
            self.soundDictionaries[4]["rock this"] = [re.compile(r"^rock this\W?$"), "sound/warp/rockthis.ogg"]
            self.soundDictionaries[4]["santa"] = [re.compile(r"^santa\W?$"), "sound/warp/santa.ogg"]
            self.soundDictionaries[4]["say my name"] = [re.compile(r"^say my name\W?$"), "sound/warp/saymyname.ogg"]
            self.soundDictionaries[4]["you can scream"] = [re.compile(r"^you can scream\W?$"), "sound/warp/scream.ogg"]
            self.soundDictionaries[4]["shart"] = [re.compile(r"^shart\W?$"), "sound/warp/shart.ogg"]
            self.soundDictionaries[4]["shartt"] = [re.compile(r"^shartt\W?$"), "sound/warp/shartt.ogg"]
            self.soundDictionaries[4]["skullcrusher"] = [re.compile(r"^skull|skullcrusher\W?$"), "sound/warp/skull.ogg"]
            self.soundDictionaries[4]["smiley face"] = [re.compile(r"^(?:smiley face\W?)|:\)|:-\)|:\]|\(:$"), "sound/warp/smileyface.ogg"]
            self.soundDictionaries[4]["oh snap"] = [re.compile(r"^(oh )?snap\W?$"), "sound/warp/snap.ogg"]
            self.soundDictionaries[4]["sneezed"] = [re.compile(r"^sneezed\W?$"), "sound/warp/sneezed.ogg"]
            self.soundDictionaries[4]["solitude"] = [re.compile(r"^solitude\W?$"), "sound/warp/solitude.ogg"]
            self.soundDictionaries[4]["sorry"] = [re.compile(r"^sorry\W?$"), "sound/warp/sorry.ogg"]
            self.soundDictionaries[4]["spagetti"] = [re.compile(r"^spagetti\W?$"), "sound/warp/spagetti.ogg"]
            self.soundDictionaries[4]["human speech"] = [re.compile(r"^(human )?speech\W?$"), "sound/warp/speech.ogg"]
            self.soundDictionaries[4]["sprechen sie dick"] = [re.compile(r"^sprechen sie dick\W?$"), "sound/warp/sprechensiedick.ogg"]
            self.soundDictionaries[4]["start over"] = [re.compile(r"^start over\W?$"), "sound/warp/startover.ogg"]
            self.soundDictionaries[4]["stfu cunt"] = [re.compile(r"^stfu cunt\W?$"), "sound/warp/stfu.ogg"]
            self.soundDictionaries[4]["study harder"] = [re.compile(r"^study harder\W?$"), "sound/warp/study_harder.ogg"]
            self.soundDictionaries[4]["stunned our ride"] = [re.compile(r"^stunned our ride\W?$"), "sound/warp/stunned.ogg"]
            self.soundDictionaries[4]["sure"] = [re.compile(r"^sure\W?$"), "sound/warp/sure.ogg"]
            self.soundDictionaries[4]["swallow"] = [re.compile(r"^swallow\W?$"), "sound/warp/swallow.ogg"]
            self.soundDictionaries[4]["take a break"] = [re.compile(r"^take a break|wally\W?$"), "sound/warp/takeabreaknow.ogg"]
            self.soundDictionaries[4]["take down"] = [re.compile(r"^take down\W?$"), "sound/warp/takedown.ogg"]
            self.soundDictionaries[4]["the creeps"] = [re.compile(r"^the creeps\W?$"), "sound/warp/tali_creeps.ogg"]
            self.soundDictionaries[4]["used to living"] = [re.compile(r"^used to living\W?$"), "sound/warp/tali_usedtoliving.ogg"]
            self.soundDictionaries[4]["talk to me"] = [re.compile(r"^talk to me\W?$"), "sound/warp/talk.ogg"]
            self.soundDictionaries[4]["asshole"] = [re.compile(r"^asshole\W?$"), "sound/warp/tastless_asshole.ogg"]
            self.soundDictionaries[4]["tears"] = [re.compile(r"^tears\W?$"), "sound/warp/tears.ogg"]
            self.soundDictionaries[4]["that's right"] = [re.compile(r"^that'?s right\W?$"), "sound/warp/thatsright.ogg"]
            self.soundDictionaries[4]["the talk"] = [re.compile(r"^the talk\W?$"), "sound/warp/the_talk.ogg"]
            self.soundDictionaries[4]["think"] = [re.compile(r"^think\W?$"), "sound/warp/think.ogg"]
            self.soundDictionaries[4]["tricked"] = [re.compile(r"^tricked\W?$"), "sound/warp/tricked.ogg"]
            self.soundDictionaries[4]["trusted"] = [re.compile(r"^trusted\W?$"), "sound/warp/trusted.ogg"]
            self.soundDictionaries[4]["trust me"] = [re.compile(r"^trust me\W?$"), "sound/warp/trustme.ogg"]
            self.soundDictionaries[4]["target"] = [re.compile(r"^target\W?$"), "sound/warp/turret_target.ogg"]
            self.soundDictionaries[4]["ugly stick"] = [re.compile(r"^ugly stick\W?$"), "sound/warp/ugly.ogg"]
            self.soundDictionaries[4]["unfair"] = [re.compile(r"^unfair\W?$"), "sound/warp/unfair.ogg"]
            self.soundDictionaries[4]["unicorn"] = [re.compile(r"^unicorn\W?$"), "sound/warp/unicorn.ogg"]
            self.soundDictionaries[4]["v3"] = [re.compile(r"^(?:v3|vestek)\W?$"), "sound/warp/v3.ogg"]
            self.soundDictionaries[4]["valid"] = [re.compile(r"^valid\W?$"), "sound/warp/valid.ogg"]
            self.soundDictionaries[4]["very nice"] = [re.compile(r"^very nice\W?$"), "sound/warp/very_nice.ogg"]
            self.soundDictionaries[4]["vewy angwy"] = [re.compile(r"^vewy angwy\W?$"), "sound/warp/vewy_angwy.ogg"]
            self.soundDictionaries[4]["volunteer"] = [re.compile(r"^volunteer\W?$"), "sound/warp/volunteer.ogg"]
            self.soundDictionaries[4]["waiting"] = [re.compile(r"^waiting\W?$"), "sound/warp/waiting.ogg"]
            self.soundDictionaries[4]["walk"] = [re.compile(r"^walk\W?$"), "sound/warp/walk.ogg"]
            self.soundDictionaries[4]["what i want"] = [re.compile(r"^what i want\W?$"), "sound/warp/want.ogg"]
            self.soundDictionaries[4]["at war"] = [re.compile(r"^at war\W?$"), "sound/warp/war.ogg"]
            self.soundDictionaries[4]["warp server intro"] = [re.compile(r"^(warp server intro)|(quality)\W?$"), "sound/warp/warpserverintro.ogg"]
            self.soundDictionaries[4]["wednesday"] = [re.compile(r"^wednesday\W?$"), "sound/warp/wednesday.ogg"]
            self.soundDictionaries[4]["wee lamb"] = [re.compile(r"^wee lamb\W?$"), "sound/warp/weelamb.ogg"]
            self.soundDictionaries[4]["well"] = [re.compile(r"^well\W?$"), "sound/warp/well.ogg"]
            self.soundDictionaries[4]["we're grownups"] = [re.compile(r"^we'?re grownups\W?$"), "sound/warp/weregrownups.ogg"]
            self.soundDictionaries[4]["what happened"] = [re.compile(r"^what happened\W?$"), "sound/warp/whathappened.ogg"]
            self.soundDictionaries[4]["what is this"] = [re.compile(r"^what is this\W?$"), "sound/warp/whatisthis.ogg"]
            self.soundDictionaries[4]["what now"] = [re.compile(r"^what now\W?$"), "sound/warp/whatnow.ogg"]
            self.soundDictionaries[4]["what the"] = [re.compile(r"^what the\W?$"), "sound/warp/whatthe.ogg"]
            self.soundDictionaries[4]["where the fuck"] = [re.compile(r"^where the( fuck)?\W?$"), "sound/warp/where_the_fuck.ogg"]
            self.soundDictionaries[4]["winnie the pew"] = [re.compile(r"^winnie( the pew)?\W?$"), "sound/warp/winnie_the_pew.ogg"]
            self.soundDictionaries[4]["with my fist"] = [re.compile(r"^(?:(with )?my fist|strat0?)\W?$"), "sound/warp/withmyfist.ogg"]
            self.soundDictionaries[4]["busy"] = [re.compile(r"^busy\W?$"), "sound/warp/wrex_busy.ogg"]
            self.soundDictionaries[4]["sometimes crazy"] = [re.compile(r"^sometimes crazy\W?$"), "sound/warp/wrex_crazy.ogg"]
            self.soundDictionaries[4]["i like"] = [re.compile(r"^i like\W?$"), "sound/warp/wrex_like.ogg"]
            self.soundDictionaries[4]["orders"] = [re.compile(r"^orders\W?$"), "sound/warp/wrex_orders.ogg"]
            self.soundDictionaries[4]["right behind you"] = [re.compile(r"^right behind you\W?$"), "sound/warp/wrex_rightbehindyou.ogg"]
            self.soundDictionaries[4]["what can i do"] = [re.compile(r"^what can i do\W?$"), "sound/warp/wrex_whatcanido.ogg"]
            self.soundDictionaries[4]["your mom"] = [re.compile(r"^(?:your mom|pug(ster)?)\W?$"), "sound/warp/yourmom.ogg"]
            self.soundDictionaries[4]["zooma"] = [re.compile(r"^(?:zooma?|xuma)\W?$"), "sound/warp/zooma.ogg"]

        if self.Enabled_SoundPacks[5]:
            self.soundDictionaries[5]["2ez"] = [re.compile(r"(?:2ez|too easy)\W?"), "sound/westcoastcrew/2ez.ogg"]
            self.soundDictionaries[5]["ability"] = [re.compile(r"ability\W?"), "sound/westcoastcrew/ability.ogg"]
            self.soundDictionaries[5]["ahsi"] = [re.compile(r"^ahsi\W?$"), "sound/westcoastcrew/ahsi.ogg"]
            self.soundDictionaries[5]["all dead"] = [re.compile(r"^all( )?dead\W?$"), "sound/westcoastcrew/alldead.ogg"]
            self.soundDictionaries[5]["kinrazed"] = [re.compile(r"kinrazed\W?"), "sound/westcoastcrew/alright.ogg"]
            self.soundDictionaries[5]["another one bites the dustt"] = [re.compile(r"(another one )?bites the dustt\W?$"), "sound/westcoastcrew/anotherbitesdust.ogg"]
            self.soundDictionaries[5]["another one bites the dust"] = [re.compile(r"(another one )?bites the dust\W?$"), "sound/westcoastcrew/anotheronebitesthedust.ogg"]
            self.soundDictionaries[5]["and another one gone"] = [re.compile(r"and another one gone\W?"), "sound/westcoastcrew/anotheronegone.ogg"]
            self.soundDictionaries[5]["atustamena"] = [re.compile(r"atustamena\W?"), "sound/westcoastcrew/atustamena.ogg"]
            self.soundDictionaries[5]["ay caramba"] = [re.compile(r"^ay caramba\W?"), "sound/westcoastcrew/aycaramba.ogg"]
            self.soundDictionaries[5]["baby back"] = [re.compile(r"^baby( )?back\W?$"), "sound/westcoastcrew/babyback.ogg"]
            self.soundDictionaries[5]["badabababa"] = [re.compile(r"^badababa(ba)?\W?$"), "sound/westcoastcrew/badabababa.ogg"]
            self.soundDictionaries[5]["baiting"] = [re.compile(r"baitin\W?"), "sound/westcoastcrew/baiting.ogg"]
            self.soundDictionaries[5]["ballin"] = [re.compile(r"^ballin\W?$"), "sound/westcoastcrew/ballin.ogg"]
            self.soundDictionaries[5]["bender"] = [re.compile(r"^bender\W?$"), "sound/westcoastcrew/bender.ogg"]
            self.soundDictionaries[5]["biff"] = [re.compile(r"biff\W?"), "sound/westcoastcrew/biff.ogg"]
            self.soundDictionaries[5]["outro"] = [re.compile(r"outro\W?"), "sound/westcoastcrew/biggerlove.ogg"]
            self.soundDictionaries[5]["bigpippin"] = [re.compile(r"^bigpippin\W?$"), "sound/westcoastcrew/bigpippin.ogg"]
            self.soundDictionaries[5]["big whoop"] = [re.compile(r"(?:big wh?oop)\W?$"), "sound/westcoastcrew/bigwhoop.ogg"]
            self.soundDictionaries[5]["bite my shiny metal ass"] = [re.compile(r"^bite my shiny metal ass\W?"), "sound/westcoastcrew/bitemyshinymetalass.ogg"]
            self.soundDictionaries[5]["bofumballs"] = [re.compile(r"^bofumb(alls)?\W?$"), "sound/westcoastcrew/bofumballs.ogg"]
            self.soundDictionaries[5]["boomshakalaka"] = [re.compile(r"boomshakalaka\W?"), "sound/westcoastcrew/boomshakalaka.ogg"]
            self.soundDictionaries[5]["borracho"] = [re.compile(r"^borracho\W?$"), "sound/westcoastcrew/borracho.ogg"]
            self.soundDictionaries[5]["bumblebee tuna"] = [re.compile(r"(?:your balls are showing|bumblebee tuna)\W?"), "sound/westcoastcrew/bumblebeetuna.ogg"]
            self.soundDictionaries[5]["bum bum"] = [re.compile(r"^bum( )?bum\W?$"), "sound/westcoastcrew/bumbum.ogg"]
            self.soundDictionaries[5]["bweenabwaana"] = [re.compile(r"^bweena(bwaana)?\W?$"), "sound/westcoastcrew/bweenabwaana.ogg"]
            self.soundDictionaries[5]["c3"] = [re.compile(r"^c3\W?$"), "sound/westcoastcrew/c3.ogg"]
            self.soundDictionaries[5]["campingtroll"] = [re.compile(r"(?:campingtroll|baby got back)\W?"), "sound/westcoastcrew/campingtroll.ogg"]
            self.soundDictionaries[5]["cann"] = [re.compile(r"^cann\W?$"), "sound/westcoastcrew/cann.ogg"]
            # repeat of FunnySounds
            #self.soundDictionaries[5]["can't touch this"] = [re.compile(r"^can'?t touch this\W?$"), "sound/westcoastcrew/CantTouchThis.ogg"]
            self.soundDictionaries[5]["captains draft"] = [re.compile(r"^captains( )?draft\W?$"), "sound/westcoastcrew/captainsdraft.ogg"]
            self.soundDictionaries[5]["cheers"] = [re.compile(r"^cheers\W?$"), "sound/westcoastcrew/cheers.ogg"]
            self.soundDictionaries[5]["cheers2"] = [re.compile(r"^cheers2\W?$"), "sound/westcoastcrew/cheers2.ogg"]
            self.soundDictionaries[5]["chocosaurus"] = [re.compile(r"^chocosaurus\W?$"), "sound/westcoastcrew/chocosaurus.ogg"]
            self.soundDictionaries[5]["clear"] = [re.compile(r"^clear\W?$"), "sound/westcoastcrew/clear.ogg"]
            self.soundDictionaries[5]["clever girl"] = [re.compile(r"^clever girl\W?"), "sound/westcoastcrew/clevergirl.ogg"]
            self.soundDictionaries[5]["clr"] = [re.compile(r"^clr\W?$"), "sound/westcoastcrew/clr.ogg"]
            self.soundDictionaries[5]["clr2"] = [re.compile(r"^clr2\W?"), "sound/westcoastcrew/clr2.ogg"]
            self.soundDictionaries[5]["counting on you"] = [re.compile(r"^counting on you\W?"), "sound/westcoastcrew/countingonyou.ogg"]
            self.soundDictionaries[5]["g1bbles"] = [re.compile(r"^g1bbles\W?"), "sound/westcoastcrew/crymeariver.ogg"]
            self.soundDictionaries[5]["cry me a river"] = [re.compile(r"^cry me a river\W?$"), "sound/westcoastcrew/crymeariver1.ogg"]
            self.soundDictionaries[5]["cry me a riverr"] = [re.compile(r"^cry me a riverr\W?$"), "sound/westcoastcrew/crymeariver2.ogg"]
            self.soundDictionaries[5]["cthree"] = [re.compile(r"^cthree\W?$"), "sound/westcoastcrew/cuttingedge.ogg"]
            self.soundDictionaries[5]["damn im good"] = [re.compile(r"^damn i'?m good\W?"), "sound/westcoastcrew/damnimgood.ogg"]
            self.soundDictionaries[5]["dead last"] = [re.compile(r"(?:yeah,? how'?d he finish again|dead ?last)\W?"), "sound/westcoastcrew/deadlast.ogg"]
            self.soundDictionaries[5]["did i do that"] = [re.compile(r"^did i do that\W?"), "sound/westcoastcrew/dididothat.ogg"]
            self.soundDictionaries[5]["DDDid i do that"] = [re.compile(r"^DDDid i do that\W?"), "sound/westcoastcrew/dididothat2.ogg"]
            # repeat of Prestige Sounds
            # self.soundDictionaries[5]["die"] = [re.compile(r"^die$"), "sound/westcoastcrew/die.ogg"]
            self.soundDictionaries[5]["die already"] = [re.compile(r"^die already\W?$"), "sound/westcoastcrew/diealready.ogg"]
            self.soundDictionaries[5]["die mothafuckas"] = [re.compile(r"^die mothafuckas\W?"), "sound/westcoastcrew/diemothafuckas.ogg"]
            self.soundDictionaries[5]["die motherfucker"] = [re.compile(r"^die motherfucker\W?"), "sound/westcoastcrew/diemotherfucker.ogg"]
            self.soundDictionaries[5]["it's a disastah"] = [re.compile(r"(?:(it'?s a )?disast(ah)?)\W?"), "sound/westcoastcrew/disastah.ogg"]
            self.soundDictionaries[5]["dominating"] = [re.compile(r"dominating\W?"), "sound/westcoastcrew/dominating.ogg"]
            self.soundDictionaries[5]["your'e doomed"] = [re.compile(r"(?:your'?e doome?'?d)"), "sound/westcoastcrew/doomed.ogg"]
            self.soundDictionaries[5]["dr1nya"] = [re.compile(r"^dr1nya\W?$"), "sound/westcoastcrew/dr1nya.ogg"]
            self.soundDictionaries[5]["drunk"] = [re.compile(r"(?:^drunk|always smokin' blunts|gettin' drunk)\W?"), "sound/westcoastcrew/drunk.ogg"]
            self.soundDictionaries[5]["dundun"] = [re.compile(r"^(?:dun ?dun)\W?$"), "sound/westcoastcrew/dundun.ogg"]
            self.soundDictionaries[5]["dundundun"] = [re.compile(r"^(?:dun dun dun|dundundun)\W?$"), "sound/westcoastcrew/dundundun.ogg"]
            self.soundDictionaries[5]["dundundundun"] = [re.compile(r"^(?:dun dun dun dun|dundundundun)\W?$"), "sound/westcoastcrew/dundundundun.ogg"]
            self.soundDictionaries[5]["easy as 123"] = [re.compile(r"(?:easy as|ABC)\W?"), "sound/westcoastcrew/easyas.ogg"]
            self.soundDictionaries[5]["easy come easy go"] = [re.compile(r"easy come easy go\W?"), "sound/westcoastcrew/easycomeeasygo.ogg"]
            self.soundDictionaries[5]["ehtogg"] = [re.compile(r"^ehtogg\W?$"), "sound/westcoastcrew/ehtogg.ogg"]
            self.soundDictionaries[5]["elo"] = [re.compile(r"^elo\W?"), "sound/westcoastcrew/elo.ogg"]
            self.soundDictionaries[5]["enemy pick"] = [re.compile(r"^enemy( )?pick\W?$"), "sound/westcoastcrew/enemypick.ogg"]
            self.soundDictionaries[5]["ez"] = [re.compile(r"(?:^ez|^easy$|so easy|that was easy|that was ez)"), "sound/westcoastcrew/ez.ogg"]
            self.soundDictionaries[5]["f33"] = [re.compile(r"f33\W?"), "sound/westcoastcrew/f3.ogg"]
            self.soundDictionaries[5]["facial"] = [re.compile(r"facial\W?"), "sound/westcoastcrew/facial.ogg"]
            self.soundDictionaries[5]["feroz"] = [re.compile(r"feroz\W?"), "sound/westcoastcrew/feroz.ogg"]
            self.soundDictionaries[5]["filthy zealot"] = [re.compile(r"(?:keep the change|filthy zealot)\W?"), "sound/westcoastcrew/filthyzealot.ogg"]
            self.soundDictionaries[5]["flush"] = [re.compile(r"flush\W?"), "sound/westcoastcrew/flush.ogg"]
            self.soundDictionaries[5]["fox"] = [re.compile(r"^fox\W?$"), "sound/westcoastcrew/fox.ogg"]
            self.soundDictionaries[5]["fuckin bitch"] = [re.compile(r"^fuckin bitch"), "sound/westcoastcrew/fuckinbitch.ogg"]
            # repeat of FunnySounds
            # self.soundDictionaries[5]["Gay"] = [re.compile(r"^Gay\W?$"), "sound/westcoastcrew/Gay.ogg"]
            self.soundDictionaries[5]["get outta here"] = [re.compile(r"^get outta here\W?"), "sound/westcoastcrew/getouttahere.ogg"]
            self.soundDictionaries[5]["gibbles"] = [re.compile(r"^gibbles\W?$"), "sound/westcoastcrew/gibbles.ogg"]
            self.soundDictionaries[5]["giggs"] = [re.compile(r"giggs\W?"), "sound/westcoastcrew/giggs.ogg"]
            self.soundDictionaries[5]["gimme a break"] = [re.compile(r"gimme a break\W?"), "sound/westcoastcrew/gimmeabreak.ogg"]
            self.soundDictionaries[5]["give up and die"] = [re.compile(r"^give up and die\W?"), "sound/westcoastcrew/giveupanddie.ogg"]
            self.soundDictionaries[5]["godlike"] = [re.compile(r"godlike\W?"), "sound/westcoastcrew/godlike.ogg"]
            self.soundDictionaries[5]["gojira"] = [re.compile(r"gojira\W?"), "sound/westcoastcrew/gojira.ogg"]
            self.soundDictionaries[5]["great shot"] = [re.compile(r"great shot\W?"), "sound/westcoastcrew/greatshot.ogg"]
            self.soundDictionaries[5]["gs"] = [re.compile(r"^gs\W?$"), "sound/westcoastcrew/gs.ogg"]
            self.soundDictionaries[5]["h2o"] = [re.compile(r"^h2o\W?$"), "sound/westcoastcrew/h2o.ogg"]
            # repeat of Warp Sounds for Quake Live
            # self.soundDictionaries[5]["haha"] = [re.compile(r"^haha\W?$"), "sound/westcoastcrew/haha.ogg"]
            self.soundDictionaries[5]["hahaha2"] = [re.compile(r"hahaha2\W?$"), "sound/westcoastcrew/hahaha.ogg"]
            self.soundDictionaries[5]["hahahaha"] = [re.compile(r"^hahahaha\W?$"), "sound/westcoastcrew/hahahaha.ogg"]
            self.soundDictionaries[5]["happy hour"] = [re.compile(r"(:?happy hour|it?'s happy hour)\W?"), "sound/westcoastcrew/happyhour.ogg"]
            self.soundDictionaries[5]["he's heating up"] = [re.compile(r"he'?s heating up\W?"), "sound/westcoastcrew/heatingup.ogg"]
            self.soundDictionaries[5]["hehe"] = [re.compile(r"^hehe\W?$"), "sound/westcoastcrew/hehe.ogg"]
            self.soundDictionaries[5]["hehehe"] = [re.compile(r"^hehehe\W?"), "sound/westcoastcrew/hehehe.ogg"]
            self.soundDictionaries[5]["hehe yeah"] = [re.compile(r"hehe yeah\W?"), "sound/westcoastcrew/heheyeah.ogg"]
            self.soundDictionaries[5]["hot steppah"] = [re.compile(r"^hot( )?steppah\W?$"), "sound/westcoastcrew/hotsteppah.ogg"]
            self.soundDictionaries[5]["i'm lovin it"] = [re.compile(r"^i'?mlovin( )?it\W?$"), "sound/westcoastcrew/imlovinit.ogg"]
            self.soundDictionaries[5]["im on fire"] = [re.compile(r"i'?m on fire\W?"), "sound/westcoastcrew/imonfire.ogg"]
            self.soundDictionaries[5]["im stephan"] = [re.compile(r"^i'?m stephan\W?"), "sound/westcoastcrew/imstephan.ogg"]
            self.soundDictionaries[5]["inspector norse"] = [re.compile(r"inspector\W?"), "sound/westcoastcrew/inspectornorse.ogg"]
            self.soundDictionaries[5]["it's in the bag"] = [re.compile(r"it'?s in the bag\W?"), "sound/westcoastcrew/inthebag1.ogg"]
            self.soundDictionaries[5]["in the bag"] = [re.compile(r"in the bag\W?"), "sound/westcoastcrew/inthebag2.ogg"]
            self.soundDictionaries[5]["in the bagg"] = [re.compile(r"in the bagg\W?"), "sound/westcoastcrew/inthebag3.ogg"]
            self.soundDictionaries[5]["in the baggg"] = [re.compile(r"in the baggg\W?"), "sound/westcoastcrew/inthebag4.ogg"]
            self.soundDictionaries[5]["in the face"] = [re.compile(r"in the face\W?"), "sound/westcoastcrew/intheface.ogg"]
            self.soundDictionaries[5]["in the zone"] = [re.compile(r"^(?:(i'?m )?in the zone)\W?$"), "sound/westcoastcrew/inthezone.ogg"]
            self.soundDictionaries[5]["doom2"] = [re.compile(r"(?:doom2$|tell me what you came here for)\W?"), "sound/westcoastcrew/intoyou.ogg"]
            self.soundDictionaries[5]["introtoo"] = [re.compile(r"^introtoo\W?$"), "sound/westcoastcrew/intro2.ogg"]
            self.soundDictionaries[5]["isabadmutha"] = [re.compile(r"^isabadmutha\W?$"), "sound/westcoastcrew/isabadmutha.ogg"]
            self.soundDictionaries[5]["jdub"] = [re.compile(r"^jdub\W?$"), "sound/westcoastcrew/jdub.ogg"]
            self.soundDictionaries[5]["jsss"] = [re.compile(r"^jsss\W?$"), "sound/westcoastcrew/jsss.ogg"]
            self.soundDictionaries[5]["killswitch"] = [re.compile(r"killswitch\W?"), "sound/westcoastcrew/killswitch.ogg"]
            self.soundDictionaries[5]["kinraze"] = [re.compile(r"^kinraze\W?$"), "sound/westcoastcrew/kinraze.ogg"]
            self.soundDictionaries[5]["lakad"] = [re.compile(r"^lakad\W?$"), "sound/westcoastcrew/lakad.ogg"]
            self.soundDictionaries[5]["lg"] = [re.compile(r"lg\W?"), "sound/westcoastcrew/lg.ogg"]
            self.soundDictionaries[5]["lol loser"] = [re.compile(r"(?:(lol )?loser)\W?"), "sound/westcoastcrew/lolloser.ogg"]
            self.soundDictionaries[5]["look what you did"] = [re.compile(r"^look what you did\W?"), "sound/westcoastcrew/lookwhatyoudid.ogg"]
            self.soundDictionaries[5]["look what you've done"] = [re.compile(r"look what you'?ve done\W?"), "sound/westcoastcrew/lookwhatyouvedone.ogg"]
            self.soundDictionaries[5]["los"] = [re.compile(r"^los$"), "sound/westcoastcrew/los.ogg"]
            self.soundDictionaries[5]["lovin' it"] = [re.compile(r"lovin'? it\W?"), "sound/westcoastcrew/lovinit.ogg"]
            self.soundDictionaries[5]["makaveli"] = [re.compile(r"(?:makaveli)\W?$"), "sound/westcoastcrew/makaveli.ogg"]
            self.soundDictionaries[5]["martin"] = [re.compile(r"martin\W?"), "sound/westcoastcrew/martin.ogg"]
            self.soundDictionaries[5]["pizza pizza"] = [re.compile(r"(?:pizza pizza|meetzah meetzah|heetzah peetzah)\W?"), "sound/westcoastcrew/meetzah.ogg"]
            self.soundDictionaries[5]["mirai"] = [re.compile(r"mirai\W?"), "sound/westcoastcrew/mirai.ogg"]
            self.soundDictionaries[5]["did you miss me"] = [re.compile(r"did you miss me\W?"), "sound/westcoastcrew/missme.ogg"]
            self.soundDictionaries[5]["mobil"] = [re.compile(r"mobil\W?"), "sound/westcoastcrew/mobil.ogg"]
            self.soundDictionaries[5]["i'm a motherfuckin monster"] = [re.compile(r"i'?m a motherfuckin monst(er)?\W?"), "sound/westcoastcrew/monster.ogg"]
            self.soundDictionaries[5]["monster kill"] = [re.compile(r"monster kill\W?"), "sound/westcoastcrew/monsterkill.ogg"]
            self.soundDictionaries[5]["muthafucka"] = [re.compile(r"^muthafucka\W?$"), "sound/westcoastcrew/muthafucka.ogg"]
            self.soundDictionaries[5]["nanana"] = [re.compile(r"^nanana\W?$"), "sound/westcoastcrew/nanana.ogg"]
            self.soundDictionaries[5]["next level"] = [re.compile(r"^next( )?level\W?$"), "sound/westcoastcrew/nextlevel.ogg"]
            self.soundDictionaries[5]["no no no no no"] = [re.compile(r"^no no no no no\W?"), "sound/westcoastcrew/nonononono.ogg"]
            self.soundDictionaries[5]["nonsense"] = [re.compile(r"^nonsense\W?"), "sound/westcoastcrew/nonsense.ogg"]
            # repeat of FunnySounds
            # self.soundDictionaries[5]["nooo"] = [re.compile(r"^nooo\W?$"), "sound/westcoastcrew/Nooo.ogg"]
            self.soundDictionaries[5]["not tonight"] = [re.compile(r"^not( )?tonight\W?$"), "sound/westcoastcrew/nottonight.ogg"]
            self.soundDictionaries[5]["no way"] = [re.compile(r"^no( )?way\W?$"), "sound/westcoastcrew/noway.ogg"]
            self.soundDictionaries[5]["oblivion"] = [re.compile(r"oblivion\W?"), "sound/westcoastcrew/obliv.ogg"]
            self.soundDictionaries[5]["obliv"] = [re.compile(r"^(?:obliv(ious)?)\W?$"), "sound/westcoastcrew/obliv2.ogg"]
            self.soundDictionaries[5]["oh boy"] = [re.compile(r"^oh boy\W?$"), "sound/westcoastcrew/ohboy.ogg"]
            # repeat of FunnySounds
            # self.soundDictionaries[5]["oh no"] = [re.compile(r"^oh no\W?$"), "sound/westcoastcrew/OhNo.ogg"]
            self.soundDictionaries[5]["he's on fire"] = [re.compile(r"he'?s on fire\W?"), "sound/westcoastcrew/onfire.ogg"]
            self.soundDictionaries[5]["ooom"] = [re.compile(r"ooom\W?"), "sound/westcoastcrew/oomwhatyousay.ogg"]
            self.soundDictionaries[5]["opinion"] = [re.compile(r"(?:opinion|well, you know, that's)\W?"), "sound/westcoastcrew/opinion.ogg"]
            self.soundDictionaries[5]["oshikia"] = [re.compile(r"^oshikia\W?$"), "sound/westcoastcrew/oshikia.ogg"]
            self.soundDictionaries[5]["oy"] = [re.compile(r"^oy\W?$"), "sound/westcoastcrew/oy.ogg"]
            self.soundDictionaries[5]["papabalyo"] = [re.compile(r"papabalyo\W?"), "sound/westcoastcrew/papabaylo.ogg"]
            self.soundDictionaries[5]["gotta pay the troll"] = [re.compile(r"gotta pay the troll\W?"), "sound/westcoastcrew/paytrolltoll.ogg"]
            self.soundDictionaries[5]["pick music"] = [re.compile(r"^pick( )?music\W?$"), "sound/westcoastcrew/pickmusic.ogg"]
            self.soundDictionaries[5]["littlemeezers"] = [re.compile(r"littlemeezers\W?"), "sound/westcoastcrew/pizzaguy.ogg"]
            self.soundDictionaries[5]["psygib"] = [re.compile(r"psygib\W?"), "sound/westcoastcrew/psygib.ogg"]
            self.soundDictionaries[5]["puff"] = [re.compile(r"puff\W?"), "sound/westcoastcrew/puff.ogg"]
            self.soundDictionaries[5]["qaaq"] = [re.compile(r"^qaaq\W?$"), "sound/westcoastcrew/qaaq.ogg"]
            self.soundDictionaries[5]["qibuqi"] = [re.compile(r"^qibuqi\W?$"), "sound/westcoastcrew/qibuqi.ogg"]
            self.soundDictionaries[5]["qqaaq"] = [re.compile(r"^qqaaq\W?$"), "sound/westcoastcrew/qqaaq.ogg"]
            self.soundDictionaries[5]["questionable"] = [re.compile(r"^questionable\W?$"), "sound/westcoastcrew/questionable.ogg"]
            self.soundDictionaries[5]["rage quit"] = [re.compile(r"rage quit\W?"), "sound/westcoastcrew/ragequit.ogg"]
            self.soundDictionaries[5]["let's get ready to rumble"] = [re.compile(r"let'?s get ready to rumble\W?"), "sound/westcoastcrew/readytorumble.ogg"]
            self.soundDictionaries[5]["really"] = [re.compile(r"^really\W?"), "sound/westcoastcrew/really.ogg"]
            self.soundDictionaries[5]["reflexes"] = [re.compile(r"(?:reflexes|it'?s all in the reflexes)"), "sound/westcoastcrew/reflexes.ogg"]
            self.soundDictionaries[5]["rekt"] = [re.compile(r"rekt\W?"), "sound/westcoastcrew/rekt.ogg"]
            # repeat of FunnySounds
            # self.soundDictionaries[5]["retard"] = [re.compile(r"retard"), "sound/westcoastcrew/Retard.ogg"]
            #self.soundDictionaries[5]["rockyouguitar"] = [re.compile(r"^rockyouguitar\W?$"), "sound/westcoastcrew/RockYouGuitar.ogg"]
            self.soundDictionaries[5]["rothkoo"] = [re.compile(r"^rothkoo\W?$"), "sound/westcoastcrew/rothko.ogg"]
            self.soundDictionaries[5]["rothko"] = [re.compile(r"^rothko\W?$"), "sound/westcoastcrew/rothko_theme.ogg"]
            self.soundDictionaries[5]["rugged"] = [re.compile(r"(?:rugged\W?$|like a rock)"), "sound/westcoastcrew/rugged.ogg"]
            self.soundDictionaries[5]["santa town"] = [re.compile(r"santa( )?town\W?"), "sound/westcoastcrew/santatown.ogg"]
            self.soundDictionaries[5]["saved"] = [re.compile(r"saved\W?"), "sound/westcoastcrew/saved.ogg"]
            self.soundDictionaries[5]["scrub"] = [re.compile(r"scrub\W?"), "sound/westcoastcrew/scrub.ogg"]
            self.soundDictionaries[5]["senth"] = [re.compile(r"^senth\W?$"), "sound/westcoastcrew/senth.ogg"]
            self.soundDictionaries[5]["shaft"] = [re.compile(r"^shaft\W?$"), "sound/westcoastcrew/shaft.ogg"]
            self.soundDictionaries[5]["shenookies cookies"] = [re.compile(r"shenookie'?s cookies\W?$"), "sound/westcoastcrew/shenook.ogg"]
            self.soundDictionaries[5]["shenookie"] = [re.compile(r"shenookie\W?$"), "sound/westcoastcrew/shenookies.ogg"]
            self.soundDictionaries[5]["you show that turd"] = [re.compile(r"(?:turd|(you )?show that turd)\W?$"), "sound/westcoastcrew/showthatturd.ogg"]
            self.soundDictionaries[5]["shufflenufiguess"] = [re.compile(r"shufflenufiguess\W?"), "sound/westcoastcrew/shufflenufflegus.ogg"]
            self.soundDictionaries[5]["skadoosh"] = [re.compile(r"skadoosh\W?"), "sound/westcoastcrew/skadoosh.ogg"]
            self.soundDictionaries[5]["slime"] = [re.compile(r"slime\W?"), "sound/westcoastcrew/slime.ogg"]
            self.soundDictionaries[5]["snort"] = [re.compile(r"^snort\W?$"), "sound/westcoastcrew/snort.ogg"]
            self.soundDictionaries[5]["snpete"] = [re.compile(r"^snpete\W?$"), "sound/westcoastcrew/SNpete.ogg"]
            self.soundDictionaries[5]["snpete2"] = [re.compile(r"(?:snpete2|chick chicky boom)\W?"), "sound/westcoastcrew/SNpete2.ogg"]
            self.soundDictionaries[5]["so is your face"] = [re.compile(r"so is your face\W?"), "sound/westcoastcrew/soisyourface.ogg"]
            self.soundDictionaries[5]["solis"] = [re.compile(r"solis\W?$"), "sound/westcoastcrew/solis.ogg"]
            self.soundDictionaries[5]["spank you"] = [re.compile(r"spank you\W?"), "sound/westcoastcrew/spankyou.ogg"]
            self.soundDictionaries[5]["stfu2"] = [re.compile(r"^stfu2"), "sound/westcoastcrew/stfu.ogg"]
            self.soundDictionaries[5]["still feel like you're mad"] = [re.compile(r"still feel like you'?re mad\W?"), "sound/westcoastcrew/stillmad.ogg"]
            self.soundDictionaries[5]["stitch"] = [re.compile(r"stitch\W?"), "sound/westcoastcrew/stitch.ogg"]
            self.soundDictionaries[5]["somebody stop me"] = [re.compile(r"somebody stop me\W?"), "sound/westcoastcrew/stopme.ogg"]
            self.soundDictionaries[5]["survey said"] = [re.compile(r"^survey said\W?"), "sound/westcoastcrew/surveysaid.ogg"]
            self.soundDictionaries[5]["swish"] = [re.compile(r"swish\W?"), "sound/westcoastcrew/swish.ogg"]
            self.soundDictionaries[5]["team complete"] = [re.compile(r"^team( )?complete\W?$"), "sound/westcoastcrew/teamcomplete2.ogg"]
            # repeat of FunnySounds
            # self.soundDictionaries[5]["teamwork"] = [re.compile(r"teamwork"), "sound/westcoastcrew/Teamwork.ogg"]
            self.soundDictionaries[5]["that's all folks"] = [re.compile(r"^that'?s all folks\W?$"), "sound/westcoastcrew/thatsallfolks.ogg"]
            self.soundDictionaries[5]["thetealduck"] = [re.compile(r"the ?teal ?duck\W?"), "sound/westcoastcrew/thetealduck.ogg"]
            self.soundDictionaries[5]["thriller"] = [re.compile(r"thriller\W?"), "sound/westcoastcrew/thriller.ogg"]
            self.soundDictionaries[5]["tooold"] = [re.compile(r"too?o?ld\W?"), "sound/westcoastcrew/tooold.ogg"]
            self.soundDictionaries[5]["troll toll"] = [re.compile(r"troll ?toll\W?"), "sound/westcoastcrew/trolltoll.ogg"]
            self.soundDictionaries[5]["turple"] = [re.compile(r"^turple\W?$"), "sound/westcoastcrew/turpled.ogg"]
            self.soundDictionaries[5]["tustamena"] = [re.compile(r"tustamena\W?"), "sound/westcoastcrew/tustamena.ogg"]
            self.soundDictionaries[5]["ty2"] = [re.compile(r"(?:thanks2|ty2)\W?"), "sound/westcoastcrew/ty.ogg"]
            self.soundDictionaries[5]["unstoppable"] = [re.compile(r"unstoppable\W?"), "sound/westcoastcrew/unstoppable.ogg"]
            self.soundDictionaries[5]["ventt"] = [re.compile(r"ventt\W?"), "sound/westcoastcrew/v3ntt.ogg"]
            self.soundDictionaries[5]["vacuum"] = [re.compile(r"vacuum\W?"), "sound/westcoastcrew/vacuum.ogg"]
            self.soundDictionaries[5]["vks"] = [re.compile(r"^(?:vks|bow)$"), "sound/westcoastcrew/vks.ogg"]
            self.soundDictionaries[5]["w3rd"] = [re.compile(r"w3rd\W?"), "sound/westcoastcrew/w3rd.ogg"]
            self.soundDictionaries[5]["wanerbuliao"] = [re.compile(r"^wanerbuliao\W?$"), "sound/westcoastcrew/wanerbuliao.ogg"]
            self.soundDictionaries[5]["waow"] = [re.compile(r"waow\W?"), "sound/westcoastcrew/waow.ogg"]
            self.soundDictionaries[5]["what did you do"] = [re.compile(r"^what did you do\W?"), "sound/westcoastcrew/whatdidyoudo.ogg"]
            self.soundDictionaries[5]["what just happened"] = [re.compile(r"^what( )?just( )?happened\W?$"), "sound/westcoastcrew/whatjusthappened.ogg"]
            self.soundDictionaries[5]["why you little"] = [re.compile(r"why you little\W?"), "sound/westcoastcrew/whyyoulittle.ogg"]
            self.soundDictionaries[5]["wolf"] = [re.compile(r"wolf\W?"), "sound/westcoastcrew/wolf.ogg"]
            self.soundDictionaries[5]["wow"] = [re.compile(r"^wow\W?$"), "sound/westcoastcrew/wow.ogg"]
            self.soundDictionaries[5]["woww"] = [re.compile(r"^woww\W?$"), "sound/westcoastcrew/wow2.ogg"]
            self.soundDictionaries[5]["wuyoga"] = [re.compile(r"wuyoga\W?"), "sound/westcoastcrew/wuyoga.ogg"]
            self.soundDictionaries[5]["xxx"] = [re.compile(r"^xxx\W?$"), "sound/westcoastcrew/xxx.ogg"]
            self.soundDictionaries[5]["ya basic"] = [re.compile(r"ya ?basic\W?"), "sound/westcoastcrew/yabasic.ogg"]
            self.soundDictionaries[5]["jdub"] = [re.compile(r"(?:jdub|y'?all ready for this)\W?$"), "sound/westcoastcrew/yallreadyforthis.ogg"]
            self.soundDictionaries[5]["yawn"] = [re.compile(r"^yawn\W?$"), "sound/westcoastcrew/yawn.ogg"]
            self.soundDictionaries[5]["yawnn"] = [re.compile(r"^yawnn+\W?$"), "sound/westcoastcrew/yawnn.ogg"]
            self.soundDictionaries[5]["yeah baby"] = [re.compile(r"yeah baby\W?"), "sound/westcoastcrew/yeahbaby.ogg"]
            # repeat of FunnySounds
            # self.soundDictionaries[5]["yhehehe"] = [re.compile(r"^yhehehe\W?$"), "sound/westcoastcrew/YHehehe.ogg"]
            self.soundDictionaries[5]["you can do it"] = [re.compile(r"you can do( it)?\W?"), "sound/westcoastcrew/youcandoit.ogg"]
            self.soundDictionaries[5]["youlose"] = [re.compile(r"youlose\W?"), "sound/westcoastcrew/youlose.ogg"]
            self.soundDictionaries[5]["your pick"] = [re.compile(r"your ?pick\W?"), "sound/westcoastcrew/yourpick.ogg"]
            self.soundDictionaries[5]["zebby"] = [re.compile(r"^zebby\W?$"), "sound/westcoastcrew/zebby.ogg"]

        self.populate_sound_lists()
        return
