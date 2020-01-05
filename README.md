# minqlx-plugins

# getmap.py
Allows downloading and removing of maps to/from your QL server from within the server or from rcon. See the description at the top of the getmap.py 

# specqueue.py
<b>This is a queueing plugin for the minqlx admin bot.</b><br>
This plugin can be used alone or with the serverBDM.py plugin.<br>

This plugin is intended to help keep the game as enjoyable as possible,<br>
 without the hassles of people making teams uneven, or someone joining later than others,<br>
 but happening to hit the join button first and cutting in line when a play spot opens.<br>

The plugin will also attempt to keep team games even, when adding 2 players at once,<br>
 by putting players into the most appropriate team, based on team scores or player BDMs.<br>

This plugin will spectate people when teams are uneven. It will, by default settings,<br>
 first look at player times then player scores to determine who, on the team with more players,<br>
 gets put to spectate. When a player gets put to spectate they will automatically get put into the<br>
 queue at the beginning of the line.<br>

There is also the option to have the players in spectate for too long (set with qlx_queueMaxSpecTime)<br>
 to be kicked. This will only kick the player, not do any kind of ban, so the player can reconnect immediately.<br>
This feature will not kick people with permission levels at or above the qlx_queueAdmin level,<br>
 or people who are in the queue.<br>

Use the command '!fix' to fix a player that is shown as sarge and not seen as an enemy or a team mate.<br>
This will set each player's model the the model recorded when they joined the server.<br>

Read the top of the file to know how to set the required cvars for your server once the default values are not desired.<br>
There are a lot of settings to help server admins set up the server to better admin the server how they desire.<br>

<b>Commands:</b><br>
!q or !queue: displays the players currently in the queue<br>
!s or !specs: Displays the players currently set to spectate only<br>
!addqueue or !addq: puts a player into the next available queue slot<br>
!qversion or !qv: displays the queue version number<br>
!ignore: will ignore uneven teams for the next round start<br>
!latch <ignore|spec|setting>: will latch the ignore setting to the action included (setting tells current state)<br>
!fix <all>: sets all players models to what was recorded by the script when the player connected (sarge bug fix)<br>

# serverBDM.py
This script collects data on the players on the server and calculates a Basic Damage Metric (BDM) rating. It works for game types Clan Arena, Freeze Tag, Free For All, Capture The Flag, Instagib Capture the Flag, and Team Death Match.

The script will do balancing and switch recommendations.<br>
*** WARNING: If you use this with other scripts that use !teams or !balance when they are enabled in serverBDM the commands in the other scripts will be unloaded. (This includes the balance.py that comes with the minqlx bot)***<br>
This script, by default, will automatically the commands from the other scripts that use !teams or !balance. The actions can be turned on/off when desired.<br>
Initial player BDM will be set based on elo gotten from qlstats.net or from the default bdm cvar setting if qlstats does not respond<br>

Read the top of the file to know how to set the required cvars for your server once the default values are not desired.<br>

<b>Commands</b>

!bdmversion or !bdmv: displayes the script version in chat<br>
!bdm: displays the reqestors BDM in chat (can be used with ID number as well)<br>
!bdmhor !bdmhistory: displays the requstors BDM, Quit percentage and previous 5 BDM ratings.<br>
!bdms: displays the BDMs of the players on the server<br>
!bteams: analyzes the teams and recommends player swaps to better even the teams based on BDM<br>
!teams: (if enabled) will work just like !bteams<br>
!a: how players agree to the switch recommendation from !bteams<br>
!do: how a server admin forces the switch recommedation made by !bteams<br>
!bbalance: will balance the teams based on BDM<br>
!balance: (if enabled) will work just like !bbalance<br>
!setbdm: set a players BDM<br>

# commands.py
This script lists the loaded plugins and the commands available for each plugin.

CVARS<br>
//Server Config cvars<br>
//Set the permission level needed to list the commands<br>
set qlx_commandsAdmin "0"<br>
//Enable to show only the commands the calling player can use, disable to show all commands (0=disable, 1=enable)<br>
set qlx_commandsOnlyEligible "1"<br>


<b>Commands</b><br>
!plugins: displays the loaded plugins<br>
!lc or listcmds or listcommands: <plugin_name> will list the minqlx commands on the server an optional<br>
    plugin search limiter can be included<br>

# bots.py
This is a plugin for the minqlx admin bot.
This keeps the server populated with bots (up to the set number) and will kick a bot to replace with a human player when they join.
This is intended to give people a place to play even when no one else is playing.

NOTE: THIS SCRIPT IS WILL NOT WORK WITHOUT THE SPECQUEUE.PY SCRIPT ON THIS PAGE.

Read the top of the file to know how to set the required cvars for your server once the default values are not desired.<br>

# battleroyale.py
This is a plugin for the minqlx admin bot.
It makes a last man standing game style played in FFA with some default weapons.

NOTE: THIS SCRIPT IS NOT COMPATIBLE WITH ANY OTHER QUEUE SCRIPT.
        IT PERFORMS QUEUEING ACTIONS TO FACILITATE A LAST MAN STANDING GAME.

Read the top of the file to know how to set the required cvars for your server once the default values are not desired.<br>

Commands available with battleroyale.py:<br>
!q or !queue: displays the players currently in the queue<br>
!s or !specs: Displays the players currently set to spectate only<br>
!score: Displays current round win standings<br>
!rules: Displays an abbreviated description of the game rules<br>
!addqueue or !addq: puts a player into the next available queue slot<br>
!brversion or !brv: displays the battelroyale.py version number<br>
!restart: reloads the SETTINGS and loads the default map<br>
!gamestatus: Shows the current game win standings in SERVER CONSOLE<br>


# funwarmup.py
It modifies the game CVARs to make warmup time a little different and hopefully more fun.
Be careful modifying the setting too much. Too many projectiles needing to be kept track of
  by the server may result in server crashes. Use/Modify this at your own risk.

Read the top of the file to know how to set the required cvars for your server once the default values are not desired.<br>
<br>
<br><br>
Commands available with funwarmup.py listed with the set permission levels

<b>•	Permission level 3</b> (set with qlx_fwAdminLevel)

<b>!setfun</b>

If the server is in warmup this will enable the Fun Warmup Mode.

Usage: !setfun

<b>!unsetfun</b>

Turns off the Fun Warmup Mode.

Usage: !unsetfun


# mapmonitor.py
This is a script to monitor the server when a map changes. If the server boots everyone due to a bad
map it will change the map to the default map. It can also monitor for the server emptying out and change
to the default map.

set qlx_mmDefaultMap "almostlost ca"    //set the default map and factory type<br>
set qlx_mmCheckTime "60"                //The amount of time the script will check after a map change for a bad map<br>
set qlx_mmChangeWhenEmpty "1"           //Enable to change to default map when all players disconnect (1=enabled, 0=disabled)<br>
<br>
<b>Commands:</b><br>
!setfun<br>

# Protect.py

I created this plugin to allow server admins to put people on a list that would not allow them to be kicked from a server.

I also added the ability to vote players to spectator if they are AFK. I added that because I didn't want someone who can't be kicked to go AFK and get stuck taking up a play slot because he/she can't be kicked. It is used by "/cv afk 'player id'" in the console.

I get tired of people being in the server that are just annoying with their chat messages or talking. I added the ability for people to callvote MUTE players on the server. It is used with "/cv mute 'player id'" in the console. To callvote to unmute someone use "/cv unmute 'plyer id'". A player can't callvote to unmute themselves.

The script also stops map voting once a match has gone active. Voting maps during warm-up still works. I wanted a way to still allow voting during a match but to not allow voting different maps throughout the match because one or two people didn't like the map.

Join messages about the map voting and the use of voting people to spectator are displayed to players upon connect to the server. These messages can be disabled seperately so both, either, or no messages will be sent upon connect.

I received requests to be able to set a teamsize to any size, even it the teamsize you want is lower than the current teamsize actually on each team. With the <i>!forcets</i> command you can do just that.

See below for the command and cvars used with my protect script.

<br><br>
Commands available with protect.py listed with the set permission levels

<b>•	Permission level 4</b>

<b>!forceteamsize</b> (alternatively !forcets)

Sets the teamsize to the desired level. Will put all players to spectate if there are more players on a team than the desired teamsize.

Usage: !forcets \<wanted teamsize\>
   
<b>•	Permission level 5</b>

<b>!protect</b>

Usage: !protect 'add|del|check|list' 'player id|steam id'
   
<b>!setpass</b>

Sets the server join password.

Usage: !setpass 'password'
   
<b>!unsetpass</b>

Removes the server join password.

Usage: !unsetpass

<b>•	Permission level set with qlx_protectPermissionLevel</b>

<b>!protectversion</b>

Checks the current protect script version that is running against the version on the GitHub website.

Usage: !protectversion


<br><br>
<b>CVARs</b>
<b>The following bot settings used in the protect script can be set with the rest of the minqlx bot settings:</b><br>
Default settings are listed.<br>

<b>set qlx_protectMapVoting “1”</b> - Enabling does not allow map voting during match play but does not affect map voting during warm-up.  ("1" on, "0" off)<br>
<b>set qlx_protectAfkVoting “1”</b> - Enabling will allow players to be voted into spectator. ("1" on, "0" off)<br>
<b>set qlx_protectJoinMapMessage “1”</b> - Sends join message to players if map voting protection is enabled. ("1" on, "0" off)<br>
<b>set qlx_protectJoinAfkMessage “1”</b> - Sends join message to players if voting players to spectator is enabled. ("1" on, "0" off)<br>
<b>set qlx_protectPermissionLevel “5”</b> - Sets the lowest level bot permission level to  automatically protect. This means anyone with the set permission level or higher will be automatically protected from being kicked.<br>
<b>set qlx_protectMuteVoting “1”</b> - Allows voting muting and unmuting of a player. ("1" on, "0" off)<br>
<b>set qlx_protectJoinMuteVoting “1”</b> - Sends join message to players if mute voting is enabled. ("1" on, "0" off)<br>
<b>set qlx_protectAdminLevel "5"</b> - Sets the minqlx server permission level needed to add/del/list the protect list, and display the protect.py version number.<br>
<b>set qlx_protectPassLevel "5"</b> - Sets the minqlx server permission level needed to set/unset the server join password.<br>
<b>set qlx_protectFTS "5"</b> - Sets the minqlx server permisson level needed to force teamsize.<br>

<br><br>
# ClanMembers.py

This script was added to help admins manage who wears their clan's tag.

There is no need to load the clan.py script that comes with the minqlx bot if you are using this plugin, 
but it wont' hurt if you forget.

This works with players trying to set their tag on the server using the !clan command.

It does not protect if people are putting the tag in their steam name. You can ban them if they won't stop.

The protected tags can be stored as you want them to appear when you are listing the protected tags, so store them with colors and case settings of your choice.
If the TagColors and LetterCase CVARs are not enabled (set to "0" as is the default), then the colors and case you stored with the tag and that the
player is trying to add are ignored and just the lettering and punctuation is compared. (SO: <b>^2Tag</b> would equal <b>^3tAG</b> or <b>tag</b> or <b>^5tag</b> etc...).
Coloring and Letter Case can be enforced individually if only one of the CVARs is turned on.
<b>NOTE:</b> Remember that turning on the Color and Lettering CVARs will make tag enforcement color and/or lettering specific.

<br><br>
Commands available with clanmembers.py listed with the default settings

<b>•	Permission level 0</b>

<b>!clan</b> (alternatively !setclan)

Usage: !clan 'tag'

<b>•	Permission level 5</b>

<b>!acm</b> (alternatively !add_clanmember)

Adds a player to your clan member list which will allow them to set their clan tag to any of the protected tags.

Usage: !acm 'client_id|steam_id name'

<b>!dcm</b> (alternatively !del_clanmember or !remove_clanmember)

Removes a player from your clan member list.

Usage: !dcm 'client_id|steam_id'

<b>!cml</b> (alternatively !listclanmembers or !list_clanmembers)

Lists players added to your clan member list.

Usage: !cml

<b>!act</b> (alternatively !add_clantag)

Adds a clan tag that you want protected so only players on the clan member list can wear the tag on your server.

Usage: !act 'clan_tag'

<b>!dct</b> (alternatively !del_clantag)

Deletes a clan tag that you had protected.

Usage: !dct 'clan_tag'

<b>!ctl</b> (alternatively !listclantag or !listclantags)

Lists clan tags added to your clan tag protection list.

Usage: !ctl

<b>!rlcm</b> (alternatively !reload_clanmembers or !load_clanmembers)

Reloads the clan members list and the protected clan tags list.

Usage: !rlcm

<b>!cmv</b> (alternatively !clanmembersversion or !clanmembers_version)

Checks to see if your server is running the latest version of the clanmembers.py plugin.

Usage: !cmv

<br><br>
<b>CVAR(s)</b>
<b>The following bot setting(s) used in the clanmembers script can be set with the rest of the minqlx bot settings:</b><br>
The setting(s) are shown with the default settings.<br>

<b>set qlx_clanmembersAdmin "5"</b> - Sets the minqlx server permisson level needed to use the clanmembers.py admin commands.<br>
<b>set qlx_clanmembersTagColors "0"</b> - If on: Tag enforcement will check for exact color matching. If off: tag colors are ignored and only the text is compared. (0 = off, 1 = on)<br>
<b>set qlx_clanmembersLetterCase "0"</b> - If on: Tag enforcement will check for exact case matching. If off: upper/lower case is ignored. (0 = off, 1 = on)<br>
<b>set qlx_clanmembersCheckSteamName "1"</b> - Checks for clan tag(s) in player's steam name and renames the player without the clan tag. (0 = off, 1 = on)<br>
<br><br>

# Handicap.py

I created this script to be able to handicap people who join the server based on their ELO.
That means you could uncap your server and just have it auto handicap people as they join.
It will not let the client change their handicap without admin permission.

<br><br>
Commands available with handicap.py listed with the default settings

<b>•	Permission level 'qlx_handicapAdminLevel'</b>

<b>!handicap</b> (alternatively !handi)

Sets the players handicap on the server, overriding the handicap calculated by the script.
This setting is good until the player connects again.

Usage: !handicap 'clientID' 'number[1-100]'

<b>!handicapon</b> (alternatively !handion)

Turns on the handicap limiting of the script. Only useful after a !handicapoff.

Usage: !handicapon

<b>!handicapoff</b> (alternatively !handioff)

Turns off the handicap limiting of the script. Effective until server restart or script reload.

Usage: !handicapoff

<b>•	Permission level 0</b>

<b>!hversion</b>

Lists the script version running on the server.

Usage: !hversion

"""
The handicap given to players above the LOWER_ELO setting.
The severity of the handicap given can be adjusted by changing the UPPER_ELO setting.
Increase it to reduce the severity of the handicap and lower it to increase the severity.
It should not be lowered further than the highest ELO connected to the server.
****Adjust the LOWER_ELO to the level you want the script to start giving handicaps***
****Adjust the UPPER_ELO to adjust the amount of handicap it gives. The higher the UPPER_ELO***
****the less severe the handicap.***
<br>Edit the PING_ADJUSTMENT setting to set at what ping the adjustments for high ping will start.<br>
Edit the handicap.py file to change these settings.
"""

<br><br>
<b>CVARs</b>
<b>The following bot settings used in the voteban script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings. Edit them to change the permission levels or on/off status.<br>

<b>set qlx_handicapAdminLevel "3"</b> - Sets the minqlx server permisson level needed execute admin level minqlx script commands.<br>
<b>set qlx_handicapMsgPlayer "1"</b> - Turns on/off the server sending messages to players who have been handicapped by the server.<br>
<br><br>

# Voteban.py

I created this script to be able to ban the annoying players from voting on the server.

The vote ban is set with an expiration time, set a long time if you want it to be effectively permanent.

<br><br>
Commands available with voteban.py listed with the default settings

<b>•	Permission level 5</b>

<b>!voteban</b> (alternatively !vote_ban)

Bans a player from voting for the set time period.

Usage: !voteban 'clientID|steamID' 'number[0-9]' 'scale[seconds?|minutes?|hours?|days?|weeks?|months?|years?]' 'name'

<b>!voteunban</b> (alternatively !vote_unban)

Unbans a player from voting.

Usage: !voteunban 'clientID|steamID'

<b>!listvoteban</b> (alternatively !list_voteban)

Lists players in the vote ban list, even expired bans that have not been removed.

Usage: !listvoteban

<b>!votebanversion</b>

checks to see if the voteban.py is up to date and lists the version running on the server.

Usage: !votebanversion

<br><br>
<b>CVARs</b>
<b>The following bot settings used in the voteban script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings. Edit them to change the permission levels or on/off status.<br>

<b>set qlx_votebanAdmin "5"</b> - Sets the minqlx server permisson level needed to add and remove someones server voting privilage. Voting privilage can only be removed from players below the qlx_votebanProtectionLevel setting.<br>
<b>set qlx_votebanProtectionLevel "5"</b> - If the person being added to the vote ban list has this minqlx server permission level, they can't be added to the vote ban list.<br>
<b>set qlx_votebanVoteBan "1"</b> - Turns on/off vote banning. Vote banning will remove voting privilages from a player on the server (1 is on, 0 is off).<br>
<b>set qlx_votebanRedisStorage "0"</b> - Set to "1" if you would rather use the Redis database for tracking vote bans.<br>

<br><br>
# InviteOnly.py

This script was dut to a request I received that would allow you to have an invite only server that wouldn't reply on passwords that can be given to anyone.

The inviteonly.py script will allow an admin to add people to the invite only list which allows them to play on the server.

Anyone not on the invite only list will be kicked from the server or confined to spectator, depending on the script settings.

Players can be allowed to spectate for a settable amount of minutes (default is 3) to allow a server admin to easily add them to the invite only list
with the connected player's client id (goten from the !id command or the /players command).

The script can also be set to kick people not on the invite only list as soon as they connect to the server.

The permission level needed to admin the invite only list is settable. See the CVAR section below for instructions.

<br><br>
Commands available with inviteonly.py listed with the default settings

<b>•	Permission level 5</b>

<b>!add_inviteonly</b> (alternatively !addinviteonly or !aio)

Adds a player to the invite only list to allow them to play on the server.

Usage: !add_inviteonly 'player id|steam id' 'name'

<b>!del_inviteonly</b> (alternatively !delinviteonly or !dio)

Removes a player from the invite only list.

Usage: !del_inviteonly 'player id|steam id'

<b>!list_inviteonly</b> (alternatively !listinviteonly or !iol)

Lists players in the invite only list.

Usage: !list_inviteonly

<b>!reload_inviteonly</b> (alternatively !load_inviteonly)

Reloads the invite only list.

Usage: !reload_inviteonly

<b>!inviteonlyversion</b>

checks to see if the inviteonly.py is up to date and lists the version running on the server.

Usage: !inviteonlyversion

<br><br>
<b>CVARs</b>
<b>The following bot settings used in the inviteonly script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings.<br>

<b>set qlx_inviteonlyAdmin "5"</b> - Sets the minqlx server permisson level needed to add and remove someone to/from the invote only list.<br>
<b>set qlx_invoteonlyAllowSpectator "0"</b> - Set to "1" to allow spectators to remain on the server indefiniltely even when not on the invite only list  (1 is on, 0 is off).<br>
<b>set qlx_inviteonlySpectatorTime "3"</b> - Sets the amount of time (in minutes) a player can be a spectaror before being kicked if not on the invote only list.<br>
<i>Set qlx_invoteonlyAllowSpectator and qlx_inviteonlySpectatorTime to "0" to kick players immediately.</i><br>

<br><br>
# Kills.py

I created this script using mattiZed's pummel.py script located here: https://github.com/mattiZed/minqlx-plugins/blob/master/pummel.py.

<b><u>***IMPORTANT***</u></b> <i>This script is designed to use the same recording style as pummel.py. Do not run both of these scripts.
You won't lose any previously recorded pummel kills if you had pummel.py loaded.</i>

This script is meant to give the players a little more fun by having some extra goals to try for in the game.
It records any pummel/gauntlet kill, any direct grenade kill, any air rocket, and any air plasma kill. It records who you
killed and how any times you have killed that person and displays the ratio of your kills to your victims kills on you.

You can look at each of the recorded types of kills with the commands !pummel, !grenades, !rockets, !plasma.
These commands will show you a total kill amount you have for each kind of kill and your kill ratio against
any player connected to the server at the time.

There are also end of the match stats posted when the map ends. These stats are per-map stats, not lifetime stats like
the stats gotten with the above commands.

***NOTE*** To disable the sounds this script plays type !sounds
This uses the built-in minqlx sounds feature.

 ******  How to set which kill types are recorded ******
 Add the values for each type of kill listed below and set that value
  to the qlx_killsMonitorKillTypes in the same location as the rest of
  your minqlx cvar's.

****Kill Monitor Values****<br>
             Pummel:  1    (records any pummel/gauntlet kill)<br>
         Air Pummel:  2    (records any pummel/gauntlet kill where killer and victim are airborne)<br>
     Direct Grenade:  4    (records any kills with direct grenade hits)<br>
        Air Rockets:  8    (records any Air Rocket kills)<br>
         Air Plasma:  16   (records any Air Plasma kills)<br>
          Air Rails:  32   (records any Air Rails kills where both the killer and victim are airborne)<br>
           Telefrag:  64   (records any enemy telefrag)<br>
  Telefrag TeamKill:  128  (records any teamkill telefrag)<br>
         Speed Kill:  256  (records any kill when the killer is traveling over the set speed)<br>

 The Default value is 'set qlx_killsMonitorKillTypes "511"' which enables
  all the kill monitor types.

<br><br>
Commands available with kills.py

<b>•	Permission level 3</b>

<b>!kgt</b> (alternatively !killsgametype)

Shows your the gametype being currently played on the server for purposes
of adding the gametype to the supported gametypes.

Usage: !kgt

<b>•	Permission level 0</b>

<b>!pummel</b> (alternatively !gauntlet)

Shows your total pummel kills on the server and your kill ratio against any connected player.

Usage: !pummel

<b>!airgauntlet</b> (alternatively !airpummel)

Shows your total air gauntlet kills on the server and your kill ratio against any connected player.
This is achieved when both the killer and the victim are in the air during the gauntlet kill.

Usage: !airgauntlet

<b>!grenades</b> (alternatively !grenade)

Shows your total direct grenade kills on the server and your kill ratio against any connected player.
NOTE: The kill does not record if it is reported as a shrapnel kill.

Usage: !grenades

<b>!rockets</b> (alternatively !rocket)

Shows your total air rocket kills on the server and your kill ratio against any connected player.
NOTE: This kill type looks at how the server reports the kill. If it is a direct rocket kill and
      the victim is reported as in the air, the kill will record.

Usage: !rockets

<b>!plasma</b>

Shows your total air plasma kills on the server and your kill ratio against any connected player.
NOTE: This kill type looks at how the server reports the kill. If it is a direct plasma kill and
      the victim is reported as in the air, the kill will record.

Usage: !plasma

<b>!airrail</b> (alternatively !airrails)

Shows your total air rail kills on the server and your kill ratio against any connected player.
NOTE: This kill type looks at how the server reports the kill. If it is a rail kill where both
      the killer and the victim is reported as in the air, the kill will record.

Usage: !airrail

<b>!telefrag</b>

Shows your total telefrag kills on enemies on the server and your kill ratio against any connected player.

Usage: !telefrag

<b>!teamtelefrag</b> (alternatively !teamtele)

Shows your total telefrag kills on teammates on the server and your kill ratio against any connected player.

Usage: !teamtelefrag

<b>!speed</b> (alternatively !speedkill)

Shows your total speed kills on the server and your kill ratio against any connected player.

Usage: !speed

<b>!speedlimit</b>

Shows the minimum speed a player must be traveling when killing someone to record a speed kill.

Usage: !speedlimit

<br><br>
<b>CVAR(s)</b>
<b>The following bot settings used in the kills script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings.<br>

<b>set qlx_killsMonitorKillTypes "255"</b> Enables/Disables the kill monitor types. See **Kill Monitor Values** above.<br>
<b>set qlx_killsSpeedMinimum "800"</b> Sets the minimum speed needed to record a speed kill
<b>set qlx_killsPlaySounds "1"</b> Enables/Disables the sounds played when a monitored kill happens.<br>
                                   Players can individually turn off sounds with !sounds.<br>

<br><br>
# Listmaps.py

I created this script to be able to list all the maps loaded on the server.

This script creates a map list when the server starts, the plugin is reloaded, or the admin enters the '!getmaps' command.
The people on the server are able to use the '!listmaps' command to see all the maps loaded on the server.
If the command is used like '!listmaps \<search string\>' it will search for maps with the search string in the names.
Ex: '!listmaps ra3' will display all the maps with ra3 in the name.

<b>To use the !mapname function put the Map_Names.txt in the Map_Names folder in your /qlds (install directory).</b>

Whenever the maps loaded on the server change the admin needs to re-run the '!getmaps' command to update the list.

<br><br>
Commands available with listmaps.py listed with the default settings

<b>•	Permission level 4</b>

<b>!getmaps</b>

Creates a new map list based on the maps loaded on the server.

Usage: !getmaps

<b>•	Permission level 0</b>

<b>!listmaps</b> (alternatively !listmap)

Lists the maps available for play on the server.

Usage: !listmaps \<optional search string\>

<b>!mapname</b>

Lists the map's name if it is listed in the Map_Name.txt file.

Usage: !mapname \<map callvote name\>

<br><br>
<b>CVARs</b>
<b>The following bot settings used in the listmaps script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings. Edit them to change the permission levels.<br>

<b>set qlx_listmapsAdmin "4"</b> - Sets the minqlx server permisson level needed to admin the listmaps script (to use !getmaps).<br>
<b>set qlx_listmapsUser "0"</b> - Permission level needed to use !listmaps, which show the user the map list generated by the !getmaps command.<br>

<br><br>
# MapLimiter.py

I created this script to limit the maps that can be voted for on a server. It does the same type of thing that
setting qlx_enforceMappool '1'. 

I wrote it for the practice and because I wanted to make the players able to search for specific maps and I wanted it listed more compactly.

By default the maps in the baseq3/mappool.txt will be used.
Set the qlx_mapLimiterFile cvar to point to a different file.
EXAMPLE:
    set qlx_mapLimiterFile "baseq3/myMapPool.txt"

The script will look in the qlds folder, so if you want to use the same map pool
file for this script as you are using for your server for map voting at the end of the
match, you need to point it to the baseq3 folder as the EXAMPLE shows.

The file used must be formatted the same way as the map pool files are for the Quake Live server.
That is one map and factory per line. map|factory

EXAMPLE:
    #specify 1 map per line, mapname|factoryid
    #ex: aerowalk|ffa
    #see factories.txt for valid factory id values
    almostlost|ffa
    almostlost|ca
    arcanecitadel|tdm
    arkinholm|tdm
    asylum|ffa
    asylum|ca
    basesiege|ctf
    beyondreality|ctf
    bitterembrace|ffa
    blackcathedral|ca
    blackcathedral|dom
    brimstoneabbey|ffa
    brimstoneabbey|ca
    brimstoneabbey|dom

As the example shows, if you want more than one game type to be allowed per map then list the map on
multiple lines with a different game type on each line.

<b>•	Permission level 0</b>

<b>!maps</b> (alternatively !votablemaps, !votemaps, !allowedmaps, !mappool, !maplist)

Lists the maps available for play on the server.

Usage: !maps \<optional search string\>

<br><br>
<b>CVARs</b>
<b>The following bot settings used in the mapLimiter script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings. Edit them to change the permission levels.<br>

<b>set qlx_mapLimiterFile "baseq3/mappool.txt"</b> - The file pointed to for map vote limiting.<br>


<br><br>
# Specall.py

This script was added to help admins running pickup games.

When the time to start picking teams arrives it can be hard to get everyone to go to spectator so the process can start. This script will put everyone to spectate wth a single command.

If the command is followed by a teamsize, the teamsize will be set to the desired size when everyone is put to spectator.

<br><br>
Commands available with specall.py listed with the default settings

<b>•	Permission level 5</b>

<b>!specall</b> (alternatively !allspec)

Puts all players to spectator. Include teamsize if you also want to set/change the teamsize (teamsize is not required). This command will not work during an active match.

Usage: !specall 'teamsize'

<b>!forcespecall</b> (alternatively !forceallspec or !specallforce)

Puts all players to spectator. Include teamsize if you also want to set/change the teamsize (teamsize is not required). This command will work at any time, use with caution.

Usage: !forcespecall 'teamsize'

<b>!v_specall</b> (alternatively !versionspecall)

Checks to see if the current released version of specall.py is running on the server.

Usage: !v_specall

<br><br>
<b>CVAR(s)</b>
<b>The following bot setting(s) used in the specall script can be set with the rest of the minqlx bot settings:</b><br>
The setting(s) are shown with the default settings.<br>

<b>qlx_specallAdminLevel "5"</b> - Sets the minqlx server permisson level needed to use the specall.py commands.<br>

<br><br>
# Voicechat.py

I created this script to allow players to set the server to Global or Team voichat through a callvote.

<br><br>
Commands available with voicechat.py listed with the default settings

<b>•	Permission level 5</b>

<b>!gvoice</b> (alternatively !globalvoice)

Sets server voicechat to GLOBAL chat.

Usage: !gvoice

<b>!tvoice</b> (alternatively !teamvoice)

Sets server voicechat to TEAM chat.

Usage: !tvoice

<b>!voicechat_version</b> (alternatively !voicechatversion)

Checks to see if the voicechat.py is up to date and lists the version running on the server.

Usage: !voicechat_version

<b>!voicechat_status</b> (alternatively !status or !settings)

Checks to see if the server is set to GLOBAL or TEAM voice chat.

Usage: !voicechat_status

<b>•	Permission level 0</b>

<b>!voicechat</b>

Gives the player the instructions to use the callvote voichat commands and
checks to see if the server is set to GLOBAL or TEAM voice chat.

Usage: !voicechat

<br><br>
<b>CVARs</b>
<b>The following bot settings used in the voicechat script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings. Edit them to change the permission levels or on/off status.<br>

<b>set qlx_voicechatAdminLevel "5"</b> - Sets the minqlx server permisson level needed to use the admin level commands in this script.<br>
<b>set qlx_voicechatVoiceChatVoting "1"</b> - Set to "1" to allow players to vote for changing the voice chat option to team/global.<br>
<b>set qlx_voicechatJoinMessage "1"</b> - Set to "1" to display the script join message to connecting players.<br>

<br><br>
# votelimiter.py

I created this script to keep people from callvoting stupid votes and votes that mess up the server but the admin hadn't thought about. This script will keep people from being able to callvote something that has not been added to the Allowed Vote List.<br>
This will stop any vote type, if enabled, that is not in the allowed vote list.<br>
This will also count the amount of votes people make and will limit it to the valuer set with "qlx_votelimiterLimit".
Quake Live has an included vote limiting feature that works well until the map changes, like in a callvote (map), then the Quake Live vote count resets. This script will keep that count until a game/match ends.<br><br>

By default the following votes are allowed:<br>
kick<br>
clientkick<br>
map<br>
teamsize<br>
cointoss<br>
shuffle<br>
map_restart<br>
<b>NOTE</b>: Use !dv \<vote\> to remove any of the default vote types if they aren't wanted. This should only need to be done the first time the script is loaded on a server.
<br><br>
Commands available with votelimiter.py listed with the default settings

<b>•	Permission level 0</b>

<b>Callvote</b>

Players can use '/cv voteban \<player name/id\>' to ban a player from being able to vote.
The player is maintianed on the list until the plyer disconnects or the server is restarted.

Usage: '/cv voteban \<player name/id\>' in console

<b>!voteslist</b> (alternatively !listvotes or !votes)

Shows the votes that the script will allow.

Usage: !voteslist

<b>•	Permission level 'qlx_votelimiterAdmin'</b>

<b>!addvote</b> (alternatively !allowvote or !av)

Adds votes to the allowed vote type list.

Usage: !addvote \<vote\>

<b>!delvote</b> (alternatively !deletevote or !dv)

Removes votes from the allowed vote type list.

Usage: !delvote \<vote\>

<b>!reload_voteslist</b> (alternatively !load_votelist or !rvl)

Reloads the vote type allowed list from the votelimiter file. Useful if the file was edited manually.

Usage: !reload_voteslist

<b>!versionvotelimiter</b> (alternatively !version_votelimiter or !vlv)

Checks to see if the votelimiter.py is up to date and lists the version running on the server.

Usage: !versionvotelimiter

<b>!unvoteban</b>

Removes a player from the votelimiter voteban list.
This voteban list only maintains a player on the list until the player disconnects ro the server is restarted.

Usage: !unvoteban \<id\>

<b>!addvoteban</b>

Adds a player to the votelimiter voteban list.
This voteban list only maintains a player on the list until the player disconnects ro the server is restarted.

Usage: !addvoteban \<id\>

<b>!votebanlist</b>

Lists the players on the votelimiter voteban list.

Usage: !votebanlist \<vote\>
<br><br>
<b>CVARs</b>
<b>The following bot settings used in the votelimiter script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings. Edit them to change the permission levels or on/off status.<br>

<b>set qlx_votelimiterAdmin "5"</b> - Sets the minqlx server permisson level needed to use the admin level commands in this script.<br>
<b>set qlx_votelimiterLimit "5"</b> - Sets the amount of votes each player is allowed to call before the end of a game/match<br>
                            This count will carry through map changes. The built in limiter for Quake Live resets
                            on map changes.<br>
<b>set qlx_votelimiterTypes "1"</b> - Enable/Disable the restricting of vote types ("1" = Enable, "0" = Disable)<br>
