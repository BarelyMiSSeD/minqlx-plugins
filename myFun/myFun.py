# This plugin is a modification of minqlx's fun.py
# https://github.com/MinoMino/minqlx

# Created by BarelyMiSSeD
# https://github.com/BarelyMiSSeD

# You are free to modify this plugin
# This plugin comes with no warranty or guarantee

"""
This plugin plays sounds on the Quake Live server
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
VERSION = 1.1

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
_re_ld3 = re.compile(r"(^die\W?$|ld3| ?die |die$)", flags=re.IGNORECASE)
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
_re_venny = re.compile(r"^venny\W?$", flags=re.IGNORECASE)
_re_ty = re.compile(r"^(?:ty|thanks|thank you)\W?$", flags=re.IGNORECASE)
_re_viewaskewer = re.compile(r"^(?:viewaskewer|view)\W?$", flags=re.IGNORECASE)
_re_whatsthat = re.compile(r"^what?'s that\W?$", flags=re.IGNORECASE)
_re_whoareyou = re.compile(r"^who are you\W?$", flags=re.IGNORECASE)

#|sf|bart`us's
_re_007 = re.compile(r"^007\W?$", flags=re.IGNORECASE)
_re_adamsfamily = re.compile(r"^adamsfamily\W?$", flags=re.IGNORECASE)
_re_allahuakbar = re.compile(r"^allahuakbar\W?$", flags=re.IGNORECASE)
_re_AllSkeetSkeet = re.compile(r"^(?:All Skeet Skeet|Skeet Skeet)\W?$", flags=re.IGNORECASE)
_re_allstar = re.compile(r"^allstar\W?$", flags=re.IGNORECASE)
_re_AllTheThings = re.compile(r"^All The Things\W?$", flags=re.IGNORECASE)
_re_Amazing = re.compile(r"^Amazing\W?$", flags=re.IGNORECASE)
_re_Ameno = re.compile(r"^Ameno\W?$", flags=re.IGNORECASE)
_re_America = re.compile(r"^America\W?$", flags=re.IGNORECASE)
_re_Amerika = re.compile(r"^Amerika\W?$", flags=re.IGNORECASE)
_re_AndNothingElse = re.compile(r"^And Nothing Else\W?$", flags=re.IGNORECASE)
_re_Animals = re.compile(r"^Animals\W?$", flags=re.IGNORECASE)
_re_AScratch = re.compile(r"^(?:A Scratch|Scratch|just a scratch)\W?$", flags=re.IGNORECASE)
_re_asskicking = re.compile(r"^asskicking\W?$", flags=re.IGNORECASE)
_re_ave = re.compile(r"^ave\W?$", flags=re.IGNORECASE)
_re_babybaby = re.compile(r"^baby baby\W?$", flags=re.IGNORECASE)
_re_babyevillaugh = re.compile(r"^baby evil\W?$", flags=re.IGNORECASE)
_re_babylaughing = re.compile(r"^babylaughing\W?$", flags=re.IGNORECASE)
_re_badboys = re.compile(r"^bad boys\W?$", flags=re.IGNORECASE)
_re_BananaBoatSong = re.compile(r"^Banana Boat\W?$", flags=re.IGNORECASE)
_re_beback = re.compile(r"^I'?ll be back\W?$", flags=re.IGNORECASE)
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
_re_cunt = re.compile(r"^you are a cunt\W?$", flags=re.IGNORECASE)
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
_re_exitlight = re.compile(r"^exitlight\W?$", flags=re.IGNORECASE)
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
_re_ibet = re.compile(r"^ibet\W?$", flags=re.IGNORECASE)
_re_icantbelieve = re.compile(r"^i can'?t believe\W?$", flags=re.IGNORECASE)
_re_ichtuedieweh = re.compile(r"^ichtuedieweh\W?$", flags=re.IGNORECASE)
_re_idoparkour = re.compile(r"^i do parkour\W?$", flags=re.IGNORECASE)
_re_ihateall = re.compile(r"^i hate all\W?$", flags=re.IGNORECASE)
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
_re_johncena = re.compile(r"^johncena\W?$", flags=re.IGNORECASE)
_re_jumpmotherfucker = re.compile(r"^jump motherfucker\W?$", flags=re.IGNORECASE)
_re_justdoit = re.compile(r"^just do it\W?$", flags=re.IGNORECASE)
_re_kamehameha = re.compile(r"^kamehameha\W?$", flags=re.IGNORECASE)
_re_keeponfighting = re.compile(r"^keep on fighting\W?$", flags=re.IGNORECASE)
_re_keepyourshirton = re.compile(r"^keep your shirt on\W?$", flags=re.IGNORECASE)
_re_KnockedDown = re.compile(r"^Knocked Down\W?$", flags=re.IGNORECASE)
_re_kommtdiesonne = re.compile(r"^kommtdiesonne\W?$", flags=re.IGNORECASE)
_re_kungfu = re.compile(r"^kungfu\W?$", flags=re.IGNORECASE)
_re_lately = re.compile(r"^lately\W?$", flags=re.IGNORECASE)
_re_Legitness = re.compile(r"^Legitness\W?$", flags=re.IGNORECASE)
_re_letsgetready = re.compile(r"^lets get ready\W?$", flags=re.IGNORECASE)
_re_letsputasmile = re.compile(r"^lets put a smile\W?$", flags=re.IGNORECASE)
_re_lightsout = re.compile(r"^lights out\W?$", flags=re.IGNORECASE)
_re_lionking = re.compile(r"^lion king\W?$", flags=re.IGNORECASE)
_re_livetowin = re.compile(r"^live to win\W?$", flags=re.IGNORECASE)
_re_losingmyreligion = re.compile(r"^losing my religion\W?$", flags=re.IGNORECASE)
_re_loveme = re.compile(r"^loveme\W?$", flags=re.IGNORECASE)
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

        if not self.last_sound:
            pass
        elif time.time() - self.last_sound < self.get_cvar("qlx_funSoundDelay", int):
            return

        if self.check_time(player):
            return

        msg = self.clean_text(msg)
        msg_lower = msg.lower()
        if _re_hahaha_yeah.match(msg):
            self.play_sound("sound/player/lucy/taunt.wav")
        elif _re_haha_yeah_haha.match(msg):
            self.play_sound("sound/player/biker/taunt.wav")
        elif _re_yeah_hahaha.match(msg):
            self.play_sound("sound/player/razor/taunt.wav")
        elif _re_duahahaha.match(msg):
            self.play_sound("sound/player/keel/taunt.wav")
        elif _re_hahaha.search(msg):
            self.play_sound("sound/player/santa/taunt.wav")
        elif _re_glhf.match(msg):
            self.play_sound("sound/vo/crash_new/39_01.wav")
        elif _re_f3.match(msg):
            self.play_sound("sound/vo/crash_new/36_04.wav")
        elif "holy shit" in msg_lower:
            self.play_sound("sound/vo_female/holy_shit")
        elif _re_welcome.match(msg):
            self.play_sound("sound/vo_evil/welcome")
        elif _re_go.match(msg):
            self.play_sound("sound/vo/go")
        elif _re_beep_boop.match(msg):
            self.play_sound("sound/player/tankjr/taunt.wav")
        elif _re_win.match(msg):
            self.play_sound("sound/vo_female/you_win.wav")
        elif _re_lose.match(msg):
            self.play_sound("sound/vo/you_lose.wav")
        elif "impressive" in msg_lower:
            self.play_sound("sound/vo_female/impressive1.wav")
        elif "excellent" in msg_lower:
            self.play_sound("sound/vo_evil/excellent1.wav")
        elif _re_denied.match(msg):
            self.play_sound("sound/vo/denied")
        elif _re_balls_out.match(msg):
            self.play_sound("sound/vo_female/balls_out")
        elif _re_one.match(msg):
            self.play_sound("sound/vo_female/one")
        elif _re_two.match(msg):
            self.play_sound("sound/vo_female/two")
        elif _re_three.match(msg):
            self.play_sound("sound/vo_female/three")
        elif _re_fight.match(msg):
            self.play_sound("sound/vo_evil/fight")
        elif _re_gauntlet.match(msg):
            self.play_sound("sound/vo_evil/gauntlet")
        elif _re_humiliation.match(msg):
            self.play_sound("sound/vo_evil/humiliation1")
        elif _re_perfect.match(msg):
            self.play_sound("sound/vo_evil/perfect")
        elif _re_wah.match(msg):
            self.play_sound("sound/misc/yousuck")
        elif _re_ah.match(msg):
            self.play_sound("sound/player/slash/taunt.wav")
        elif _re_oink.match(msg):
            self.play_sound("sound/player/sorlag/pain50_1.wav")
        elif _re_argh.match(msg):
            self.play_sound("sound/player/doom/taunt.wav")
        elif _re_hah_haha.match(msg):
            self.play_sound("sound/player/hunter/taunt.wav")
        elif _re_woohoo.match(msg):
            self.play_sound("sound/player/janet/taunt.wav")
        elif _re_quakelive.match(msg):
            self.play_sound("sound/vo_female/quake_live")
        elif _re_chaching.search(msg):
            self.play_sound("sound/misc/chaching")
        elif _re_uh_ah.match(msg):
            self.play_sound("sound/player/mynx/taunt.wav")
        elif _re_oohwee.match(msg):
            self.play_sound("sound/player/anarki/taunt.wav")
        elif _re_erah.match(msg):
            self.play_sound("sound/player/bitterman/taunt.wav")
        elif _re_yeahhh.match(msg):
            self.play_sound("sound/player/major/taunt.wav")
        elif _re_scream.match(msg):
            self.play_sound("sound/player/bones/taunt.wav")
        elif _re_salute.match(msg):
            self.play_sound("sound/player/sarge/taunt.wav")
        elif _re_squish.match(msg):
            self.play_sound("sound/player/orbb/taunt.wav")
        elif _re_oh_god.match(msg):
            self.play_sound("sound/player/ranger/taunt.wav")
        elif _re_snarl.match(msg):
            self.play_sound("sound/player/sorlag/taunt.wav")

        #Viewaskewer
        elif _re_assholes.match(msg):
            self.play_sound("soundbank/assholes")
        elif _re_assshafter.match(msg):
            self.play_sound("soundbank/assshafterloud")
        elif _re_babydoll.match(msg):
            self.play_sound("soundbank/babydoll")
        elif _re_barelymissed.match(msg):
            self.play_sound("soundbank/barelymissed")
        elif _re_belly.search(msg):
            self.play_sound("soundbank/belly")
        elif _re_bitch.match(msg):
            self.play_sound("soundbank/bitch")
        elif _re_blud.match(msg):
            self.play_sound("soundbank/dtblud")
        elif _re_boats.match(msg):
            self.play_sound("soundbank/boats")
        elif _re_bobg.match(msg):
            self.play_sound("soundbank/bobg")
        elif _re_bogdog.match(msg):
            self.play_sound("soundbank/bogdog")
        elif _re_boom.match(msg):
            self.play_sound("soundbank/boom")
        elif _re_boom2.match(msg):
            self.play_sound("soundbank/boom2")
        elif _re_buk.match(msg):
            self.play_sound("soundbank/buk")
        elif _re_bullshit.match(msg):
            self.play_sound("soundbank/bullshit")
        elif _re_butthole.match(msg):
            self.play_sound("soundbank/butthole")
        elif _re_buttsex.match(msg):
            self.play_sound("soundbank/buttsex")
        elif _re_cheeks.match(msg):
            self.play_sound("soundbank/cheeks")
        elif _re_cocksucker.match(msg):
            self.play_sound("soundbank/cocksucker")
        elif _re_conquer.match(msg):
            self.play_sound("soundbank/conquer")
        elif _re_countdown.match(msg):
            self.play_sound("soundbank/countdown")
        elif _re_cum.match(msg):
            self.play_sound("soundbank/cum")
        elif _re_cumming.match(msg):
            self.play_sound("soundbank/cumming")
        elif _re_cunt.match(msg):
            self.play_sound("soundbank/cunt")
        elif _re_dirkfunk.match(msg):
            self.play_sound("soundbank/dirkfunk")
        elif _re_disappointment.match(msg):
            self.play_sound("soundbank/disappointment")
        elif _re_doom.match(msg):
            self.play_sound("soundbank/doom")
        elif _re_drumset.match(msg):
            self.play_sound("soundbank/drumset")
        elif _re_eat.match(msg):
            self.play_sound("soundbank/eat")
        elif _re_eatme.match(msg):
            self.play_sound("soundbank/eatme")
        elif _re_fag.match(msg):
            self.play_sound("soundbank/fag")
        elif _re_fingerass.match(msg):
            self.play_sound("soundbank/fingerass")
        elif _re_flash.match(msg):
            self.play_sound("soundbank/flash")
        elif _re_fuckface.match(msg):
            self.play_sound("soundbank/fuckface")
        elif _re_fuck_you.match(msg):
            self.play_sound("soundbank/fuckyou")
        elif _re_getemm.match(msg):
            self.play_sound("soundbank/getemm")
        elif _re_gonads.match(msg):
            self.play_sound("soundbank/gonads")
        elif _re_gtfo.match(msg):
            self.play_sound("soundbank/gtfo")
        elif _re_HIT.match(msg):
            self.play_sound("soundbank/doom")
        elif _re_hugitout.match(msg):
            self.play_sound("soundbank/hugitout")
        elif _re_idiot.match(msg):
            self.play_sound("soundbank/idiot")
        elif _re_idiot2.match(msg):
            self.play_sound("soundbank/idiot2")
        elif _re_itstime.match(msg):
            self.play_sound("soundbank/itstime")
        elif _re_jeopardy.match(msg):
            self.play_sound("soundbank/jeopardy")
        elif _re_jerkoff.match(msg):
            self.play_sound("soundbank/jerkoff")
        elif _re_killo.match(msg):
            self.play_sound("soundbank/killo")
        elif _re_knocked.match(msg):
            self.play_sound("soundbank/knocked")
        elif _re_ld3.search(msg):
            self.play_sound("soundbank/ld3")
        elif _re_liquidswords.match(msg):
            self.play_sound("soundbank/liquid")
        elif _re_massacre.match(msg):
            self.play_sound("soundbank/massacre")
        elif _re_mixer.match(msg):
            self.play_sound("soundbank/mixer")
        elif _re_mjman.match(msg):
            self.play_sound("soundbank/mjman")
        elif _re_mmmm.match(msg):
            self.play_sound("soundbank/mmmm")
        elif _re_monty.match(msg):
            self.play_sound("soundbank/monty")
        elif _re_n8.match(msg):
            self.play_sound("soundbank/n8")
        elif _re_nikon.match(msg):
            self.play_sound("soundbank/nikon")
        elif _re_nina.match(msg):
            self.play_sound("soundbank/nina")
        elif _re_nthreem.match(msg):
            self.play_sound("sound/vo_female/impressive1.wav")
        elif _re_olhip.match(msg):
            self.play_sound("soundbank/hip")
        elif _re_organic.match(msg):
            self.play_sound("soundbank/organic")
        elif _re_paintball.match(msg):
            self.play_sound("soundbank/paintball")
        elif _re_pigfucker.match(msg):
            self.play_sound("soundbank/pigfer")
        elif _re_popeye.match(msg):
            self.play_sound("soundbank/popeye")
        elif _re_rosie.match(msg):
            self.play_sound("soundbank/rosie")
        elif _re_seaweed.match(msg):
            self.play_sound("soundbank/seaweed")
        elif _re_shit.match(msg):
            self.play_sound("soundbank/shit")
        elif _re_sit.search(msg):
            self.play_sound("soundbank/sit")
        elif _re_soulianis.search(msg):
            self.play_sound("soundbank/soulianis")
        elif _re_spam.match(msg):
            self.play_sound("soundbank/spam3")
        elif _re_stalin.match(msg):
            self.play_sound("soundbank/ussr")
        elif _re_stfu.match(msg):
            self.play_sound("soundbank/stfu")
        elif _re_suckadick.match(msg):
            self.play_sound("soundbank/suckadick")
        elif _re_suckit.match(msg):
            self.play_sound("soundbank/suckit")
        elif _re_suckmydick.match(msg):
            self.play_sound("soundbank/suckmydick")
        elif _re_teapot.match(msg):
            self.play_sound("soundbank/teapot")
        elif _re_thankgod.match(msg):
            self.play_sound("soundbank/thankgod")
        elif _re_traxion.match(msg):
            self.play_sound("soundbank/traxion")
        elif _re_trixy.match(msg):
            self.play_sound("soundbank/trixy")
        elif _re_twoon.match(msg):
            self.play_sound("soundbank/twoon")
        elif _re_venny.match(msg):
            self.play_sound("soundbank/venny")
        elif _re_ty.match(msg):
            self.play_sound("soundbank/thankyou")
        elif _re_viewaskewer.match(msg):
            self.play_sound("soundbank/view")
        elif _re_whatsthat.match(msg):
            self.play_sound("soundbank/whatsthat")
        elif _re_whoareyou.match(msg):
            self.play_sound("soundbank/whoareyou")

        #|sf|bart`us's
        elif _re_007.match(msg):
            self.play_sound("sound/funnysounds/007.wav")
        elif _re_adamsfamily.match(msg):
            self.play_sound("sound/funnysounds/adamsfamily.ogg")
        elif _re_allahuakbar.match(msg):
            self.play_sound("sound/funnysounds/allahuakbar.ogg")
        elif _re_AllSkeetSkeet.match(msg):
            self.play_sound("sound/funnysounds/AllSkeetSkeet.ogg")
        elif _re_allstar.match(msg):
            self.play_sound("sound/funnysounds/allstar.ogg")
        elif _re_AllTheThings.match(msg):
            self.play_sound("sound/funnysounds/AllTheThings.ogg")
        elif _re_allthethings.match(msg):
            self.play_sound("sound/funnysounds/allthethings.ogg")
        elif _re_Amazing.match(msg):
            self.play_sound("sound/funnysounds/Amazing.ogg")
        elif _re_amazing.match(msg):
            self.play_sound("sound/funnysounds/amazing.ogg")
        elif _re_Ameno.match(msg):
            self.play_sound("sound/funnysounds/Ameno.ogg")
        elif _re_ameno.match(msg):
            self.play_sound("sound/funnysounds/ameno.ogg")
        elif _re_America.match(msg):
            self.play_sound("sound/funnysounds/America.ogg")
        elif _re_america.match(msg):
            self.play_sound("sound/funnysounds/america.ogg")
        elif _re_Amerika.match(msg):
            self.play_sound("sound/funnysounds/Amerika.ogg")
        elif _re_amerika.match(msg):
            self.play_sound("sound/funnysounds/amerika.ogg")
        elif _re_AndNothingElse.match(msg):
            self.play_sound("sound/funnysounds/AndNothingElse.ogg")
        elif _re_andnothingelse.match(msg):
            self.play_sound("sound/funnysounds/andnothingelse.ogg")
        elif _re_Animals.match(msg):
            self.play_sound("sound/funnysounds/Animals.ogg")
        elif _re_animals.match(msg):
            self.play_sound("sound/funnysounds/animals.ogg")
        elif _re_AScratch.match(msg):
            self.play_sound("sound/funnysounds/AScratch.ogg")
        elif _re_ascratch.match(msg):
            self.play_sound("sound/funnysounds/ascratch.ogg")
        elif _re_asskicking.match(msg):
            self.play_sound("sound/funnysounds/asskicking.ogg")
        elif _re_ave.match(msg):
            self.play_sound("sound/funnysounds/ave.ogg")
        elif _re_babybaby.match(msg):
            self.play_sound("sound/funnysounds/babybaby.ogg")
        elif _re_babybaby.match(msg):
            self.play_sound("sound/funnysounds/babybaby.ogg")
        elif _re_babyevillaugh.match(msg):
            self.play_sound("sound/funnysounds/babyevillaugh.ogg")
        elif _re_babylaughing.match(msg):
            self.play_sound("sound/funnysounds/babylaughing.ogg")
        elif _re_badboys.match(msg):
            self.play_sound("sound/funnysounds/badboys.ogg")
        elif _re_BananaBoatSong.match(msg):
            self.play_sound("sound/funnysounds/BananaBoatSong.ogg")
        elif _re_beback.match(msg):
            self.play_sound("sound/funnysounds/beback.ogg")
        elif _re_bennyhill.match(msg):
            self.play_sound("sound/funnysounds/bennyhill.ogg")
        elif _re_benzin.match(msg):
            self.play_sound("sound/funnysounds/benzin.ogg")
        elif _re_bluewins.match(msg):
            self.play_sound("sound/funnysounds/bluewins.ogg")
        elif _re_bonkers.match(msg):
            self.play_sound("sound/funnysounds/bonkers.ogg")
        elif _re_boomheadshot.match(msg):
            self.play_sound("sound/funnysounds/boomheadshot.ogg")
        elif _re_booo.match(msg):
            self.play_sound("sound/funnysounds/booo.ogg")
        elif _re_boring.match(msg):
            self.play_sound("sound/funnysounds/boring.ogg")
        elif _re_boze.match(msg):
            self.play_sound("sound/funnysounds/boze.ogg")
        elif _re_brightsideoflife.match(msg):
            self.play_sound("sound/funnysounds/brightsideoflife.ogg")
        elif _re_buckdich.match(msg):
            self.play_sound("sound/funnysounds/buckdich.ogg")
        elif _re_bullshitter.match(msg):
            self.play_sound("sound/funnysounds/bullshitter.ogg")
        elif _re_burnsburns.match(msg):
            self.play_sound("sound/funnysounds/burnsburns.ogg")
        elif _re_cameltoe.match(msg):
            self.play_sound("sound/funnysounds/cameltoe.ogg")
        elif _re_canttouchthis.match(msg):
            self.play_sound("sound/funnysounds/canttouchthis.ogg")
        elif _re_cccp.match(msg):
            self.play_sound("sound/funnysounds/cccp.ogg")
        elif _re_champions.match(msg):
            self.play_sound("sound/funnysounds/champions.ogg")
        elif _re_chicken.match(msg):
            self.play_sound("sound/funnysounds/chicken.ogg")
        elif _re_chocolaterain.match(msg):
            self.play_sound("sound/funnysounds/chocolaterain.ogg")
        elif _re_coin.match(msg):
            self.play_sound("sound/funnysounds/coin.ogg")
        elif _re_come.match(msg):
            self.play_sound("sound/funnysounds/come.ogg")
        elif _re_ComeWithMeNow.match(msg):
            self.play_sound("sound/funnysounds/ComeWithMeNow.ogg")
        elif _re_Count_down.match(msg):
            self.play_sound("sound/funnysounds/Countdown.ogg")
        elif _re_cowards.match(msg):
            self.play_sound("sound/funnysounds/cowards.ogg")
        elif _re_crazy.match(msg):
            self.play_sound("sound/funnysounds/crazy.ogg")
        elif _re_cunt.match(msg):
            self.play_sound("sound/funnysounds/cunt.ogg")
        elif _re_damnit.match(msg):
            self.play_sound("sound/funnysounds/damnit.ogg")
        elif _re_DangerZone.match(msg):
            self.play_sound("sound/funnysounds/DangerZone.ogg")
        elif _re_deadsoon.match(msg):
            self.play_sound("sound/funnysounds/deadsoon.ogg")
        elif _re_defeated.match(msg):
            self.play_sound("sound/funnysounds/defeated.ogg")
        elif _re_devil.match(msg):
            self.play_sound("sound/funnysounds/devil.ogg")
        elif _re_doesntloveyou.match(msg):
            self.play_sound("sound/funnysounds/doesntloveyou.ogg")
        elif _re_dubist.match(msg):
            self.play_sound("sound/funnysounds/dubist.ogg")
        elif _re_duhast.match(msg):
            self.play_sound("sound/funnysounds/duhast.ogg")
        elif _re_dumbways.match(msg):
            self.play_sound("sound/funnysounds/dumbways.ogg")
        elif _re_EatPussy.match(msg):
            self.play_sound("sound/funnysounds/EatPussy.ogg")
        elif _re_education.match(msg):
            self.play_sound("sound/funnysounds/education.ogg")
        elif _re_einschrei.match(msg):
            self.play_sound("sound/funnysounds/einschrei.ogg")
        elif _re_EinsZwei.match(msg):
            self.play_sound("sound/funnysounds/EinsZwei.ogg")
        elif _re_electro.match(msg):
            self.play_sound("sound/funnysounds/electro.ogg")
        elif _re_elementary.match(msg):
            self.play_sound("sound/funnysounds/elementary.ogg")
        elif _re_engel.match(msg):
            self.play_sound("sound/funnysounds/engel.ogg")
        elif _re_erstwenn.match(msg):
            self.play_sound("sound/funnysounds/erstwenn.ogg")
        elif _re_exitlight.match(msg):
            self.play_sound("sound/funnysounds/exitlight.ogg")
        elif _re_faint.match(msg):
            self.play_sound("sound/funnysounds/faint.ogg")
        elif _re_fatality.match(msg):
            self.play_sound("sound/funnysounds/fatality.ogg")
        elif _re_FeelGood.match(msg):
            self.play_sound("sound/funnysounds/FeelGood.ogg")
        elif _re_fleshwound.match(msg):
            self.play_sound("sound/funnysounds/fleshwound.ogg")
        elif _re_foryou.match(msg):
            self.play_sound("sound/funnysounds/foryou.ogg")
        elif _re_freestyler.match(msg):
            self.play_sound("sound/funnysounds/freestyler.ogg")
        elif _re_fuckfuck.match(msg):
            self.play_sound("sound/funnysounds/fuckfuck.ogg")
        elif _re_fuckingburger.match(msg):
            self.play_sound("sound/funnysounds/fuckingburger.ogg")
        elif _re_fuckingkids.match(msg):
            self.play_sound("sound/funnysounds/fuckingkids.ogg")
        elif _re_gangnam.match(msg):
            self.play_sound("sound/funnysounds/gangnam.ogg")
        elif _re_ganjaman.match(msg):
            self.play_sound("sound/funnysounds/ganjaman.ogg")
        elif _re_gay.match(msg):
            self.play_sound("sound/funnysounds/gay.ogg")
        elif _re_getcrowbar.match(msg):
            self.play_sound("sound/funnysounds/getcrowbar.ogg")
        elif _re_getouttheway.match(msg):
            self.play_sound("sound/funnysounds/getouttheway.ogg")
        elif _re_ghostbusters.match(msg):
            self.play_sound("sound/funnysounds/ghostbusters.ogg")
        elif _re_girllook.match(msg):
            self.play_sound("sound/funnysounds/girllook.ogg")
        elif _re_girly.match(msg):
            self.play_sound("sound/funnysounds/girly.ogg")
        elif _re_gnrguitar.match(msg):
            self.play_sound("sound/funnysounds/gnrguitar.ogg")
        elif _re_goddamnright.match(msg):
            self.play_sound("sound/funnysounds/goddamnright.ogg")
        elif _re_goodbyeandrea.match(msg):
            self.play_sound("sound/funnysounds/goodbyeandrea.ogg")
        elif _re_goodbyesarah.match(msg):
            self.play_sound("sound/funnysounds/goodbyesarah.ogg")
        elif _re_gotcha.match(msg):
            self.play_sound("sound/funnysounds/gotcha.ogg")
        elif _re_hakunamatata.match(msg):
            self.play_sound("sound/funnysounds/hakunamatata.ogg")
        elif _re_hammertime.match(msg):
            self.play_sound("sound/funnysounds/hammertime.ogg")
        elif _re_hello.match(msg):
            self.play_sound("sound/funnysounds/hello.ogg")
        elif _re_hellstestern.match(msg):
            self.play_sound("sound/funnysounds/hellstestern.ogg")
        elif _re_holy.match(msg):
            self.play_sound("sound/funnysounds/holy.ogg")
        elif _re_hoppereiter.match(msg):
            self.play_sound("sound/funnysounds/hoppereiter.ogg")
        elif _re_howareyou.match(msg):
            self.play_sound("sound/funnysounds/howareyou.ogg")
        elif _re_hush.match(msg):
            self.play_sound("sound/funnysounds/hush.ogg")
        elif _re_ibet.match(msg):
            self.play_sound("sound/funnysounds/ibet.ogg")
        elif _re_icantbelieve.match(msg):
            self.play_sound("sound/funnysounds/icantbelieve.ogg")
        elif _re_ichtuedieweh.match(msg):
            self.play_sound("sound/funnysounds/ichtuedieweh.ogg")
        elif _re_idoparkour.match(msg):
            self.play_sound("sound/funnysounds/idoparkour.ogg")
        elif _re_ihateall.match(msg):
            self.play_sound("sound/funnysounds/ihateall.ogg")
        elif _re_imperial.match(msg):
            self.play_sound("sound/funnysounds/imperial.ogg")
        elif _re_imsexy.match(msg):
            self.play_sound("sound/funnysounds/imsexy.ogg")
        elif _re_imyourfather.match(msg):
            self.play_sound("sound/funnysounds/imyourfather.ogg")
        elif _re_incoming.match(msg):
            self.play_sound("sound/funnysounds/incoming.ogg")
        elif _re_indianajones.match(msg):
            self.play_sound("sound/funnysounds/indianajones.ogg")
        elif _re_inyourheadzombie.match(msg):
            self.play_sound("sound/funnysounds/inyourheadzombie.ogg")
        elif _re_iseeassholes.match(msg):
            self.play_sound("sound/funnysounds/iseeassholes.ogg")
        elif _re_iseedeadpeople.match(msg):
            self.play_sound("sound/funnysounds/iseedeadpeople.ogg")
        elif _re_itsmylife.match(msg):
            self.play_sound("sound/funnysounds/itsmylife.ogg")
        elif _re_itsnot.match(msg):
            self.play_sound("sound/funnysounds/itsnot.ogg")
        elif _re_jackpot.match(msg):
            self.play_sound("sound/funnysounds/jackpot.ogg")
        elif _re_jesus.match(msg):
            self.play_sound("sound/funnysounds/jesus.ogg")
        elif _re_jesusOh.match(msg):
            self.play_sound("sound/funnysounds/JesusOh.ogg")
        elif _re_johncena.match(msg):
            self.play_sound("sound/funnysounds/johncena.ogg")
        elif _re_jumpmotherfucker.match(msg):
            self.play_sound("sound/funnysounds/jumpmotherfucker.ogg")
        elif _re_justdoit.match(msg):
            self.play_sound("sound/funnysounds/justdoit.ogg")
        elif _re_kamehameha.match(msg):
            self.play_sound("sound/funnysounds/kamehameha.ogg")
        elif _re_keeponfighting.match(msg):
            self.play_sound("sound/funnysounds/keeponfighting.ogg")
        elif _re_keepyourshirton.match(msg):
            self.play_sound("sound/funnysounds/keepyourshirton.ogg")
        elif _re_KnockedDown.match(msg):
            self.play_sound("sound/funnysounds/KnockedDown.ogg")
        elif _re_kommtdiesonne.match(msg):
            self.play_sound("sound/funnysounds/kommtdiesonne.ogg")
        elif _re_kungfu.match(msg):
            self.play_sound("sound/funnysounds/kungfu.ogg")
        elif _re_lately.match(msg):
            self.play_sound("sound/funnysounds/lately.ogg")
        elif _re_Legitness.match(msg):
            self.play_sound("sound/funnysounds/Legitness.ogg")
        elif _re_letsgetready.match(msg):
            self.play_sound("sound/funnysounds/letsgetready.ogg")
        elif _re_letsputasmile.match(msg):
            self.play_sound("sound/funnysounds/letsputasmile.ogg")
        elif _re_lightsout.match(msg):
            self.play_sound("sound/funnysounds/lightsout.ogg")
        elif _re_lionking.match(msg):
            self.play_sound("sound/funnysounds/lionking.ogg")
        elif _re_livetowin.match(msg):
            self.play_sound("sound/funnysounds/livetowin.ogg")
        elif _re_losingmyreligion.match(msg):
            self.play_sound("sound/funnysounds/losingmyreligion.ogg")
        elif _re_loveme.match(msg):
            self.play_sound("sound/funnysounds/loveme.ogg")
        elif _re_low.match(msg):
            self.play_sound("sound/funnysounds/low.ogg")
        elif _re_luck.match(msg):
            self.play_sound("sound/funnysounds/luck.ogg")
        elif _re_lust.match(msg):
            self.play_sound("sound/funnysounds/lust.ogg")
        elif _re_mahnamahna.match(msg):
            self.play_sound("sound/funnysounds/mahnamahna.ogg")
        elif _re_mario.match(msg):
            self.play_sound("sound/funnysounds/mario.ogg")
        elif _re_Me.match(msg):
            self.play_sound("sound/funnysounds/Me.ogg")
        elif _re_meinland.match(msg):
            self.play_sound("sound/funnysounds/meinland.ogg")
        elif _re_message.match(msg):
            self.play_sound("sound/funnysounds/message.ogg")
        elif _re_mimimi.match(msg):
            self.play_sound("sound/funnysounds/mimimi.ogg")
        elif _re_mission.match(msg):
            self.play_sound("sound/funnysounds/mission.ogg")
        elif _re_moan.match(msg):
            self.play_sound("sound/funnysounds/moan.ogg")
        elif _re_mortalkombat.match(msg):
            self.play_sound("sound/funnysounds/mortalkombat.ogg")
        elif _re_moveass.match(msg):
            self.play_sound("sound/funnysounds/moveass.ogg")
        elif _re_muppetopening.match(msg):
            self.play_sound("sound/funnysounds/muppetopening.ogg")
        elif _re_mylittlepony.match(msg):
            self.play_sound("sound/funnysounds/mylittlepony.ogg")
        elif _re_myname.match(msg):
            self.play_sound("sound/funnysounds/myname.ogg")
        elif _re_neverseen.match(msg):
            self.play_sound("sound/funnysounds/neverseen.ogg")
        elif _re_nightmare.match(msg):
            self.play_sound("sound/funnysounds/nightmare.ogg")
        elif _re_nobodylikesyou.match(msg):
            self.play_sound("sound/funnysounds/nobodylikesyou.ogg")
        elif _re_nonie.match(msg):
            self.play_sound("sound/funnysounds/nonie.ogg")
        elif _re_nooo.match(msg):
            self.play_sound("sound/funnysounds/nooo.ogg")
        elif _re_notimeforloosers.match(msg):
            self.play_sound("sound/funnysounds/notimeforloosers.ogg")
        elif _re_numanuma.match(msg):
            self.play_sound("sound/funnysounds/numanuma.ogg")
        elif _re_nyancat.match(msg):
            self.play_sound("sound/funnysounds/nyancat.ogg")
        elif _re_ofuck.match(msg):
            self.play_sound("sound/funnysounds/ofuck.ogg")
        elif _re_ohmygod.match(msg):
            self.play_sound("sound/funnysounds/ohmygod.ogg")
        elif _re_OhMyGosh.match(msg):
            self.play_sound("sound/funnysounds/OhMyGosh.ogg")
        elif _re_ohnedich.match(msg):
            self.play_sound("sound/funnysounds/ohnedich.ogg")
        elif _re_ohno.match(msg):
            self.play_sound("sound/funnysounds/ohno.ogg")
        elif _re_ohnoe.match(msg):
            self.play_sound("sound/funnysounds/ohnoe.ogg")
        elif _re_pacman.match(msg):
            self.play_sound("sound/funnysounds/pacman.ogg")
        elif _re_pickmeup.match(msg):
            self.play_sound("sound/funnysounds/pickmeup.ogg")
        elif _re_pikachu.match(msg):
            self.play_sound("sound/funnysounds/pikachu.ogg")
        elif _re_pinkiepie.match(msg):
            self.play_sound("sound/funnysounds/pinkiepie.ogg")
        elif _re_PinkPanther.match(msg):
            self.play_sound("sound/funnysounds/PinkPanther.ogg")
        elif _re_pipe.match(msg):
            self.play_sound("sound/funnysounds/pipe.ogg")
        elif _re_pissmeoff.match(msg):
            self.play_sound("sound/funnysounds/pissmeoff.ogg")
        elif _re_playagame.match(msg):
            self.play_sound("sound/funnysounds/playagame.ogg")
        elif _re_pooping.match(msg):
            self.play_sound("sound/funnysounds/pooping.ogg")
        elif _re_powerpuff.match(msg):
            self.play_sound("sound/funnysounds/powerpuff.ogg")
        elif _re_radioactive.match(msg):
            self.play_sound("sound/funnysounds/radioactive.ogg")
        elif _re_rammsteinriff.match(msg):
            self.play_sound("sound/funnysounds/rammsteinriff.ogg")
        elif _re_redwins.match(msg):
            self.play_sound("sound/funnysounds/redwins.ogg")
        elif _re_renegade.match(msg):
            self.play_sound("sound/funnysounds/renegade.ogg")
        elif _re_retard.match(msg):
            self.play_sound("sound/funnysounds/retard.ogg")
        elif _re_rocky.match(msg):
            self.play_sound("sound/funnysounds/rocky")
        elif _re_rockyouguitar.match(msg):
            self.play_sound("sound/funnysounds/rockyouguitar.ogg")
        elif _re_sail.match(msg):
            self.play_sound("sound/funnysounds/sail.ogg")
        elif _re_Salil.match(msg):
            self.play_sound("sound/funnysounds/Salil.ogg")
        elif _re_samba.match(msg):
            self.play_sound("sound/funnysounds/samba.ogg")
        elif _re_sandstorm.match(msg):
            self.play_sound("sound/funnysounds/sandstorm.ogg")
        elif _re_saymyname.match(msg):
            self.play_sound("sound/funnysounds/saymyname.ogg")
        elif _re_scatman.match(msg):
            self.play_sound("sound/funnysounds/scatman.ogg")
        elif _re_sellyouall.match(msg):
            self.play_sound("sound/funnysounds/sellyouall.ogg")
        elif _re_senseofhumor.match(msg):
            self.play_sound("sound/funnysounds/senseofhumor.ogg")
        elif _re_shakesenora.match(msg):
            self.play_sound("sound/funnysounds/shakesenora.ogg")
        elif _re_shutthefuckup.match(msg):
            self.play_sound("sound/funnysounds/shutthefuckup.ogg")
        elif _re_shutyourfuckingmouth.match(msg):
            self.play_sound("sound/funnysounds/shutyourfuckingmouth.ogg")
        elif _re_silence.match(msg):
            self.play_sound("sound/funnysounds/silence.ogg")
        elif _re_smoothcriminal.match(msg):
            self.play_sound("sound/funnysounds/smoothcriminal.ogg")
        elif _re_socobatevira.match(msg):
            self.play_sound("sound/funnysounds/socobatevira.ogg")
        elif _re_socobateviraend.match(msg):
            self.play_sound("sound/funnysounds/socobateviraend.ogg")
        elif _re_socobatevirafast.match(msg):
            self.play_sound("sound/funnysounds/socobatevirafast.ogg")
        elif _re_socobateviraslow.match(msg):
            self.play_sound("sound/funnysounds/socobateviraslow.ogg")
        elif _re_sogivemereason.match(msg):
            self.play_sound("sound/funnysounds/sogivemereason.ogg")
        elif _re_sostupid.match(msg):
            self.play_sound("sound/funnysounds/sostupid.ogg")
        elif _re_SpaceJam.match(msg):
            self.play_sound("sound/funnysounds/SpaceJam.ogg")
        elif _re_spaceunicorn.match(msg):
            self.play_sound("sound/funnysounds/spaceunicorn.ogg")
        elif _re_spierdalaj.match(msg):
            self.play_sound("sound/funnysounds/spierdalaj.ogg")
        elif _re_stampon.match(msg):
            self.play_sound("sound/funnysounds/stampon.ogg")
        elif _re_starwars.match(msg):
            self.play_sound("sound/funnysounds/starwars.ogg")
        elif _re_stayinalive.match(msg):
            self.play_sound("sound/funnysounds/stayinalive.ogg")
        elif _re_stoning.match(msg):
            self.play_sound("sound/funnysounds/stoning.ogg")
        elif _re_Stop.match(msg):
            self.play_sound("sound/funnysounds/Stop.ogg")
        elif _re_story.match(msg):
            self.play_sound("sound/funnysounds/story.ogg")
        elif _re_surprise.match(msg):
            self.play_sound("sound/funnysounds/surprise.ogg")
        elif _re_swedishchef.match(msg):
            self.play_sound("sound/funnysounds/swedishchef.ogg")
        elif _re_sweetdreams.match(msg):
            self.play_sound("sound/funnysounds/sweetdreams.ogg")
        elif _re_takemedown.match(msg):
            self.play_sound("sound/funnysounds/takemedown.ogg")
        elif _re_talkscotish.match(msg):
            self.play_sound("sound/funnysounds/talkscotish.ogg")
        elif _re_teamwork.match(msg):
            self.play_sound("sound/funnysounds/teamwork.ogg")
        elif _re_technology.match(msg):
            self.play_sound("sound/funnysounds/technology.ogg")
        elif _re_thisissparta.match(msg):
            self.play_sound("sound/funnysounds/thisissparta.ogg")
        elif _re_thunderstruck.match(msg):
            self.play_sound("sound/funnysounds/thunderstruck.ogg")
        elif _re_tochurch.match(msg):
            self.play_sound("sound/funnysounds/tochurch.ogg")
        elif _re_tsunami.match(msg):
            self.play_sound("sound/funnysounds/tsunami.ogg")
        elif _re_tuturu.match(msg):
            self.play_sound("sound/funnysounds/tuturu.ogg")
        elif _re_tututu.match(msg):
            self.play_sound("sound/funnysounds/tututu.ogg")
        elif _re_unbelievable.match(msg):
            self.play_sound("sound/funnysounds/unbelievable.ogg")
        elif _re_undderhaifisch.match(msg):
            self.play_sound("sound/funnysounds/undderhaifisch.ogg")
        elif _re_uptowngirl.match(msg):
            self.play_sound("sound/funnysounds/uptowngirl.ogg")
        elif _re_valkyries.match(msg):
            self.play_sound("sound/funnysounds/valkyries.ogg")
        elif _re_wahwahwah.search(msg):
            self.play_sound("sound/funnysounds/wahwahwah.ogg")
        elif _re_wantyou.match(msg):
            self.play_sound("sound/funnysounds/wantyou.ogg")
        elif _re_wazzup.match(msg):
            self.play_sound("sound/funnysounds/wazzup.ogg")
        elif _re_wehmirohweh.match(msg):
            self.play_sound("sound/funnysounds/wehmirohweh.ogg")
        elif _re_whatislove.match(msg):
            self.play_sound("sound/funnysounds/whatislove.ogg")
        elif _re_whenangels.match(msg):
            self.play_sound("sound/funnysounds/whenangels.ogg")
        elif _re_whereareyou.match(msg):
            self.play_sound("sound/funnysounds/whereareyou.ogg")
        elif _re_whistle.match(msg):
            self.play_sound("sound/funnysounds/whistle.ogg")
        elif _re_WillBeSinging.match(msg):
            self.play_sound("sound/funnysounds/WillBeSinging.ogg")
        elif _re_wimbaway.match(msg):
            self.play_sound("sound/funnysounds/wimbaway.ogg")
        elif _re_windows.match(msg):
            self.play_sound("sound/funnysounds/windows.ogg")
        elif _re_wouldyoulike.match(msg):
            self.play_sound("sound/funnysounds/wouldyoulike.ogg")
        elif _re_wtf.match(msg):
            self.play_sound("sound/funnysounds/wtf.ogg")
        elif _re_yeee.match(msg):
            self.play_sound("sound/funnysounds/yeee.ogg")
        elif _re_yesmaster.match(msg):
            self.play_sound("sound/funnysounds/yesmaster.ogg")
        elif _re_yhehehe.match(msg):
            self.play_sound("sound/funnysounds/yhehehe.ogg")
        elif _re_ymca.match(msg):
            self.play_sound("sound/funnysounds/ymca.ogg")
        elif _re_You.match(msg):
            self.play_sound("sound/funnysounds/You.ogg")
        elif _re_youfuckedmywife.match(msg):
            self.play_sound("sound/funnysounds/youfuckedmywife.ogg")
        elif _re_YouRealise.match(msg):
            self.play_sound("sound/funnysounds/YouRealise.ogg")

        #Duke Nukem
        elif _re_myride.match(msg):
            self.play_sound("sound/duke/2ride06.wav")
        elif _re_abort.match(msg):
            self.play_sound("sound/duke/abort01.wav")
        elif _re_ahhh.match(msg):
            self.play_sound("sound/duke/ahh04.wav")
        elif _re_muchbetter.match(msg):
            self.play_sound("sound/duke/ahmuch03.wav")
        elif _re_aisle4.match(msg):
            self.play_sound("sound/duke/aisle402.wav")
        elif _re_amess.match(msg):
            self.play_sound("sound/duke/amess06.wav")
        elif _re_annoying.match(msg):
            self.play_sound("sound/duke/annoy03.wav")
        elif _re_bitchin.match(msg):
            self.play_sound("sound/duke/bitchn04.wav")
        elif _re_blowitout.match(msg):
            self.play_sound("sound/duke/blowit01.wav")
        elif _re_boobytrap.match(msg):
            self.play_sound("sound/duke/booby04.wav")
        elif _re_bookem.match(msg):
            self.play_sound("sound/duke/bookem03.wav")
        elif _re_borntobewild.match(msg):
            self.play_sound("sound/duke/born01.wav")
        elif _re_chewgum.match(msg):
            self.play_sound("sound/duke/chew05.wav")
        elif _re_comeon.match(msg):
            self.play_sound("sound/duke/comeon02.wav")
        elif _re_thecon.match(msg):
            self.play_sound("sound/duke/con03.wav")
        elif _re_cool.match(msg):
            self.play_sound("sound/duke/cool01.wav")
        elif _re_notcrying.match(msg):
            self.play_sound("sound/duke/cry01.wav")
        elif _re_daamn.match(msg):
            self.play_sound("sound/duke/damn03.wav")
        elif _re_damit.match(msg):
            self.play_sound("sound/duke/damnit04.wav")
        elif _re_dance.match(msg):
            self.play_sound("sound/duke/dance01.wav")
        elif _re_diesob.match(msg):
            self.play_sound("sound/duke/diesob03.wav")
        elif _re_doomed.match(msg):
            self.play_sound("sound/duke/doomed16.wav")
        elif _re_eyye.match(msg):
            self.play_sound("sound/duke/dscrem38.wav")
        elif _re_dukenukem.match(msg):
            self.play_sound("sound/duke/duknuk14.wav")
        elif _re_noway.match(msg):
            self.play_sound("sound/duke/eat08.wav")
        elif _re_eatshit.match(msg):
            self.play_sound("sound/duke/eatsht01.wav")
        elif _re_escape.match(msg):
            self.play_sound("sound/duke/escape01.wav")
        elif _re_faceass.match(msg):
            self.play_sound("sound/duke/face01.wav")
        elif _re_aforce.match(msg):
            self.play_sound("sound/duke/force01.wav")
        elif _re_getcrap.match(msg):
            self.play_sound("sound/duke/getcrap1.wav")
        elif _re_getsome.match(msg):
            self.play_sound("sound/duke/getsom1a.wav")
        elif _re_gameover.match(msg):
            self.play_sound("sound/duke/gmeovr05.wav")
        elif _re_gottahurt.match(msg):
            self.play_sound("sound/duke/gothrt01.wav")
        elif _re_groovy.match(msg):
            self.play_sound("sound/duke/groovy02.wav")
        elif _re_guyssuck.match(msg):
            self.play_sound("sound/duke/guysuk01.wav")
        elif _re_hailking.match(msg):
            self.play_sound("sound/duke/hail01.wav")
        elif _re_shithappens.match(msg):
            self.play_sound("sound/duke/happen01.wav")
        elif _re_holycow.match(msg):
            self.play_sound("sound/duke/holycw01.wav")
        elif _re_holyshit.match(msg):
            self.play_sound("sound/duke/holysh02.wav")
        elif _re_imgood.match(msg):
            self.play_sound("sound/duke/imgood12.wav")
        elif _re_independence.match(msg):
            self.play_sound("sound/duke/indpnc01.wav")
        elif _re_inhell.match(msg):
            self.play_sound("sound/duke/inhell01.wav")
        elif _re_goingin.match(msg):
            self.play_sound("sound/duke/introc.wav")
        elif _re_drjones.match(msg):
            self.play_sound("sound/duke/jones04.wav")
        elif _re_kickyourass.match(msg):
            self.play_sound("sound/duke/kick01-i.wav")
        elif _re_ktit.match(msg):
            self.play_sound("sound/duke/ktitx.wav")
        elif _re_letgod.match(msg):
            self.play_sound("sound/duke/letgod01.wav")
        elif _re_letsrock.match(msg):
            self.play_sound("sound/duke/letsrk03.wav")
        elif _re_lookingood.match(msg):
            self.play_sound("sound/duke/lookin01.wav")
        elif _re_makemyday.match(msg):
            self.play_sound("sound/duke/makeday1.wav")
        elif _re_midevil.match(msg):
            self.play_sound("sound/duke/mdevl01.wav")
        elif _re_mymeat.match(msg):
            self.play_sound("sound/duke/meat04-n.wav")
        elif _re_notime.match(msg):
            self.play_sound("sound/duke/myself3a.wav")
        elif _re_neededthat.match(msg):
            self.play_sound("sound/duke/needed03.wav")
        elif _re_nobody.match(msg):
            self.play_sound("sound/duke/nobody01.wav")
        elif _re_onlyone.match(msg):
            self.play_sound("sound/duke/onlyon03.wav")
        elif _re_mykindaparty.match(msg):
            self.play_sound("sound/duke/party03.wav")
        elif _re_gonnapay.match(msg):
            self.play_sound("sound/duke/pay02.wav")
        elif _re_pissesmeoff.match(msg):
            self.play_sound("sound/duke/pisses01.wav")
        elif _re_pissinmeoff.match(msg):
            self.play_sound("sound/duke/pissin01.wav")
        elif _re_postal.match(msg):
            self.play_sound("sound/duke/postal01.wav")
        elif _re_aintafraid.match(msg):
            self.play_sound("sound/duke/quake06.wav")
        elif _re_randr.match(msg):
            self.play_sound("sound/duke/r&r01.wav")
        elif _re_readyforaction.match(msg):
            self.play_sound("sound/duke/ready2a.wav")
        elif _re_ripheadoff.match(msg):
            self.play_sound("sound/duke/rip01.wav")
        elif _re_ripem.match(msg):
            self.play_sound("sound/duke/ripem08.wav")
        elif _re_rockin.match(msg):
            self.play_sound("sound/duke/rockin02.wav")
        elif _re_shakeit.match(msg):
            self.play_sound("sound/duke/shake2a.wav")
        elif _re_slacker.match(msg):
            self.play_sound("sound/duke/slacker1.wav")
        elif _re_smackdab.match(msg):
            self.play_sound("sound/duke/smack02.wav")
        elif _re_sohelpme.match(msg):
            self.play_sound("sound/duke/sohelp02.wav")
        elif _re_suckitdown.match(msg):
            self.play_sound("sound/duke/sukit01.wav")
        elif _re_terminated.match(msg):
            self.play_sound("sound/duke/termin01.wav")
        elif _re_thissucks.match(msg):
            self.play_sound("sound/duke/thsuk13a.wav")
        elif _re_vacation.match(msg):
            self.play_sound("sound/duke/vacatn01.wav")
        elif _re_christmas.match(msg):
            self.play_sound("sound/duke/waitin03.wav")
        elif _re_wnatssome.match(msg):
            self.play_sound("sound/duke/wansom4a.wav")
        elif _re_youandme.match(msg):
            self.play_sound("sound/duke/whipyu01.wav")
        elif _re_where.match(msg):
            self.play_sound("sound/duke/whrsit05.wav")
        elif _re_yippiekaiyay.match(msg):
            self.play_sound("sound/duke/yippie01.wav")
        elif _re_bottleofjack.match(msg):
            self.play_sound("sound/duke/yohoho01.wav")
        elif _re_longwalk.match(msg):
            self.play_sound("sound/duke/yohoho09.wav")

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
