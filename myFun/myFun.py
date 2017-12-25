# This plugin is a modification of minqlx's fun.py
# https://github.com/MinoMino/minqlx

# Created by BarelyMiSSeD
# https://github.com/BarelyMiSSeD

# You are free to modify this plugin
# This plugin comes with no warranty or guarantee

"""
This is my replacement for the minqlx fun.py so if you use this file make sure not to load fun.py

This plugin plays sounds on the Quake Live server
It plays the sounds included in fun.py and some from three other workshop items.

This will limit sound spamming to the server.
It only allows one sound to be played at a time and each user is limited in the frequency they can play sounds.


To set the time required between sounds add this line to your server.cfg and edit the "5":
set qlx_funSoundDelay "5"

To set the time a player has to wait after playing a sound add this like to your server.cfg and edit the "30":
set qlx_funPlayerSoundRepeat "30"


Three extra workshop items need to be loaded on the server for it to work correctly:
#prestige worldwide sounds workshop
585892371
#Funny Sounds Pack for Minqlx
620087103
#Duke Nukem Sounds
572453229

The minqlx 'workshop' plugin needs to be loaded and the required workshop
 items added to the set qlx_workshopReferences line
  (this example shows only these three required workshop items):
set qlx_workshopReferences "585892371, 620087103, 572453229"

Put the sound_names.txt file into the server's fs_homepath directory for
the !listsounds to work on the server.
!listsounds can be issued by itself to see all the sounds that can be played on the server
or it can be issued with one argument to limit the listed sounds to the sound phrases that contain that argument.
Example: '!listsounds yeah' would list all the sound phrases containing 'yeah'
 and would print this to the player's console (based on sound_names.txt at the time of this file creation):

SOUNDS: Type These words/phrases in normal chat to get a sound to play on the server.
haha yeah haha    hahaha yeah    yeah hahaha    yeahhh
4 SOUNDS: These are the sounds that work on this server.

If you edit the sound_names.txt put one sound phrase on each line and any line beginning with a # will be ignored
"""

import minqlx
import random
import time
import re
import os

from minqlx.database import Redis


FILE_NAME = 'sound_names.txt'
VERSION = 1.4

class myFun(minqlx.Plugin):
    database = Redis

    def __init__(self):
        super().__init__()
        self.add_hook("chat", self.handle_chat)
        self.add_hook("server_command", self.handle_server_command)
        self.add_command("cookies", self.cmd_cookies)
        self.last_sound = None

        #Let players with perm level 5 play sounds after the "qlx_funSoundDelay" timeout (no player time restriction)
        self.set_cvar_once("qlx_funUnrestrictAdmin", "0")
        #Delay between sounds being played
        self.set_cvar_once("qlx_funSoundDelay", "5")
        #**** Used for limiting players spamming sounds. ****
        # Amount of seconds player has to wait before allowed to play another sound
        self.set_cvar_once("qlx_funPlayerSoundRepeat", "30")
        #Keep muted players from playing sounds
        self.set_cvar_once("qlx_funDisableMutedPlayers", "1")

        # Dictionary used to store player sound call times.
        self.sound_limiting = {}
        #List to store steam ids of muted players
        self.muted_players = []

        self.add_hook("player_disconnect", self.player_disconnect)
        self.add_command(("getsounds", "listsounds", "listsound"), self.cmd_listsounds)

        #variable to show when a sound has been played
        self.played = False
        #variable to store the sound to be called
        self.soundFile = ""

    def player_disconnect(self, player, reason):
        try:
            del self.sound_limiting[player.steam_id]
        except KeyError:
            pass
        except TypeError:
            logger.debug("myFun.py: player_disconnect - invalid player steam id: {}".format(player.steam_id))
        try:
            del self.muted_players[player.steam_id]
        except KeyError:
            pass
        except TypeError:
            logger.debug("myFun.py: player_disconnect - invalid player steam id: {}".format(player.steam_id))

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

    def handle_chat(self, player, msg, channel):
        if channel != "chat" or player.steam_id in self.muted_players:
            return

        msg = self.clean_text(msg)
        if self.find_sound_trigger(msg):
            if self.check_time(player):
                if self.get_cvar("qlx_funUnrestrictAdmin", bool) and self.db.get_permission(player.steam_id) == 5:
                    pass
                else:
                    player.tell("^3You played a sound in last {} seconds. Try again after your timeout."
                                .format(self.get_cvar("qlx_funPlayerSoundRepeat")))
                    return

            if not self.last_sound:
                pass
            elif time.time() - self.last_sound < self.get_cvar("qlx_funSoundDelay", int):
                player.tell("^3A sound has been played in last {} seconds. Try again after the timeout."
                            .format(self.get_cvar("qlx_funSoundDelay")))
                return
            self.play_sound(self.soundFile)


        if self.played:
            self.sound_limiting[player.steam_id] = time.time()

        self.played = False

    def play_sound(self, path):
        self.played = True

        self.last_sound = time.time()
        for p in self.players():
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                super().play_sound(path, p)

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
            if time.time() - saved_time > self.get_cvar("qlx_funPlayerSoundRepeat", int):
                return False
            else:
                return True
        except KeyError:
            return False

    def cmd_listsounds(self, player, msg, channel):
        sounds = "^4SOUNDS^7: ^3Type These words/phrases in normal chat to get a sound to play on the server.^1"
        try:
            f = open(os.path.join(self.get_cvar("fs_homepath"), FILE_NAME), 'r')
            lines = f.readlines()
            f.close()
        except IOError:
            channel.reply("^4Server^7: Reading Sound List file ^1failed^7. Contact a server admin.")
            return
        lines.sort()
        items = 0
        if len(msg) < 2:
            for line in lines:
                if line.startswith("#"): continue
                addSound = line.strip()
                soundLine = sounds.split("\n")[-1]
                sounds += self.line_up(soundLine, addSound)
                items += 1

        else:
            count = 0
            search = msg[1]
            for line in lines:
                if line.startswith("#"): continue
                addSound = line.strip()
                if search in addSound:
                    count += 1
                    soundLine = sounds.split("\n")[-1]
                    sounds += self.line_up(soundLine, addSound)
                    items += 1
            if count == 0:
                player.tell("^4Server^7: No sounds contain the search string ^1{}^7.".format(search))
                return
        if sounds.endswith("\n"):
            sounds += "^2{} ^4SOUNDS^7: ^3These are the sounds that work on this server.".format(items)
        else:
            sounds += "\n^2{} ^4SOUNDS^7: ^3These are the sounds that work on this server.".format(items)

        if "console" == channel:
            showConsole = sounds.split("\n")
            for line in showConsole:
                minqlx.console_print("^1" + line)
            return

        player.tell(sounds)
        return

    def line_up(self, soundLine, addSound):
        length = len(soundLine)
        if length == 0:
            append = addSound
        elif length < 14:
            append = " " * (14 - length) + addSound
        elif length < 29:
            append = " " * (29 - length) + addSound
        elif length < 44:
            append = " " * (44 - length) + addSound
        elif length < 59:
            append = " " * (59 - length) + addSound
        elif length < 74:
            append = " " * (74 - length) + addSound
        else:
            append = "\n" + addSound
        return append

    def find_sound_trigger(self, msg):
        msg_lower = msg.lower()
        if re.compile(r"^haha(?:ha)?,? yeah?\W?$").match(msg_lower):
            self.soundFile = "sound/player/lucy/taunt.wav"
            return True
        elif re.compile(r"^haha(?:ha)?,? yeah?,? haha\W?$").match(msg_lower):
            self.soundFile = "sound/player/biker/taunt.wav"
            return True
        elif re.compile(r"^yeah?,? haha(?:ha)\W?$").match(msg_lower):
            self.soundFile = "sound/player/razor/taunt.wav"
            return True
        elif re.compile(r"^duahaha(?:ha)?\W?$").match(msg_lower):
            self.soundFile = "sound/player/keel/taunt.wav"
            return True
        elif re.compile(r"^hahaha").search(msg_lower):
            self.soundFile = "sound/player/santa/taunt.wav"
            return True
        elif re.compile(r"^(?:gl ?hf\W?)|(?:hf\W?)|(?:gl hf\W?)").match(msg_lower):
            self.soundFile ="sound/vo/crash_new/39_01.wav"
            return True
        elif re.compile(r"^(?:(?:press )?f3)|ready(?: up)?\W?").match(msg_lower):
            self.soundFile ="sound/vo/crash_new/36_04.wav"
            return True
        elif "holy shit" in msg_lower:
            self.soundFile ="sound/vo_female/holy_shit"
            return True
        elif re.compile(r"^welcome to (?:ql|quake live)\W?$").match(msg_lower):
            self.soundFile ="sound/vo_evil/welcome"
            return True
        elif re.compile(r"^go\W?$").match(msg_lower):
            self.soundFile ="sound/vo/go"
            return True
        elif re.compile(r"^beep boop\W?$").match(msg_lower):
            self.soundFile ="sound/player/tankjr/taunt.wav"
            return True
        elif re.compile(r"^you win\W?$").match(msg_lower):
            self.soundFile ="sound/vo_female/you_win.wav"
            return True
        elif re.compile(r"^you lose\W?$").match(msg_lower):
            self.soundFile ="sound/vo/you_lose.wav"
            return True
        elif "impressive" in msg_lower:
            self.soundFile ="sound/vo_female/impressive1.wav"
            return True
        elif "excellent" in msg_lower:
            self.soundFile ="sound/vo_evil/excellent1.wav"
            return True
        elif re.compile(r"^denied\W?$").match(msg_lower):
            self.soundFile ="sound/vo/denied"
            return True
        elif re.compile(r"^ball'?s out\W?$").match(msg_lower):
            self.soundFile ="sound/vo_female/balls_out"
            return True
        elif re.compile(r"^one\W?$").match(msg_lower):
            self.soundFile ="sound/vo_female/one"
            return True
        elif re.compile(r"^two\W?$").match(msg_lower):
            self.soundFile ="sound/vo_female/two"
            return True
        elif re.compile(r"^three\W?$").match(msg_lower):
            self.soundFile ="sound/vo_female/three"
            return True
        elif re.compile(r"^fight\W?$").match(msg_lower):
            self.soundFile ="sound/vo_evil/fight"
            return True
        elif re.compile(r"^gauntlet\W?$").match(msg_lower):
            self.soundFile ="sound/vo_evil/gauntlet"
            return True
        elif re.compile(r"^humiliation\W?$").match(msg_lower):
            self.soundFile ="sound/vo_evil/humiliation1"
            return True
        elif re.compile(r"^perfect\W?$").match(msg_lower):
            self.soundFile ="sound/vo_evil/perfect"
            return True
        elif re.compile(r"^wa+h wa+h wa+h wa+h\W?$").match(msg_lower):
            self.soundFile ="sound/misc/yousuck"
            return True
        elif re.compile(r"^a+h a+h a+h\W?$").match(msg_lower):
            self.soundFile ="sound/player/slash/taunt.wav"
            return True
        elif re.compile(r"^oink\W?$").match(msg_lower):
            self.soundFile ="sound/player/sorlag/pain50_1.wav"
            return True
        elif re.compile(r"^a+rgh\W?$").match(msg_lower):
            self.soundFile ="sound/player/doom/taunt.wav"
            return True
        elif re.compile(r"^hah haha\W?$").match(msg_lower):
            self.soundFile ="sound/player/hunter/taunt.wav"
            return True
        elif re.compile(r"^woo+hoo+\W?$").match(msg_lower):
            self.soundFile ="sound/player/janet/taunt.wav"
            return True
        elif re.compile(r"^(?:ql|quake live)\W?$").match(msg_lower):
            self.soundFile ="sound/vo_female/quake_live"
            return True
        elif re.compile(r"(?:\$|€|£|chaching)").search(msg_lower):
            self.soundFile ="sound/misc/chaching"
            return True
        elif re.compile(r"^uh ah$").match(msg_lower):
            self.soundFile ="sound/player/mynx/taunt.wav"
            return True
        elif re.compile(r"^ooh+wee\W?$").match(msg_lower):
            self.soundFile ="sound/player/anarki/taunt.wav"
            return True
        elif re.compile(r"^erah\W?$").match(msg_lower):
            self.soundFile ="sound/player/bitterman/taunt.wav"
            return True
        elif re.compile(r"^yeahhh\W?$").match(msg_lower):
            self.soundFile ="sound/player/major/taunt.wav"
            return True
        elif re.compile(r"^scream\W?$").match(msg_lower):
            self.soundFile ="sound/player/bones/taunt.wav"
            return True
        elif re.compile(r"^salute\W?$").match(msg_lower):
            self.soundFile ="sound/player/sarge/taunt.wav"
            return True
        elif re.compile(r"^squish\W?$").match(msg_lower):
            self.soundFile ="sound/player/orbb/taunt.wav"
            return True
        elif re.compile(r"^oh god\W?$").match(msg_lower):
            self.soundFile ="sound/player/ranger/taunt.wav"
            return True
        elif re.compile(r"^snarl\W?$").match(msg_lower):
            self.soundFile ="sound/player/sorlag/taunt.wav"
            return True

        #Viewaskewer
        elif re.compile(r"^assholes\W?$").match(msg_lower):
            self.soundFile ="soundbank/assholes.ogg"
            return True
        elif re.compile(r"^(?:assshafter|asshafter|ass shafter)\W?$").match(msg_lower):
            self.soundFile ="soundbank/assshafterloud.ogg"
            return True
        elif re.compile(r"^babydoll\W?$").match(msg_lower):
            self.soundFile ="soundbank/babydoll.ogg"
            return True
        elif re.compile(r"^(?:barelymissed|barely)\W?$").match(msg_lower):
            self.soundFile ="soundbank/barelymissed.ogg"
            return True
        elif re.compile(r"^belly\W?$").match(msg_lower):
            self.soundFile ="soundbank/belly.ogg"
            return True
        elif re.compile(r"^bitch\W?$").match(msg_lower):
            self.soundFile ="soundbank/bitch.ogg"
            return True
        elif re.compile(r"^(?:dtblud|blud)\W?$").match(msg_lower):
            self.soundFile ="soundbank/dtblud.ogg"
            return True
        elif re.compile(r"^boats\W?$").match(msg_lower):
            self.soundFile ="soundbank/boats.ogg"
            return True
        elif re.compile(r"^(?:bobg|bob)\W?$").match(msg_lower):
            self.soundFile ="soundbank/bobg.ogg"
            return True
        elif re.compile(r"^bogdog\W?$").match(msg_lower):
            self.soundFile ="soundbank/bogdog.ogg"
            return True
        elif re.compile(r"^boom\W?$").match(msg_lower):
            self.soundFile ="soundbank/boom.ogg"
            return True
        elif re.compile(r"^boom2\W?$").match(msg_lower):
            self.soundFile ="soundbank/boom2.ogg"
            return True
        elif re.compile(r"^(?:buk|ibbukn)\W?$").match(msg_lower):
            self.soundFile ="soundbank/buk.ogg"
            return True
        elif re.compile(r"^(?:bullshit|bull shit|bs)\W?$").match(msg_lower):
            self.soundFile ="soundbank/bullshit.ogg"
            return True
        elif re.compile(r"^butthole\W?$").match(msg_lower):
            self.soundFile ="soundbank/butthole.ogg"
            return True
        elif re.compile(r"^buttsex\W?$").match(msg_lower):
            self.soundFile ="soundbank/buttsex.ogg"
            return True
        elif re.compile(r"^cheeks\W?$").match(msg_lower):
            self.soundFile ="soundbank/cheeks.ogg"
            return True
        elif re.compile(r"^(?:cocksucker|cs)\W?$").match(msg_lower):
            self.soundFile ="soundbank/cocksucker.ogg"
            return True
        elif re.compile(r"^conquer\W?$").match(msg_lower):
            self.soundFile ="soundbank/conquer.ogg"
            return True
        elif re.compile(r"^countdown\W?$").match(msg_lower):
            self.soundFile ="soundbank/countdown.ogg"
            return True
        elif re.compile(r"^cum\W?$").match(msg_lower):
            self.soundFile ="soundbank/cum.ogg"
            return True
        elif re.compile(r"^cumming\W?$").match(msg_lower):
            self.soundFile ="soundbank/cumming.ogg"
            return True
        elif re.compile(r"^cunt\W?$").match(msg_lower):
            self.soundFile ="soundbank/cunt.ogg"
            return True
        elif re.compile(r"^(?:dirkfunk|dirk)\W?$").match(msg_lower):
            self.soundFile ="soundbank/dirkfunk.ogg"
            return True
        elif re.compile(r"^disappointment\W?$").match(msg_lower):
            self.soundFile ="soundbank/disappointment.ogg"
            return True
        elif re.compile(r"^(?:doom|doomsday)\W?$").match(msg_lower):
            self.soundFile ="soundbank/doom.ogg"
            return True
        elif re.compile(r"^drumset\W?$").match(msg_lower):
            self.soundFile ="soundbank/drumset.ogg"
            return True
        elif re.compile(r"^eat\W?$").match(msg_lower):
            self.soundFile ="soundbank/eat.ogg"
            return True
        elif re.compile(r"^(?:eatme|eat me|byte me)\W?$").match(msg_lower):
            self.soundFile ="soundbank/eatme.ogg"
            return True
        elif re.compile(r"^(?:fag|homo|homosexual)\W?$").match(msg_lower):
            self.soundFile ="soundbank/fag.ogg"
            return True
        elif re.compile(r"^fingerass\W?$").match(msg_lower):
            self.soundFile ="soundbank/fingerass.ogg"
            return True
        elif re.compile(r"^(?:flashsoul|flash)\W?$").match(msg_lower):
            self.soundFile ="soundbank/flash.ogg"
            return True
        elif re.compile(r"^fuckface\W?$").match(msg_lower):
            self.soundFile ="soundbank/fuckface.ogg"
            return True
        elif re.compile(r"^fuckyou\W?$").match(msg_lower):
            self.soundFile ="soundbank/fuckyou.ogg"
            return True
        elif re.compile(r"^(?:getem+|get em+)\W?$").match(msg_lower):
            self.soundFile ="soundbank/getemm.ogg"
            return True
        elif re.compile(r"^(?:gonads|nads)\W?$").match(msg_lower):
            self.soundFile ="soundbank/gonads.ogg"
            return True
        elif re.compile(r"^gtfo\W?$").match(msg_lower):
            self.soundFile ="soundbank/gtfo.ogg"
            return True
        elif re.compile(r"^HIT\W?$").match(msg):
            self.soundFile ="soundbank/doom.ogg"
            return True
        elif re.compile(r"^hug it out\W?$").match(msg_lower):
            self.soundFile ="soundbank/hugitout.ogg"
            return True
        elif re.compile(r"^(?:idiot|andycreep|d3phx|gladiat0r)\W?$").match(msg_lower):
            self.soundFile ="soundbank/idiot.ogg"
            return True
        elif re.compile(r"^idiot2\W?$").match(msg_lower):
            self.soundFile ="soundbank/idiot2.ogg"
            return True
        elif re.compile(r"^it?'s time\W?$").match(msg_lower):
            self.soundFile ="soundbank/itstime.ogg"
            return True
        elif re.compile(r"^jeopardy\W?$").match(msg_lower):
            self.soundFile ="soundbank/jeopardy.ogg"
            return True
        elif re.compile(r"^(?:jerk off|jerkoff)\W?$").match(msg_lower):
            self.soundFile ="soundbank/jerkoff.ogg"
            return True
        elif re.compile(r"^killo\W?$").match(msg_lower):
            self.soundFile ="soundbank/killo.ogg"
            return True
        elif re.compile(r"^knocked\W?$").match(msg_lower):
            self.soundFile ="soundbank/knocked.ogg"
            return True
        elif re.compile(r"^(?:die|ld3)\W?$").match(msg_lower):
            self.soundFile ="soundbank/ld3.ogg"
            return True
        elif re.compile(r"^(?:liquidswords|liquid)\W?$").match(msg_lower):
            self.soundFile ="soundbank/liquid.ogg"
            return True
        elif re.compile(r"^massacre\W?$").match(msg_lower):
            self.soundFile ="soundbank/massacre.ogg"
            return True
        elif re.compile(r"^mixer\W?$").match(msg_lower):
            self.soundFile ="soundbank/mixer.ogg"
            return True
        elif re.compile(r"^(?:mjman|marijuanaman)\W?$").match(msg_lower):
            self.soundFile ="soundbank/mjman.ogg"
            return True
        elif re.compile(r"^mmmm\W?$").match(msg_lower):
            self.soundFile ="soundbank/mmmm.ogg"
            return True
        elif re.compile(r"^monty\W?$").match(msg_lower):
            self.soundFile ="soundbank/monty.ogg"
            return True
        elif re.compile(r"^(?:n8|_n8)\W?$").match(msg_lower):
            self.soundFile ="soundbank/n8.ogg"
            return True
        elif re.compile(r"^(?:nikon|niko|nikonguru)\W?$").match(msg_lower):
            self.soundFile ="soundbank/nikon.ogg"
            return True
        elif re.compile(r"^nina\W?$").match(msg_lower):
            self.soundFile ="soundbank/nina.ogg"
            return True
        elif re.compile(r"^nthreem\W?$").match(msg_lower):
            self.soundFile ="sound/vo_female/impressive1.wav"
            return True
        elif re.compile(r"^(?:olhip|hip)\W?$").match(msg_lower):
            self.soundFile ="soundbank/hip.ogg"
            return True
        elif re.compile(r"^(?:organic|org)\W?$").match(msg_lower):
            self.soundFile ="soundbank/organic.ogg"
            return True
        elif re.compile(r"^paintball\W?$").match(msg_lower):
            self.soundFile ="soundbank/paintball.ogg"
            return True
        elif re.compile(r"^(?:pigfucker|pig fucker|pf)\W?$").match(msg_lower):
            self.soundFile ="soundbank/pigfer.ogg"
            return True
        elif re.compile(r"^popeye\W?$").match(msg_lower):
            self.soundFile ="soundbank/popeye.ogg"
            return True
        elif re.compile(r"^rosie\W?$").match(msg_lower):
            self.soundFile ="soundbank/rosie.ogg"
            return True
        elif re.compile(r"^seaweed\W?$").match(msg_lower):
            self.soundFile ="soundbank/seaweed.ogg"
            return True
        elif re.compile(r"^shit\W?$").match(msg_lower):
            self.soundFile ="soundbank/shit.ogg"
            return True
        elif re.compile(r"(^sit\W?$| sit | sit$)").search(msg):
            self.soundFile ="soundbank/sit.ogg"
            return True
        elif re.compile(r"^(?:soulianis|soul)\W?$").search(msg):
            self.soundFile ="soundbank/soulianis.ogg"
            return True
        elif re.compile(r"^spam\W?$").match(msg_lower):
            self.soundFile ="soundbank/spam3.ogg"
            return True
        elif re.compile(r"^stalin\W?$").match(msg_lower):
            self.soundFile ="soundbank/ussr.ogg"
            return True
        elif re.compile(r"^stfu\W?$").match(msg_lower):
            self.soundFile ="soundbank/stfu.ogg"
            return True
        elif re.compile(r"^suck a dick\W?$").match(msg_lower):
            self.soundFile ="soundbank/suckadick.ogg"
            return True
        elif re.compile(r"^suckit\W?$").match(msg_lower):
            self.soundFile ="soundbank/suckit.ogg"
            return True
        elif re.compile(r"^suck my dick\W?$").match(msg_lower):
            self.soundFile ="soundbank/suckmydick.ogg"
            return True
        elif re.compile(r"^teapot\W?$").match(msg_lower):
            self.soundFile ="soundbank/teapot.ogg"
            return True
        elif re.compile(r"^(?:thankgod|thank god)\W?$").match(msg_lower):
            self.soundFile ="soundbank/thankgod.ogg"
            return True
        elif re.compile(r"^traxion\W?$").match(msg_lower):
            self.soundFile ="soundbank/traxion.ogg"
            return True
        elif re.compile(r"^trixy\W?$").match(msg_lower):
            self.soundFile ="soundbank/trixy.ogg"
            return True
        elif re.compile(r"^(?:twoon|2pows)\W?$").match(msg_lower):
            self.soundFile ="soundbank/twoon.ogg"
            return True
        elif re.compile(r"^(?:ty|thanks|thank you)\W?$").match(msg_lower):
            self.soundFile ="soundbank/thankyou.ogg"
            return True
        elif re.compile(r"^venny\W?$").match(msg_lower):
            self.soundFile ="soundbank/venny.ogg"
            return True
        elif re.compile(r"^(?:viewaskewer|view)\W?$").match(msg_lower):
            self.soundFile ="soundbank/view.ogg"
            return True
        elif re.compile(r"^what?'s that\W?$").match(msg_lower):
            self.soundFile ="soundbank/whatsthat.ogg"
            return True
        elif re.compile(r"^who are you\W?$").match(msg_lower):
            self.soundFile ="soundbank/whoareyou.ogg"
            return True

        #|sf|bart`us's
        elif re.compile(r"^007\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/007.ogg"
            return True
        elif re.compile(r"^(?:a scratch|scratch|just a scratch)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/AScratch.ogg"
            return True
        elif re.compile(r"^(?:adamsfamily|adams family)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/adamsfamily.ogg"
            return True
        elif re.compile(r"^allahuakbar\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/allahuakbar.ogg"
            return True
        elif re.compile(r"^allstar\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/allstar.ogg"
            return True
        elif re.compile(r"^all the things\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/AllTheThings.ogg"
            return True
        elif re.compile(r"^amazing\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Amazing.ogg"
            return True
        elif re.compile(r"^ameno\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Ameno.ogg"
            return True
        elif re.compile(r"^america\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/America.ogg"
            return True
        elif re.compile(r"^amerika\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Amerika.ogg"
            return True
        elif re.compile(r"^and nothing else\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/AndNothingElse.ogg"
            return True
        elif re.compile(r"^animals\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Animals.ogg"
            return True
        elif re.compile(r"^asskicking\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/asskicking.ogg"
            return True
        elif re.compile(r"^ave\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ave.ogg"
            return True
        elif re.compile(r"^baby baby\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/babybaby.ogg"
            return True
        elif re.compile(r"^baby evil\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/babyevillaugh.ogg"
            return True
        elif re.compile(r"^(?:babylaughing|baby laughing)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/babylaughing.ogg"
            return True
        elif re.compile(r"^bad boys\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/badboys.ogg"
            return True
        elif re.compile(r"^banana boat\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/BananaBoatSong.ogg"
            return True
        elif re.compile(r"^benny hill\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/bennyhill.ogg"
            return True
        elif re.compile(r"^benzin\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/benzin.ogg"
            return True
        elif re.compile(r"^blue wins\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/bluewins.ogg"
            return True
        elif re.compile(r"^bonkers\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/bonkers.ogg"
            return True
        elif re.compile(r"^boom headshot\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/boomheadshot.ogg"
            return True
        elif re.compile(r"^booo\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/booo.ogg"
            return True
        elif re.compile(r"^boring\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/boring.ogg"
            return True
        elif re.compile(r"^boze\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/boze.ogg"
            return True
        elif re.compile(r"^(?:brightsideoflife|bright side of life)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/brightsideoflife.ogg"
            return True
        elif re.compile(r"^buckdich\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/buckdich.ogg"
            return True
        elif re.compile(r"^bullshitter\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/bullshitter.ogg"
            return True
        elif re.compile(r"^burns burns\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/burnsburns.ogg"
            return True
        elif re.compile(r"^camel toe\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/cameltoe.ogg"
            return True
        elif re.compile(r"^can'?t touch this\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/canttouchthis.ogg"
            return True
        elif re.compile(r"^(?:cccp|ussr)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/cccp.ogg"
            return True
        elif re.compile(r"^champions\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/champions.ogg"
            return True
        elif re.compile(r"^chicken\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/chicken.ogg"
            return True
        elif re.compile(r"^chocolate rain\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/chocolaterain.ogg"
            return True
        elif re.compile(r"^coin\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/coin.ogg"
            return True
        elif re.compile(r"^come\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/come.ogg"
            return True
        elif re.compile(r"^come with me now\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ComeWithMeNow.ogg"
            return True
        elif re.compile(r"^count down\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Countdown.ogg"
            return True
        elif re.compile(r"^cowards\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/cowards.ogg"
            return True
        elif re.compile(r"^crazy\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/crazy.ogg"
            return True
        elif re.compile(r"^damnit\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/damnit.ogg"
            return True
        elif re.compile(r"^danger zone\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/DangerZone.ogg"
            return True
        elif re.compile(r"^(?:deadsoon|dead soon)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/deadsoon.ogg"
            return True
        elif re.compile(r"^defeated\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/defeated.ogg"
            return True
        elif re.compile(r"^devil\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/devil.ogg"
            return True
        elif re.compile(r"^doesn'?t love you\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/doesntloveyou.ogg"
            return True
        elif re.compile(r"^du bist\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/dubist.ogg"
            return True
        elif re.compile(r"^du hast\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/duhast.ogg"
            return True
        elif re.compile(r"^dumb ways\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/dumbways.ogg"
            return True
        elif re.compile(r"^eat pussy\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/EatPussy.ogg"
            return True
        elif re.compile(r"^education\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/education.ogg"
            return True
        elif re.compile(r"^einschrei\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/einschrei.ogg"
            return True
        elif re.compile(r"^eins zwei\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/EinsZwei.ogg"
            return True
        elif re.compile(r"^electro\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/electro.ogg"
            return True
        elif re.compile(r"^elementary\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/elementary.ogg"
            return True
        elif re.compile(r"^engel\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/engel.ogg"
            return True
        elif re.compile(r"^erstwenn\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/erstwenn.ogg"
            return True
        elif re.compile(r"^(?:exitlight|exit light)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/exitlight.ogg"
            return True
        elif re.compile(r"^faint\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/faint.ogg"
            return True
        elif re.compile(r"^fatality\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/fatality.ogg"
            return True
        elif re.compile(r"^feel good\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/FeelGood.ogg"
            return True
        elif re.compile(r"^flesh wound\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/fleshwound.ogg"
            return True
        elif re.compile(r"^for you\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/foryou.ogg"
            return True
        elif re.compile(r"^freestyler\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/freestyler.ogg"
            return True
        elif re.compile(r"^fuckfuck\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/fuckfuck.ogg"
            return True
        elif re.compile(r"^fucking burger\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/fuckingburger.ogg"
            return True
        elif re.compile(r"^fucking kids\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/fuckingkids.ogg"
            return True
        elif re.compile(r"^gangnam\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/gangnam.ogg"
            return True
        elif re.compile(r"^ganjaman\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ganjaman.ogg"
            return True
        elif re.compile(r"^gay\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/gay.ogg"
            return True
        elif re.compile(r"^get crowbar\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/getcrowbar.ogg"
            return True
        elif re.compile(r"^get out the way\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/getouttheway.ogg"
            return True
        elif re.compile(r"^ghostbusters\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ghostbusters.ogg"
            return True
        elif re.compile(r"^girl look\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/girllook.ogg"
            return True
        elif re.compile(r"^girly\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/girly.ogg"
            return True
        elif re.compile(r"^gnr guitar\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/gnrguitar.ogg"
            return True
        elif re.compile(r"^goddamn right\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/goddamnright.ogg"
            return True
        elif re.compile(r"^goodbye andrea\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/goodbyeandrea.ogg"
            return True
        elif re.compile(r"^goodbye sarah\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/goodbyesarah.ogg"
            return True
        elif re.compile(r"^gotcha\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/gotcha.ogg"
            return True
        elif re.compile(r"^hakunamatata\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/hakunamatata.ogg"
            return True
        elif re.compile(r"^hammertime\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/hammertime.ogg"
            return True
        elif re.compile(r"^hello\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/hello.ogg"
            return True
        elif re.compile(r"^hellstestern\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/hellstestern.ogg"
            return True
        elif re.compile(r"^holy\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/holy.ogg"
            return True
        elif re.compile(r"^hoppereiter\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/hoppereiter.ogg"
            return True
        elif re.compile(r"^how are you\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/howareyou.ogg"
            return True
        elif re.compile(r"^hush\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/hush.ogg"
            return True
        elif re.compile(r"^(?:ibet|i bet)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ibet.ogg"
            return True
        elif re.compile(r"^i can'?t believe\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/icantbelieve.ogg"
            return True
        elif re.compile(r"^ichtuedieweh\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ichtuedieweh.ogg"
            return True
        elif re.compile(r"^i do parkour\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/idoparkour.ogg"
            return True
        elif re.compile(r"^i hate all\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ihateall.ogg"
            return True
        elif re.compile(r"^i'?ll be back\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/beback.ogg"
            return True
        elif re.compile(r"^imperial\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/imperial.ogg"
            return True
        elif re.compile(r"^im sexy\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/imsexy.ogg"
            return True
        elif re.compile(r"^i'?m your father\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/imyourfather.ogg"
            return True
        elif re.compile(r"^incoming\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/incoming.ogg"
            return True
        elif re.compile(r"^indiana jones\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/indianajones.ogg"
            return True
        elif re.compile(r"^in your head zombie\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/inyourheadzombie.ogg"
            return True
        elif re.compile(r"^i see assholes\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/iseeassholes.ogg"
            return True
        elif re.compile(r"^i see dead people\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/iseedeadpeople.ogg"
            return True
        elif re.compile(r"^it'?s my life\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/itsmylife.ogg"
            return True
        elif re.compile(r"^it'?s not\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/itsnot.ogg"
            return True
        elif re.compile(r"^jackpot\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/jackpot.ogg"
            return True
        elif re.compile(r"^jesus\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/jesus.ogg"
            return True
        elif re.compile(r"^jesus Oh\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/JesusOh.ogg"
            return True
        elif re.compile(r"^(?:johncena|john cena)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/johncena.ogg"
            return True
        elif re.compile(r"^jump motherfucker\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/jumpmotherfucker.ogg"
            return True
        elif re.compile(r"^just do it\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/justdoit.ogg"
            return True
        elif re.compile(r"^kamehameha\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/kamehameha.ogg"
            return True
        elif re.compile(r"^keep on fighting\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/keeponfighting.ogg"
            return True
        elif re.compile(r"^keep your shirt on\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/keepyourshirton.ogg"
            return True
        elif re.compile(r"^knocked down\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/KnockedDown.ogg"
            return True
        elif re.compile(r"^kommtdiesonne\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/kommtdiesonne.ogg"
            return True
        elif re.compile(r"^(?:kungfu|kung fu)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/kungfu.ogg"
            return True
        elif re.compile(r"^lately\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/lately.ogg"
            return True
        elif re.compile(r"^legitness\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Legitness.ogg"
            return True
        elif re.compile(r"^lets get ready\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/letsgetready.ogg"
            return True
        elif re.compile(r"^lets put a smile\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/letsputasmile.ogg"
            return True
        elif re.compile(r"^lights out\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/lightsout.ogg"
            return True
        elif re.compile(r"^lion king\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/lionking.ogg"
            return True
        elif re.compile(r"^live to win\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/livetowin.ogg"
            return True
        elif re.compile(r"^losing my religion\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/losingmyreligion.ogg"
            return True
        elif re.compile(r"^(?:loveme|love me)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/loveme.ogg"
            return True
        elif re.compile(r"^low\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/low.ogg"
            return True
        elif re.compile(r"^luck\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/luck.ogg"
            return True
        elif re.compile(r"^lust\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/lust.ogg"
            return True
        elif re.compile(r"^mahnamahna\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/mahnamahna.ogg"
            return True
        elif re.compile(r"^mario\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/mario.ogg"
            return True
        elif re.compile(r"^me\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Me.ogg"
            return True
        elif re.compile(r"^meinland\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/meinland.ogg"
            return True
        elif re.compile(r"^message\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/message.ogg"
            return True
        elif re.compile(r"^mimimi\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/mimimi.ogg"
            return True
        elif re.compile(r"^mission\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/mission.ogg"
            return True
        elif re.compile(r"^moan\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/moan.ogg"
            return True
        elif re.compile(r"^mortal kombat\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/mortalkombat.ogg"
            return True
        elif re.compile(r"^move ass\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/moveass.ogg"
            return True
        elif re.compile(r"^muppet opening\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/muppetopening.ogg"
            return True
        elif re.compile(r"^my little pony\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/mylittlepony.ogg"
            return True
        elif re.compile(r"^my name\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/myname.ogg"
            return True
        elif re.compile(r"^never seen\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/neverseen.ogg"
            return True
        elif re.compile(r"^nightmare\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/nightmare.ogg"
            return True
        elif re.compile(r"^nobody likes you\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/nobodylikesyou.ogg"
            return True
        elif re.compile(r"^nonie\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/nonie.ogg"
            return True
        elif re.compile(r"^nooo\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/nooo.ogg"
            return True
        elif re.compile(r"^no time for loosers\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/notimeforloosers.ogg"
            return True
        elif re.compile(r"^numanuma\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/numanuma.ogg"
            return True
        elif re.compile(r"^nyancat\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/nyancat.ogg"
            return True
        elif re.compile(r"^o fuck\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ofuck.ogg"
            return True
        elif re.compile(r"^oh my god\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ohmygod.ogg"
            return True
        elif re.compile(r"^oh my gosh\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/OhMyGosh.ogg"
            return True
        elif re.compile(r"^ohnedich\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ohnedich.ogg"
            return True
        elif re.compile(r"^oh no\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ohno.ogg"
            return True
        elif re.compile(r"^oh noe\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ohnoe.ogg"
            return True
        elif re.compile(r"^pacman\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/pacman.ogg"
            return True
        elif re.compile(r"^pick me up\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/pickmeup.ogg"
            return True
        elif re.compile(r"^pikachu\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/pikachu.ogg"
            return True
        elif re.compile(r"^pinkiepie\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/pinkiepie.ogg"
            return True
        elif re.compile(r"^pink panther\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/PinkPanther.ogg"
            return True
        elif re.compile(r"^pipe\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/pipe.ogg"
            return True
        elif re.compile(r"^piss me off\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/pissmeoff.ogg"
            return True
        elif re.compile(r"^play a game\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/playagame.ogg"
            return True
        elif re.compile(r"^pooping\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/pooping.ogg"
            return True
        elif re.compile(r"^powerpuff\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/powerpuff.ogg"
            return True
        elif re.compile(r"^radioactive\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/radioactive.ogg"
            return True
        elif re.compile(r"^rammsteinriff\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/rammsteinriff.ogg"
            return True
        elif re.compile(r"^redwins\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/redwins.ogg"
            return True
        elif re.compile(r"^renegade\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/renegade.ogg"
            return True
        elif re.compile(r"^retard\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/retard.ogg"
            return True
        elif re.compile(r"^rocky\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/rocky"
            return True
        elif re.compile(r"^rockyouguitar\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/rockyouguitar.ogg"
            return True
        elif re.compile(r"^sail\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/sail.ogg"
            return True
        elif re.compile(r"^salil\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Salil.ogg"
            return True
        elif re.compile(r"^samba\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/samba.ogg"
            return True
        elif re.compile(r"^sandstorm\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/sandstorm.ogg"
            return True
        elif re.compile(r"^saymyname\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/saymyname.ogg"
            return True
        elif re.compile(r"^scatman\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/scatman.ogg"
            return True
        elif re.compile(r"^sell you all\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/sellyouall.ogg"
            return True
        elif re.compile(r"^sense of humor\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/senseofhumor.ogg"
            return True
        elif re.compile(r"^shakesenora\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/shakesenora.ogg"
            return True
        elif re.compile(r"^shut the fuck up\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/shutthefuckup.ogg"
            return True
        elif re.compile(r"^shut your fucking mouth\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/shutyourfuckingmouth.ogg"
            return True
        elif re.compile(r"^silence\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/silence.ogg"
            return True
        elif re.compile(r"^(?:all skeet skeet|skeet skeet)\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/AllSkeetSkeet.ogg"
            return True
        elif re.compile(r"^smooth criminal\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/smoothcriminal.ogg"
            return True
        elif re.compile(r"^socobatevira\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/socobatevira.ogg"
            return True
        elif re.compile(r"^socobatevira end\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/socobateviraend.ogg"
            return True
        elif re.compile(r"^socobatevira fast\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/socobatevirafast.ogg"
            return True
        elif re.compile(r"^socobatevira slow\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/socobateviraslow.ogg"
            return True
        elif re.compile(r"^sogivemereason\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/sogivemereason.ogg"
            return True
        elif re.compile(r"^so stupid\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/sostupid.ogg"
            return True
        elif re.compile(r"^space jam\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/SpaceJam.ogg"
            return True
        elif re.compile(r"^space unicorn\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/spaceunicorn.ogg"
            return True
        elif re.compile(r"^spierdalaj\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/spierdalaj.ogg"
            return True
        elif re.compile(r"^stamp on\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/stampon.ogg"
            return True
        elif re.compile(r"^star wars\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/starwars.ogg"
            return True
        elif re.compile(r"^stayin alive\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/stayinalive.ogg"
            return True
        elif re.compile(r"^stoning\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/stoning.ogg"
            return True
        elif re.compile(r"^stop\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/Stop.ogg"
            return True
        elif re.compile(r"^story\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/story.ogg"
            return True
        elif re.compile(r"^surprise\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/surprise.ogg"
            return True
        elif re.compile(r"^swedish chef\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/swedishchef.ogg"
            return True
        elif re.compile(r"^sweet dreams\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/sweetdreams.ogg"
            return True
        elif re.compile(r"^take me down\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/takemedown.ogg"
            return True
        elif re.compile(r"^talk scotish\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/talkscotish.ogg"
            return True
        elif re.compile(r"^teamwork\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/teamwork.ogg"
            return True
        elif re.compile(r"^technology\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/technology.ogg"
            return True
        elif re.compile(r"^this is sparta\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/thisissparta.ogg"
            return True
        elif re.compile(r"^thunderstruck\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/thunderstruck.ogg"
            return True
        elif re.compile(r"^to church\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/tochurch.ogg"
            return True
        elif re.compile(r"^tsunami\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/tsunami.ogg"
            return True
        elif re.compile(r"^tuturu\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/tuturu.ogg"
            return True
        elif re.compile(r"^tututu\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/tututu.ogg"
            return True
        elif re.compile(r"^unbelievable\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/unbelievable.ogg"
            return True
        elif re.compile(r"^undderhaifisch\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/undderhaifisch.ogg"
            return True
        elif re.compile(r"^up town girl\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/uptowngirl.ogg"
            return True
        elif re.compile(r"^valkyries\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/valkyries.ogg"
            return True
        elif re.compile(r"(?:wahwahwah|dcmattic|mattic)").search(msg):
            self.soundFile ="sound/funnysounds/wahwahwah.ogg"
            return True
        elif re.compile(r"^want you\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/wantyou.ogg"
            return True
        elif re.compile(r"^wazzup\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/wazzup.ogg"
            return True
        elif re.compile(r"^wehmirohweh\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/wehmirohweh.ogg"
            return True
        elif re.compile(r"^what is love\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/whatislove.ogg"
            return True
        elif re.compile(r"^when angels\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/whenangels.ogg"
            return True
        elif re.compile(r"^where are you\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/whereareyou.ogg"
            return True
        elif re.compile(r"^whistle\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/whistle.ogg"
            return True
        elif re.compile(r"^will be singing\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/WillBeSinging.ogg"
            return True
        elif re.compile(r"^wimbaway\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/wimbaway.ogg"
            return True
        elif re.compile(r"^windows\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/windows.ogg"
            return True
        elif re.compile(r"^would you like\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/wouldyoulike.ogg"
            return True
        elif re.compile(r"^wtf\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/wtf.ogg"
            return True
        elif re.compile(r"^yeee\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/yeee.ogg"
            return True
        elif re.compile(r"^yes master\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/yesmaster.ogg"
            return True
        elif re.compile(r"^yhehehe\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/yhehehe.ogg"
            return True
        elif re.compile(r"^ymca\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/ymca.ogg"
            return True
        elif re.compile(r"^you\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/You.ogg"
            return True
        elif re.compile(r"^you are a cunt\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/cunt.ogg"
            return True
        elif re.compile(r"^you fucked my wife\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/youfuckedmywife.ogg"
            return True
        elif re.compile(r"^you realise\W?$").match(msg_lower):
            self.soundFile ="sound/funnysounds/YouRealise.ogg"
            return True

        #Duke Nukem
        elif re.compile(r"^my ride\W?$").match(msg_lower):
            self.soundFile ="sound/duke/2ride06.wav"
            return True
        elif re.compile(r"^abort\W?$").match(msg_lower):
            self.soundFile ="sound/duke/abort01.wav"
            return True
        elif re.compile(r"^ahhh\W?$").match(msg_lower):
            self.soundFile ="sound/duke/ahh04.wav"
            return True
        elif re.compile(r"^much better\W?$").match(msg_lower):
            self.soundFile ="sound/duke/ahmuch03.wav"
            return True
        elif re.compile(r"^aisle 4\W?$").match(msg_lower):
            self.soundFile ="sound/duke/aisle402.wav"
            return True
        elif re.compile(r"^a mess\W?$").match(msg_lower):
            self.soundFile ="sound/duke/amess06.wav"
            return True
        elif re.compile(r"^annoying\W?$").match(msg_lower):
            self.soundFile ="sound/duke/annoy03.wav"
            return True
        elif re.compile(r"^bitchin\W?$").match(msg_lower):
            self.soundFile ="sound/duke/bitchn04.wav"
            return True
        elif re.compile(r"^blow it out\W?$").match(msg_lower):
            self.soundFile ="sound/duke/blowit01.wav"
            return True
        elif re.compile(r"^booby trap\W?$").match(msg_lower):
            self.soundFile ="sound/duke/booby04.wav"
            return True
        elif re.compile(r"^bookem\W?$").match(msg_lower):
            self.soundFile ="sound/duke/bookem03.wav"
            return True
        elif re.compile(r"^born to be wild\W?$").match(msg_lower):
            self.soundFile ="sound/duke/born01.wav"
            return True
        elif re.compile(r"^chew gum\W?$").match(msg_lower):
            self.soundFile ="sound/duke/chew05.wav"
            return True
        elif re.compile(r"^come on\W?$").match(msg_lower):
            self.soundFile ="sound/duke/comeon02.wav"
            return True
        elif re.compile(r"^the con\W?$").match(msg_lower):
            self.soundFile ="sound/duke/con03.wav"
            return True
        elif re.compile(r"^cool\W?$").match(msg_lower):
            self.soundFile ="sound/duke/cool01.wav"
            return True
        elif re.compile(r"^not crying\W?$").match(msg_lower):
            self.soundFile ="sound/duke/cry01.wav"
            return True
        elif re.compile(r"^daamn\W?$").match(msg_lower):
            self.soundFile ="sound/duke/damn03.wav"
            return True
        elif re.compile(r"^damit\W?$").match(msg_lower):
            self.soundFile ="sound/duke/damnit04.wav"
            return True
        elif re.compile(r"^dance\W?$").match(msg_lower):
            self.soundFile ="sound/duke/dance01.wav"
            return True
        elif re.compile(r"^diesob\W?$").match(msg_lower):
            self.soundFile ="sound/duke/diesob03.wav"
            return True
        elif re.compile(r"^doomed\W?$").match(msg_lower):
            self.soundFile ="sound/duke/doomed16.wav"
            return True
        elif re.compile(r"^eyye\W?$").match(msg_lower):
            self.soundFile ="sound/duke/dscrem38.wav"
            return True
        elif re.compile(r"^duke nukem\W?$").match(msg_lower):
            self.soundFile ="sound/duke/duknuk14.wav"
            return True
        elif re.compile(r"^no way\W?$").match(msg_lower):
            self.soundFile ="sound/duke/eat08.wav"
            return True
        elif re.compile(r"^eat shit\W?$").match(msg_lower):
            self.soundFile ="sound/duke/eatsht01.wav"
            return True
        elif re.compile(r"^escape\W?$").match(msg_lower):
            self.soundFile ="sound/duke/escape01.wav"
            return True
        elif re.compile(r"^face ass\W?$").match(msg_lower):
            self.soundFile ="sound/duke/face01.wav"
            return True
        elif re.compile(r"^a force\W?$").match(msg_lower):
            self.soundFile ="sound/duke/force01.wav"
            return True
        elif re.compile(r"^get that crap\W?$").match(msg_lower):
            self.soundFile ="sound/duke/getcrap1.wav"
            return True
        elif re.compile(r"^get some\W?$").match(msg_lower):
            self.soundFile ="sound/duke/getsom1a.wav"
            return True
        elif re.compile(r"^game over\W?$").match(msg_lower):
            self.soundFile ="sound/duke/gmeovr05.wav"
            return True
        elif re.compile(r"^gotta hurt\W?$").match(msg_lower):
            self.soundFile ="sound/duke/gothrt01.wav"
            return True
        elif re.compile(r"^groovy\W?$").match(msg_lower):
            self.soundFile ="sound/duke/groovy02.wav"
            return True
        elif re.compile(r"^you guys suck\W?$").match(msg_lower):
            self.soundFile ="sound/duke/guysuk01.wav"
            return True
        elif re.compile(r"^hail king\W?$").match(msg_lower):
            self.soundFile ="sound/duke/hail01.wav"
            return True
        elif re.compile(r"^shit happens\W?$").match(msg_lower):
            self.soundFile ="sound/duke/happen01.wav"
            return True
        elif re.compile(r"^holy cow\W?$").match(msg_lower):
            self.soundFile ="sound/duke/holycw01.wav"
            return True
        elif re.compile(r"^holy shit\W?$").match(msg_lower):
            self.soundFile ="sound/duke/holysh02.wav"
            return True
        elif re.compile(r"^im good\W?$").match(msg_lower):
            self.soundFile ="sound/duke/imgood12.wav"
            return True
        elif re.compile(r"^independence\W?$").match(msg_lower):
            self.soundFile ="sound/duke/indpnc01.wav"
            return True
        elif re.compile(r"^in hell\W?$").match(msg_lower):
            self.soundFile ="sound/duke/inhell01.wav"
            return True
        elif re.compile(r"^going in\W?$").match(msg_lower):
            self.soundFile ="sound/duke/introc.wav"
            return True
        elif re.compile(r"^dr jones\W?$").match(msg_lower):
            self.soundFile ="sound/duke/jones04.wav"
            return True
        elif re.compile(r"^kick your ass\W?$").match(msg_lower):
            self.soundFile ="sound/duke/kick01-i.wav"
            return True
        elif re.compile(r"^ktit\W?$").match(msg_lower):
            self.soundFile ="sound/duke/ktitx.wav"
            return True
        elif re.compile(r"^let god\W?$").match(msg_lower):
            self.soundFile ="sound/duke/letgod01.wav"
            return True
        elif re.compile(r"^lets rock\W?$").match(msg_lower):
            self.soundFile ="sound/duke/letsrk03.wav"
            return True
        elif re.compile(r"^lookin good\W?$").match(msg_lower):
            self.soundFile ="sound/duke/lookin01.wav"
            return True
        elif re.compile(r"^make my day\W?$").match(msg_lower):
            self.soundFile ="sound/duke/makeday1.wav"
            return True
        elif re.compile(r"^midevil\W?$").match(msg_lower):
            self.soundFile ="sound/duke/mdevl01.wav"
            return True
        elif re.compile(r"^my meat\W?$").match(msg_lower):
            self.soundFile ="sound/duke/meat04-n.wav"
            return True
        elif re.compile(r"^no time\W?$").match(msg_lower):
            self.soundFile ="sound/duke/myself3a.wav"
            return True
        elif re.compile(r"^i needed that\W?$").match(msg_lower):
            self.soundFile ="sound/duke/needed03.wav"
            return True
        elif re.compile(r"^nobody\W?$").match(msg_lower):
            self.soundFile ="sound/duke/nobody01.wav"
            return True
        elif re.compile(r"^only one\W?$").match(msg_lower):
            self.soundFile ="sound/duke/onlyon03.wav"
            return True
        elif re.compile(r"^my kinda party\W?$").match(msg_lower):
            self.soundFile ="sound/duke/party03.wav"
            return True
        elif re.compile(r"^gonna pay\W?$").match(msg_lower):
            self.soundFile ="sound/duke/pay02.wav"
            return True
        elif re.compile(r"^pisses me off\W?$").match(msg_lower):
            self.soundFile ="sound/duke/pisses01.wav"
            return True
        elif re.compile(r"^pissin me off\W?$").match(msg_lower):
            self.soundFile ="sound/duke/pissin01.wav"
            return True
        elif re.compile(r"^postal\W?$").match(msg_lower):
            self.soundFile ="sound/duke/postal01.wav"
            return True
        elif re.compile(r"^aintafraid\W?$").match(msg_lower):
            self.soundFile ="sound/duke/quake06.wav"
            return True
        elif re.compile(r"^r and r\W?$").match(msg_lower):
            self.soundFile ="sound/duke/r&r01.wav"
            return True
        elif re.compile(r"^ready for action\W?$").match(msg_lower):
            self.soundFile ="sound/duke/ready2a.wav"
            return True
        elif re.compile(r"^rip your head off\W?$").match(msg_lower):
            self.soundFile ="sound/duke/rip01.wav"
            return True
        elif re.compile(r"^rip em\W?$").match(msg_lower):
            self.soundFile ="sound/duke/ripem08.wav"
            return True
        elif re.compile(r"^rockin\W?$").match(msg_lower):
            self.soundFile ="sound/duke/rockin02.wav"
            return True
        elif re.compile(r"^shake it\W?$").match(msg_lower):
            self.soundFile ="sound/duke/shake2a.wav"
            return True
        elif re.compile(r"^slacker\W?$").match(msg_lower):
            self.soundFile ="sound/duke/slacker1.wav"
            return True
        elif re.compile(r"^smack dab\W?$").match(msg_lower):
            self.soundFile ="sound/duke/smack02.wav"
            return True
        elif re.compile(r"^so help me\W?$").match(msg_lower):
            self.soundFile ="sound/duke/sohelp02.wav"
            return True
        elif re.compile(r"^suck it down\W?$").match(msg_lower):
            self.soundFile ="sound/duke/sukit01.wav"
            return True
        elif re.compile(r"^terminated\W?$").match(msg_lower):
            self.soundFile ="sound/duke/termin01.wav"
            return True
        elif re.compile(r"^this sucks\W?$").match(msg_lower):
            self.soundFile ="sound/duke/thsuk13a.wav"
            return True
        elif re.compile(r"^vacation\W?$").match(msg_lower):
            self.soundFile ="sound/duke/vacatn01.wav"
            return True
        elif re.compile(r"^christmas\W?$").match(msg_lower):
            self.soundFile ="sound/duke/waitin03.wav"
            return True
        elif re.compile(r"^wants some\W?$").match(msg_lower):
            self.soundFile ="sound/duke/wansom4a.wav"
            return True
        elif re.compile(r"^you and me\W?$").match(msg_lower):
            self.soundFile ="sound/duke/whipyu01.wav"
            return True
        elif re.compile(r"^where\W?$").match(msg_lower):
            self.soundFile ="sound/duke/whrsit05.wav"
            return True
        elif re.compile(r"^yippie kai yay\W?$").match(msg_lower):
            self.soundFile ="sound/duke/yippie01.wav"
            return True
        elif re.compile(r"^bottle of jack\W?$").match(msg_lower):
            self.soundFile ="sound/duke/yohoho01.wav"
            return True
        elif re.compile(r"^long walk\W?$").match(msg_lower):
            self.soundFile ="sound/duke/yohoho09.wav"
            return True
        return False
