#!/usr/bin/python
# -*- coding:utf-8 -*-

#import time
import datetime
import os.path
import socket
import psycopg2

# Variables de sistema
APP_PATH = '/home/aisuser/aislib/proc_utils/'
BASE_PATH = '/home/aisuser/mt_sync/'
BASE_PATH_CSV = BASE_PATH + "csv/"
BASE_PATH_JSON = BASE_PATH + 'json/'
LOG = BASE_PATH + "logs/mt_proc_data.log"
LOCK = BASE_PATH + "mt_proc_data.lock"

# Fecha
date = datetime.datetime.now()
fecha = date.strftime("%Y-%m-%d_%H:%M:%S")

# Fichero log
file_log = open(LOG,'w+')
file_log.write("-+- START "+fecha+"-+-\n")

'''

    1. PROCESAR DATOS: INTRODUCIR CSV EN DDBB

'''

#Cabecera tabla
# id | name | mmsi | ship_cargo_name | sog | cog | latitude | longitude | status | date_time 
campos = "(name, mmsi, ship_cargo_name, sog, cog, latitude, longitude, status, date_time)"
tabla = "marine_traffic.ais_raw"

#Conexion ddbb
#connectStr = "dbname='"+options.databaseName+"' user='"+options.databaseUser+"' host='"+options.databaseHost+"'"
opciones_db = " dbname=ais user=postgres password=+mngp0st+ port=5433 host=scb-dattest"

# Check if it is already running
if os.path.isfile(LOCK):
    file_log.write("ERROR: lock file already exists\n")
    exit
else:
    file_lock = open(LOCK,'w+')
    file_lock.write("$$ "+socket.gethostname())

    date_ayer = date - datetime.timedelta(days=1)
    fecha_ayer = date_ayer.strftime("%Y-%m-%d_%H:%M:%S")
    year = date_ayer.year
    month = date_ayer.month
    day = date_ayer.day
    print "date: {}".format(str(date))
    print "fecha: {}".format(str(fecha))
    print "ayer: {}".format(str(date_ayer))
    print "fecha2: {}".format(str(fecha_ayer))
    print "anyo: {} mes: {}  dia: {}".format(str(year),str(month), str(day))

    # Recorrer el directorio base buscando los ficheros *.csv
    for root, dirnames, filenames in os.walk(BASE_PATH_CSV):
        for filename in filenames:
            if filename.endswith('.csv'):
               print "fichero: {}".format(str(filename))
               sentencia="COPY "+tabla+" "+campos+" FROM '"+root+"/"+filename+"' WITH DELIMITER ';' CSV HEADER;"
               print sentencia
	       conexion = psycopg2.connect(opciones_db)
               cursor_con = conexion.cursor()
               cursor_con.execute(sentencia)
               conexion.commit()
        break # para evitar que profundice en los directorios

    cursor_con.close()
    conexion.close()

    file_lock.close()
    os.remove(LOCK)

file_log.write("-+- END "+fecha+"-+-\n")
file_log.close()
