# databaseElo.py is a plugin for minqlx to:
# -Store player ELOs on the server in the event qlstats goes down.
# -This scripts command work like the normal commands you are used to
# - with elo usage, the commands with this script have a d before them like !delo
# -The script will store player's elo as they connect to the server.
# created by BarelyMiSSeD on 5-13-16
#

import minqlx
import requests
import re

VERSION = "1.04.1"
TEAM_BASED_GAMETYPES = ("ca", "ctf", "ft", "tdm")
ELO_GAMETYPES = ("duel", "ft", "tdm", "ca", "ctf", "ffa")
DEFAULT_ELO = 1200
MAX_ATTEMPTS = 3
ELO_KEY = "minqlx:players:{}:elo:{}:{}"


class databaseElo(minqlx.Plugin):
    def __init__(self):
        # queue cvars
        self.set_cvar_once("qlx_deloAdmin", "3")

        # Minqlx bot Hooks
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("vote_called", self.handle_vote_called)

        # Minqlx bot commands
        self.add_command("dversion", self.cmd_dbversion)
        self.add_command("delo", self.dbelo_cmd)
        self.add_command("delos", self.dbelos_cmd)
        self.add_command("dteams", self.dbteams_cmd)
        self.add_command("da", self.cmd_dbagree)
        self.add_command("do", self.cmd_dbdo, self.get_cvar("qlx_deloAdmin", int))
        self.add_command("setselo", self.cmd_set_dbelo, self.get_cvar("qlx_deloAdmin", int))
        self.add_command("getallelos", self.cmd_update_all_elos, self.get_cvar("qlx_deloAdmin", int))
        self.add_command("dbalance", self.cmd_dbbalance, self.get_cvar("qlx_deloAdmin", int))
        self.add_command(("delodict", "dbelos"), self.cmd_dbelodict, self.get_cvar("qlx_deloAdmin", int))
        self.add_command(("unload", "reload"), self.kill_script, 5)

        # Debugging Cmds
        self.add_command("selodb", self.show_elo_dict, 5)

        # Script Variables, Lists, and Dictionaries
        self._elo_dict = {}
        self._elo_b_dict = {}
        self.agreeing_players = None
        self.players_agree = [False, False]
        self.in_countdown = False
        self.attempts = 0

        # Initialize Commands
        self.cmd_update_all_elos()

    # ==============================================
    #               Event Handler's
    # ==============================================

    def handle_player_connect(self, player):
        @minqlx.thread
        def get_elo():
            sid = player.steam_id
            response = False
            url = "http://{}/elo/{}".format(self.get_cvar("qlx_balanceUrl"), sid)
            attempts = 0
            while attempts < MAX_ATTEMPTS:
                attempts += 1
                info = requests.get(url)
                if info.status_code != requests.codes.ok:
                    continue
                info_js = info.json()
                if "players" in info_js:
                    attempts = MAX_ATTEMPTS
                    response = True
            if response:
                for record in info_js["players"]:
                    self._elo_dict[str(sid)] = {}
                    for gt in ELO_GAMETYPES:
                        if gt in record:
                            score = record[str(gt)]["elo"]
                        else:
                            score = DEFAULT_ELO
                        self.db[ELO_KEY.format(int(sid), "elo", gt)] = int(score)
                        self._elo_dict[str(sid)][gt] = int(score)

            response = False
            url = "http://{}/elo_b/{}".format(self.get_cvar("qlx_balanceUrl"), sid)
            attempts = 0
            while attempts < MAX_ATTEMPTS:
                attempts += 1
                info = requests.get(url)
                if info.status_code != requests.codes.ok:
                    continue
                info_js = info.json()
                if "players" in info_js:
                    attempts = MAX_ATTEMPTS
                    response = True
            if response:
                for record in info_js["players"]:
                    self._elo_b_dict[str(sid)] = {}
                    for gt in ELO_GAMETYPES:
                        if gt in record:
                            score = record[str(gt)]["elo"]
                        else:
                            score = DEFAULT_ELO
                        self.db[ELO_KEY.format(int(sid), "elo_b", gt)] = int(score)
                        self._elo_b_dict[str(sid)][gt] = int(score)
        get_elo()

    def handle_player_disconnect(self, player, reason):
        if player.steam_id in self._elo_dict:
            del self._elo_dict[str(player.steam_id)]

    def handle_round_countdown(self, *args, **kwargs):
        if all(self.players_agree):
            # If we don't delay the switch a bit, the round countdown sound and
            # text disappears for some weird reason.
            @minqlx.next_frame
            def f():
                self.execute_switch()
            f()

        self.in_countdown = True

    def handle_round_start(self, *args, **kwargs):
        self.in_countdown = False

    def handle_vote_called(self, caller, vote, args):
        if vote.lower() == "dbalance":
            self.callvote("qlx !dbalance", "Balance Teams based on database stored ELOs?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL

    # ==============================================
    #               Minqlx Bot Commands
    # ==============================================

    def cmd_set_dbelo(self, player, msg, channel):
        gtype = self.game.type_short
        if gtype not in ELO_GAMETYPES:
            player.tell("^7This is not a supported ELO gametype.")
            return minqlx.RET_STOP_ALL
        if len(msg) < 3:
            player.tell("^7Usage: <player id> <rating>")
            return minqlx.RET_STOP_ALL
        try:
            pid = int(msg[1])
            rating = int(msg[2])
        except ValueError:
            player.tell("^1Invalid player ID or RATING.")
            return minqlx.RET_STOP_ALL
        if pid < 0 or pid > 63:
            player.tell("^1Invalid player ID")
            return minqlx.RET_STOP_ALL
        target_player = self.player(pid)
        if not target_player:
            player.tell("^1There is no player using that player ID.")
            return minqlx.RET_STOP_ALL
        if rating > 3000 or rating < 200:
            player.tell("^1Unreasonable player RATING.")
            return minqlx.RET_STOP_ALL
        elo = self.get_cvar("qlx_balanceApi")
        sid = target_player.steam_id
        self.db[ELO_KEY.format(sid, elo, gtype)] = rating
        if str(elo) == "elo":
            self._elo_dict[str(sid)][gtype] = int(rating)
        elif str(elo) == "elo_b":
            self._elo_b_dict[str(sid)][gtype] = int(rating)
        player.tell("^4Rating^7: The player {} ^7has been set to a {} rating of ^1{}^7 for game type {}."
                    .format(target_player, elo, rating, gtype))
        player.tell("The rating will be overwritten when the player next connects if the {} stats site responds."
                    .format(self.get_cvar("qlx_balanceUrl")))

    def dbelo_cmd(self, player, msg, channel):
        gtype = self.game.type_short
        rating = None
        if gtype in ELO_GAMETYPES:
            elo = self.get_cvar("qlx_balanceApi")
            if len(msg) > 1:
                try:
                    pid = int(msg[1])
                    player = self.player(pid)
                except minqlx.NonexistentPlayerError:
                    player.tell("Invalid client ID.")
                    return
                except ValueError:
                    player.tell("^3Use a valid player ID.")
                    return minqlx.RET_STOP_ALL
            try:
                if str(elo) == "elo":
                    rating = self._elo_dict[str(player.steam_id)][gtype]
                elif str(elo) == "elo_b":
                    rating = self._elo_b_dict[str(player.steam_id)][gtype]
            except:
                rating = self.db.get(ELO_KEY.format(player.steam_id, elo, gtype))
            if not rating:
                sid = player.steam_id
                response = False
                url = "http://{}/{}/{}".format(self.get_cvar("qlx_balanceUrl"), elo, sid)
                attempts = 0
                while attempts < MAX_ATTEMPTS:
                    attempts += 1
                    info = requests.get(url)
                    if info.status_code != requests.codes.ok:
                        continue
                    info_js = info.json()
                    if "players" in info_js:
                        attempts = MAX_ATTEMPTS
                        response = True
                if response:
                    for info in info_js["players"]:
                        if sid == int(info["steamid"]):
                            self.db[ELO_KEY.format(sid, elo, gtype)] = int(info[str(gtype)]["elo"])
                            if str(elo) == "elo":
                                self._elo_dict[str(info["steamid"])][gtype] = int(info[str(gtype)]["elo"])
                            elif str(elo) == "elo_b":
                                self._elo_b_dict[str(info["steamid"])][gtype] = int(info[str(gtype)]["elo"])
                            rating = int(info[str(gtype)]["elo"])
            if rating:
                try:
                    completed = int(self.db.get("minqlx:players:{}:games_completed".format(player.steam_id)))
                except:
                    completed = 0
                try:
                    left = int(self.db.get("minqlx:players:{}:games_left".format(player.steam_id)))
                except:
                    left = 0
                games_here = left + completed
                channel.reply("^7The ^3{}^7 {} for ^7{} ^7is ^2{} ^7(games here: ^6{}^7)"
                              .format(gtype, elo, player, rating, games_here))
            else:
                channel.reply("^7There is no stored ^3{} ^7{} for {}^7. A rating of ^6{} ^7will be used."
                              .format(gtype, elo, player, DEFAULT_ELO))

    @minqlx.thread
    def dbelos_cmd(self, player, msg, channel):
        gtype = self.game.type_short
        if gtype in ELO_GAMETYPES:
            elo = self.get_cvar("qlx_balanceApi")
            teams = self.teams()

            clients = len(teams["red"])
            if clients:
                t_dict = {}
                r_msg = []
                for p in teams["red"]:
                    try:
                        if str(elo) == "elo":
                            rating = self._elo_dict[str(p.steam_id)][gtype]
                        elif str(elo) == "elo_b":
                            rating = self._elo_b_dict[str(p.steam_id)][gtype]
                    except:
                        rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                    finally:
                        if not rating:
                            rating = DEFAULT_ELO
                    t_dict[str(p)] = rating
                r_dict = sorted(((v, k) for k, v in t_dict.items()), reverse=True)
                for k, v in r_dict:
                    r_msg.append("^7{}^7:^1{}^7".format(v, k))
                self.msg(", ".join(r_msg))

            clients = len(teams["blue"])
            if clients:
                t_dict = {}
                b_msg = []
                for p in teams["blue"]:
                    try:
                        if str(elo) == "elo":
                            rating = self._elo_dict[str(p.steam_id)][gtype]
                        elif str(elo) == "elo_b":
                            rating = self._elo_b_dict[str(p.steam_id)][gtype]
                    except:
                        rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                    finally:
                        if not rating:
                            rating = DEFAULT_ELO
                    t_dict[str(p)] = rating
                b_dict = sorted(((v, k) for k, v in t_dict.items()), reverse=True)
                for k, v in b_dict:
                    b_msg.append("^7{}^7:^4{}^7".format(v, k))
                self.msg(", ".join(b_msg))

            clients = len(teams["free"])
            if clients:
                t_dict = {}
                f_msg = []
                for p in teams["free"]:
                    try:
                        if str(elo) == "elo":
                            rating = self._elo_dict[str(p.steam_id)][gtype]
                        elif str(elo) == "elo_b":
                            rating = self._elo_b_dict[str(p.steam_id)][gtype]
                    except:
                        rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                    finally:
                        if not rating:
                            rating = DEFAULT_ELO
                    t_dict[str(p)] = rating
                f_dict = sorted(((v, k) for k, v in t_dict.items()), reverse=True)
                for k, v in f_dict:
                    f_msg.append("^7{}^7:^2{}^7".format(v, k))
                self.msg(", ".join(f_msg))

            clients = len(teams["spectator"])
            if clients:
                t_dict = {}
                s_msg = []
                for p in teams["spectator"]:
                    try:
                        if str(elo) == "elo":
                            rating = self._elo_dict[str(p.steam_id)][gtype]
                        elif str(elo) == "elo_b":
                            rating = self._elo_b_dict[str(p.steam_id)][gtype]
                    except:
                        rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                    finally:
                        if not rating:
                            rating = DEFAULT_ELO
                    t_dict[str(p)] = rating
                s_dict = sorted((v, k) for k, v in t_dict.items())
                for k, v in s_dict:
                    s_msg.append("^7{}^7:^3{}^7".format(v, k))
                self.msg(", ".join(s_msg))

        else:
            self.msg("^7The current ^2{} ^7gametype does not have player elo ratings.".format(gtype))

    @minqlx.thread
    def cmd_update_all_elos(self, player=None, msg=None, channel=None):
        sids = []
        for pl in self.players():
            sids.append(str(pl.steam_id))

        response = False
        url = "http://{}/{}/{}".format(self.get_cvar("qlx_balanceUrl"), "elo", "+".join(sids))
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            info = requests.get(url)
            if info.status_code != requests.codes.ok:
                continue
            info_js = info.json()
            if "players" in info_js:
                attempts = MAX_ATTEMPTS
                response = True
        if response:
            for record in info_js["players"]:
                self._elo_dict[str(record["steamid"])] = {}
                for gt in ELO_GAMETYPES:
                    if gt in record:
                        score = record[str(gt)]["elo"]
                    else:
                        score = DEFAULT_ELO
                    self.db[ELO_KEY.format(int(record["steamid"]), "elo", gt)] = int(score)
                    self._elo_dict[str(record["steamid"])][gt] = int(score)
            if player:
                player.tell("ELOs updated.")
        else:
            if player:
                player.tell("No response from {} for ELO request".format(self.get_cvar("qlx_balanceUrl")))

        response = False
        url = "http://{}/{}/{}".format(self.get_cvar("qlx_balanceUrl"), "elo_b", "+".join(sids))
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            info = requests.get(url)
            if info.status_code != requests.codes.ok:
                continue
            info_js = info.json()
            if "players" in info_js:
                attempts = MAX_ATTEMPTS
                response = True
        if response:
            for record in info_js["players"]:
                self._elo_b_dict[str(record["steamid"])] = {}
                for gt in ELO_GAMETYPES:
                    if gt in record:
                        score = record[str(gt)]["elo"]
                    else:
                        score = DEFAULT_ELO
                    self.db[ELO_KEY.format(int(record["steamid"]), "elo_b", gt)] = int(score)
                    self._elo_b_dict[str(record["steamid"])][gt] = int(score)
            if player:
                player.tell("ELO_Bs updated.")
        else:
            if player:
                player.tell("No response from {} for ELO_B request".format(self.get_cvar("qlx_balanceUrl")))

    @minqlx.thread
    def cmd_dbelodict(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3Usage: <Player_ID|Steam_ID>")
            return minqlx.RET_STOP_ALL

        try:
            pid = int(msg[1])
            if 0 <= pid <= 63:
                try:
                    target_player = self.player(pid)
                except minqlx.NonexistentPlayerError:
                    player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                    return minqlx.RET_STOP_EVENT
                if not target_player:
                    player.tell("^3Invalid client ID. Use either a client ID or a SteamID64.")
                    return minqlx.RET_STOP_EVENT
                pid = int(target_player.steam_id)
            elif pid < 0:
                player.tell("^3Usage: <Player_ID|Steam_ID>")
                return minqlx.RET_STOP_EVENT
            elif len(str(pid)) != 17:
                player.tell("^3The STEAM ID given needs to be 17 digits in length.")
                return minqlx.RET_STOP_EVENT
            else:
                target_player = self.player(pid)
        except ValueError:
            player.tell("^3Invalid ID. Use either a client ID or a SteamID64.")
            return minqlx.RET_STOP_EVENT

        elos = ["^7{} ^7:^4ELO^7:".format(target_player)]
        for gtype in ELO_GAMETYPES:
            elos.append(" ^4{}^7:^2{} ".format(gtype, self._elo_dict[str(pid)][gtype]))

        elos.append("\n^7{} ^7:^4ELO_B^7:".format(target_player))
        for gtype in ELO_GAMETYPES:
            elos.append(" ^4{}^7:^2{} ".format(gtype, self._elo_b_dict[str(pid)][gtype]))

        channel.reply("".join(elos))

    @minqlx.thread
    def dbteams_cmd(self, player, msg, channel):
        # Only allow one instance of the command to run
        gtype = self.game.type_short
        if gtype in TEAM_BASED_GAMETYPES and gtype in ELO_GAMETYPES:
            elo = self.get_cvar("qlx_balanceApi")
            teams = self.teams()
            red_clients = len(teams["red"])
            blue_clients = len(teams["blue"])
            red_team_elo = {}
            blue_team_elo = {}
            red_elo = 0
            blue_elo = 0

            if red_clients == 0 and blue_clients == 0:
                self.msg("^3The teams are empty of players.")
                return
            elif red_clients != blue_clients:
                self.msg("^3Both teams should have the same number of players.")
                return

            for client in teams["red"]:
                try:
                    if str(elo) == "elo":
                        rating = self._elo_dict[str(client.steam_id)][gtype]
                    elif str(elo) == "elo_b":
                        rating = self._elo_b_dict[str(client.steam_id)][gtype]
                except:
                    rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                if not rating:
                    rating = DEFAULT_ELO
                red_elo += rating
                red_team_elo[str(client)] = rating
            red_elo /= red_clients

            for client in teams["blue"]:
                try:
                    if str(elo) == "elo":
                        rating = self._elo_dict[str(client.steam_id)][gtype]
                    elif str(elo) == "elo_b":
                        rating = self._elo_b_dict[str(client.steam_id)][gtype]
                except:
                    rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                if not rating:
                    rating = DEFAULT_ELO
                blue_elo += rating
                blue_team_elo[str(client)] = rating
            blue_elo /= blue_clients

            message = ["^7Team Balance: ^1{} ^7vs. ^4{}".format(round(red_elo), round(blue_elo))]
            difference = round(red_elo) - round(blue_elo)
            if difference > 0:
                message.append(" ^7- Difference: ^1{}".format(difference))
            elif difference < 0:
                message.append(" ^7- Difference: ^4{}".format(abs(difference)))
            else:
                message.append(" ^7- ^2EVEN")
            self.msg("".join(message))

            min_suggestion = self.get_cvar("qlx_balanceMinimumSuggestionDiff", int)
            if abs(difference) >= min_suggestion:
                diff = 99999
                new_difference = 99999
                players = [None, None]
                for r in red_team_elo:
                    for b in blue_team_elo:
                        temp_r = red_team_elo.copy()
                        temp_b = blue_team_elo.copy()
                        temp_r[b] = temp_b[b]
                        temp_b[r] = temp_r[r]
                        del temp_r[r]
                        del temp_b[b]
                        avg_r = 0
                        for p in temp_r:
                            avg_r += temp_r[p]
                        avg_r /= red_clients
                        avg_b = 0
                        for p in temp_b:
                            avg_b += temp_b[p]
                        avg_b /= blue_clients
                        if abs(avg_r - avg_b) < diff:
                            new_difference = round(avg_r - avg_b)
                            diff = abs(avg_r - avg_b)
                            players = (r, b)

                if abs(new_difference) < abs(difference) and abs(difference) >= min_suggestion:
                    self.agreeing_players = (players[0], players[1])
                    self.players_agree = [False, False]
                    self.msg("^6Switch ^1::^7{}^1::^7<-> ^4::^7{}^4:: ^6{}sa ^7to agree."
                             .format(players[0], players[1], self.get_cvar("qlx_commandPrefix")))
                else:
                    self.msg("^6Teams look good.")
            else:
                self.msg("^6Teams look good.")
        else:
            channel.reply("^7This gametype is not a supported team-based ELO gametype.")

    def cmd_dbagree(self, player, msg, channel):
        """After the bot suggests a switch, players in question can use this to agree to the switch."""
        if self.agreeing_players and not all(self.players_agree):
            p1, p2 = self.agreeing_players
            if str(p1) == str(player):
                self.players_agree[0] = True
            elif str(p2) == str(player):
                self.players_agree[1] = True
            if all(self.players_agree):
                # If the game's in progress and we're not in the round countdown, wait for next round.
                if self.game.state == "in_progress" and not self.in_countdown:
                    self.msg("The players will be switched at the start of next round.")
                    return
                # Otherwise, switch right away.
                self.execute_switch()

    def cmd_dbversion(self, player, msg, channel):
        channel.reply("^7This server has installed ^2{0} version {1} by BarelyMiSSeD\n"
                      "https://github.com/BarelyMiSSeD/minqlx-plugins".format(self.__class__.__name__, VERSION))

    def cmd_dbdo(self, player, msg, channel):
        """Forces a suggested switch to be done."""
        if self.agreeing_players:
            self.execute_switch()

    def cmd_dbbalance(self, player, msg, channel):
        gtype = self.game.type_short
        if gtype in TEAM_BASED_GAMETYPES and gtype not in ELO_GAMETYPES:
            self.msg("This is not a team based gaemtype with elo ratings.")
            return
        elif gtype not in TEAM_BASED_GAMETYPES:
            self.msg("This is not a gaemtype supported by this balance function.")
            return
        elo = self.get_cvar("qlx_balanceApi")
        teams = self.teams()
        if len(teams["red"] + teams["blue"]) % 2 != 0:
            self.msg("The total number of players should be an even number.")
            return
        # Start out by evening out the number of players on each team.
        diff = len(teams["red"]) - len(teams["blue"])
        if abs(diff) > 1:
            if diff > 0:
                for i in range(diff - 1):
                    p = teams["red"].pop()
                    p.put("blue")
                    teams["blue"].append(p)
            elif diff < 0:
                for i in range(abs(diff) - 1):
                    p = teams["blue"].pop()
                    p.put("red")
                    teams["red"].append(p)
        # Start shuffling by looping through our suggestion function until
        # there are no more switches that can be done to improve teams.
        switch = self.suggest_switch(teams, gtype, elo)
        if switch:
            while switch:
                p1 = switch[0]
                p2 = switch[1]
                self.switch(p1, p2)
                teams["blue"].append(p1)
                teams["red"].append(p2)
                teams["blue"].remove(p2)
                teams["red"].remove(p1)
                switch = self.suggest_switch(teams, gtype, elo)
            avg_red = self.team_average(teams["red"], gtype, elo)
            avg_blue = self.team_average(teams["blue"], gtype, elo)
            message = ["^7Team Balance: ^1{} ^7vs. ^4{}".format(round(avg_red), round(avg_blue))]
            difference = round(avg_red - avg_blue)
            if difference > 0:
                message.append(" ^7- Difference: ^1{}".format(difference))
            elif difference < 0:
                message.append(" ^7- Difference: ^4{}".format(abs(difference)))
            else:
                message.append(" ^7- ^2EVEN")
            self.msg("".join(message))
        else:
            self.msg("^4Teams look good^1! ^7Nothing to balance.")

    def kill_script(self, player, msg, channel):
        if msg[1] == "storedElo":
            del self._elo_dict
            del self._elo_b_dict

    # ==============================================
    #               Script Commands
    # ==============================================

    def team_average(self, team, gtype, elo):
        """Calculates the average rating of a team."""
        avg = 0
        if team:
            if elo == "elo_b":
                for p in team:
                    try:
                        rating = self._elo_b_dict[str(p.steam_id)][gtype]
                    except:
                        rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                    if not rating:
                        rating = DEFAULT_ELO
                    avg += rating
            else:
                for p in team:
                    try:
                        rating = self._elo_dict[str(p.steam_id)][gtype]
                    except:
                        rating = self.db.get(ELO_KEY.format(p.steam_id, elo, gtype))
                    if not rating:
                        rating = DEFAULT_ELO
                    avg += rating
            avg /= len(team)
        return round(avg)

    def suggest_switch(self, teams, gtype, elo):
        red_elo = self.team_average(teams["red"], gtype, elo)
        blue_elo = self.team_average(teams["blue"], gtype, elo)
        difference = round(abs(red_elo - blue_elo))
        diff = 99999
        new_difference = 99999
        players = None
        for r in teams["red"]:
            for b in teams["blue"]:
                temp_r = teams["red"].copy()
                temp_b = teams["blue"].copy()
                temp_r.append(b)
                temp_b.append(r)
                temp_r.remove(r)
                temp_b.remove(b)
                avg_r = self.team_average(temp_r, gtype, elo)
                avg_b = self.team_average(temp_b, gtype, elo)
                if abs(avg_r - avg_b) < diff:
                    new_difference = round(abs(avg_r - avg_b))
                    diff = abs(avg_r - avg_b)
                    players = (r, b)
        if new_difference < difference:
            return players
        else:
            return None

    def return_elo(self, steam_id, gtype, elo_type):
        if len(str(steam_id)) != 17:
            return "Invalid Steam ID"
        if gtype not in ELO_GAMETYPES:
            return "No ELO for that gametype"
        if elo_type == "elo_b":
            try:
                rating = self._elo_b_dict[str(steam_id)][gtype]
            except:
                rating = self.db.get(ELO_KEY.format(steam_id, elo_type, gtype))
        else:
            try:
                rating = self._elo_dict[str(steam_id)][str(gtype)]
            except:
                rating = self.db.get(ELO_KEY.format(steam_id, elo_type, gtype))
        if not rating:
            rating = DEFAULT_ELO
        return rating

    # ==============================================
    #               Debug Commands
    # ==============================================

    def show_elo_dict(self, player, msg, channel):
        player.tell(str(self._elo_dict))
        player.tell(str(self._elo_b_dict))
        player.tell(str(self.teams()))
        player.tess(str(self.players()))
