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
from netCDF4 import Dataset
import numpy


# Variables de sistema
APP_PATH = '/home/aisuser/netcdf/'
BASE_PATH = '/home/aisuser/netcdf/'
LOG = BASE_PATH + "netcdf.log"
LOCK = BASE_PATH + "netcdf.lock"
LOG_ERROR_FILE = BASE_PATH + "netcdf.err"

# Configuración logging
log_error = logging.getLogger('netcdf')
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

# Fichero netcdf salida
nc_name_file = BASE_PATH + "mt.nc"
ncfile = Dataset(nc_name_file, 'w');

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


    # Definir netcdf
    # Definir dimensiones
    time = ncfile.createDimension('time', None); # None
    lat = ncfile.createDimension('lat',2);
    lon = ncfile.createDimension('lon',2);


    # Definir variables
    times = ncfile.createVariable('time','f8',('time',))
    latitudes = ncfile.createVariable('latitude','f8',('lat',))
    longitudes = ncfile.createVariable('longitude','f8',('lon',))

    # Variable 3D para almacenar los datos
 #   ais = ncfile.createVariable('ais','f8',('time','lat','lon'))


    fecha = '2014-06-01'
    #sentencia = "SELECT marine_traffic.tracking();"
    sentencia = "SELECT * FROM marine_traffic.grid_time_shipcargo_daily WHERE date='"+fecha+"'::date LIMIT 2;"
    file_log.write("fecha consulta: "+fecha+"\n")
    file_log.write("Va a ejecutar .... "+sentencia+"\n")
    cursor_con = conexion.cursor()
    cursor_cont = 0
    print "antes de execute"
    try:
        print "entra en el try para ejecutar"
        numi = cursor_con.execute(sentencia)
        AA = numpy.asarray(cursor_con.fetchall())
        print "AA: {}".format(AA)
        results = cursor_con.fetchall()
        print "resultados: {}".format(results)
	num_rows = int(cursor_con.rowcount)
        print "num de filas: {}".format(num_rows)
        print "numi: {}".format(numi)
        # recast this nested tuple to a python list and flatten it so it's a proper iterable:
        print "primer bloque!"
        #x = map(list, list(results))              # change the type
        #x = sum(x, [])                            # flatten
        #print "antes del seugdo blqoe"
        # D is a 1D NumPy array
        #D = NP.fromiter(iterable=x, dtype=float, count=-6)  
        #print "antes del tercer bloque"
        # 'restore' the original dimensions of the result set:
        #D = D.reshape(num_rows, -1)
        #A = numpy.fromiter(cursos_con, dtype=('f8,f8,f8,f8,f8,f8'))
        #A = numpy.fromiter(results, dtype=('f8,f8,f8,f8,f8,f8'))
        #A = np.asarray(results)
        print "voy a imprimir columnas"
        results_c1 = AA['f0']
        results_c2 = AA['f1']
        #print "D reshape: {}".format(D)
        print "results_c1: {}".format(results_c1)
        print "results_c2: {}".format(results_c2)
        while True:
           reg = cursor_con.fetchone();
           print "Dentro del cursor: " % (cursor_cont)

           if reg == None:
               # escribir netcdf
               ncfile.close()
               break

        print "he salido del cursor"

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
        #log_error.exception("Excepcion: tipo %s; código: %s \n%s", str(type(e)), e.pgcode, e)
        log_error.exception("Excepcion: tipo %s; \n%s", str(type(e)), e)
    else: # se ejecuta si ha ido bien el try - arvhicar ficheros
        file_log.write("EJECUCION OK \n")
        cursor_con.close()
        conexion.close()

    file_lock.close()
    os.remove(LOCK)


file_log.write("-+- END "+fecha+"-+-\n")
file_log.close()

