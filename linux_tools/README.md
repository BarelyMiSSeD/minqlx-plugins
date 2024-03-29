# Download Files
I put the download files together to allow server admins to update their maps on their server by just running these bash shell scripts.<br>
*** Make sure to set execute permissions on these .sh files ***<br>

Here is how I use them:<br>
1) Shut down all the servers running on the same Quake Live server install<br>
2) Run the redownload.sh using one of your workshop.txt files. (If you only have one workshop file, skip to step 4)<br>
3) Run the download_new.sh for each of the workshop files you have, including the one you ran the redownload on, so you can catch any that were missed or see why they didn't download. (you can rename the files to something like download_new_server2.sh, but make sure to have a .sh file for each workshop.txt file)<br>
4) start your servers.<br>

The autodownload.sh is there if you like the way it downloads and overwrites the current files, but I don't use this file.<br>
See the descriptions for each file below.<br>


# autodownload.sh <br>
*** This works best if ran when the server is not running .. because of updates to the appworkshop_282440.acf file *** <br>
This file is for downloading maps to your quake live server without messing with what has already downloaded. <br>
Unlike when the server starts up, this gives a lot more time for the workshop item to download. <br>
Line 10: Edit the workshopFile name to match the name of your server's workshop file.<br>
Line 11: Edit the steamCMD to match the containing directory structure of the steamcmd.sh file.<br>
Line 12: Edit the installLocation to match the directory where your quake live server is installed.<br>

The remaining variables should not need to be edited.<br>

# redownload.sh
*** This needs to be ran when the server is not running .. because it moves the workshop items to a different location so the server will not have access to them until the downloads are complete. *** <br>
This file is for re-downloading maps to your quake live server. <br>
Unlike when the server starts up, this gives a lot more time for the workshop item to download. <br>
It moves the workshop items to a directory named 282440_old then downloads the items to the default directory.<br>
It renames the file used to record what has been downloaded to appworkshop_282440.acf.old so steam thinks nothing has been downloaded.<br>
Line 10: Edit the workshopFile name to match the name of your server's workshop file.<br>
Line 11: Edit the steamCMD to match the containing directory structure of the steamcmd.sh file.<br>
Line 12: Edit the installLocation to match the directory where your quake live server is installed.<br>

The remaining variables should not need to be edited.<br>

# download_new.sh
*** This should be ran when the server is not running .. because the server will not know of the existence of the workshop items until it is started again and editing the appworkshop_282440.acf when the server is running is problematic. *** <br>
This file is for downloading new workshop items added to your workshop items file,<br>
or items that did not load with redownload.sh. <br>
It will skip items that have already been downloaded.<br>
The download messages from steamcmd will be displayed using this file so you can see if a workshop item does not exist.<br>
Line 10: Edit the workshopFile name to match the name of your server's workshop file.<br>
Line 11: Edit the steamCMD to match the containing directory structure of the steamcmd.sh file.<br>
Line 12: Edit the installLocation to match the directory where your quake live server is installed.<br>

The remaining variables should not need to be edited.<br>


If the status messages are not appearing correctly you may have a workshop.txt that is not correctly formatted for Linux.<br>
Try running dos2unix on the file. EX: dos2unix workshop.txt<br>
This will convert the line feeds from windows format to the standard linux format.

# Server Restarting
<b>server_reboot.py and ServerStatus.py</b><br>
The files must be used together. They allow rebooting the linux server if the Quake Live servers are empty.<br>
The server_reboot.py is responsible for checking and rebooting the linux server.<br>
The ServerStatus.py is a minqlx plugin that saves the current player count to the redis database so it can be read by server_reboot.py.<br>
The setup instructions for the files are in the files at the top. The ServerStatus.py should only need to be loaded as a plugin on each Quake Live server, it has no variables that need to be set.<br>
The server_reboot.py has variables at the top of the file, the ones in all CAPS, that need to be set. The redis database password is the only one that HAS to be set if you use a password for your database, otherwise set it to "".<br>
