#! /bin/bash
timestamp() {
  date +"%T"
}

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
	if [ ! -d "$installLocation/steamapps/workshop/content/282440/$currentID" ]; then
		echo -e "$(timestamp) Downloading item $(expr $counter + 1) of $numOfIDs from Steam with id $currentID"
		$steamCMD/steamcmd.sh +login anonymous +force_install_dir $installLocation/ +workshop_download_item 282440 $currentID +quit > /dev/null
		if [ $? -ne 0 ]; then
			echo -e "$(timestamp) Download of id $currentID failed with steamcmd error code $?"
		else
			echo -e "$(timestamp) Download of id $currentID completed"
    fi
	else
		echo -e "Steam directory for workshop item $currentID already exists, skipping."
	fi
	((counter++))
done
echo "=== Done === $(date) ==="
exit 0
