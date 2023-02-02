# *** This is my replacement for the minqlx fun.py so if you use this file make sure not to load fun.py ***<br>

This plugin plays sounds for players on the Quake Live server<br>
It plays the sounds included in fun.py and some from other workshop item sound packs.<br>

This can limit sound spamming to the server.<br>
It only allows one sound to be played at a time and each user is limited in the frequency they can play sounds.<br>
If you desire no restriction then set both of the 2 following cvars to "0".<br>
The default qlx_funSoundDelay setting will require 5 seconds from the start of any sound<br>
before another sound can be played by anyone.<br>
The default qlx_funPlayerSoundRepeat setting will require 30 seconds from the start of a player called sound before<br>
that player can call another sound.<br>

#To set the time required between any sound add this line to your server.cfg and edit the "5":<br>
set qlx_funSoundDelay "5"<br>

#To set the time a player has to wait after playing a sound add this like to your server.cfg and edit the "30":<br>
set qlx_funPlayerSoundRepeat "30"<br>

#Play Join Sound when players connect (set to "path/file" like below example to play sound)<br>
#*** Disable the MOTD sound to use this with set qlx_motdSound "0" ****<br>
set qlx_funJoinSound "sound/feedback/welcome_02.wav"<br>

#Play Join Sound even if players have sounds disabled<br>
set qlx_funJoinSoundForEveryone "0"<br>

#Play Join Sound on every map change (set to "1" to play join sound every map change)<br>
set qlx_funJoinSoundEveryMap "0"<br>

#Join sound path/file<br>
set qlx_funJoinSound "sound/feedback/welcome_02.wav"<br>

#Play Sound when last 2 players alive (should set to "3" to play sounds always)<br>
#0 = don't play sound for anyone when the last 2 (or  1 on either team of a team based game) remains<br>
#1 = play sound for all except those alive when the last 2 (or  1 on either team of a team based game) remains<br>
#2 = only play sounds for people who are dead/spectating when game is active<br>
#3 = play sound for everyone with sounds enabled<br>
set qlx_funLast2Sound "3"<br>

#Enable to use a dictionary to store sounds, faster responses to trigger text (0=disable, 1=enable)
#Enabling will cause the server to use more memory, only enable if memory is available.
#Must be enabled on server startup or it will not work.
set qlx_funFastSoundLookup "0"<br>


#These extra workshop items need to be loaded on the server for it to work correctly if all sound packs are enabled:<br>
#(put the workshop item numbers in your workshop.txt file)<br>
#Prestige Worldwide Soundhonks<br>
585892371<br>
#Funny Sounds Pack for Minqlx<br>
620087103<br>
#Duke Nukem Voice Sound Pack for minqlx<br>
572453229<br>
#Warp Sounds for Quake Live<br>
1250689005<br>
#West Coast Crew Sound<br>
1733859113<br>

#The minqlx 'workshop' plugin needs to be loaded and the required workshop<br>
#items added to the set qlx_workshopReferences line<br>
#(This example shows only these required workshop items):<br>
set qlx_workshopReferences "585892371, 620087103, 572453229, 1250689005, 908031086"<br>
#(Only include the sound pack workshop item numbers that you decide to enable on the server)<br>
#(The Default sounds use sounds already available as part of the Quake Live install)<br>

<b>Soundpacks</b>:<br>
<b>1)</b> The <b>Default</b> soundpack uses sounds that are already included in the Quake Live install.<br>
<b>2)</b> The <b>Prestige Worldwide Soundhonks</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=585892371">HERE</a>.<br>
<b>3)</b> The <b>Funny Sounds Pack for Minqlx</b> can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=620087103">HERE</a>.<br>
<b>4)</b> The <b>Duke Nukem Voice Sound Pack for minqlx</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=572453229">HERE</a>.<br>
<b>5)</b> The <b>Warp Sounds for Quake Live</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=1250689005">HERE</a>.<br>
<b>6)</b> The <b>West Coast Crew Sound</b> soundpack can be seen <a href="http://steamcommunity.com/sharedfiles/filedetails/?id=1733859113">HERE</a>.<br>

The soundpacks are all enabled by default. Which soundpacks are enabled can be set.<br>
set qlx_funEnableSoundPacks "63"   : Enables all sound packs.<br>
<b>******  How to set which sound packs are enabled ******</b><br>
Add the values for each sound pack listed below and set that value to the qlx_funEnableSoundPacks in the same location as the rest of your minqlx cvar's.<br><br>
**** Sound Pack Values ****<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Default: 1<br>
 Prestige Worldwide Soundhonks: 2<br>
 &nbsp;&nbsp;&nbsp;&nbsp;Funny Sounds Pack for Minqlx: 4<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Duke Nukem Voice Sound Pack for minqlx: 8<br>
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
Duke Nukem Voice Sound Pack for minqlx<br>
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


########################################################################################
#    Adding Additional Sound Packs
########################################################################################<br>
***** To add new sound packs without editing this file "much" *****<br>
Sound Pack File Requirements:<br>
The sound file names will use a sound trigger based on the file name. The sound file name will replace<br>
 underscores (_) with spaces or insert spaces after words starting with a capital letter.<br>
 The path inside the sound_pack.pk3 is not used to generate the sound trigger, only the sound file name.<br>
 I.E. The sound 'sound/warp/bend_me_over.ogg' will create the sound trigger 'bend me over'.<br>
      The sound 'sound/warp/BendMeOver.ogg' will also create the sound trigger 'bend me over'.<br>
 *** Note: These are the only 2 formats that will be correctly interpreted. I.E. 'sound/warp/bendMeOver.ogg' will not<br>
     generate the full sound trigger correctly.<br>
 *** NOTE: The name of the sound pack file stored in the baseq3 directory of the server does not have to match the<br>
     name of the sound pack file in the steam workshop. As long as the contents of the file are exactly the same.<br>
     You can rename the file stored in the baseq3 to whatever you want the sound pack called, ending it with<br>
     the .pk3 file extension. Use underscores for spaces in the sound pack name. (i.e. My_Enjoyable_Sounds.pk3 will be<br>
     shown as the sound pack 'My Enjoyable Sounds'.<br>
<br>
1) put the <sound_pack.pk3> file into the baseq3 directory of the server.<br>
    The baseq3 sub-directory stored in the cvar fs_basepath.<br>
2) add the <sound_pack.pk3> file name to the ADDITIONAL_SOUNDPACKS below with the format<br>
    ADDITIONAL_SOUNDPACKS = ['sound_pack.pk3', 'sound_pack_2.pk3', 'sound_pack_3.pk3']<br>
3) add the steam workshop item number to the qlx_workshopReferences cvar in the server.cfg<br>
    set qlx_workshopReferences "585892371, 620087103, 572453229, 1250689005, 1733859113, <new workshop item number>"<br>
<br>
The sound pack will be added starting at the end of the list, as sound pack 6 if nothing else was edited in the file.<br>
Any sound pack added here will automatically be enabled.<br>


# Commands
<br><br>
Commands available with myFun.py listed with the set permission levels.

<b>•	Permission level 0</b>

<b>!listsounds</b> (alternatively !ls)

Retrieves the sounds available to lay on the server.<br>
The command can be issued with optional search parameters:<br>
!listsounds \<#Category\> \<search string\><br>
The user can include one or both of the optional search parameters to narrow the search results.

Usage: !listsounds \<#Category\> \<search string\>

<b>!off</b> (alternatively !soundoff)

Disables the just played sound for the player issuing the command.<br>
The command can be issued with optional disable parameters:<br>
!off \<sound trigger\><br>
The user can include a sound trigger to disable the sound that is called with that sound trigger.
Use !listsounds to find the sound trigger desired.<br>

Usage: !off \<sound trigger\>

<b>!on</b> (alternatively !soundon)

Re-enables the just played sound for the player issuing the command.<br>
The command can be issued with optional disable parameters:<br>
!on \<sound trigger\><br>
The user can include a sound trigger to re-enable the sound that is called with that sound trigger.
Use !listsounds to find the sound trigger desired.<br>

Usage: !on \<sound trigger\>

<b>!offlist</b> (alternatively !soundofflist)

Shows the sounds to the player that that player has disabled.<br>

Usage: !offlist

<b>!cookies</b>

Randomly returns one of a few funny responses.

Usage: !cookies

<b>•	Permission level 3</b>

<b>!playsound</b> (alternatively !ps or !sound)

Plays a sound on the server for all the players with sounds enabled.<br>
This does not use the sound anti-spam function.

Usage: !playsound \<sound_path/file\>

<b>!listtriggers</b> (alternatively !lt)

Lists the custom sound trigers that have been added for the sound.

Usage: !listtriggers \<sound trigger\>

<b>•	Permission level 5</b>

These 2 commands will reset the enabled sounds to the qlx_funEnableSoundPacks cvar and reload the sounds dictionaries.
This erases the sound triggers in the Redis database. The Redis database is controlled by an ouside process,
so the execution of the filldb command should not be immediately after the erasedb command (wait a couple of seconds is all).

Usage: !erasedb<br>
Usage: !filldb

<b>!disablesound</b> (alternatively !ds)

Disables a specific sound on the server.<br>
!disablesound \<sound trigger\><br>
The command must include a sound trigger to disable the sound that is called with that sound trigger.
Use !listsounds to find the sound trigger desired.<br>

Usage: !disablesound \<sound trigger\><br>

<b>!enablesound</b> (alternatively !es)

Re-enables a specific sound on the server.<br>
!enablesound \<sound trigger\><br>
The command must include a sound trigger to re-enable the sound that is called with that sound trigger.
Use !listsounds to find the sound trigger desired.<br>

Usage: !enablesound \<sound trigger\><br>

<b>!listdisabled</b> (alternatively !ld)

Shows the sounds to the player that are disabled on the server.<br>

Usage: !listdisabled

<b>!addtrigger</b> (alternatively !at)

Adds the desired trigger to the custom sound triggers. The default trigger and cutom trigger must be seperated by an = sign.<br>

Usage: !addtrigger \<default trigger\> = \<add trigger\>

<b>!deltrigger</b> (alternatively !dt)

Removes the desired trigger from the custom sound triggers. The default trigger and cutom trigger must be seperated by an = sign.

Usage: !deltrigger \<default trigger\> = \<del trigger\>

<b>!adminlevel</b>

Sets the admin level for playing un-restricted sounds.

Usage: !adminlevel <perms_level>

<b>!restrictadmin</b>

Set the admin play sounds restriction level.<br>
0-Restricted like all players; 1-Unrestricted for player time limits only; 2-Unrestricted from any time limit.

Usage: !restrictadmin <0/1/2>


<br><br>

# CVARs

Read the top section of the myFun.py file
