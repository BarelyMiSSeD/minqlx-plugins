This is my replacement for the minqlx fun.py so if you use this file make sure not to load fun.py

This plugin plays sounds on the Quake Live server<br>
It plays the sounds included in fun.py and some from three other workshop items.<br>

This will limit sound spamming to the server.<br>
It only allows one sound to be played at a time and each user is limited in the frequency they can play sounds.<br>


To set the time required between sounds add this line to your server.cfg and edit the "5":<br>
<b>set qlx_funSoundDelay "5"</b>

To set the time a player has to wait after playing a sound add this like to your server.cfg and edit the "30":<br>
<b>set qlx_funPlayerSoundRepeat "30"</b>

To remove the individual sound repeat restriction from players with perm level 5 set this cvar to "1" the qlx_funSoundDelay restriction still applies:<br>
<b>set qlx_funUnrestrictAdmin "0"</b>


Three extra workshop items need to be loaded on the server for it to work correctly:<br>
#prestige worldwide sounds workshop<br>
585892371<br>
#Funny Sounds Pack for Minqlx<br>
620087103<br>
#Duke Nukem Sounds<br>
572453229<br>

The minqlx 'workshop' plugin needs to be loaded and the required workshop
 items added to the set qlx_workshopReferences line of your server.cfg
  (this example shows only these three required workshop items):
set qlx_workshopReferences "585892371, 620087103, 572453229"

Put the sound_names.txt file into the server's fs_homepath directory for
the !listsounds to work on the server.<br>
!listsounds can be issued by itself to see all the sounds that can be played on the server
or it can be issued with one argument to limit the listed sounds to the sound phrases that contain that argument.<br>
Example: '!listsounds yeah' would list all the sound phrases containing 'yeah'
 and would print this to the player's console (based on sound_names.txt at the time of this file creation):

SOUNDS: Type These words/phrases in normal chat to get a sound to play on the server.
haha yeah haha    hahaha yeah    yeah hahaha    yeahhh
4 SOUNDS: These are the sounds that work on this server.

If you edit the sound_names.txt put one sound phrase on each line and any line beginning with a # will be ignored
