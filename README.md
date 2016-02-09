# minqlx-plugins
# Protect.py
Commands available with Protect.py listed with the set permission levels

•	Permission level 4

!forceteamsize (alternatively !forcets)
   Sets the teamsize to the desired level. Will put all players to spectate if there are more players on a team than the desired teamsize.\n
   Usage: ! forcets <wanted teamsize>
   
!unsetpass
   Removes the server join password.
   Usage: !unsetpass
   
•	Permission level 5

!protect
   Usage: !protect < add|del|check|list <player id> >



The following bot settings used in the protect script can be set with the rest of the minqlx bot settings:
set qlx_protectMapVoting “1” - Enabling does not allow map voting during match play but does not affect map voting during warm-up
set qlx_protectAfkVoting “1” - Enabling will allow players to be voted into spectator
set qlx_protectJoinMapMessage “1” - Sends join message to players if map voting protection is enabled
set qlx_protectJoinAfkMessage “1” - Sends join message to players if voting players to spectator is enabled
set qlx_protectPermissionLevel “5” - Sets the lowest level bot permission level to  automatically protect

