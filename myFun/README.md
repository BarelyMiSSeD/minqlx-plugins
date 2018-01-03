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
#Duke Nukem Voice Sound Pack for minqlx<br>
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

<b>Soundpacks</b>:<br>
<b>1)</b> The <b>Default</b> soundpack uses sounds that are already included in the Quake Live install.<br>
<b>2)</b> The <b>Prestige Worldwide Soundhonks</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=585892371">HERE</a>.<br>
<b>3)</b> The <b>Funny Sounds Pack for Minqlx</b> can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=620087103">HERE</a>.<br>
<b>4)</b> The <b>Duke Nukem Sounds</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=572453229">HERE</a>.<br>
<b>5)</b> The <b>Warp Sounds for Quake Live</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=1250689005">HERE</a>.<br>
<b>6)</b> The <b>West Coast Crew Sound</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=908031086">HERE</a>.<br>

The soundpacks are all enabled by default. Which soundpacks are enabled can be set.<br>
set qlx_funEnableSoundPacks "63"   : Enables all sound packs.<br>
<b>******  How to set which sound packs are enabled ******</b><br>
Add the values for each sound pack listed below and set that value to the qlx_funEnableSoundPacks in the same location as the rest of your minqlx cvar's.<br><br>
 ****Sound Pack Values****<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 1<br>
 Prestige Worldwide Soundhonks: 2<br>
 &nbsp;&nbsp;&nbsp;&nbsp;Funny Sounds Pack for Minqlx: 4<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Duke Nukem Sounds: 8<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Warp Sounds for Quake Live:  16<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;West Coast Crew Sound: 32<br>

 <b>Duke Nukem Soundpack Disabled EXAMPLE</b>: set qlx_funEnableSoundPacks "55"<br>

When a player issues the <b>!listsounds</b> command it wil list all of the sounds available on the server with
the sounds displayed in a tabbed format to help enable the redability of the sounds without requiring the use of pages or exessie scrolling. Only the soundpacks that are enabled will be shown. Any disabled soundpacks will not be displayed and will not
be searchable.<br>

If <b>!listsounds</b> is issued with a search term it will search for sounds that contain that term and diplay each enabled soundpack and the sounds found in them.<br>

Example: <b>!listsounds yeah</b> would list all the sound phrases containing 'yeah'<br>
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

If <b>!listsounds</b> is issued with a sound pack limiting value it will only search that soundpack for sounds.<br>
<b>!listsounds #Default</b> would only list the sounds in the Default soundpack, if it is enabled.<br>

Example: '<b>!listsounds #Default yeah</b>' would list all the sounds containing 'yeah' but limit that search to<br>
 just the Default sounds and produce the following output:<br>

SOUNDS: Type these words/phrases in normal chat to play a sound on the server.<br>
Default<br>
haha yeah haha      hahaha yeah      yeah hahaha      yeahhh<br>
4 SOUNDS: Type these words/phrases in normal chat to play a sound on the server.<br>
