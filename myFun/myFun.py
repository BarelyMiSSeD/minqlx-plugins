# This plugin is a modification of minqlx's fun.py
# https://github.com/MinoMino/minqlx

# Created by BarelyMiSSeD
# https://github.com/BarelyMiSSeD

# You are free to modify this plugin
# This plugin comes with no warranty or guarantee

"""
This is my replacement for the minqlx fun.py so if you use this file make sure not to load fun.py

This plugin plays sounds on the Quake Live server
It plays the sounds included in fun.py and some from three other workshop items.

This will limit sound spamming to the server.
It only allows one sound to be played at a time and each user is limited in the frequency they can play sounds.


To set the time required between sounds add this line to your server.cfg and edit the "5":
set qlx_funSoundDelay "5"

To set the time a player has to wait after playing a sound add this like to your server.cfg and edit the "30":
set qlx_funPlayerSoundRepeat "30"


Three extra workshop items need to be loaded on the server for it to work correctly:
#prestige worldwide sounds workshop
585892371
#Funny Sounds Pack for Minqlx
620087103
#Duke Nukem Sounds
572453229

The minqlx 'workshop' plugin needs to be loaded and the required workshop
 items added to the set qlx_workshopReferences line
  (this example shows only these three required workshop items):
set qlx_workshopReferences "585892371, 620087103, 572453229"

Put the sound_names.txt file into the server's fs_homepath directory for
the !listsounds to work on the server.
!listsounds can be issued by itself to see all the sounds that can be played on the server
or it can be issued with one argument to limit the listed sounds to the sound phrases that contain that argument.
Example: '!listsounds yeah' would list all the sound phrases containing 'yeah'
 and would print this to the player's console (based on sound_names.txt at the time of this file creation):

SOUNDS: Type These words/phrases in normal chat to get a sound to play on the server.
haha yeah haha    hahaha yeah    yeah hahaha    yeahhh
4 SOUNDS: These are the sounds that work on this server.

If you edit the sound_names.txt put one sound phrase on each line and any line beginning with a # will be ignored
"""

import minqlx
import random
import time
import re
import os

from minqlx.database import Redis


FILE_NAME = 'sound_names.txt'
VERSION = 1.3

_re_hahaha_yeah = re.compile(r"^haha(?:ha)?,? yeah?\W?$", flags=re.IGNORECASE)
_re_haha_yeah_haha = re.compile(r"^haha(?:ha)?,? yeah?,? haha\W?$", flags=re.IGNORECASE)
_re_yeah_hahaha = re.compile(r"^yeah?,? haha(?:ha)\W?$", flags=re.IGNORECASE)
_re_duahahaha = re.compile(r"^duahaha(?:ha)?\W?$", flags=re.IGNORECASE)
_re_hahaha = re.compile(r"hahaha", flags=re.IGNORECASE)
_re_glhf = re.compile(r"^(?:gl ?hf\W?)|(?:hf\W?)|(?:gl hf\W?)", flags=re.IGNORECASE)
_re_f3 = re.compile(r"^(?:(?:press )?f3)|ready(?: up)?\W?", flags=re.IGNORECASE)
_re_welcome = re.compile(r"^welcome to (?:ql|quake live)\W?$", flags=re.IGNORECASE)
_re_go = re.compile(r"^go\W?$", flags=re.IGNORECASE)
_re_win = re.compile(r"^you win\W?$", flags=re.IGNORECASE)
_re_lose = re.compile(r"^you lose\W?$", flags=re.IGNORECASE)
_re_beep_boop = re.compile(r"^beep boop\W?$", flags=re.IGNORECASE)
_re_denied = re.compile(r"^denied\W?$", flags=re.IGNORECASE)
_re_balls_out = re.compile(r"^ball'?s out\W?$", flags=re.IGNORECASE)
_re_one = re.compile(r"^one\W?$", flags=re.IGNORECASE)
_re_two = re.compile(r"^two\W?$", flags=re.IGNORECASE)
_re_three = re.compile(r"^three\W?$", flags=re.IGNORECASE)
_re_fight = re.compile(r"^fight\W?$", flags=re.IGNORECASE)
_re_gauntlet = re.compile(r"^gauntlet\W?$", flags=re.IGNORECASE)
_re_humiliation = re.compile(r"^humiliation\W?$", flags=re.IGNORECASE)
_re_perfect = re.compile(r"^perfect\W?$", flags=re.IGNORECASE)
_re_wah = re.compile(r"^wa+h wa+h wa+h wa+h\W?$", flags=re.IGNORECASE)
_re_ah = re.compile(r"^a+h a+h a+h\W?$", flags=re.IGNORECASE)
_re_oink = re.compile(r"^oink\W?$", flags=re.IGNORECASE)
_re_argh = re.compile(r"^a+rgh\W?$", flags=re.IGNORECASE)
_re_hah_haha = re.compile(r"^hah haha\W?$", flags=re.IGNORECASE)
_re_woohoo = re.compile(r"^woo+hoo+\W?$", flags=re.IGNORECASE)
_re_quakelive = re.compile(r"^(?:ql|quake live)\W?$", flags=re.IGNORECASE)
_re_chaching = re.compile(r"(?:\$|€|£|chaching)", flags=re.IGNORECASE)
_re_uh_ah = re.compile(r"^uh ah$", flags=re.IGNORECASE)
_re_oohwee = re.compile(r"^ooh+wee\W?$", flags=re.IGNORECASE)
_re_erah = re.compile(r"^erah\W?$", flags=re.IGNORECASE)
_re_yeahhh = re.compile(r"^yeahhh\W?$", flags=re.IGNORECASE)
_re_scream = re.compile(r"^scream\W?$", flags=re.IGNORECASE)
_re_salute = re.compile(r"^salute\W?$", flags=re.IGNORECASE)
_re_squish = re.compile(r"^squish\W?$", flags=re.IGNORECASE)
_re_oh_god = re.compile(r"^oh god\W?$", flags=re.IGNORECASE)
_re_snarl = re.compile(r"^snarl\W?$", flags=re.IGNORECASE)

#Viewaskewer's
_re_assholes = re.compile(r"^assholes\W?$", flags=re.IGNORECASE)
_re_assshafter = re.compile(r"^(?:assshafter|asshafter|ass shafter)\W?$", flags=re.IGNORECASE)
_re_babydoll = re.compile(r"^babydoll\W?$", flags=re.IGNORECASE)
_re_barelymissed = re.compile(r"^(?:barelymissed|barely)\W?$", flags=re.IGNORECASE)
_re_belly = re.compile(r"belly", flags=re.IGNORECASE)
_re_bitch = re.compile(r"^bitch\W?$", flags=re.IGNORECASE)
_re_blud = re.compile(r"^(?:dtblud|blud)\W?$", flags=re.IGNORECASE)
_re_boats = re.compile(r"^boats\W?$", flags=re.IGNORECASE)
_re_bobg = re.compile(r"^(?:bobg|bob)\W?$", flags=re.IGNORECASE)
_re_bogdog = re.compile(r"^bogdog\W?$", flags=re.IGNORECASE)
_re_boom = re.compile(r"^boom\W?$", flags=re.IGNORECASE)
_re_boom2 = re.compile(r"^boom2\W?$", flags=re.IGNORECASE)
_re_buk = re.compile(r"^(?:buk|ibbukn)\W?$", flags=re.IGNORECASE)
_re_bullshit = re.compile(r"^(?:bullshit|bull shit|bs)\W?$", flags=re.IGNORECASE)
_re_butthole = re.compile(r"^butthole\W?$", flags=re.IGNORECASE)
_re_buttsex = re.compile(r"^buttsex\W?$", flags=re.IGNORECASE)
_re_cheeks = re.compile(r"^cheeks\W?$", flags=re.IGNORECASE)
_re_cocksucker = re.compile(r"^(?:cocksucker|cs)\W?$", flags=re.IGNORECASE)
_re_conquer = re.compile(r"^conquer\W?$", flags=re.IGNORECASE)
_re_countdown = re.compile(r"^countdown\W?$", flags=re.IGNORECASE)
_re_cum = re.compile(r"^cum\W?$", flags=re.IGNORECASE)
_re_cumming = re.compile(r"^cumming\W?$", flags=re.IGNORECASE)
_re_cunt = re.compile(r"^cunt\W?$", flags=re.IGNORECASE)
_re_dirkfunk = re.compile(r"^(?:dirkfunk|dirk)\W?$", flags=re.IGNORECASE)
_re_disappointment = re.compile(r"^disappointment\W?$", flags=re.IGNORECASE)
_re_doom = re.compile(r"^(?:doom|doomsday)\W?$", flags=re.IGNORECASE)
_re_drumset = re.compile(r"^drumset\W?$", flags=re.IGNORECASE)
_re_eat = re.compile(r"^eat\W?$", flags=re.IGNORECASE)
_re_eatme = re.compile(r"^(?:eatme|eat me|byte me)\W?$", flags=re.IGNORECASE)
_re_fag = re.compile(r"^(?:fag|homo|homosexual)\W?$", flags=re.IGNORECASE)
_re_fingerass = re.compile(r"^fingerass\W?$", flags=re.IGNORECASE)
_re_flash = re.compile(r"^(?:flashsoul|flash)\W?$", flags=re.IGNORECASE)
_re_fuckface = re.compile(r"^fuckface\W?$", flags=re.IGNORECASE)
_re_fuck_you = re.compile(r"^fuckyou\W?$", flags=re.IGNORECASE)
_re_getemm = re.compile(r"^(?:getem+|get em+)\W?$", flags=re.IGNORECASE)
_re_gonads = re.compile(r"^(?:gonads|nads)\W?$", flags=re.IGNORECASE)
_re_gtfo = re.compile(r"^gtfo\W?$", flags=re.IGNORECASE)
_re_HIT = re.compile(r"^HIT\W?$")
_re_hugitout = re.compile(r"^hug it out\W?$")
_re_idiot = re.compile(r"^(?:idiot|andycreep|d3phx|gladiat0r)\W?$", flags=re.IGNORECASE)
_re_idiot2 = re.compile(r"^idiot2\W?$", flags=re.IGNORECASE)
_re_itstime = re.compile(r"^it?'s time\W?$", flags=re.IGNORECASE)
_re_jeopardy = re.compile(r"^jeopardy\W?$", flags=re.IGNORECASE)
_re_jerkoff = re.compile(r"^(?:jerk off|jerkoff)\W?$", flags=re.IGNORECASE)
_re_killo = re.compile(r"^killo\W?$", flags=re.IGNORECASE)
_re_knocked = re.compile(r"^knocked\W?$", flags=re.IGNORECASE)
_re_ld3 = re.compile(r"^(?:die|ld3)\W?$", flags=re.IGNORECASE)
_re_liquidswords = re.compile(r"^(?:liquidswords|liquid)\W?$", flags=re.IGNORECASE)
_re_massacre = re.compile(r"^massacre\W?$", flags=re.IGNORECASE)
_re_mixer = re.compile(r"^mixer\W?$", flags=re.IGNORECASE)
_re_mjman = re.compile(r"^(?:mjman|marijuanaman)\W?$", flags=re.IGNORECASE)
_re_mmmm = re.compile(r"^mmmm\W?$", flags=re.IGNORECASE)
_re_monty = re.compile(r"^monty\W?$", flags=re.IGNORECASE)
_re_n8 = re.compile(r"^(?:n8|_n8)\W?$", flags=re.IGNORECASE)
_re_nikon = re.compile(r"^(?:nikon|niko|nikonguru)\W?$", flags=re.IGNORECASE)
_re_nina = re.compile(r"^nina\W?$", flags=re.IGNORECASE)
_re_nthreem = re.compile(r"^nthreem\W?$", flags=re.IGNORECASE)
_re_olhip = re.compile(r"^(?:olhip|hip)\W?$", flags=re.IGNORECASE)
_re_organic = re.compile(r"^(?:organic|org)\W?$", flags=re.IGNORECASE)
_re_paintball = re.compile(r"^paintball\W?$", flags=re.IGNORECASE)
_re_pigfucker = re.compile(r"^(?:pigfucker|pig fucker|pf)\W?$", flags=re.IGNORECASE)
_re_popeye = re.compile(r"^popeye\W?$", flags=re.IGNORECASE)
_re_rosie = re.compile(r"^rosie\W?$", flags=re.IGNORECASE)
_re_seaweed = re.compile(r"^seaweed\W?$", flags=re.IGNORECASE)
_re_shit = re.compile(r"^shit", flags=re.IGNORECASE)
_re_sit = re.compile(r"(^sit\W?$| sit | sit$)", flags=re.IGNORECASE)
_re_soulianis = re.compile(r"^(?:soulianis|soul)\W?$", flags=re.IGNORECASE)
_re_spam = re.compile(r"^spam\W?$", flags=re.IGNORECASE)
_re_stalin = re.compile(r"^stalin\W?$", flags=re.IGNORECASE)
_re_stfu = re.compile(r"^stfu\W?$", flags=re.IGNORECASE)
_re_suckadick = re.compile(r"^suck a dick\W?$", flags=re.IGNORECASE)
_re_suckit = re.compile(r"^suckit\W?$", flags=re.IGNORECASE)
_re_suckmydick = re.compile(r"^suck my dick\W?$", flags=re.IGNORECASE)
_re_teapot = re.compile(r"^teapot\W?$", flags=re.IGNORECASE)
_re_thankgod = re.compile(r"^(?:thankgod|thank god)\W?$", flags=re.IGNORECASE)
_re_traxion = re.compile(r"^traxion\W?$", flags=re.IGNORECASE)
_re_trixy = re.compile(r"^trixy\W?$", flags=re.IGNORECASE)
_re_twoon = re.compile(r"^(?:twoon|2pows)\W?$", flags=re.IGNORECASE)
_re_ty = re.compile(r"^(?:ty|thanks|thank you)\W?$", flags=re.IGNORECASE)
_re_venny = re.compile(r"^venny\W?$", flags=re.IGNORECASE)
_re_viewaskewer = re.compile(r"^(?:viewaskewer|view)\W?$", flags=re.IGNORECASE)
_re_whatsthat = re.compile(r"^what?'s that\W?$", flags=re.IGNORECASE)
_re_whoareyou = re.compile(r"^who are you\W?$", flags=re.IGNORECASE)

#|sf|bart`us's
_re_007 = re.compile(r"^007\W?$", flags=re.IGNORECASE)
_re_AScratch = re.compile(r"^(?:A Scratch|Scratch|just a scratch)\W?$", flags=re.IGNORECASE)
_re_adamsfamily = re.compile(r"^(?:adamsfamily|adams family)\W?$", flags=re.IGNORECASE)
_re_allahuakbar = re.compile(r"^allahuakbar\W?$", flags=re.IGNORECASE)
_re_allstar = re.compile(r"^allstar\W?$", flags=re.IGNORECASE)
_re_AllTheThings = re.compile(r"^All The Things\W?$", flags=re.IGNORECASE)
_re_Amazing = re.compile(r"^Amazing\W?$", flags=re.IGNORECASE)
_re_Ameno = re.compile(r"^Ameno\W?$", flags=re.IGNORECASE)
_re_America = re.compile(r"^America\W?$", flags=re.IGNORECASE)
_re_Amerika = re.compile(r"^Amerika\W?$", flags=re.IGNORECASE)
_re_AndNothingElse = re.compile(r"^And Nothing Else\W?$", flags=re.IGNORECASE)
_re_Animals = re.compile(r"^Animals\W?$", flags=re.IGNORECASE)
_re_asskicking = re.compile(r"^asskicking\W?$", flags=re.IGNORECASE)
_re_ave = re.compile(r"^ave\W?$", flags=re.IGNORECASE)
_re_babybaby = re.compile(r"^baby baby\W?$", flags=re.IGNORECASE)
_re_babyevillaugh = re.compile(r"^baby evil\W?$", flags=re.IGNORECASE)
_re_babylaughing = re.compile(r"^(?:babylaughing|baby laughing)\W?$", flags=re.IGNORECASE)
_re_badboys = re.compile(r"^bad boys\W?$", flags=re.IGNORECASE)
_re_BananaBoatSong = re.compile(r"^Banana Boat\W?$", flags=re.IGNORECASE)
_re_bennyhill = re.compile(r"^benny hill\W?$", flags=re.IGNORECASE)
_re_benzin = re.compile(r"^benzin\W?$", flags=re.IGNORECASE)
_re_bluewins = re.compile(r"^blue wins\W?$", flags=re.IGNORECASE)
_re_bonkers = re.compile(r"^bonkers\W?$", flags=re.IGNORECASE)
_re_boomheadshot = re.compile(r"^boom headshot\W?$", flags=re.IGNORECASE)
_re_booo = re.compile(r"^booo\W?$", flags=re.IGNORECASE)
_re_boring = re.compile(r"^boring\W?$", flags=re.IGNORECASE)
_re_boze = re.compile(r"^boze\W?$", flags=re.IGNORECASE)
_re_brightsideoflife = re.compile(r"^(?:brightsideoflife|bright side of life)\W?$", flags=re.IGNORECASE)
_re_buckdich = re.compile(r"^buckdich\W?$", flags=re.IGNORECASE)
_re_bullshitter = re.compile(r"^bullshitter\W?$", flags=re.IGNORECASE)
_re_burnsburns = re.compile(r"^burns burns\W?$", flags=re.IGNORECASE)
_re_cameltoe = re.compile(r"^camel toe\W?$", flags=re.IGNORECASE)
_re_canttouchthis = re.compile(r"^can'?t touch this\W?$", flags=re.IGNORECASE)
_re_cccp = re.compile(r"^cccp\W?$", flags=re.IGNORECASE)
_re_champions = re.compile(r"^champions\W?$", flags=re.IGNORECASE)
_re_chicken = re.compile(r"^chicken\W?$", flags=re.IGNORECASE)
_re_chocolaterain = re.compile(r"^chocolate rain\W?$", flags=re.IGNORECASE)
_re_coin = re.compile(r"^coin\W?$", flags=re.IGNORECASE)
_re_come = re.compile(r"^come\W?$", flags=re.IGNORECASE)
_re_ComeWithMeNow = re.compile(r"^Come With Me Now\W?$", flags=re.IGNORECASE)
_re_Count_down = re.compile(r"^Count down\W?$", flags=re.IGNORECASE)
_re_cowards = re.compile(r"^cowards\W?$", flags=re.IGNORECASE)
_re_crazy = re.compile(r"^crazy\W?$", flags=re.IGNORECASE)
_re_damnit = re.compile(r"^damnit\W?$", flags=re.IGNORECASE)
_re_DangerZone = re.compile(r"^Danger Zone\W?$", flags=re.IGNORECASE)
_re_deadsoon = re.compile(r"^(?:deadsoon|dead soon)\W?$", flags=re.IGNORECASE)
_re_defeated = re.compile(r"^defeated\W?$", flags=re.IGNORECASE)
_re_devil = re.compile(r"^devil\W?$", flags=re.IGNORECASE)
_re_doesntloveyou = re.compile(r"^doesn'?t love you\W?$", flags=re.IGNORECASE)
_re_dubist = re.compile(r"^du bist\W?$", flags=re.IGNORECASE)
_re_duhast = re.compile(r"^du hast\W?$", flags=re.IGNORECASE)
_re_dumbways = re.compile(r"^dumb ways\W?$", flags=re.IGNORECASE)
_re_EatPussy = re.compile(r"^Eat Pussy\W?$", flags=re.IGNORECASE)
_re_education = re.compile(r"^education\W?$", flags=re.IGNORECASE)
_re_einschrei = re.compile(r"^einschrei\W?$", flags=re.IGNORECASE)
_re_EinsZwei = re.compile(r"^Eins Zwei\W?$", flags=re.IGNORECASE)
_re_electro = re.compile(r"^electro\W?$", flags=re.IGNORECASE)
_re_elementary = re.compile(r"^elementary\W?$", flags=re.IGNORECASE)
_re_engel = re.compile(r"^engel\W?$", flags=re.IGNORECASE)
_re_erstwenn = re.compile(r"^erstwenn\W?$", flags=re.IGNORECASE)
_re_exitlight = re.compile(r"^(?:exitlight|exit light)\W?$", flags=re.IGNORECASE)
_re_faint = re.compile(r"^faint\W?$", flags=re.IGNORECASE)
_re_fatality = re.compile(r"^fatality\W?$", flags=re.IGNORECASE)
_re_FeelGood = re.compile(r"^Feel Good\W?$", flags=re.IGNORECASE)
_re_fleshwound = re.compile(r"^flesh wound\W?$", flags=re.IGNORECASE)
_re_foryou = re.compile(r"^for you\W?$", flags=re.IGNORECASE)
_re_freestyler = re.compile(r"^freestyler\W?$", flags=re.IGNORECASE)
_re_fuckfuck = re.compile(r"^fuckfuck\W?$", flags=re.IGNORECASE)
_re_fuckingburger = re.compile(r"^fucking burger\W?$", flags=re.IGNORECASE)
_re_fuckingkids = re.compile(r"^fucking kids\W?$", flags=re.IGNORECASE)
_re_gangnam = re.compile(r"^gangnam\W?$", flags=re.IGNORECASE)
_re_ganjaman = re.compile(r"^ganjaman\W?$", flags=re.IGNORECASE)
_re_gay = re.compile(r"^gay\W?$", flags=re.IGNORECASE)
_re_getcrowbar = re.compile(r"^get crowbar\W?$", flags=re.IGNORECASE)
_re_getouttheway = re.compile(r"^get out the way\W?$", flags=re.IGNORECASE)
_re_ghostbusters = re.compile(r"^ghostbusters\W?$", flags=re.IGNORECASE)
_re_girllook = re.compile(r"^girl look\W?$", flags=re.IGNORECASE)
_re_girly = re.compile(r"^girly\W?$", flags=re.IGNORECASE)
_re_gnrguitar = re.compile(r"^gnr guitar\W?$", flags=re.IGNORECASE)
_re_goddamnright = re.compile(r"^goddamn right\W?$", flags=re.IGNORECASE)
_re_goodbyeandrea = re.compile(r"^goodbye andrea\W?$", flags=re.IGNORECASE)
_re_goodbyesarah = re.compile(r"^goodbye sarah\W?$", flags=re.IGNORECASE)
_re_gotcha = re.compile(r"^gotcha\W?$", flags=re.IGNORECASE)
_re_hakunamatata = re.compile(r"^hakunamatata\W?$", flags=re.IGNORECASE)
_re_hammertime = re.compile(r"^hammertime\W?$", flags=re.IGNORECASE)
_re_hello = re.compile(r"^hello\W?$", flags=re.IGNORECASE)
_re_hellstestern = re.compile(r"^hellstestern\W?$", flags=re.IGNORECASE)
_re_holy = re.compile(r"^holy\W?$", flags=re.IGNORECASE)
_re_hoppereiter = re.compile(r"^hoppereiter\W?$", flags=re.IGNORECASE)
_re_howareyou = re.compile(r"^how are you\W?$", flags=re.IGNORECASE)
_re_hush = re.compile(r"^hush\W?$", flags=re.IGNORECASE)
_re_ibet = re.compile(r"^(?:ibet|i bet)\W?$", flags=re.IGNORECASE)
_re_icantbelieve = re.compile(r"^i can'?t believe\W?$", flags=re.IGNORECASE)
_re_ichtuedieweh = re.compile(r"^ichtuedieweh\W?$", flags=re.IGNORECASE)
_re_idoparkour = re.compile(r"^i do parkour\W?$", flags=re.IGNORECASE)
_re_ihateall = re.compile(r"^i hate all\W?$", flags=re.IGNORECASE)
_re_illbeback = re.compile(r"^I'?ll be back\W?$", flags=re.IGNORECASE)
_re_imperial = re.compile(r"^imperial\W?$", flags=re.IGNORECASE)
_re_imsexy = re.compile(r"^im sexy\W?$", flags=re.IGNORECASE)
_re_imyourfather = re.compile(r"^i'?m your father\W?$", flags=re.IGNORECASE)
_re_incoming = re.compile(r"^incoming\W?$", flags=re.IGNORECASE)
_re_indianajones = re.compile(r"^indiana jones\W?$", flags=re.IGNORECASE)
_re_inyourheadzombie = re.compile(r"^in your head zombie\W?$", flags=re.IGNORECASE)
_re_iseeassholes = re.compile(r"^i see assholes\W?$", flags=re.IGNORECASE)
_re_iseedeadpeople = re.compile(r"^i see dead people\W?$", flags=re.IGNORECASE)
_re_itsmylife = re.compile(r"^it'?s my life\W?$", flags=re.IGNORECASE)
_re_itsnot = re.compile(r"^it'?s not\W?$", flags=re.IGNORECASE)
_re_jackpot = re.compile(r"^jackpot\W?$", flags=re.IGNORECASE)
_re_jesus = re.compile(r"^jesus\W?$", flags=re.IGNORECASE)
_re_jesusOh = re.compile(r"^jesus Oh\W?$", flags=re.IGNORECASE)
_re_johncena = re.compile(r"^(?:johncena|john cena)\W?$", flags=re.IGNORECASE)
_re_jumpmotherfucker = re.compile(r"^jump motherfucker\W?$", flags=re.IGNORECASE)
_re_justdoit = re.compile(r"^just do it\W?$", flags=re.IGNORECASE)
_re_kamehameha = re.compile(r"^kamehameha\W?$", flags=re.IGNORECASE)
_re_keeponfighting = re.compile(r"^keep on fighting\W?$", flags=re.IGNORECASE)
_re_keepyourshirton = re.compile(r"^keep your shirt on\W?$", flags=re.IGNORECASE)
_re_KnockedDown = re.compile(r"^Knocked Down\W?$", flags=re.IGNORECASE)
_re_kommtdiesonne = re.compile(r"^kommtdiesonne\W?$", flags=re.IGNORECASE)
_re_kungfu = re.compile(r"^(?:kungfu|kung fu)\W?$", flags=re.IGNORECASE)
_re_lately = re.compile(r"^lately\W?$", flags=re.IGNORECASE)
_re_Legitness = re.compile(r"^Legitness\W?$", flags=re.IGNORECASE)
_re_letsgetready = re.compile(r"^lets get ready\W?$", flags=re.IGNORECASE)
_re_letsputasmile = re.compile(r"^lets put a smile\W?$", flags=re.IGNORECASE)
_re_lightsout = re.compile(r"^lights out\W?$", flags=re.IGNORECASE)
_re_lionking = re.compile(r"^lion king\W?$", flags=re.IGNORECASE)
_re_livetowin = re.compile(r"^live to win\W?$", flags=re.IGNORECASE)
_re_losingmyreligion = re.compile(r"^losing my religion\W?$", flags=re.IGNORECASE)
_re_loveme = re.compile(r"^(?:loveme|love me)\W?$", flags=re.IGNORECASE)
_re_low = re.compile(r"^low\W?$", flags=re.IGNORECASE)
_re_luck = re.compile(r"^luck\W?$", flags=re.IGNORECASE)
_re_lust = re.compile(r"^lust\W?$", flags=re.IGNORECASE)
_re_mahnamahna = re.compile(r"^mahnamahna\W?$", flags=re.IGNORECASE)
_re_mario = re.compile(r"^mario\W?$", flags=re.IGNORECASE)
_re_Me = re.compile(r"^Me\W?$", flags=re.IGNORECASE)
_re_meinland = re.compile(r"^meinland\W?$", flags=re.IGNORECASE)
_re_message = re.compile(r"^message\W?$", flags=re.IGNORECASE)
_re_mimimi = re.compile(r"^mimimi\W?$", flags=re.IGNORECASE)
_re_mission = re.compile(r"^mission\W?$", flags=re.IGNORECASE)
_re_moan = re.compile(r"^moan\W?$", flags=re.IGNORECASE)
_re_mortalkombat = re.compile(r"^mortal kombat\W?$", flags=re.IGNORECASE)
_re_moveass = re.compile(r"^move ass\W?$", flags=re.IGNORECASE)
_re_muppetopening = re.compile(r"^muppet opening\W?$", flags=re.IGNORECASE)
_re_mylittlepony = re.compile(r"^my little pony\W?$", flags=re.IGNORECASE)
_re_myname = re.compile(r"^my name\W?$", flags=re.IGNORECASE)
_re_neverseen = re.compile(r"^never seen\W?$", flags=re.IGNORECASE)
_re_nightmare = re.compile(r"^nightmare\W?$", flags=re.IGNORECASE)
_re_nobodylikesyou = re.compile(r"^nobody likes you\W?$", flags=re.IGNORECASE)
_re_nonie = re.compile(r"^nonie\W?$", flags=re.IGNORECASE)
_re_nooo = re.compile(r"^nooo\W?$", flags=re.IGNORECASE)
_re_notimeforloosers = re.compile(r"^no time for loosers\W?$", flags=re.IGNORECASE)
_re_numanuma = re.compile(r"^numanuma\W?$", flags=re.IGNORECASE)
_re_nyancat = re.compile(r"^nyancat\W?$", flags=re.IGNORECASE)
_re_ofuck = re.compile(r"^o fuck\W?$", flags=re.IGNORECASE)
_re_ohmygod = re.compile(r"^oh my god\W?$", flags=re.IGNORECASE)
_re_OhMyGosh = re.compile(r"^Oh My Gosh\W?$", flags=re.IGNORECASE)
_re_ohnedich = re.compile(r"^ohnedich\W?$", flags=re.IGNORECASE)
_re_ohno = re.compile(r"^oh no\W?$", flags=re.IGNORECASE)
_re_ohnoe = re.compile(r"^oh noe\W?$", flags=re.IGNORECASE)
_re_pacman = re.compile(r"^pacman\W?$", flags=re.IGNORECASE)
_re_pickmeup = re.compile(r"^pick me up\W?$", flags=re.IGNORECASE)
_re_pikachu = re.compile(r"^pikachu\W?$", flags=re.IGNORECASE)
_re_pinkiepie = re.compile(r"^pinkiepie\W?$", flags=re.IGNORECASE)
_re_PinkPanther = re.compile(r"^Pink Panther\W?$", flags=re.IGNORECASE)
_re_pipe = re.compile(r"^pipe\W?$", flags=re.IGNORECASE)
_re_pissmeoff = re.compile(r"^piss me off\W?$", flags=re.IGNORECASE)
_re_playagame = re.compile(r"^play a game\W?$", flags=re.IGNORECASE)
_re_pooping = re.compile(r"^pooping\W?$", flags=re.IGNORECASE)
_re_powerpuff = re.compile(r"^powerpuff\W?$", flags=re.IGNORECASE)
_re_radioactive = re.compile(r"^radioactive\W?$", flags=re.IGNORECASE)
_re_rammsteinriff = re.compile(r"^rammsteinriff\W?$", flags=re.IGNORECASE)
_re_redwins = re.compile(r"^redwins\W?$", flags=re.IGNORECASE)
_re_renegade = re.compile(r"^renegade\W?$", flags=re.IGNORECASE)
_re_retard = re.compile(r"^retard\W?$", flags=re.IGNORECASE)
_re_rocky = re.compile(r"^rocky\W?$", flags=re.IGNORECASE)
_re_rockyouguitar = re.compile(r"^rockyouguitar\W?$", flags=re.IGNORECASE)
_re_sail = re.compile(r"^sail\W?$", flags=re.IGNORECASE)
_re_Salil = re.compile(r"^Salil\W?$", flags=re.IGNORECASE)
_re_samba = re.compile(r"^samba\W?$", flags=re.IGNORECASE)
_re_sandstorm = re.compile(r"^sandstorm\W?$", flags=re.IGNORECASE)
_re_saymyname = re.compile(r"^saymyname\W?$", flags=re.IGNORECASE)
_re_scatman = re.compile(r"^scatman\W?$", flags=re.IGNORECASE)
_re_sellyouall = re.compile(r"^sell you all\W?$", flags=re.IGNORECASE)
_re_senseofhumor = re.compile(r"^sense of humor\W?$", flags=re.IGNORECASE)
_re_shakesenora = re.compile(r"^shakesenora\W?$", flags=re.IGNORECASE)
_re_shutthefuckup = re.compile(r"^shut the fuck up\W?$", flags=re.IGNORECASE)
_re_shutyourfuckingmouth = re.compile(r"^shut your fucking mouth\W?$", flags=re.IGNORECASE)
_re_silence = re.compile(r"^silence\W?$", flags=re.IGNORECASE)
_re_SkeetSkeet = re.compile(r"^(?:All Skeet Skeet|Skeet Skeet)\W?$", flags=re.IGNORECASE)
_re_smoothcriminal = re.compile(r"^smooth criminal\W?$", flags=re.IGNORECASE)
_re_socobatevira = re.compile(r"^socobatevira\W?$", flags=re.IGNORECASE)
_re_socobateviraend = re.compile(r"^socobatevira end\W?$", flags=re.IGNORECASE)
_re_socobatevirafast = re.compile(r"^socobatevira fast\W?$", flags=re.IGNORECASE)
_re_socobateviraslow = re.compile(r"^socobatevira slow\W?$", flags=re.IGNORECASE)
_re_sogivemereason = re.compile(r"^sogivemereason\W?$", flags=re.IGNORECASE)
_re_sostupid = re.compile(r"^so stupid\W?$", flags=re.IGNORECASE)
_re_SpaceJam = re.compile(r"^Space Jam\W?$", flags=re.IGNORECASE)
_re_spaceunicorn = re.compile(r"^space unicorn\W?$", flags=re.IGNORECASE)
_re_spierdalaj = re.compile(r"^spierdalaj\W?$", flags=re.IGNORECASE)
_re_stampon = re.compile(r"^stamp on\W?$", flags=re.IGNORECASE)
_re_starwars = re.compile(r"^star wars\W?$", flags=re.IGNORECASE)
_re_stayinalive = re.compile(r"^stayin alive\W?$", flags=re.IGNORECASE)
_re_stoning = re.compile(r"^stoning\W?$", flags=re.IGNORECASE)
_re_Stop = re.compile(r"^Stop\W?$", flags=re.IGNORECASE)
_re_story = re.compile(r"^story\W?$", flags=re.IGNORECASE)
_re_surprise = re.compile(r"^surprise\W?$", flags=re.IGNORECASE)
_re_swedishchef = re.compile(r"^swedish chef\W?$", flags=re.IGNORECASE)
_re_sweetdreams = re.compile(r"^sweet dreams\W?$", flags=re.IGNORECASE)
_re_takemedown = re.compile(r"^take me down\W?$", flags=re.IGNORECASE)
_re_talkscotish = re.compile(r"^talk scotish\W?$", flags=re.IGNORECASE)
_re_teamwork = re.compile(r"^teamwork\W?$", flags=re.IGNORECASE)
_re_technology = re.compile(r"^technology\W?$", flags=re.IGNORECASE)
_re_thisissparta = re.compile(r"^this is sparta\W?$", flags=re.IGNORECASE)
_re_thunderstruck = re.compile(r"^thunderstruck\W?$", flags=re.IGNORECASE)
_re_tochurch = re.compile(r"^to church\W?$", flags=re.IGNORECASE)
_re_tsunami = re.compile(r"^tsunami\W?$", flags=re.IGNORECASE)
_re_tuturu = re.compile(r"^tuturu\W?$", flags=re.IGNORECASE)
_re_tututu = re.compile(r"^tututu\W?$", flags=re.IGNORECASE)
_re_unbelievable = re.compile(r"^unbelievable\W?$", flags=re.IGNORECASE)
_re_undderhaifisch = re.compile(r"^undderhaifisch\W?$", flags=re.IGNORECASE)
_re_uptowngirl = re.compile(r"^up town girl\W?$", flags=re.IGNORECASE)
_re_valkyries = re.compile(r"^valkyries\W?$", flags=re.IGNORECASE)
_re_wahwahwah = re.compile(r"(?:wahwahwah|dcmattic|mattic)", flags=re.IGNORECASE)
_re_wantyou = re.compile(r"^want you\W?$", flags=re.IGNORECASE)
_re_wazzup = re.compile(r"^wazzup\W?$", flags=re.IGNORECASE)
_re_wehmirohweh = re.compile(r"^wehmirohweh\W?$", flags=re.IGNORECASE)
_re_whatislove = re.compile(r"^what is love\W?$", flags=re.IGNORECASE)
_re_whenangels = re.compile(r"^when angels\W?$", flags=re.IGNORECASE)
_re_whereareyou = re.compile(r"^where are you\W?$", flags=re.IGNORECASE)
_re_whistle = re.compile(r"^whistle\W?$", flags=re.IGNORECASE)
_re_WillBeSinging = re.compile(r"^Will Be Singing\W?$", flags=re.IGNORECASE)
_re_wimbaway = re.compile(r"^wimbaway\W?$", flags=re.IGNORECASE)
_re_windows = re.compile(r"^windows\W?$", flags=re.IGNORECASE)
_re_wouldyoulike = re.compile(r"^would you like\W?$", flags=re.IGNORECASE)
_re_wtf = re.compile(r"^wtf\W?$", flags=re.IGNORECASE)
_re_yeee = re.compile(r"^yeee\W?$", flags=re.IGNORECASE)
_re_yesmaster = re.compile(r"^yes master\W?$", flags=re.IGNORECASE)
_re_yhehehe = re.compile(r"^yhehehe\W?$", flags=re.IGNORECASE)
_re_ymca = re.compile(r"^ymca\W?$", flags=re.IGNORECASE)
_re_You = re.compile(r"^You\W?$", flags=re.IGNORECASE)
_re_yacunt = re.compile(r"^you are a cunt\W?$", flags=re.IGNORECASE)
_re_youfuckedmywife = re.compile(r"^you fucked my wife\W?$", flags=re.IGNORECASE)
_re_YouRealise = re.compile(r"^You Realise\W?$", flags=re.IGNORECASE)

#Duke Nukem
_re_myride = re.compile(r"^my ride\W?$", flags=re.IGNORECASE)
_re_abort = re.compile(r"^abort\W?$", flags=re.IGNORECASE)
_re_ahhh = re.compile(r"^ahhh\W?$", flags=re.IGNORECASE)
_re_muchbetter = re.compile(r"^much better\W?$", flags=re.IGNORECASE)
_re_aisle4 = re.compile(r"^aisle 4\W?$", flags=re.IGNORECASE)
_re_amess = re.compile(r"^a mess\W?$", flags=re.IGNORECASE)
_re_annoying = re.compile(r"^annoying\W?$", flags=re.IGNORECASE)
_re_bitchin = re.compile(r"^bitchin\W?$", flags=re.IGNORECASE)
_re_blowitout = re.compile(r"^blow it out\W?$", flags=re.IGNORECASE)
_re_boobytrap = re.compile(r"^booby trap\W?$", flags=re.IGNORECASE)
_re_bookem = re.compile(r"^bookem\W?$", flags=re.IGNORECASE)
_re_borntobewild = re.compile(r"^born to be wild\W?$", flags=re.IGNORECASE)
_re_chewgum = re.compile(r"^chew gum\W?$", flags=re.IGNORECASE)
_re_comeon = re.compile(r"^come on\W?$", flags=re.IGNORECASE)
_re_thecon = re.compile(r"^the con\W?$", flags=re.IGNORECASE)
_re_cool = re.compile(r"^cool\W?$", flags=re.IGNORECASE)
_re_notcrying = re.compile(r"^not crying\W?$", flags=re.IGNORECASE)
_re_daamn = re.compile(r"^daamn\W?$", flags=re.IGNORECASE)
_re_damit = re.compile(r"^damit\W?$", flags=re.IGNORECASE)
_re_dance = re.compile(r"^dance\W?$", flags=re.IGNORECASE)
_re_diesob = re.compile(r"^diesob\W?$", flags=re.IGNORECASE)
_re_doomed = re.compile(r"^doomed\W?$", flags=re.IGNORECASE)
_re_eyye = re.compile(r"^eyye\W?$", flags=re.IGNORECASE)
_re_dukenukem = re.compile(r"^duke nukem\W?$", flags=re.IGNORECASE)
_re_noway = re.compile(r"^no way\W?$", flags=re.IGNORECASE)
_re_eatshit = re.compile(r"^eat shit\W?$", flags=re.IGNORECASE)
_re_escape = re.compile(r"^escape\W?$", flags=re.IGNORECASE)
_re_faceass = re.compile(r"^face ass\W?$", flags=re.IGNORECASE)
_re_aforce = re.compile(r"^a force\W?$", flags=re.IGNORECASE)
_re_getcrap = re.compile(r"^get that crap\W?$", flags=re.IGNORECASE)
_re_getsome = re.compile(r"^get some\W?$", flags=re.IGNORECASE)
_re_gameover = re.compile(r"^game over\W?$", flags=re.IGNORECASE)
_re_gottahurt = re.compile(r"^gotta hurt\W?$", flags=re.IGNORECASE)
_re_groovy = re.compile(r"^groovy\W?$", flags=re.IGNORECASE)
_re_guyssuck = re.compile(r"^you guys suck\W?$", flags=re.IGNORECASE)
_re_hailking = re.compile(r"^hail king\W?$", flags=re.IGNORECASE)
_re_shithappens = re.compile(r"^shit happens\W?$", flags=re.IGNORECASE)
_re_holycow = re.compile(r"^holy cow\W?$", flags=re.IGNORECASE)
_re_holyshit = re.compile(r"^holy shit\W?$", flags=re.IGNORECASE)
_re_imgood = re.compile(r"^im good\W?$", flags=re.IGNORECASE)
_re_independence = re.compile(r"^independence\W?$", flags=re.IGNORECASE)
_re_inhell = re.compile(r"^in hell\W?$", flags=re.IGNORECASE)
_re_goingin = re.compile(r"^going in\W?$", flags=re.IGNORECASE)
_re_drjones = re.compile(r"^dr jones\W?$", flags=re.IGNORECASE)
_re_kickyourass = re.compile(r"^kick your ass\W?$", flags=re.IGNORECASE)
_re_ktit = re.compile(r"^ktit\W?$", flags=re.IGNORECASE)
_re_letgod = re.compile(r"^let god\W?$", flags=re.IGNORECASE)
_re_letsrock = re.compile(r"^lets rock\W?$", flags=re.IGNORECASE)
_re_lookingood = re.compile(r"^lookin good\W?$", flags=re.IGNORECASE)
_re_makemyday = re.compile(r"^make my day\W?$", flags=re.IGNORECASE)
_re_midevil = re.compile(r"^midevil\W?$", flags=re.IGNORECASE)
_re_mymeat = re.compile(r"^my meat\W?$", flags=re.IGNORECASE)
_re_notime = re.compile(r"^no time\W?$", flags=re.IGNORECASE)
_re_neededthat = re.compile(r"^i needed that\W?$", flags=re.IGNORECASE)
_re_nobody = re.compile(r"^nobody\W?$", flags=re.IGNORECASE)
_re_onlyone = re.compile(r"^only one\W?$", flags=re.IGNORECASE)
_re_mykindaparty = re.compile(r"^my kinda party\W?$", flags=re.IGNORECASE)
_re_gonnapay = re.compile(r"^gonna pay\W?$", flags=re.IGNORECASE)
_re_pissesmeoff = re.compile(r"^pisses me off\W?$", flags=re.IGNORECASE)
_re_pissinmeoff = re.compile(r"^pissin me off\W?$", flags=re.IGNORECASE)
_re_postal = re.compile(r"^postal\W?$", flags=re.IGNORECASE)
_re_aintafraid = re.compile(r"^aintafraid\W?$", flags=re.IGNORECASE)
_re_randr = re.compile(r"^r and r\W?$", flags=re.IGNORECASE)
_re_readyforaction = re.compile(r"^ready for action\W?$", flags=re.IGNORECASE)
_re_ripheadoff = re.compile(r"^rip your head off\W?$", flags=re.IGNORECASE)
_re_ripem = re.compile(r"^rip em\W?$", flags=re.IGNORECASE)
_re_rockin = re.compile(r"^rockin\W?$", flags=re.IGNORECASE)
_re_shakeit = re.compile(r"^shake it\W?$", flags=re.IGNORECASE)
_re_slacker = re.compile(r"^slacker\W?$", flags=re.IGNORECASE)
_re_smackdab = re.compile(r"^smack dab\W?$", flags=re.IGNORECASE)
_re_sohelpme = re.compile(r"^so help me\W?$", flags=re.IGNORECASE)
_re_suckitdown = re.compile(r"^suck it down\W?$", flags=re.IGNORECASE)
_re_terminated = re.compile(r"^terminated\W?$", flags=re.IGNORECASE)
_re_thissucks = re.compile(r"^this sucks\W?$", flags=re.IGNORECASE)
_re_vacation = re.compile(r"^vacation\W?$", flags=re.IGNORECASE)
_re_christmas = re.compile(r"^christmas\W?$", flags=re.IGNORECASE)
_re_wnatssome = re.compile(r"^wants some\W?$", flags=re.IGNORECASE)
_re_youandme = re.compile(r"^you and me\W?$", flags=re.IGNORECASE)
_re_where = re.compile(r"^where\W?$", flags=re.IGNORECASE)
_re_yippiekaiyay = re.compile(r"^yippie kai yay\W?$", flags=re.IGNORECASE)
_re_bottleofjack = re.compile(r"^bottle of jack\W?$", flags=re.IGNORECASE)
_re_longwalk = re.compile(r"^long walk\W?$", flags=re.IGNORECASE)

class myFun(minqlx.Plugin):
    database = Redis

    def __init__(self):
        super().__init__()
        self.add_hook("chat", self.handle_chat)
        self.add_command("cookies", self.cmd_cookies)
        self.last_sound = None

        #Let players with perm level 5 play sounds after the "qlx_funSoundDelay" timeout (no player time restriction)
        self.set_cvar_once("qlx_funUnrestrictAdmin", "0")

        #Delay between sounds being played
        self.set_cvar_once("qlx_funSoundDelay", "5")

        #**** Used for limiting players spamming sounds. ****
        # Amount of seconds player has to wait before allowed to play another sound
        self.set_cvar_once("qlx_funPlayerSoundRepeat", "30")
        # Dictionary used to store player sound call times.
        self.sound_limiting = {}

        self.add_hook("player_disconnect", self.player_disconnect)
        self.add_command(("getsounds", "listsounds", "listsound"), self.cmd_listsounds)

        #variable to show when a sound has been played
        self.played = False
        #variable to store the sound to be called
        self.soundFile = ""

    def player_disconnect(self, player, reason):
        try:
            del self.sound_limiting[player.steam_id]
        except KeyError:
            pass
        except TypeError:
            logger.debug("myFun.py: player_disconnect - invalid player steam id: {}".format(player.steam_id))

    def handle_chat(self, player, msg, channel):
        if channel != "chat":
            return

        msg = self.clean_text(msg)
        if self.find_sound_trigger(msg):
            if self.check_time(player):
                if self.get_cvar("qlx_funUnrestrictAdmin", bool) and self.db.get_permission(player.steam_id) == 5:
                    pass
                else:
                    player.tell("^3You played a sound in last {} seconds. Try again after your timeout."
                                .format(self.get_cvar("qlx_funPlayerSoundRepeat")))
                    return

            if not self.last_sound:
                pass
            elif time.time() - self.last_sound < self.get_cvar("qlx_funSoundDelay", int):
                player.tell("^3A sound has been played in last {} seconds. Try again after the timeout."
                            .format(self.get_cvar("qlx_funSoundDelay")))
                return
            self.play_sound(self.soundFile)


        if self.played:
            self.sound_limiting[player.steam_id] = time.time()

        self.played = False

    def play_sound(self, path):
        self.played = True

        self.last_sound = time.time()
        for p in self.players():
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                super().play_sound(path, p)

    def cmd_cookies(self, player, msg, channel):
        x = random.randint(0, 100)
        if not x:
            channel.reply("^6♥ ^7Here you go, {}. I baked these just for you! ^6♥".format(player))
        elif x == 1:
            channel.reply("What, you thought ^6you^7 would get cookies from me, {}? Hah, think again.".format(player))
        elif x < 50:
            channel.reply("For me? Thank you, {}!".format(player))
        else:
            channel.reply("I'm out of cookies right now, {}. Sorry!".format(player))

    def check_time(self, player):
        if self.get_cvar("qlx_funUnrestrictAdmin", bool) and self.db.get_permission(player.steam_id) == 5:
            return False
        try:
            saved_time = self.sound_limiting[player.steam_id]
            if time.time() - saved_time > self.get_cvar("qlx_funPlayerSoundRepeat", int):
                return False
            else:
                return True
        except KeyError:
            return False

    def cmd_listsounds(self, player, msg, channel):
        sounds = "^4SOUNDS^7: ^3Type These words/phrases in normal chat to get a sound to play on the server.^1"
        try:
            f = open(os.path.join(self.get_cvar("fs_homepath"), FILE_NAME), 'r')
            lines = f.readlines()
            f.close()
        except IOError:
            channel.reply("^4Server^7: Reading Sound List file ^1failed^7. Contact a server admin.")
            return
        lines.sort()
        items = 0
        if len(msg) < 2:
            for line in lines:
                if line.startswith("#"): continue
                addSound = line.strip()
                soundLine = sounds.split("\n")[-1]
                sounds += self.line_up(soundLine, addSound)
                items += 1

        else:
            count = 0
            search = msg[1]
            for line in lines:
                if line.startswith("#"): continue
                addSound = line.strip()
                if search in addSound:
                    count += 1
                    soundLine = sounds.split("\n")[-1]
                    sounds += self.line_up(soundLine, addSound)
                    items += 1
            if count == 0:
                player.tell("^4Server^7: No sounds contain the search string ^1{}^7.".format(search))
                return
        if sounds.endswith("\n"):
            sounds += "^2{} ^4SOUNDS^7: ^3These are the sounds that work on this server.".format(items)
        else:
            sounds += "\n^2{} ^4SOUNDS^7: ^3These are the sounds that work on this server.".format(items)

        if "console" == channel:
            showConsole = sounds.split("\n")
            for line in showConsole:
                minqlx.console_print("^1" + line)
            return

        player.tell(sounds)
        return

    def line_up(self, soundLine, addSound):
        length = len(soundLine)
        if length == 0:
            append = addSound
        elif length < 14:
            append = " " * (14 - length) + addSound
        elif length < 29:
            append = " " * (29 - length) + addSound
        elif length < 44:
            append = " " * (44 - length) + addSound
        elif length < 59:
            append = " " * (59 - length) + addSound
        elif length < 74:
            append = " " * (74 - length) + addSound
        else:
            append = "\n" + addSound
        return append

    def find_sound_trigger(self, msg):
        #self.soundFile = ""
        msg_lower = msg.lower()
        if _re_hahaha_yeah.match(msg):
            self.soundFile = "sound/player/lucy/taunt.wav"
            return True
        elif _re_haha_yeah_haha.match(msg):
            self.soundFile = "sound/player/biker/taunt.wav"
            return True
        elif _re_yeah_hahaha.match(msg):
            self.soundFile = "sound/player/razor/taunt.wav"
            return True
        elif _re_duahahaha.match(msg):
            self.soundFile = "sound/player/keel/taunt.wav"
            return True
        elif _re_hahaha.search(msg):
            self.soundFile = "sound/player/santa/taunt.wav"
            return True
        elif _re_glhf.match(msg):
            self.soundFile ="sound/vo/crash_new/39_01.wav"
            return True
        elif _re_f3.match(msg):
            self.soundFile ="sound/vo/crash_new/36_04.wav"
            return True
        elif "holy shit" in msg_lower:
            self.soundFile ="sound/vo_female/holy_shit"
            return True
        elif _re_welcome.match(msg):
            self.soundFile ="sound/vo_evil/welcome"
            return True
        elif _re_go.match(msg):
            self.soundFile ="sound/vo/go"
            return True
        elif _re_beep_boop.match(msg):
            self.soundFile ="sound/player/tankjr/taunt.wav"
            return True
        elif _re_win.match(msg):
            self.soundFile ="sound/vo_female/you_win.wav"
            return True
        elif _re_lose.match(msg):
            self.soundFile ="sound/vo/you_lose.wav"
            return True
        elif "impressive" in msg_lower:
            self.soundFile ="sound/vo_female/impressive1.wav"
            return True
        elif "excellent" in msg_lower:
            self.soundFile ="sound/vo_evil/excellent1.wav"
            return True
        elif _re_denied.match(msg):
            self.soundFile ="sound/vo/denied"
            return True
        elif _re_balls_out.match(msg):
            self.soundFile ="sound/vo_female/balls_out"
            return True
        elif _re_one.match(msg):
            self.soundFile ="sound/vo_female/one"
            return True
        elif _re_two.match(msg):
            self.soundFile ="sound/vo_female/two"
            return True
        elif _re_three.match(msg):
            self.soundFile ="sound/vo_female/three"
            return True
        elif _re_fight.match(msg):
            self.soundFile ="sound/vo_evil/fight"
            return True
        elif _re_gauntlet.match(msg):
            self.soundFile ="sound/vo_evil/gauntlet"
            return True
        elif _re_humiliation.match(msg):
            self.soundFile ="sound/vo_evil/humiliation1"
            return True
        elif _re_perfect.match(msg):
            self.soundFile ="sound/vo_evil/perfect"
            return True
        elif _re_wah.match(msg):
            self.soundFile ="sound/misc/yousuck"
            return True
        elif _re_ah.match(msg):
            self.soundFile ="sound/player/slash/taunt.wav"
            return True
        elif _re_oink.match(msg):
            self.soundFile ="sound/player/sorlag/pain50_1.wav"
            return True
        elif _re_argh.match(msg):
            self.soundFile ="sound/player/doom/taunt.wav"
            return True
        elif _re_hah_haha.match(msg):
            self.soundFile ="sound/player/hunter/taunt.wav"
            return True
        elif _re_woohoo.match(msg):
            self.soundFile ="sound/player/janet/taunt.wav"
            return True
        elif _re_quakelive.match(msg):
            self.soundFile ="sound/vo_female/quake_live"
            return True
        elif _re_chaching.search(msg):
            self.soundFile ="sound/misc/chaching"
            return True
        elif _re_uh_ah.match(msg):
            self.soundFile ="sound/player/mynx/taunt.wav"
            return True
        elif _re_oohwee.match(msg):
            self.soundFile ="sound/player/anarki/taunt.wav"
            return True
        elif _re_erah.match(msg):
            self.soundFile ="sound/player/bitterman/taunt.wav"
            return True
        elif _re_yeahhh.match(msg):
            self.soundFile ="sound/player/major/taunt.wav"
            return True
        elif _re_scream.match(msg):
            self.soundFile ="sound/player/bones/taunt.wav"
            return True
        elif _re_salute.match(msg):
            self.soundFile ="sound/player/sarge/taunt.wav"
            return True
        elif _re_squish.match(msg):
            self.soundFile ="sound/player/orbb/taunt.wav"
            return True
        elif _re_oh_god.match(msg):
            self.soundFile ="sound/player/ranger/taunt.wav"
            return True
        elif _re_snarl.match(msg):
            self.soundFile ="sound/player/sorlag/taunt.wav"
            return True

        #Viewaskewer
        elif _re_assholes.match(msg):
            self.soundFile ="soundbank/assholes.ogg"
            return True
        elif _re_assshafter.match(msg):
            self.soundFile ="soundbank/assshafterloud.ogg"
            return True
        elif _re_babydoll.match(msg):
            self.soundFile ="soundbank/babydoll.ogg"
            return True
        elif _re_barelymissed.match(msg):
            self.soundFile ="soundbank/barelymissed.ogg"
            return True
        elif _re_belly.search(msg):
            self.soundFile ="soundbank/belly.ogg"
            return True
        elif _re_bitch.match(msg):
            self.soundFile ="soundbank/bitch.ogg"
            return True
        elif _re_blud.match(msg):
            self.soundFile ="soundbank/dtblud.ogg"
            return True
        elif _re_boats.match(msg):
            self.soundFile ="soundbank/boats.ogg"
            return True
        elif _re_bobg.match(msg):
            self.soundFile ="soundbank/bobg.ogg"
            return True
        elif _re_bogdog.match(msg):
            self.soundFile ="soundbank/bogdog.ogg"
            return True
        elif _re_boom.match(msg):
            self.soundFile ="soundbank/boom.ogg"
            return True
        elif _re_boom2.match(msg):
            self.soundFile ="soundbank/boom2.ogg"
            return True
        elif _re_buk.match(msg):
            self.soundFile ="soundbank/buk.ogg"
            return True
        elif _re_bullshit.match(msg):
            self.soundFile ="soundbank/bullshit.ogg"
            return True
        elif _re_butthole.match(msg):
            self.soundFile ="soundbank/butthole.ogg"
            return True
        elif _re_buttsex.match(msg):
            self.soundFile ="soundbank/buttsex.ogg"
            return True
        elif _re_cheeks.match(msg):
            self.soundFile ="soundbank/cheeks.ogg"
            return True
        elif _re_cocksucker.match(msg):
            self.soundFile ="soundbank/cocksucker.ogg"
            return True
        elif _re_conquer.match(msg):
            self.soundFile ="soundbank/conquer.ogg"
            return True
        elif _re_countdown.match(msg):
            self.soundFile ="soundbank/countdown.ogg"
            return True
        elif _re_cum.match(msg):
            self.soundFile ="soundbank/cum.ogg"
            return True
        elif _re_cumming.match(msg):
            self.soundFile ="soundbank/cumming.ogg"
            return True
        elif _re_cunt.match(msg):
            self.soundFile ="soundbank/cunt.ogg"
            return True
        elif _re_dirkfunk.match(msg):
            self.soundFile ="soundbank/dirkfunk.ogg"
            return True
        elif _re_disappointment.match(msg):
            self.soundFile ="soundbank/disappointment.ogg"
            return True
        elif _re_doom.match(msg):
            self.soundFile ="soundbank/doom.ogg"
            return True
        elif _re_drumset.match(msg):
            self.soundFile ="soundbank/drumset.ogg"
            return True
        elif _re_eat.match(msg):
            self.soundFile ="soundbank/eat.ogg"
            return True
        elif _re_eatme.match(msg):
            self.soundFile ="soundbank/eatme.ogg"
            return True
        elif _re_fag.match(msg):
            self.soundFile ="soundbank/fag.ogg"
            return True
        elif _re_fingerass.match(msg):
            self.soundFile ="soundbank/fingerass.ogg"
            return True
        elif _re_flash.match(msg):
            self.soundFile ="soundbank/flash.ogg"
            return True
        elif _re_fuckface.match(msg):
            self.soundFile ="soundbank/fuckface.ogg"
            return True
        elif _re_fuck_you.match(msg):
            self.soundFile ="soundbank/fuckyou.ogg"
            return True
        elif _re_getemm.match(msg):
            self.soundFile ="soundbank/getemm.ogg"
            return True
        elif _re_gonads.match(msg):
            self.soundFile ="soundbank/gonads.ogg"
            return True
        elif _re_gtfo.match(msg):
            self.soundFile ="soundbank/gtfo.ogg"
            return True
        elif _re_HIT.match(msg):
            self.soundFile ="soundbank/doom.ogg"
            return True
        elif _re_hugitout.match(msg):
            self.soundFile ="soundbank/hugitout.ogg"
            return True
        elif _re_idiot.match(msg):
            self.soundFile ="soundbank/idiot.ogg"
            return True
        elif _re_idiot2.match(msg):
            self.soundFile ="soundbank/idiot2.ogg"
            return True
        elif _re_itstime.match(msg):
            self.soundFile ="soundbank/itstime.ogg"
            return True
        elif _re_jeopardy.match(msg):
            self.soundFile ="soundbank/jeopardy.ogg"
            return True
        elif _re_jerkoff.match(msg):
            self.soundFile ="soundbank/jerkoff.ogg"
            return True
        elif _re_killo.match(msg):
            self.soundFile ="soundbank/killo.ogg"
            return True
        elif _re_knocked.match(msg):
            self.soundFile ="soundbank/knocked.ogg"
            return True
        elif _re_ld3.search(msg):
            self.soundFile ="soundbank/ld3.ogg"
            return True
        elif _re_liquidswords.match(msg):
            self.soundFile ="soundbank/liquid.ogg"
            return True
        elif _re_massacre.match(msg):
            self.soundFile ="soundbank/massacre.ogg"
            return True
        elif _re_mixer.match(msg):
            self.soundFile ="soundbank/mixer.ogg"
            return True
        elif _re_mjman.match(msg):
            self.soundFile ="soundbank/mjman.ogg"
            return True
        elif _re_mmmm.match(msg):
            self.soundFile ="soundbank/mmmm.ogg"
            return True
        elif _re_monty.match(msg):
            self.soundFile ="soundbank/monty.ogg"
            return True
        elif _re_n8.match(msg):
            self.soundFile ="soundbank/n8.ogg"
            return True
        elif _re_nikon.match(msg):
            self.soundFile ="soundbank/nikon.ogg"
            return True
        elif _re_nina.match(msg):
            self.soundFile ="soundbank/nina.ogg"
            return True
        elif _re_nthreem.match(msg):
            self.soundFile ="sound/vo_female/impressive1.wav"
            return True
        elif _re_olhip.match(msg):
            self.soundFile ="soundbank/hip.ogg"
            return True
        elif _re_organic.match(msg):
            self.soundFile ="soundbank/organic.ogg"
            return True
        elif _re_paintball.match(msg):
            self.soundFile ="soundbank/paintball.ogg"
            return True
        elif _re_pigfucker.match(msg):
            self.soundFile ="soundbank/pigfer.ogg"
            return True
        elif _re_popeye.match(msg):
            self.soundFile ="soundbank/popeye.ogg"
            return True
        elif _re_rosie.match(msg):
            self.soundFile ="soundbank/rosie.ogg"
            return True
        elif _re_seaweed.match(msg):
            self.soundFile ="soundbank/seaweed.ogg"
            return True
        elif _re_shit.match(msg):
            self.soundFile ="soundbank/shit.ogg"
            return True
        elif _re_sit.search(msg):
            self.soundFile ="soundbank/sit.ogg"
            return True
        elif _re_soulianis.search(msg):
            self.soundFile ="soundbank/soulianis.ogg"
            return True
        elif _re_spam.match(msg):
            self.soundFile ="soundbank/spam3.ogg"
            return True
        elif _re_stalin.match(msg):
            self.soundFile ="soundbank/ussr.ogg"
            return True
        elif _re_stfu.match(msg):
            self.soundFile ="soundbank/stfu.ogg"
            return True
        elif _re_suckadick.match(msg):
            self.soundFile ="soundbank/suckadick.ogg"
            return True
        elif _re_suckit.match(msg):
            self.soundFile ="soundbank/suckit.ogg"
            return True
        elif _re_suckmydick.match(msg):
            self.soundFile ="soundbank/suckmydick.ogg"
            return True
        elif _re_teapot.match(msg):
            self.soundFile ="soundbank/teapot.ogg"
            return True
        elif _re_thankgod.match(msg):
            self.soundFile ="soundbank/thankgod.ogg"
            return True
        elif _re_traxion.match(msg):
            self.soundFile ="soundbank/traxion.ogg"
            return True
        elif _re_trixy.match(msg):
            self.soundFile ="soundbank/trixy.ogg"
            return True
        elif _re_twoon.match(msg):
            self.soundFile ="soundbank/twoon.ogg"
            return True
        elif _re_ty.match(msg):
            self.soundFile ="soundbank/thankyou.ogg"
            return True
        elif _re_venny.match(msg):
            self.soundFile ="soundbank/venny.ogg"
            return True
        elif _re_viewaskewer.match(msg):
            self.soundFile ="soundbank/view.ogg"
            return True
        elif _re_whatsthat.match(msg):
            self.soundFile ="soundbank/whatsthat.ogg"
            return True
        elif _re_whoareyou.match(msg):
            self.soundFile ="soundbank/whoareyou.ogg"
            return True

        #|sf|bart`us's
        elif _re_007.match(msg):
            self.soundFile ="sound/funnysounds/007.ogg"
            return True
        elif _re_adamsfamily.match(msg):
            self.soundFile ="sound/funnysounds/adamsfamily.ogg"
            return True
        elif _re_allahuakbar.match(msg):
            self.soundFile ="sound/funnysounds/allahuakbar.ogg"
            return True
        elif _re_allstar.match(msg):
            self.soundFile ="sound/funnysounds/allstar.ogg"
            return True
        elif _re_AllTheThings.match(msg):
            self.soundFile ="sound/funnysounds/AllTheThings.ogg"
            return True
        elif _re_Amazing.match(msg):
            self.soundFile ="sound/funnysounds/Amazing.ogg"
            return True
        elif _re_Ameno.match(msg):
            self.soundFile ="sound/funnysounds/Ameno.ogg"
            return True
        elif _re_America.match(msg):
            self.soundFile ="sound/funnysounds/America.ogg"
            return True
        elif _re_Amerika.match(msg):
            self.soundFile ="sound/funnysounds/Amerika.ogg"
            return True
        elif _re_AndNothingElse.match(msg):
            self.soundFile ="sound/funnysounds/AndNothingElse.ogg"
            return True
        elif _re_Animals.match(msg):
            self.soundFile ="sound/funnysounds/Animals.ogg"
            return True
        elif _re_AScratch.match(msg):
            self.soundFile ="sound/funnysounds/AScratch.ogg"
            return True
        elif _re_asskicking.match(msg):
            self.soundFile ="sound/funnysounds/asskicking.ogg"
            return True
        elif _re_ave.match(msg):
            self.soundFile ="sound/funnysounds/ave.ogg"
            return True
        elif _re_babybaby.match(msg):
            self.soundFile ="sound/funnysounds/babybaby.ogg"
            return True
        elif _re_babyevillaugh.match(msg):
            self.soundFile ="sound/funnysounds/babyevillaugh.ogg"
            return True
        elif _re_babylaughing.match(msg):
            self.soundFile ="sound/funnysounds/babylaughing.ogg"
            return True
        elif _re_badboys.match(msg):
            self.soundFile ="sound/funnysounds/badboys.ogg"
            return True
        elif _re_BananaBoatSong.match(msg):
            self.soundFile ="sound/funnysounds/BananaBoatSong.ogg"
            return True
        elif _re_bennyhill.match(msg):
            self.soundFile ="sound/funnysounds/bennyhill.ogg"
            return True
        elif _re_benzin.match(msg):
            self.soundFile ="sound/funnysounds/benzin.ogg"
            return True
        elif _re_bluewins.match(msg):
            self.soundFile ="sound/funnysounds/bluewins.ogg"
            return True
        elif _re_bonkers.match(msg):
            self.soundFile ="sound/funnysounds/bonkers.ogg"
            return True
        elif _re_boomheadshot.match(msg):
            self.soundFile ="sound/funnysounds/boomheadshot.ogg"
            return True
        elif _re_booo.match(msg):
            self.soundFile ="sound/funnysounds/booo.ogg"
            return True
        elif _re_boring.match(msg):
            self.soundFile ="sound/funnysounds/boring.ogg"
            return True
        elif _re_boze.match(msg):
            self.soundFile ="sound/funnysounds/boze.ogg"
            return True
        elif _re_brightsideoflife.match(msg):
            self.soundFile ="sound/funnysounds/brightsideoflife.ogg"
            return True
        elif _re_buckdich.match(msg):
            self.soundFile ="sound/funnysounds/buckdich.ogg"
            return True
        elif _re_bullshitter.match(msg):
            self.soundFile ="sound/funnysounds/bullshitter.ogg"
            return True
        elif _re_burnsburns.match(msg):
            self.soundFile ="sound/funnysounds/burnsburns.ogg"
            return True
        elif _re_cameltoe.match(msg):
            self.soundFile ="sound/funnysounds/cameltoe.ogg"
            return True
        elif _re_canttouchthis.match(msg):
            self.soundFile ="sound/funnysounds/canttouchthis.ogg"
            return True
        elif _re_cccp.match(msg):
            self.soundFile ="sound/funnysounds/cccp.ogg"
            return True
        elif _re_champions.match(msg):
            self.soundFile ="sound/funnysounds/champions.ogg"
            return True
        elif _re_chicken.match(msg):
            self.soundFile ="sound/funnysounds/chicken.ogg"
            return True
        elif _re_chocolaterain.match(msg):
            self.soundFile ="sound/funnysounds/chocolaterain.ogg"
            return True
        elif _re_coin.match(msg):
            self.soundFile ="sound/funnysounds/coin.ogg"
            return True
        elif _re_come.match(msg):
            self.soundFile ="sound/funnysounds/come.ogg"
            return True
        elif _re_ComeWithMeNow.match(msg):
            self.soundFile ="sound/funnysounds/ComeWithMeNow.ogg"
            return True
        elif _re_Count_down.match(msg):
            self.soundFile ="sound/funnysounds/Countdown.ogg"
            return True
        elif _re_cowards.match(msg):
            self.soundFile ="sound/funnysounds/cowards.ogg"
            return True
        elif _re_crazy.match(msg):
            self.soundFile ="sound/funnysounds/crazy.ogg"
            return True
        elif _re_yacunt.match(msg):
            self.soundFile ="sound/funnysounds/cunt.ogg"
            return True
        elif _re_damnit.match(msg):
            self.soundFile ="sound/funnysounds/damnit.ogg"
            return True
        elif _re_DangerZone.match(msg):
            self.soundFile ="sound/funnysounds/DangerZone.ogg"
            return True
        elif _re_deadsoon.match(msg):
            self.soundFile ="sound/funnysounds/deadsoon.ogg"
            return True
        elif _re_defeated.match(msg):
            self.soundFile ="sound/funnysounds/defeated.ogg"
            return True
        elif _re_devil.match(msg):
            self.soundFile ="sound/funnysounds/devil.ogg"
            return True
        elif _re_doesntloveyou.match(msg):
            self.soundFile ="sound/funnysounds/doesntloveyou.ogg"
            return True
        elif _re_dubist.match(msg):
            self.soundFile ="sound/funnysounds/dubist.ogg"
            return True
        elif _re_duhast.match(msg):
            self.soundFile ="sound/funnysounds/duhast.ogg"
            return True
        elif _re_dumbways.match(msg):
            self.soundFile ="sound/funnysounds/dumbways.ogg"
            return True
        elif _re_EatPussy.match(msg):
            self.soundFile ="sound/funnysounds/EatPussy.ogg"
            return True
        elif _re_education.match(msg):
            self.soundFile ="sound/funnysounds/education.ogg"
            return True
        elif _re_einschrei.match(msg):
            self.soundFile ="sound/funnysounds/einschrei.ogg"
            return True
        elif _re_EinsZwei.match(msg):
            self.soundFile ="sound/funnysounds/EinsZwei.ogg"
            return True
        elif _re_electro.match(msg):
            self.soundFile ="sound/funnysounds/electro.ogg"
            return True
        elif _re_elementary.match(msg):
            self.soundFile ="sound/funnysounds/elementary.ogg"
            return True
        elif _re_engel.match(msg):
            self.soundFile ="sound/funnysounds/engel.ogg"
            return True
        elif _re_erstwenn.match(msg):
            self.soundFile ="sound/funnysounds/erstwenn.ogg"
            return True
        elif _re_exitlight.match(msg):
            self.soundFile ="sound/funnysounds/exitlight.ogg"
            return True
        elif _re_faint.match(msg):
            self.soundFile ="sound/funnysounds/faint.ogg"
            return True
        elif _re_fatality.match(msg):
            self.soundFile ="sound/funnysounds/fatality.ogg"
            return True
        elif _re_FeelGood.match(msg):
            self.soundFile ="sound/funnysounds/FeelGood.ogg"
            return True
        elif _re_fleshwound.match(msg):
            self.soundFile ="sound/funnysounds/fleshwound.ogg"
            return True
        elif _re_foryou.match(msg):
            self.soundFile ="sound/funnysounds/foryou.ogg"
            return True
        elif _re_freestyler.match(msg):
            self.soundFile ="sound/funnysounds/freestyler.ogg"
            return True
        elif _re_fuckfuck.match(msg):
            self.soundFile ="sound/funnysounds/fuckfuck.ogg"
            return True
        elif _re_fuckingburger.match(msg):
            self.soundFile ="sound/funnysounds/fuckingburger.ogg"
            return True
        elif _re_fuckingkids.match(msg):
            self.soundFile ="sound/funnysounds/fuckingkids.ogg"
            return True
        elif _re_gangnam.match(msg):
            self.soundFile ="sound/funnysounds/gangnam.ogg"
            return True
        elif _re_ganjaman.match(msg):
            self.soundFile ="sound/funnysounds/ganjaman.ogg"
            return True
        elif _re_gay.match(msg):
            self.soundFile ="sound/funnysounds/gay.ogg"
            return True
        elif _re_getcrowbar.match(msg):
            self.soundFile ="sound/funnysounds/getcrowbar.ogg"
            return True
        elif _re_getouttheway.match(msg):
            self.soundFile ="sound/funnysounds/getouttheway.ogg"
            return True
        elif _re_ghostbusters.match(msg):
            self.soundFile ="sound/funnysounds/ghostbusters.ogg"
            return True
        elif _re_girllook.match(msg):
            self.soundFile ="sound/funnysounds/girllook.ogg"
            return True
        elif _re_girly.match(msg):
            self.soundFile ="sound/funnysounds/girly.ogg"
            return True
        elif _re_gnrguitar.match(msg):
            self.soundFile ="sound/funnysounds/gnrguitar.ogg"
            return True
        elif _re_goddamnright.match(msg):
            self.soundFile ="sound/funnysounds/goddamnright.ogg"
            return True
        elif _re_goodbyeandrea.match(msg):
            self.soundFile ="sound/funnysounds/goodbyeandrea.ogg"
            return True
        elif _re_goodbyesarah.match(msg):
            self.soundFile ="sound/funnysounds/goodbyesarah.ogg"
            return True
        elif _re_gotcha.match(msg):
            self.soundFile ="sound/funnysounds/gotcha.ogg"
            return True
        elif _re_hakunamatata.match(msg):
            self.soundFile ="sound/funnysounds/hakunamatata.ogg"
            return True
        elif _re_hammertime.match(msg):
            self.soundFile ="sound/funnysounds/hammertime.ogg"
            return True
        elif _re_hello.match(msg):
            self.soundFile ="sound/funnysounds/hello.ogg"
            return True
        elif _re_hellstestern.match(msg):
            self.soundFile ="sound/funnysounds/hellstestern.ogg"
            return True
        elif _re_holy.match(msg):
            self.soundFile ="sound/funnysounds/holy.ogg"
            return True
        elif _re_hoppereiter.match(msg):
            self.soundFile ="sound/funnysounds/hoppereiter.ogg"
            return True
        elif _re_howareyou.match(msg):
            self.soundFile ="sound/funnysounds/howareyou.ogg"
            return True
        elif _re_hush.match(msg):
            self.soundFile ="sound/funnysounds/hush.ogg"
            return True
        elif _re_ibet.match(msg):
            self.soundFile ="sound/funnysounds/ibet.ogg"
            return True
        elif _re_icantbelieve.match(msg):
            self.soundFile ="sound/funnysounds/icantbelieve.ogg"
            return True
        elif _re_ichtuedieweh.match(msg):
            self.soundFile ="sound/funnysounds/ichtuedieweh.ogg"
            return True
        elif _re_idoparkour.match(msg):
            self.soundFile ="sound/funnysounds/idoparkour.ogg"
            return True
        elif _re_ihateall.match(msg):
            self.soundFile ="sound/funnysounds/ihateall.ogg"
            return True
        elif _re_illbeback.match(msg):
            self.soundFile ="sound/funnysounds/beback.ogg"
            return True
        elif _re_imperial.match(msg):
            self.soundFile ="sound/funnysounds/imperial.ogg"
            return True
        elif _re_imsexy.match(msg):
            self.soundFile ="sound/funnysounds/imsexy.ogg"
            return True
        elif _re_imyourfather.match(msg):
            self.soundFile ="sound/funnysounds/imyourfather.ogg"
            return True
        elif _re_incoming.match(msg):
            self.soundFile ="sound/funnysounds/incoming.ogg"
            return True
        elif _re_indianajones.match(msg):
            self.soundFile ="sound/funnysounds/indianajones.ogg"
            return True
        elif _re_inyourheadzombie.match(msg):
            self.soundFile ="sound/funnysounds/inyourheadzombie.ogg"
            return True
        elif _re_iseeassholes.match(msg):
            self.soundFile ="sound/funnysounds/iseeassholes.ogg"
            return True
        elif _re_iseedeadpeople.match(msg):
            self.soundFile ="sound/funnysounds/iseedeadpeople.ogg"
            return True
        elif _re_itsmylife.match(msg):
            self.soundFile ="sound/funnysounds/itsmylife.ogg"
            return True
        elif _re_itsnot.match(msg):
            self.soundFile ="sound/funnysounds/itsnot.ogg"
            return True
        elif _re_jackpot.match(msg):
            self.soundFile ="sound/funnysounds/jackpot.ogg"
            return True
        elif _re_jesus.match(msg):
            self.soundFile ="sound/funnysounds/jesus.ogg"
            return True
        elif _re_jesusOh.match(msg):
            self.soundFile ="sound/funnysounds/JesusOh.ogg"
            return True
        elif _re_johncena.match(msg):
            self.soundFile ="sound/funnysounds/johncena.ogg"
            return True
        elif _re_jumpmotherfucker.match(msg):
            self.soundFile ="sound/funnysounds/jumpmotherfucker.ogg"
            return True
        elif _re_justdoit.match(msg):
            self.soundFile ="sound/funnysounds/justdoit.ogg"
            return True
        elif _re_kamehameha.match(msg):
            self.soundFile ="sound/funnysounds/kamehameha.ogg"
            return True
        elif _re_keeponfighting.match(msg):
            self.soundFile ="sound/funnysounds/keeponfighting.ogg"
            return True
        elif _re_keepyourshirton.match(msg):
            self.soundFile ="sound/funnysounds/keepyourshirton.ogg"
            return True
        elif _re_KnockedDown.match(msg):
            self.soundFile ="sound/funnysounds/KnockedDown.ogg"
            return True
        elif _re_kommtdiesonne.match(msg):
            self.soundFile ="sound/funnysounds/kommtdiesonne.ogg"
            return True
        elif _re_kungfu.match(msg):
            self.soundFile ="sound/funnysounds/kungfu.ogg"
            return True
        elif _re_lately.match(msg):
            self.soundFile ="sound/funnysounds/lately.ogg"
            return True
        elif _re_Legitness.match(msg):
            self.soundFile ="sound/funnysounds/Legitness.ogg"
            return True
        elif _re_letsgetready.match(msg):
            self.soundFile ="sound/funnysounds/letsgetready.ogg"
            return True
        elif _re_letsputasmile.match(msg):
            self.soundFile ="sound/funnysounds/letsputasmile.ogg"
            return True
        elif _re_lightsout.match(msg):
            self.soundFile ="sound/funnysounds/lightsout.ogg"
            return True
        elif _re_lionking.match(msg):
            self.soundFile ="sound/funnysounds/lionking.ogg"
            return True
        elif _re_livetowin.match(msg):
            self.soundFile ="sound/funnysounds/livetowin.ogg"
            return True
        elif _re_losingmyreligion.match(msg):
            self.soundFile ="sound/funnysounds/losingmyreligion.ogg"
            return True
        elif _re_loveme.match(msg):
            self.soundFile ="sound/funnysounds/loveme.ogg"
            return True
        elif _re_low.match(msg):
            self.soundFile ="sound/funnysounds/low.ogg"
            return True
        elif _re_luck.match(msg):
            self.soundFile ="sound/funnysounds/luck.ogg"
            return True
        elif _re_lust.match(msg):
            self.soundFile ="sound/funnysounds/lust.ogg"
            return True
        elif _re_mahnamahna.match(msg):
            self.soundFile ="sound/funnysounds/mahnamahna.ogg"
            return True
        elif _re_mario.match(msg):
            self.soundFile ="sound/funnysounds/mario.ogg"
            return True
        elif _re_Me.match(msg):
            self.soundFile ="sound/funnysounds/Me.ogg"
            return True
        elif _re_meinland.match(msg):
            self.soundFile ="sound/funnysounds/meinland.ogg"
            return True
        elif _re_message.match(msg):
            self.soundFile ="sound/funnysounds/message.ogg"
            return True
        elif _re_mimimi.match(msg):
            self.soundFile ="sound/funnysounds/mimimi.ogg"
            return True
        elif _re_mission.match(msg):
            self.soundFile ="sound/funnysounds/mission.ogg"
            return True
        elif _re_moan.match(msg):
            self.soundFile ="sound/funnysounds/moan.ogg"
            return True
        elif _re_mortalkombat.match(msg):
            self.soundFile ="sound/funnysounds/mortalkombat.ogg"
            return True
        elif _re_moveass.match(msg):
            self.soundFile ="sound/funnysounds/moveass.ogg"
            return True
        elif _re_muppetopening.match(msg):
            self.soundFile ="sound/funnysounds/muppetopening.ogg"
            return True
        elif _re_mylittlepony.match(msg):
            self.soundFile ="sound/funnysounds/mylittlepony.ogg"
            return True
        elif _re_myname.match(msg):
            self.soundFile ="sound/funnysounds/myname.ogg"
            return True
        elif _re_neverseen.match(msg):
            self.soundFile ="sound/funnysounds/neverseen.ogg"
            return True
        elif _re_nightmare.match(msg):
            self.soundFile ="sound/funnysounds/nightmare.ogg"
            return True
        elif _re_nobodylikesyou.match(msg):
            self.soundFile ="sound/funnysounds/nobodylikesyou.ogg"
            return True
        elif _re_nonie.match(msg):
            self.soundFile ="sound/funnysounds/nonie.ogg"
            return True
        elif _re_nooo.match(msg):
            self.soundFile ="sound/funnysounds/nooo.ogg"
            return True
        elif _re_notimeforloosers.match(msg):
            self.soundFile ="sound/funnysounds/notimeforloosers.ogg"
            return True
        elif _re_numanuma.match(msg):
            self.soundFile ="sound/funnysounds/numanuma.ogg"
            return True
        elif _re_nyancat.match(msg):
            self.soundFile ="sound/funnysounds/nyancat.ogg"
            return True
        elif _re_ofuck.match(msg):
            self.soundFile ="sound/funnysounds/ofuck.ogg"
            return True
        elif _re_ohmygod.match(msg):
            self.soundFile ="sound/funnysounds/ohmygod.ogg"
            return True
        elif _re_OhMyGosh.match(msg):
            self.soundFile ="sound/funnysounds/OhMyGosh.ogg"
            return True
        elif _re_ohnedich.match(msg):
            self.soundFile ="sound/funnysounds/ohnedich.ogg"
            return True
        elif _re_ohno.match(msg):
            self.soundFile ="sound/funnysounds/ohno.ogg"
            return True
        elif _re_ohnoe.match(msg):
            self.soundFile ="sound/funnysounds/ohnoe.ogg"
            return True
        elif _re_pacman.match(msg):
            self.soundFile ="sound/funnysounds/pacman.ogg"
            return True
        elif _re_pickmeup.match(msg):
            self.soundFile ="sound/funnysounds/pickmeup.ogg"
            return True
        elif _re_pikachu.match(msg):
            self.soundFile ="sound/funnysounds/pikachu.ogg"
            return True
        elif _re_pinkiepie.match(msg):
            self.soundFile ="sound/funnysounds/pinkiepie.ogg"
            return True
        elif _re_PinkPanther.match(msg):
            self.soundFile ="sound/funnysounds/PinkPanther.ogg"
            return True
        elif _re_pipe.match(msg):
            self.soundFile ="sound/funnysounds/pipe.ogg"
            return True
        elif _re_pissmeoff.match(msg):
            self.soundFile ="sound/funnysounds/pissmeoff.ogg"
            return True
        elif _re_playagame.match(msg):
            self.soundFile ="sound/funnysounds/playagame.ogg"
            return True
        elif _re_pooping.match(msg):
            self.soundFile ="sound/funnysounds/pooping.ogg"
            return True
        elif _re_powerpuff.match(msg):
            self.soundFile ="sound/funnysounds/powerpuff.ogg"
            return True
        elif _re_radioactive.match(msg):
            self.soundFile ="sound/funnysounds/radioactive.ogg"
            return True
        elif _re_rammsteinriff.match(msg):
            self.soundFile ="sound/funnysounds/rammsteinriff.ogg"
            return True
        elif _re_redwins.match(msg):
            self.soundFile ="sound/funnysounds/redwins.ogg"
            return True
        elif _re_renegade.match(msg):
            self.soundFile ="sound/funnysounds/renegade.ogg"
            return True
        elif _re_retard.match(msg):
            self.soundFile ="sound/funnysounds/retard.ogg"
            return True
        elif _re_rocky.match(msg):
            self.soundFile ="sound/funnysounds/rocky"
            return True
        elif _re_rockyouguitar.match(msg):
            self.soundFile ="sound/funnysounds/rockyouguitar.ogg"
            return True
        elif _re_SkeetSkeet.match(msg):
            self.soundFile ="sound/funnysounds/AllSkeetSkeet.ogg"
            return True
        elif _re_sail.match(msg):
            self.soundFile ="sound/funnysounds/sail.ogg"
            return True
        elif _re_Salil.match(msg):
            self.soundFile ="sound/funnysounds/Salil.ogg"
            return True
        elif _re_samba.match(msg):
            self.soundFile ="sound/funnysounds/samba.ogg"
            return True
        elif _re_sandstorm.match(msg):
            self.soundFile ="sound/funnysounds/sandstorm.ogg"
            return True
        elif _re_saymyname.match(msg):
            self.soundFile ="sound/funnysounds/saymyname.ogg"
            return True
        elif _re_scatman.match(msg):
            self.soundFile ="sound/funnysounds/scatman.ogg"
            return True
        elif _re_sellyouall.match(msg):
            self.soundFile ="sound/funnysounds/sellyouall.ogg"
            return True
        elif _re_senseofhumor.match(msg):
            self.soundFile ="sound/funnysounds/senseofhumor.ogg"
            return True
        elif _re_shakesenora.match(msg):
            self.soundFile ="sound/funnysounds/shakesenora.ogg"
            return True
        elif _re_shutthefuckup.match(msg):
            self.soundFile ="sound/funnysounds/shutthefuckup.ogg"
            return True
        elif _re_shutyourfuckingmouth.match(msg):
            self.soundFile ="sound/funnysounds/shutyourfuckingmouth.ogg"
            return True
        elif _re_silence.match(msg):
            self.soundFile ="sound/funnysounds/silence.ogg"
            return True
        elif _re_smoothcriminal.match(msg):
            self.soundFile ="sound/funnysounds/smoothcriminal.ogg"
            return True
        elif _re_socobatevira.match(msg):
            self.soundFile ="sound/funnysounds/socobatevira.ogg"
            return True
        elif _re_socobateviraend.match(msg):
            self.soundFile ="sound/funnysounds/socobateviraend.ogg"
            return True
        elif _re_socobatevirafast.match(msg):
            self.soundFile ="sound/funnysounds/socobatevirafast.ogg"
            return True
        elif _re_socobateviraslow.match(msg):
            self.soundFile ="sound/funnysounds/socobateviraslow.ogg"
            return True
        elif _re_sogivemereason.match(msg):
            self.soundFile ="sound/funnysounds/sogivemereason.ogg"
            return True
        elif _re_sostupid.match(msg):
            self.soundFile ="sound/funnysounds/sostupid.ogg"
            return True
        elif _re_SpaceJam.match(msg):
            self.soundFile ="sound/funnysounds/SpaceJam.ogg"
            return True
        elif _re_spaceunicorn.match(msg):
            self.soundFile ="sound/funnysounds/spaceunicorn.ogg"
            return True
        elif _re_spierdalaj.match(msg):
            self.soundFile ="sound/funnysounds/spierdalaj.ogg"
            return True
        elif _re_stampon.match(msg):
            self.soundFile ="sound/funnysounds/stampon.ogg"
            return True
        elif _re_starwars.match(msg):
            self.soundFile ="sound/funnysounds/starwars.ogg"
            return True
        elif _re_stayinalive.match(msg):
            self.soundFile ="sound/funnysounds/stayinalive.ogg"
            return True
        elif _re_stoning.match(msg):
            self.soundFile ="sound/funnysounds/stoning.ogg"
            return True
        elif _re_Stop.match(msg):
            self.soundFile ="sound/funnysounds/Stop.ogg"
            return True
        elif _re_story.match(msg):
            self.soundFile ="sound/funnysounds/story.ogg"
            return True
        elif _re_surprise.match(msg):
            self.soundFile ="sound/funnysounds/surprise.ogg"
            return True
        elif _re_swedishchef.match(msg):
            self.soundFile ="sound/funnysounds/swedishchef.ogg"
            return True
        elif _re_sweetdreams.match(msg):
            self.soundFile ="sound/funnysounds/sweetdreams.ogg"
            return True
        elif _re_takemedown.match(msg):
            self.soundFile ="sound/funnysounds/takemedown.ogg"
            return True
        elif _re_talkscotish.match(msg):
            self.soundFile ="sound/funnysounds/talkscotish.ogg"
            return True
        elif _re_teamwork.match(msg):
            self.soundFile ="sound/funnysounds/teamwork.ogg"
            return True
        elif _re_technology.match(msg):
            self.soundFile ="sound/funnysounds/technology.ogg"
            return True
        elif _re_thisissparta.match(msg):
            self.soundFile ="sound/funnysounds/thisissparta.ogg"
            return True
        elif _re_thunderstruck.match(msg):
            self.soundFile ="sound/funnysounds/thunderstruck.ogg"
            return True
        elif _re_tochurch.match(msg):
            self.soundFile ="sound/funnysounds/tochurch.ogg"
            return True
        elif _re_tsunami.match(msg):
            self.soundFile ="sound/funnysounds/tsunami.ogg"
            return True
        elif _re_tuturu.match(msg):
            self.soundFile ="sound/funnysounds/tuturu.ogg"
            return True
        elif _re_tututu.match(msg):
            self.soundFile ="sound/funnysounds/tututu.ogg"
            return True
        elif _re_unbelievable.match(msg):
            self.soundFile ="sound/funnysounds/unbelievable.ogg"
            return True
        elif _re_undderhaifisch.match(msg):
            self.soundFile ="sound/funnysounds/undderhaifisch.ogg"
            return True
        elif _re_uptowngirl.match(msg):
            self.soundFile ="sound/funnysounds/uptowngirl.ogg"
            return True
        elif _re_valkyries.match(msg):
            self.soundFile ="sound/funnysounds/valkyries.ogg"
            return True
        elif _re_wahwahwah.search(msg):
            self.soundFile ="sound/funnysounds/wahwahwah.ogg"
            return True
        elif _re_wantyou.match(msg):
            self.soundFile ="sound/funnysounds/wantyou.ogg"
            return True
        elif _re_wazzup.match(msg):
            self.soundFile ="sound/funnysounds/wazzup.ogg"
            return True
        elif _re_wehmirohweh.match(msg):
            self.soundFile ="sound/funnysounds/wehmirohweh.ogg"
            return True
        elif _re_whatislove.match(msg):
            self.soundFile ="sound/funnysounds/whatislove.ogg"
            return True
        elif _re_whenangels.match(msg):
            self.soundFile ="sound/funnysounds/whenangels.ogg"
            return True
        elif _re_whereareyou.match(msg):
            self.soundFile ="sound/funnysounds/whereareyou.ogg"
            return True
        elif _re_whistle.match(msg):
            self.soundFile ="sound/funnysounds/whistle.ogg"
            return True
        elif _re_WillBeSinging.match(msg):
            self.soundFile ="sound/funnysounds/WillBeSinging.ogg"
            return True
        elif _re_wimbaway.match(msg):
            self.soundFile ="sound/funnysounds/wimbaway.ogg"
            return True
        elif _re_windows.match(msg):
            self.soundFile ="sound/funnysounds/windows.ogg"
            return True
        elif _re_wouldyoulike.match(msg):
            self.soundFile ="sound/funnysounds/wouldyoulike.ogg"
            return True
        elif _re_wtf.match(msg):
            self.soundFile ="sound/funnysounds/wtf.ogg"
            return True
        elif _re_yeee.match(msg):
            self.soundFile ="sound/funnysounds/yeee.ogg"
            return True
        elif _re_yesmaster.match(msg):
            self.soundFile ="sound/funnysounds/yesmaster.ogg"
            return True
        elif _re_yhehehe.match(msg):
            self.soundFile ="sound/funnysounds/yhehehe.ogg"
            return True
        elif _re_ymca.match(msg):
            self.soundFile ="sound/funnysounds/ymca.ogg"
            return True
        elif _re_You.match(msg):
            self.soundFile ="sound/funnysounds/You.ogg"
            return True
        elif _re_youfuckedmywife.match(msg):
            self.soundFile ="sound/funnysounds/youfuckedmywife.ogg"
            return True
        elif _re_YouRealise.match(msg):
            self.soundFile ="sound/funnysounds/YouRealise.ogg"
            return True

        #Duke Nukem
        elif _re_myride.match(msg):
            self.soundFile ="sound/duke/2ride06.wav"
            return True
        elif _re_abort.match(msg):
            self.soundFile ="sound/duke/abort01.wav"
            return True
        elif _re_ahhh.match(msg):
            self.soundFile ="sound/duke/ahh04.wav"
            return True
        elif _re_muchbetter.match(msg):
            self.soundFile ="sound/duke/ahmuch03.wav"
            return True
        elif _re_aisle4.match(msg):
            self.soundFile ="sound/duke/aisle402.wav"
            return True
        elif _re_amess.match(msg):
            self.soundFile ="sound/duke/amess06.wav"
            return True
        elif _re_annoying.match(msg):
            self.soundFile ="sound/duke/annoy03.wav"
            return True
        elif _re_bitchin.match(msg):
            self.soundFile ="sound/duke/bitchn04.wav"
            return True
        elif _re_blowitout.match(msg):
            self.soundFile ="sound/duke/blowit01.wav"
            return True
        elif _re_boobytrap.match(msg):
            self.soundFile ="sound/duke/booby04.wav"
            return True
        elif _re_bookem.match(msg):
            self.soundFile ="sound/duke/bookem03.wav"
            return True
        elif _re_borntobewild.match(msg):
            self.soundFile ="sound/duke/born01.wav"
            return True
        elif _re_chewgum.match(msg):
            self.soundFile ="sound/duke/chew05.wav"
            return True
        elif _re_comeon.match(msg):
            self.soundFile ="sound/duke/comeon02.wav"
            return True
        elif _re_thecon.match(msg):
            self.soundFile ="sound/duke/con03.wav"
            return True
        elif _re_cool.match(msg):
            self.soundFile ="sound/duke/cool01.wav"
            return True
        elif _re_notcrying.match(msg):
            self.soundFile ="sound/duke/cry01.wav"
            return True
        elif _re_daamn.match(msg):
            self.soundFile ="sound/duke/damn03.wav"
            return True
        elif _re_damit.match(msg):
            self.soundFile ="sound/duke/damnit04.wav"
            return True
        elif _re_dance.match(msg):
            self.soundFile ="sound/duke/dance01.wav"
            return True
        elif _re_diesob.match(msg):
            self.soundFile ="sound/duke/diesob03.wav"
            return True
        elif _re_doomed.match(msg):
            self.soundFile ="sound/duke/doomed16.wav"
            return True
        elif _re_eyye.match(msg):
            self.soundFile ="sound/duke/dscrem38.wav"
            return True
        elif _re_dukenukem.match(msg):
            self.soundFile ="sound/duke/duknuk14.wav"
            return True
        elif _re_noway.match(msg):
            self.soundFile ="sound/duke/eat08.wav"
            return True
        elif _re_eatshit.match(msg):
            self.soundFile ="sound/duke/eatsht01.wav"
            return True
        elif _re_escape.match(msg):
            self.soundFile ="sound/duke/escape01.wav"
            return True
        elif _re_faceass.match(msg):
            self.soundFile ="sound/duke/face01.wav"
            return True
        elif _re_aforce.match(msg):
            self.soundFile ="sound/duke/force01.wav"
            return True
        elif _re_getcrap.match(msg):
            self.soundFile ="sound/duke/getcrap1.wav"
            return True
        elif _re_getsome.match(msg):
            self.soundFile ="sound/duke/getsom1a.wav"
            return True
        elif _re_gameover.match(msg):
            self.soundFile ="sound/duke/gmeovr05.wav"
            return True
        elif _re_gottahurt.match(msg):
            self.soundFile ="sound/duke/gothrt01.wav"
            return True
        elif _re_groovy.match(msg):
            self.soundFile ="sound/duke/groovy02.wav"
            return True
        elif _re_guyssuck.match(msg):
            self.soundFile ="sound/duke/guysuk01.wav"
            return True
        elif _re_hailking.match(msg):
            self.soundFile ="sound/duke/hail01.wav"
            return True
        elif _re_shithappens.match(msg):
            self.soundFile ="sound/duke/happen01.wav"
            return True
        elif _re_holycow.match(msg):
            self.soundFile ="sound/duke/holycw01.wav"
            return True
        elif _re_holyshit.match(msg):
            self.soundFile ="sound/duke/holysh02.wav"
            return True
        elif _re_imgood.match(msg):
            self.soundFile ="sound/duke/imgood12.wav"
            return True
        elif _re_independence.match(msg):
            self.soundFile ="sound/duke/indpnc01.wav"
            return True
        elif _re_inhell.match(msg):
            self.soundFile ="sound/duke/inhell01.wav"
            return True
        elif _re_goingin.match(msg):
            self.soundFile ="sound/duke/introc.wav"
            return True
        elif _re_drjones.match(msg):
            self.soundFile ="sound/duke/jones04.wav"
            return True
        elif _re_kickyourass.match(msg):
            self.soundFile ="sound/duke/kick01-i.wav"
            return True
        elif _re_ktit.match(msg):
            self.soundFile ="sound/duke/ktitx.wav"
            return True
        elif _re_letgod.match(msg):
            self.soundFile ="sound/duke/letgod01.wav"
            return True
        elif _re_letsrock.match(msg):
            self.soundFile ="sound/duke/letsrk03.wav"
            return True
        elif _re_lookingood.match(msg):
            self.soundFile ="sound/duke/lookin01.wav"
            return True
        elif _re_makemyday.match(msg):
            self.soundFile ="sound/duke/makeday1.wav"
            return True
        elif _re_midevil.match(msg):
            self.soundFile ="sound/duke/mdevl01.wav"
            return True
        elif _re_mymeat.match(msg):
            self.soundFile ="sound/duke/meat04-n.wav"
            return True
        elif _re_notime.match(msg):
            self.soundFile ="sound/duke/myself3a.wav"
            return True
        elif _re_neededthat.match(msg):
            self.soundFile ="sound/duke/needed03.wav"
            return True
        elif _re_nobody.match(msg):
            self.soundFile ="sound/duke/nobody01.wav"
            return True
        elif _re_onlyone.match(msg):
            self.soundFile ="sound/duke/onlyon03.wav"
            return True
        elif _re_mykindaparty.match(msg):
            self.soundFile ="sound/duke/party03.wav"
            return True
        elif _re_gonnapay.match(msg):
            self.soundFile ="sound/duke/pay02.wav"
            return True
        elif _re_pissesmeoff.match(msg):
            self.soundFile ="sound/duke/pisses01.wav"
            return True
        elif _re_pissinmeoff.match(msg):
            self.soundFile ="sound/duke/pissin01.wav"
            return True
        elif _re_postal.match(msg):
            self.soundFile ="sound/duke/postal01.wav"
            return True
        elif _re_aintafraid.match(msg):
            self.soundFile ="sound/duke/quake06.wav"
            return True
        elif _re_randr.match(msg):
            self.soundFile ="sound/duke/r&r01.wav"
            return True
        elif _re_readyforaction.match(msg):
            self.soundFile ="sound/duke/ready2a.wav"
            return True
        elif _re_ripheadoff.match(msg):
            self.soundFile ="sound/duke/rip01.wav"
            return True
        elif _re_ripem.match(msg):
            self.soundFile ="sound/duke/ripem08.wav"
            return True
        elif _re_rockin.match(msg):
            self.soundFile ="sound/duke/rockin02.wav"
            return True
        elif _re_shakeit.match(msg):
            self.soundFile ="sound/duke/shake2a.wav"
            return True
        elif _re_slacker.match(msg):
            self.soundFile ="sound/duke/slacker1.wav"
            return True
        elif _re_smackdab.match(msg):
            self.soundFile ="sound/duke/smack02.wav"
            return True
        elif _re_sohelpme.match(msg):
            self.soundFile ="sound/duke/sohelp02.wav"
            return True
        elif _re_suckitdown.match(msg):
            self.soundFile ="sound/duke/sukit01.wav"
            return True
        elif _re_terminated.match(msg):
            self.soundFile ="sound/duke/termin01.wav"
            return True
        elif _re_thissucks.match(msg):
            self.soundFile ="sound/duke/thsuk13a.wav"
            return True
        elif _re_vacation.match(msg):
            self.soundFile ="sound/duke/vacatn01.wav"
            return True
        elif _re_christmas.match(msg):
            self.soundFile ="sound/duke/waitin03.wav"
            return True
        elif _re_wnatssome.match(msg):
            self.soundFile ="sound/duke/wansom4a.wav"
            return True
        elif _re_youandme.match(msg):
            self.soundFile ="sound/duke/whipyu01.wav"
            return True
        elif _re_where.match(msg):
            self.soundFile ="sound/duke/whrsit05.wav"
            return True
        elif _re_yippiekaiyay.match(msg):
            self.soundFile ="sound/duke/yippie01.wav"
            return True
        elif _re_bottleofjack.match(msg):
            self.soundFile ="sound/duke/yohoho01.wav"
            return True
        elif _re_longwalk.match(msg):
            self.soundFile ="sound/duke/yohoho09.wav"
            return True
        return False
