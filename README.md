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
Clan tags must be spelled exactly like what you want to protect. Different colors are different tags as are caps and lowercase.

Usage: !act 'clan_tag'

<b>!dct</b> (alternatively !del_clantag)

Deletes a clan tag that you had protected.

Usage: !dct 'clan_tag'

<b>!ctl</b> (alternatively !listclanmembers or !list_clanmembers)

Lists clan tags added to your clan tag protection list.

Usage: !ctl

<b>!rlcm</b> (alternatively !reload_clanmembers or !load_clanmembers)

Reloads the clan members list and the protected clan tags list.

Usage: !rlcm

<b>!cmv</b> (alternatively !versionclanmembers or !version_clanmembers)

Checks to see if your server is running the latest version of the clanmembers.py plugin.

Usage: !cmv

<br><br>
<b>CVAR(s)</b>
<b>The following bot setting(s) used in the clanmembers script can be set with the rest of the minqlx bot settings:</b><br>
The setting(s) are shown with the default settings.<br>

<b>qlx_clanmembersAdmin "5"</b> - Sets the minqlx server permisson level needed to use the clanmembers.py admin commands.<br>

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
<b>set qlx_votebanVoteBan "1"</b> - Toruns on/off vote banning. Vote banning will remove voting privilages from a player on the server (1 is on, 0 is off).<br>

<br><br>
#InviteOnly.py

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
