#!/bin/bash

APP_PATH="/home/sysuser/proc_utils/"
LOG="${APP_PATH}/logs/archive_ais_csv.log"
LOCK="${APP_PATH}/archive_ais_csv.lock"

base_path='/home/jllodra/workspace/aisHijack/csv/'

echo "-+- START: $(date) -+-" >> $LOG

# Check if it is already running
if [ -e $LOCK ]; then
        echo "ERROR: lock file already exists" >> $LOG
        return 1
else
        echo "$$ $HOSTNAME" > $LOCK
fi

#archivar los ficheros del dia anterior
year=$(date -d "-1 day" +%Y)
month=$(date -d "-1 day" +%m)
day=$(date -d "-1 day" +%d)

echo "año: "$year
echo "mes: "$month
echo "dia: "$day

archive_path=${base_path}'/'${year}'/'${month}

#ais_marinetraffic_2014-01-21_16:10:01_UTC.kml.csv
files_to_be_archive=`find ${base_path} -maxdepth 1 -name "ais_marinetraffic_${year}-${month}-${day}_*.kml.csv"`
echo "ficheros: " $files_to_be_archive

number_of_chars=`echo $files_to_be_archive | wc -c`
        
if [ $number_of_chars -gt 1 ]; then
            
	#Create the archive path if not exists
	mkdir -p ${archive_path}
        # Move each file to the archive path
	mv -f ${files_to_be_archive} ${archive_path}

        echo "Files archived to "${archive_path} >> $LOG

else

	echo "There aren't new file inside the input directory "${base_path} >> $LOG

fi

# Remove lock file
rm -f "$LOCK" &> /dev/null

echo "-+- END: $(date) -+-" >> "$LOG"
