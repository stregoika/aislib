#!/usr/bin/python
# -*- coding: utf-8 -*-

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
file_log.write("-+- START " + fecha + "-+-\n")


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
    file_lock = open(LOCK, 'w+')
    file_lock.write("$$ " + socket.gethostname())

    # 1º abrir conexion ddbb
    file_log.write("Conectando a la base de datos ....\n")
    try: 
        conexion = psycopg2.connect(opciones_db)
    except psycopg.DatabaseError, e:
        file_log.write("Error conexión ddbb\n")

    date_ayer = date - datetime.timedelta(days=1)
    fecha_ayer = date_ayer.strftime("%Y-%m-%d")
    
    print "date: {}".format(str(date))
    print "fecha: {}".format(str(fecha))
    print "ayer: {}".format(str(date_ayer))
    print "fecha2: {}".format(str(fecha_ayer))
    
    init_file = "ais_marinetraffic_" + fecha_ayer + "_"
    end_file = "_UTC.kml.csv" 

    # Recorrer el directorio base buscando los ficheros *.csv
    count_file = 0
    for root, dirnames, filenames in os.walk(BASE_PATH_CSV):
        for filename in filenames:
            if filename.startswith(init_file) and filename.endswith(end_file):
               count_file += 1
               print "({}) fichero: {}".format(count_file,str(filename))
               sentencia="COPY "+tabla+" "+campos+" FROM '"+root+"/"+filename+"' WITH DELIMITER ';' CSV HEADER;"
               print sentencia
	       file_log.write("sentencia: "+sentencia+" \n")
	       conexion = psycopg2.connect(opciones_db)
               cursor_con = conexion.cursor()
	       try:
                   print "va a ejecutar"
                   cursor_con.execute(sentencia)
                   conexion.commit()
                   print "a comiteado"
               except psycopg2.DatabaseError, e:
                   if conexion:
		       conexion.rollback()
	           #file_log.write("Database Error: "+str(e.NameError)+" \n")
	           file_log.write("Database Error \n")
                   break
               except psycopg2.IntegrityError, e:
                   if conexion:
		       conexion.rollback()
	           #file_log.write("Integrity Error: "+str(e.NameError)+" \n")
	           file_log.write("Integrity Error \n")
                   break
               #except Exception as e:
	           #file_log.write("Excepcion: "+str(e.NameError)+" \n")
	        #   file_log.write("Excepcion \n")
                 #  break
        print "******numero total de ficheros: {}".format(count_file)
        if count_file > 0:
            cursor_con.close()
            conexion.close()          
	break # para evitar que profundice en los directorios

    file_lock.close()
    os.remove(LOCK)




'''

   2. ARCHIVAR DATOS HISTORICOS: CSV

'''
year = date_ayer.year
month = date_ayer.month
day = date_ayer.day

ARCHIVE_PATH = BASE_PATH_CSV + year + '/' + month + '/'

#ais_marinetraffic_2014-01-21_16:10:01_UTC.kml.csv



file_log.write("-+- END "+fecha+"-+-\n")
file_log.close()
