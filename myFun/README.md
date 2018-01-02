This is my replacement for the minqlx fun.py so if you use this file make sure not to load fun.py<br>

This plugin plays sounds for players on the Quake Live server<br>
It plays the sounds included in fun.py and some from other workshop item sound packs.<br>

This can limit sound spamming to the server.<br>
It only allows one sound to be played at a time and each user is limited in the frequency they can play sounds.<br>
If you desire no restriction then set both of the 2 following cvars to "0".<br>
The default qlx_funSoundDelay setting will require 5 seconds from the start of any sound<br>
 before another sound can be played by anyone.<br>
The default qlx_funPlayerSoundRepeat setting will require 30 seconds from the start of a player called sound before<br>
 that player can call another sound.<br>

To set the time required between any sound add this line to your server.cfg and edit the "5":<br>
<b>set qlx_funSoundDelay "5"</b><br>

To set the time a player has to wait after playing a sound add this like to your server.cfg and edit the "30":<br>
<b>set qlx_funPlayerSoundRepeat "30"</b><br>


These extra workshop items need to be loaded on the server for it to work correctly if all sound packs are enabled:<br>
(put the workshop item numbers in your workshop.txt file)<br>
#Prestige Worldwide Soundhonks<br>
585892371<br>
#Funny Sounds Pack for Minqlx<br>
620087103<br>
#Duke Nukem Sounds<br>
572453229<br>
#Warp Sounds for Quake Live<br>
1250689005<br>
#West Coast Crew Sound<br>
908031086<br>

The minqlx 'workshop' plugin needs to be loaded and the required workshop<br>
 items added to the set qlx_workshopReferences line<br>
  (This example shows only these required workshop items):<br>
set qlx_workshopReferences "585892371, 620087103, 572453229, 1250689005, 908031086"<br>
  (Only include the sound pack workshop item numbers that you decide to enable on the server)<br>
  (The Default sounds use sounds already available as part of the Quake Live install)<br>

set qlx_funEnableSoundPacks "63"   : Enables all 5 sound packs.<br>
******  How to set which sound packs are enabled ******<br>
Add the values for each sound pack listed below and set that value<br>
 to the qlx_funEnableSoundPacks in the same location as the rest of<br>
 your minqlx cvar's.<br>
 ****Sound Pack Values****<br>
                              Default:  1<br>
        Prestige Worldwide Soundhonks:  2<br>
         Funny Sounds Pack for Minqlx:  4<br>
                    Duke Nukem Sounds:  8<br>
           Warp Sounds for Quake Live:  16<br>
                West Coast Crew Sound:  32<br>

   <b>Duke Nukem Soundpack Disabled Example</b>: set qlx_funEnableSoundPacks "55"<br>

!listsounds can be issued by itself to see all the sounds that can be played on the server<br>
or it can be issued with one argument to limit the listed sounds to the sound phrases that contain that argument.<br>

Example: '!listsounds yeah' would list all the sound phrases containing 'yeah'<br>
 and would print this to the player's console (assuming all sound packs are enabled):<br>

SOUNDS: Type these words/phrases in normal chat to play a sound on the server.<br>
Default<br>
haha yeah haha    hahaha yeah    yeah hahaha    yeahhh<br>
Prestige Worldwide Soundhonks<br>
No Matches<br>
Funny Sounds Pack for Minqlx<br>
No Matches<br>
Duke Nukem Sounds<br>
No Matches<br>
Warp Sounds for Quake Live<br>
No Matches<br>
West Coast Crew Sound<br>
No Matches<br>
4 SOUNDS: Type these words/phrases in normal chat to play a sound on the server.<br>

If !listsounds is issued with a sound pack limiting value it will only search that soundpack for sounds.<br>
 Another sound limiting argument can also be added to see the matching sounds in that sound pack.<br>

Example: '!listsounds #Default yeah' would list all the sounds containing 'yeah' but limit that search to<br>
 just the Default sounds and produce the following output:<br>

SOUNDS: Type these words/phrases in normal chat to play a sound on the server.<br>
Default<br>
haha yeah haha    hahaha yeah    yeah hahaha    yeahhh<br>
4 SOUNDS: Type these words/phrases in normal chat to play a sound on the server.<br>
