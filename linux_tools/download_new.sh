#! /bin/bash

me=`basename "$0"`
echo "========== $me has started. =========="
echo "========= $(date) ========="

workshopIDs=`cat /home/steam/steamcmd/steamapps/common/qlds/baseq3/workshop.txt | grep -v '#' | sed '/^[ \t]*$/d'`
numOfIDs=`echo "$workshopIDs" | wc -l`
counter=0
installLocation='/home/steam/steamcmd/steamapps/common/qlds/steamapps/workshop/content/282440/'

while [ $counter -lt $numOfIDs ]; do
	currentID=`echo $workshopIDs | awk '{ print $1 }'`
	workshopIDs=`echo $workshopIDs | cut -d ' ' -f2-`
	if [ ! -d "$installLocation$currentID" ]; then
		echo -e "Downloading item $(expr $counter + 1) of $numOfIDs from Steam with id $currentID"
		/home/steam/steamcmd/steamcmd.sh +login anonymous +force_install_dir /home/steam/steamcmd/steamapps/common/qlds/ +workshop_download_item 282440 $currentID +quit > /dev/null
		if [ $? -ne 0 ]; then
			echo -e "Download of id $currentID failed with steamcmd error code $?"
		else
			echo -e "Download of id $currentID completed"
    fi
	else
		echo -e "Steam directory for workshop item $currentID already exists, skipping."
	fi
	((counter++))
done
echo "Done."
exit 0
