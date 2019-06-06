# autodownload.sh <br>
*** This works best if ran when the server is not running .. because of updates to the appworkshop_282440.acf file *** <br>
This file is for downloading maps to your quake live server. <br>
Unlike when the server starts up, this gives a lot more time for the workshop item to download. <br>
edit the locations on line 7, and 14 for your server. <br>
Line 7: is the location and file name for your workshop.txt <br>
Line 14: is the location and filename of steamcmd.sh and then the install directory of your quake live server. <br>


If the status messages are not appearing correctly you may have a workshop.txt that is not correctly formatted for Linux.<br>
Try running dos2unix on the file. EX: dos2unix workshop.txt
This will convert the line feeds from windows format to the standard linux format.
