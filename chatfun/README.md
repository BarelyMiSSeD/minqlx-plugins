# Chatfun.py

I created this plugin to create a little bit of fun on the server that doesn't ahve to do with playing.

The server will respond to things said in the server in chat and with some !commands.

Use <b>!fun</b> to see what commands will get a repsonse.

<br><br>
Command(s) available with chatfun.py listed with the set permission level.

<b>•	Permission level 4</b>

<b>!chatfun</b>

Turns the automatic response to certain words said in normal chat on or off.
This will override the setting in the config until the server is restarted.

Usage: !chatfun on|off
   
<br><br>
CVARs to be set. The settings are shown with the default settings. Set these in the same config file you set the other minqlx bot cvars.


<b>set qlx_chatfunAdmin "4"</b> - Sets the minqlx permission level needed to turn the chatfun auto responses on/off in game with
                        !chatfun <on|off>. This will override the qlx_chatfunReply setting until the server is restarted.
<b>set qlx_chatfunPauseTime "5"</b> - Sets the amount of seconds between each response from the server.
<b>set qlx_chatfunReply "1"</b> - Turns on/off the auto responses from the server to trigger text said in normal chat.
