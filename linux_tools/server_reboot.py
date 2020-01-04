#!/usr/bin/env python3.5

"""
This program checks the database entries from the Quake Live servers and reboots the server if the servers are empty.
It requires that the Quake servers run minqlx and the ServerStatus.py plugin for minqlx.
Set the environment variables for this by editing the values below after the equals signs, using the descriptions.

This needs to be run as root.
To make it execute on a schedule I entered it as a linux cron job. Follow these steps:
1) log into your server as root or run commands with sudo
2) on command line run: crontab -e
   If this is the first time crontab was run choose the editor type you want to use (i pick the default)
3) add this line at the end of the file: 1 4 * * * /home/steam/server_reboot.py
   the last part is the path and executable file name
   the 5 items before are described in the crontab file, the 1 4 and * * * will make it execute at 4am every day
   the 4am is based on your server's system time.
4) exit the crontab editor and the cron job execution should give a message like 'crontab: installing new crontab'
   this shows the job was scheduled with the linux operating system

Load the ServerStatus onto your Quake Live server just like every other plugin, it has no variables to set on the server
"""

import os
import time
import redis

# The REDIS_DATABASE values are all of the unique settings used by the Quake Live server's minqlx qlx_redisDatabase
# values. This example meas there are 3 servers. The servers each have a different qlx_redisDatabase setting.
# One has a '0', another a '1', and the last a '2'.
REDIS_DATABASES = [0, 1, 2]  # This tells which databases are used by the QL servers *** NEEDS TO BE SET CORRECTLY ***
REDIS_PASS = "Redis_Server_Password_Here"  # Redis password ( "" if none)
CHECK_KEY = "minqlx:connected"  # Must match COUNT_KEY in ServerStatus.py (should not need to edit)
REDIS_ADDRESS = "127.0.0.1"  # address of the redis server (127.0.0.1 is the same as localhost, should not need to edit)
LOG_MESSAGES = True  # Enable status logging to linux system log
USE_SYSLOG = False  # Set the logging (if enabled) to use the OS's system log
RECHECK_SERVERS = True  # Check the servers again if they are not empty (enable=True, disable=False)
WAIT_TIME = 20  # The minutes the process will wait before checking again if the servers are not empty
MAX_CHECKS = 10  # The maximum amount of times the process will check for an empty server (0 to disable)
FORCE_RESTART = False  # If MAX_CHECKS has been met, should the server be restarted anyway (True or False)

if LOG_MESSAGES:
    if USE_SYSLOG:
        import syslog
    else:
        import sys
        # edit the file name to include the path, otherwise it will be in the root home directory)
        sys.stdout = open("server_reboot.log", "a")


# ====================================================================
#                               Redis
# ====================================================================
class Redis:
    _conn = None
    _pool = None
    _pass = REDIS_PASS
    _counter = 0

    def __init__(self):
        self.__class__._counter += 1

    def __del__(self):
        self.__class__._counter -= 1
        self.close()

    def __contains__(self, key):
        return self.r.exists(key)

    def __getitem__(self, key):
        res = self.r.get(key)
        if res is None:
            raise KeyError("The key '{}' is not present in the database.".format(key))
        else:
            return res

    def __setitem__(self, key, item):
        res = self.r.set(key, item)
        if res is False:
            raise RuntimeError("The database assignment failed.")

    def __delitem__(self, key):
        res = self.r.delete(key)
        if res == 0:
            raise KeyError("The key '{}' is not present in the database.".format(key))

    def __getattr__(self, attr):
        return getattr(self.r, attr)

    @property
    def r(self):
        return self.connect()

    def connect(self, host="127.0.0.1", database=0, unix_socket=False, password=None):
        if not host and not self._conn:
            if not Redis._conn:
                _host = REDIS_ADDRESS
                _db = database
                _unixsocket = unix_socket
                if _unixsocket:
                    Redis._conn = redis.StrictRedis(unix_socket_path=_host, db=_db, password=Redis._pass,
                                                    decode_responses=True)
                else:
                    split_host = _host.split(":")
                    if len(split_host) > 1:
                        port = int(split_host[1])
                    else:
                        port = 6379  # Default port.
                    Redis._pool = redis.ConnectionPool(host=split_host[0], port=port, db=_db, password=Redis._pass,
                                                       decode_responses=True)
                    Redis._conn = redis.StrictRedis(connection_pool=Redis._pool, decode_responses=True)
                    self._conn = None
            return Redis._conn
        elif not self._conn:
            split_host = host.split(":")
            if len(split_host) > 1:
                port = int(split_host[1])
            else:
                port = 6379  # Default port.

            if unix_socket:
                self._conn = redis.StrictRedis(unix_socket_path=host, db=database, password=password,
                                               decode_responses=True)
            else:
                self._pool = redis.ConnectionPool(host=split_host[0], port=port, db=database, password=password,
                                                  decode_responses=True)
                self._conn = redis.StrictRedis(connection_pool=self._pool, decode_responses=True)
        return self._conn

    def close(self):
        if self._conn:
            self._conn = None
            if self._pool:
                self._pool.disconnect()
                self._pool = None

        if Redis._counter <= 1 and Redis._conn:
            Redis._conn = None
            if Redis._pool:
                Redis._pool.disconnect()
                Redis._pool = None


# ====================================================================
#                       Get Total Player Count
# ====================================================================
class PlayerCount:
    def __init__(self):
        self.usage = 0
        self.r = Redis()

    def get_occupied_count(self):
        count = 0
        for x in REDIS_DATABASES:
            self.r.connect(REDIS_ADDRESS, x, False, REDIS_PASS)
            if self.r[CHECK_KEY.format(x)]:
                count += int(self.r[CHECK_KEY.format(x)])
            self.r.close()
        if LOG_MESSAGES:
            if USE_SYSLOG:
                syslog.syslog("Player Count: {}\n".format(count))
            else:
                print("{} Player Count: {}".format(time.strftime("(%d %b %Y %H:%M:%S)"), count))
        return count


# ====================================================================
#                              Reboot
# ====================================================================
if __name__ == "__main__":
    check_count = 0
    if LOG_MESSAGES:
        if USE_SYSLOG:
            syslog.syslog("Checking server(s) player count")
        else:
            print("{} Checking server(s) player count".format(time.strftime("(%d %b %Y %H:%M:%S)")))
    player_count = PlayerCount()
    total_players = player_count.get_occupied_count()
    while total_players != 0 and check_count < MAX_CHECKS and RECHECK_SERVERS:
        check_count += 1
        if LOG_MESSAGES:
            if USE_SYSLOG:
                syslog.syslog("Servers are not empty. Waiting {} minutes".format(WAIT_TIME))
            else:
                print("{} Servers are not empty. Waiting {} minutes"
                      .format(time.strftime("(%d %b %Y %H:%M:%S)"), WAIT_TIME))
        time.sleep(WAIT_TIME * 60)
        total_players = player_count.get_occupied_count()

    if total_players == 0:
        print("Player Count: {}".format(total_players))
        if LOG_MESSAGES:
            if USE_SYSLOG:
                syslog.syslog("Servers are empty: Rebooting")
            else:
                print("{} Servers are empty: Rebooting".format(time.strftime("(%d %b %Y %H:%M:%S)")))
        os.system('/sbin/shutdown -r now')
    elif check_count >= MAX_CHECKS and RECHECK_SERVERS and FORCE_RESTART:
        if LOG_MESSAGES:
            if USE_SYSLOG:
                syslog.syslog("MAX_CHECKS has been met: forcing Reboot")
            else:
                print("{} MAX_CHECKS has been met: forcing Reboot".format(time.strftime("(%d %b %Y %H:%M:%S)")))
        os.system('/sbin/shutdown -r now')
