#! /bin/bash

me=`basename "$0"`
echo "========== $me has started. =========="
echo "========= $(date) ========="

installLocation='/home/steam/steamcmd/steamapps/common/qlds'
workshopIDs=`cat $installLocation/baseq3/workshop.txt | grep -v '#' | sed '/^[ \t]*$/d'`
numOfIDs=`echo "$workshopIDs" | wc -l`
counter=0

if [ -f "$installLocation/steamapps/workshop/appworkshop_282440.acf" ]; then
  echo -e "Renaming workshop item appworkshop_282440.acf to appworkshop_282440.acf.old"
  mv -f $installLocation/steamapps/workshop/appworkshop_282440.acf $installLocation/steamapps/workshop/appworkshop_282440.acf.old
fi
if [ -d "$installLocation/steamapps/workshop/content/282440_old" ]; then
  rm -rf $installLocation/steamapps/workshop/content/282440_old
fi
if [ -d "$installLocation/steamapps/workshop/content/282440" ]; then
  echo -e "Remaming workshop directory $installLocation/steamapps/workshop/content/282440 to $installLocation/steamapps/workshop/content/282440_old"
  mv $installLocation/steamapps/workshop/content/282440 $installLocation/steamapps/workshop/content/282440_old
fi

while [ $counter -lt $numOfIDs ]; do
	currentID=`echo $workshopIDs | awk '{ print $1 }'`
	workshopIDs=`echo $workshopIDs | cut -d ' ' -f2-`
	echo -e "Downloading item $(expr $counter + 1) of $numOfIDs from Steam with id $currentID"
	/home/steam/steamcmd/steamcmd.sh +login anonymous +force_install_dir $installLocation/ +workshop_download_item 282440 $currentID +quit > /dev/null
	if [ $? -ne 0 ]; then
		echo -e "Download of id $currentID failed with steamcmd error code $?"
	else
		echo -e "Download of id $currentID completed"
	fi
	((counter++))
done
echo "Done."
exit 0
