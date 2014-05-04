#!/usr/bin/python

import time
import os.path
import socket

# Variables de sistema
APP_PATH='/home/sysuser/proc_utils/'
BASE_PATH='/home/jllodra/workspace/aisHijack/csv/'
LOG=APP_PATH + "logs/mt_import_db.log"
LOCK= APP_PATH + "mt_import_db.lock"

#print "app_path: {}".format(APP_PATH)

# Fecha
tiempo=time.localtime()
fecha=time.strftime("%Y-%m-%d_%H:%M:%S",tiempo)

file_log = open(LOG,'w+')
file_log.write("-+- START "+fecha+"-+-\n")

# Check if it is already running
if os.path.isfile(LOCK):
    file_log.write("ERROR: lock file already exists\n")
    exit
else:
    file_lock = open(LOCK,'w+')
    file_lock.write("$$ "+socket.gethostname())
    file_log.write("$$ "+socket.gethostname())

    year=time.strftime("%Y",tiempo)
#fn = '/home/helmi/world.csv'
#columns = file(fn).readline()
#print 'create table world (%s text);' % " text,".join(columns.split(','))
#print "copy world from '%s' with csv header;" % fn

#base_path='/home/jllodra/workspace/aisHijack/csv/'

#archivar los ficheros del dia anterior
#year=$(date -d "-1 day" +%Y)
#month=$(date -d "-1 day" +%m)
#day=$(date -d "-1 day" +%d)

#echo "anyo: "$year
#echo "mes: "$month
#echo "dia: "$day

#archive_path=${base_path}'/'${year}'/'${month}

#ais_marinetraffic_2014-01-21_16:10:01_UTC.kml.csv
#files_to_be_archive=`find ${base_path} -maxdepth 1 -name "ais_marinetraffic_${year}-${month}-${day}_*.kml.csv"`
#echo "ficheros: " $files_to_be_archive

#number_of_chars=`echo $files_to_be_archive | wc -c`
        
#if [ $number_of_chars -gt 1 ]; then
            
	#Create the archive path if not exists
#	mkdir -p ${archive_path}
        # Move each file to the archive path
#	mv -f ${files_to_be_archive} ${archive_path}
#
#        echo "Files archived to "${archive_path} >> $LOG
#
#else

#	echo "There aren't new file inside the input directory "${base_path} >> $LOG

#fi

# Remove lock file
#rm -f "$LOCK" &> /dev/null

#echo "-+- END: $(date) -+-" >> "$LOG"
    file_lock.close()
    os.remove(LOCK)

file_log.close()
