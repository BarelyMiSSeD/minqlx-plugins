# mapLimiter is a plugin for the minqlx bot to limit the maps and
# game types that can be voted for on a server.
#
# Created by BarelyMiSSeD 12/10/2017

"""
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
    # specify 1 map per line, mapname|factoryid
    # ex: aerowalk|ffa
    # see factories.txt for valid factory id values
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
"""

import minqlx

VERSION = 1.0

class mapLimiter(minqlx.Plugin):
    def __init__(self):
        # Cvars.
        self.set_cvar_once("qlx_mapLimiterFile", "baseq3/mappool.txt")

        # Minqlx Hooks
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)

        # Minqlx server commands
        self.add_command(("votablemaps", "votemaps", "allowedmaps", "mappool", "maps", "maplist"), self.voteable_maps)

        # Allowed maps dictionary with the allowed factories for each map
        self.allowed_maps = {}

        self.get_allowed_maps()
        self.unload_overlapping_commands()

    @minqlx.delay(1)
    def unload_overlapping_commands(self):
        try:
            essentials = minqlx.Plugin._loaded_plugins['essentials']
            remove_commands = set(['maps'])
            for cmd in essentials.commands.copy():
                if remove_commands.intersection(cmd.name):
                    essentials.remove_command(cmd.name, cmd.handler)
        except Exception as e:
            pass

    def handle_vote_called(self, caller, vote, args):
        vote = vote.lower()
        if vote == "map":
            #caller.tell("^3Map voting is not allowed during an active match")
            #minqlx.console_print(str(args))
            values = args.split(" ")
            if values[0] not in self.allowed_maps:
                caller.tell("^3That map is not votable on this server. Type ^1!maps ^3to see the allowed list.")
                return minqlx.RET_STOP_ALL
            if values[1] and values[1] not in self.allowed_maps[values[0]]:
                caller.tell("^1{0} ^3is not allowed on {1}. Type ^1!maps {1} ^3to see the allowed list."
                            .format(values[1], values[0]))
                return minqlx.RET_STOP_ALL


    def get_allowed_maps(self):
        self.allowed_maps.clear()
        try:
            f = open(self.get_cvar("qlx_mapLimiterFile"), 'r')
            lines = f.readlines()
            f.close()
        except IOError:
            channel.reply("^4Server^7: Map List ^1Not Available^7. Contact a server admin.")
            return
        lines.sort()
        for line in lines:
            if line.startswith("#"):
                continue
            map = line.split("|")
            map_name = map[0]
            game_type = map[1].strip("\n")
            if map_name in self.allowed_maps:
                self.allowed_maps[map_name].append(game_type)
            else:
                self.allowed_maps[map_name] = [game_type]

    @minqlx.thread
    def voteable_maps(self, player, msg, channel):
        title = ["^1MAPS: These are the ^3map ^4factories^1, not always the map name. Use these in a callvote.^7\n"]
        map_list = []
        type_list = []
        items = 0

        for map_name in self.allowed_maps:
            if len(msg) > 1 and msg[1] not in map_name:
                continue
            type_list.clear()
            if len(self.allowed_maps[map_name]):
                for type in self.allowed_maps[map_name]:
                    type_list.append(type)
            else:
                type_list.append("not restricted")
            map_list.append("^3{} ^4{}".format(map_name, ", ".join(type_list)))
            items += 1

        title.append("\n^2{} ^1MAPS: These are the map designations, not always the map name. Use these in a callvote."
                     .format(items))

        map_list.sort()

        list_lines = []
        for item in map_list:
            line = len(list_lines)
            line -= 1
            try:
                display_line = list_lines[line]
            except IndexError:
                display_line = ""
            part1, part2 = self.line_up(display_line, item)
            try:
                list_lines[line] = part1
            except IndexError:
                list_lines.append(part1)
            if part2:
                list_lines.append(part2)

        if "console" == channel:
            minqlx.console_print(title[0].strip("\n"))
            for line in list_lines:
                minqlx.console_print(line)
            minqlx.console_print(title[1].strip("\n"))
            return

        player.tell("{}{}{}".format(title[0], "\n".join(list_lines), title[1]))
        return

    def line_up(self, mapLine, addMap):
        length = len(mapLine)
        newLine = None
        if length == 0:
            line = addMap
        elif length < 15:
            line = mapLine + " " * (15 - length) + addMap
        elif length < 30:
            line = mapLine + " " * (30 - length) + addMap
        elif length < 45:
            line = mapLine + " " * (45 - length) + addMap
        elif length < 60:
            line = mapLine + " " * (60 - length) + addMap
        elif length < 75:
            line = mapLine + " " * (75 - length) + addMap
        else:
            line = mapLine
            newLine = addMap
        return line, newLine

