#!/bin/bash

APP_PATH="/home/dataprocuser/archive_data/archive-radar-site-input-data"
LOG="${APP_PATH}/logs/archive_data.log"
LOCK="${APP_PATH}/lock"

base_path='/home/radar/data_rt/radar_system_eivissa'

echo "-+- START: $(date) -+-" >> $LOG

# Check if it is already running
if [ -e $LOCK ]; then
        echo "ERROR: lock file already exists" >> $LOG
        return 1
else
        echo "$$ $HOSTNAME" > $LOCK
fi

year=$(date -d "-1 month" +%Y)
month=$(date -d "-1 month" +%m)

for site in SCB-CODARSSSITE001 SCB-CODARSSSITE002
do

        site_base_path=${base_path}'/'$site

        base_archive_path=${site_base_path}'/raw_archive'
        input_path=${site_base_path}'/raw_input'

        archive_path=${base_archive_path}'/'${year}'/'${month}

        files_to_be_archive=`find ${input_path} -name "RDL[m|i]_*_${year}_${month}*"`
        number_of_chars=`echo $files_to_be_archive | wc -c`
        
        if [ $number_of_chars -gt 1 ]; then
            
            # Create the archive path if not exists
            mkdir -p ${archive_path}
            # Move each file to the archive path
            mv -f ${files_to_be_archive} ${archive_path}

            echo "Files archived to "${archive_path} >> $LOG

        else

            echo "There aren't new file inside the input directory "${input_path} >> $LOG

        fi

done

# Remove lock file
rm -f "$LOCK" &> /dev/null

echo "-+- END: $(date) -+-" >> "$LOG"