# specall.py is a plugin for minqlx to:
# -designed to put all players on the server into spectator
# -a desired teamsize can be included after the command to set a teamsize while putting all to spectator.
# created by BarelyMiSSeD on 2-29-16
#
"""
Set these cvar(s) in your server.cfg (or wherever you set your minqlx variables):
qlx_specallAdminLevel "5" - Sets the minqlx server permission level needed to put everyone into spectate.


Commands:
!specall (!allspec) : Puts everyone into spectate if the game has not started.
        If a number is inculded after the command the teamsize will be set to that value.
!specallforce (!forceallspec, !forcespecall): Puts everyone to spectate at any time.
        If a number is inculded after the command the teamsize will be set to that value.
!specallversion (!specall_version) : Checks the version number of the plugin and
        compares it to the version available for download.
"""

import minqlx
import requests

VERSION = "v1.4"


class specall(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_loaded", self.player_loaded)

        # Cvar(s).
        self.set_cvar_once("qlx_specallAdminLevel", "5")

        # Commands: permission level is set using some of the Cvars. See the Cvars descrition at the top of the file.
        self.add_command(("specall", "allspec"), self.cmd_specAll, int(self.get_cvar("qlx_specallAdminLevel")))
        self.add_command(("specallforce", "forceallspec", "forcespecall"), self.cmd_specAllForce, int(self.get_cvar("qlx_specallAdminLevel")))
        self.add_command(("specallversion", "specall_version"), self.specAll_version, int(self.get_cvar("qlx_specallAdminLevel")))

    # protect.py version checker. Thanks to iouonegirl for most of this section's code.
    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}.py".format(self.__class__.__name__)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^4Server: ^7Currently using  ^4BarelyMiSSeD^7's ^6{}^7 plugin ^1outdated^7"
                                  " version ^6{}^7. The latest version is ^6{}"
                                  .format(self.__class__.__name__, VERSION, line.decode()))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^4Server: ^7Currently using ^4BarelyMiSSeD^7's  latest ^6{}^7 plugin version ^6{}^7."
                                  .format(self.__class__.__name__, VERSION))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    try:
                        player.tell("^4Server: ^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and"
                                    " you're using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                        player.tell("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                    except Exception as e: minqlx.console_command("echo {}".format(e))
                return

    def specAll_version(self, player, msg, channel):
        self.check_version(channel=channel)

    # Player Join actions. Version checker.
    @minqlx.delay(4)
    def player_loaded(self, player):
        try:
            if player.steam_id == minqlx.owner() or \
                    self.db.has_permission(player, self.get_cvar("qlx_specallAdminLevel", int)):
                self.check_version(player=player)
        except:
            return

    # Forces everyone on the server to spectate.
    # If a teamsize is included after the command it will also set the teamsize.
    def cmd_specAll(self, player, msg, channel):

        if self.game.state == "in_progress":
            player.tell("^4Server: ^7There is a game in progress. To force everyone to spectator use the"
                        " ^1!specallforce ^7command")
            return minqlx.RET_STOP_EVENT

        try:
            wanted_teamsize = int(msg[1])
        except:
            if len(msg) > 1:
                player.tell("^4Server: ^7If a temasize was intended to be set please include an intelligible"
                            " teamsize in the command.")
            wanted_teamsize = int(0)

        teams = self.teams()

        for client in teams["red"]:
            client.put("spectator")
        for client in teams["blue"]:
            client.put("spectator")

        if wanted_teamsize:
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7, players were put to spectator to allow the change."
                     .format(wanted_teamsize))
            return minqlx.RET_STOP_EVENT

        self.msg("^4Server: ^7All players were put to spectator by a server admin.")
        return minqlx.RET_STOP_EVENT

    def cmd_specAllForce(self, player, msg, channel):
        try:
            wanted_teamsize = int(msg[1])
        except:
            if len(msg) > 1:
                player.tell("^4Server: ^7If a temasize was intended to be set please include an intelligible"
                            " teamsize in the command.")
            wanted_teamsize = int(0)

        teams = self.teams()

        for client in teams["red"]:
            client.put("spectator")
        for client in teams["blue"]:
            client.put("spectator")

        if wanted_teamsize:
            self.game.teamsize = wanted_teamsize
            self.msg("^4Server: ^7The teamsize was set to ^1{}^7, players were put to spectator to allow the change."
                     .format(wanted_teamsize))
            return minqlx.RET_STOP_EVENT
        self.msg("^4Server: ^7All players were put to spectator by a server admin.")
        return minqlx.RET_STOP_EVENT
