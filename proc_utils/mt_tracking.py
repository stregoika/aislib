#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os.path
import socket
import psycopg2
import sys
import errno
import logging
import traceback

# Variables de sistema
APP_PATH = '/home/aisuser/aislib/proc_utils/'
BASE_PATH = '/home/aisuser/mt_sync/'
LOG = BASE_PATH + "logs/mt_tracking.log"
LOCK = BASE_PATH + "mt_tracking.lock"
LOG_ERROR_FILE = BASE_PATH + "logs/mt_tracking.err" 

# Configuración logging
log_error = logging.getLogger('mt_tracking')
log_error.setLevel(logging.WARN)
# Create the file handler
log_error_hd = logging.FileHandler(LOG_ERROR_FILE)
log_error_hd.setLevel(logging.ERROR)
# Formateador asignado al handler
log_error_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_error_hd.setFormatter(log_error_format)
# Añadir el handler al logger
log_error.addHandler(log_error_hd)

# Fecha
date = datetime.datetime.now()
fecha = date.strftime("%Y-%m-%d_%H:%M:%S")

# Fichero log
file_log = open(LOG,'w+')
file_log.write("-+- START " + fecha + "-+-\n")

#Conexion ddbb
opciones_db = " dbname=ais user=postgres password=+mngp0st+ port=5433 host=scb-dattest"

# Check if it is already running
if os.path.isfile(LOCK):
    print "lock existe"
    log_error.error("ERROR: lock file already exists\n")
else:
    print "lock no existe"
    file_lock = open(LOCK, 'w+')
    file_lock.write("$$ " + socket.gethostname())

    # 1º abrir conexion ddbb
    file_log.write("Conectando a la base de datos ....\n")
    try: 
        conexion = psycopg2.connect(opciones_db)
    except Exception, e:
        log_error.error("Error conexión ddbb. Código: %s. Error: %s",e.pgcode, e.pgerror)
	file_log.write("-+- END "+fecha+"-+-\n")
        file_log.close()
        sys.exit("DDBB ERROR")

    date_ayer = date - datetime.timedelta(days=1)
    fecha_ayer = date_ayer.strftime("%Y-%m-%d")
    
    #print "fecha2: {}".format(str(fecha_ayer))
 
    sentencia = "SELECT marine_traffic.tracking();"   
    file_log.write("fecha ayer tracking: "+fecha_ayer+"\n")
    file_log.write("Va a ejecutar .... "+sentencia+"\n")
    cursor_con = conexion.cursor()
    try:
        cursor_con.execute(sentencia)
        conexion.commit()
    except psycopg2.DatabaseError, e:
        if conexion:
            conexion.rollback()
	log_error.exception("Database Error: tipo %s; código: %s \n%s", str(type(e)), e.pgcode, e)
    except psycopg2.IntegrityError, e:
        if conexion:
            conexion.rollback()
        log_error.exception("Integrity Error: tipo %s; código: %s \n%s", str(type(e)), e.pgcode, e)
    except Exception, e: #resto de excepciones
        if conexion:
            conexion.rollback()
        log_error.exception("Excepcion: tipo %s; código: %s \n%s", str(type(e)), e.pgcode, e)
    else: # se ejecuta si ha ido bien el try - arvhicar ficheros
	file_log.write("EJECUCION OK" \n")
        cursor_con.close()
        conexion.close()
    
    file_lock.close()
    os.remove(LOCK)

file_log.write("-+- END "+fecha+"-+-\n")
file_log.close()
