#! /bin/bash

me=`basename "$0"`
echo "========== $me has started. =========="
echo "========= $(date) ========="

workshopFile='workshop.txt'
steamCMD='/home/steam/steamcmd'
installLocation='/home/steam/steamcmd/steamapps/common/qlds'
workshopIDs=`cat $installLocation/baseq3/$workshopFile | grep -v '#' | sed '/^[ \t]*$/d'`
numOfIDs=`echo "$workshopIDs" | wc -l`
counter=0

while [ $counter -lt $numOfIDs ]; do
	currentID=`echo $workshopIDs | awk '{ print $1 }'`
	workshopIDs=`echo $workshopIDs | cut -d ' ' -f2-`
	echo -e "Downloading item $(expr $counter + 1) of $numOfIDs from Steam with id $currentID"
	$steamCMD/steamcmd.sh +login anonymous +force_install_dir /home/steam/steamcmd/steamapps/common/qlds/ +workshop_download_item 282440 $currentID +quit > /dev/null
  if [ $? -ne 0 ]; then
      echo -e "Download of id $currentID failed with steamcmd error code $?"
  else
      echo -e "Download of id $currentID completed"
  fi
	((counter++))
done
echo "Done."
exit 0
