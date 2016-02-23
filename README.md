# minqlx-plugins
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

Usage: !forcets <wanted teamsize>
   
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
<b>The following bot settings used in the protect script can be set with the rest of the minqlx bot settings:</b><br>

<b>set qlx_protectMapVoting “1”</b> - Enabling does not allow map voting during match play but does not affect map voting during warm-up<br>
<b>set qlx_protectAfkVoting “1”</b> - Enabling will allow players to be voted into spectator<br>
<b>set qlx_protectJoinMapMessage “1”</b> - Sends join message to players if map voting protection is enabled<br>
<b>set qlx_protectJoinAfkMessage “1”</b> - Sends join message to players if voting players to spectator is enabled<br>
<b>set qlx_protectPermissionLevel “5”</b> - Sets the lowest level bot permission level to  automatically protect. This means anyone with the set permission level or higher will be automatically protected from being kicked.<br>
<b>qlx_protectMuteVoting “1”</b> - Allows muting and unmuting of a player.<br>
<b>qlx_protectJoinMuteVoting “1”</b> - Sends join message to players if mute voting is enabled.<br>

# Voteban.py

I created this script to be able to ban the annoying players from voting on the server.

The vote ban is set with an expiration time, set a long time if you want it to be effectively permanent.

<br><br>
Commands available with voteban.py listed with the default permission levels

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
<b>The following bot settings used in the voteban script can be set with the rest of the minqlx bot settings:</b><br>
The settings are shown with the default settings. Edit them to change the permission levels or on/off status.<br>

<b>set qlx_votebanAdmin "5"</b> - Sets the permisson level needed to add and remove someones server voting privilage. Voting privilage can only be removed from players below the qlx_votebanProtectionLevel setting.<br>
<b>set qlx_votebanProtectionLevel "5"</b> - If the person being added to the vote ban list has this minqlx server permission level, they can't be added to the vote ban list.<br>
<b>set qlx_votebanVoteBan "1"</b> - Toruns on/off vote banning. Vote banning will remove voting privilages from a player on the server. (1 is on, 0 is off).<br>
