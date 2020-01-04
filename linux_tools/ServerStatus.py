# ServerStatus.py is a plugin for minqlx to:
# -Store the current player count into the redis database to be read by server_reboot.py
# created by BarelyMiSSeD on 1-4-2020
#

import minqlx

COUNT_KEY = "minqlx:connected"  # Must match CHECK_KEY in server_reboot.py  (should not need to edit)

VERSION = "1.1"


class ServerStatus(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_disconnect", self.handle_player_disconnect)

        self.save_count()

    def handle_player_loaded(self, player):
        self.save_count()
        return

    def handle_player_disconnect(self, player, reason):
        self.save_count()
        return

    @minqlx.delay(2)
    def save_count(self):
        connected_count = len(self.players())
        if connected_count < 0:
            connected_count = 0
        self.db.set(COUNT_KEY, connected_count)
