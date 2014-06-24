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
    
    fecha = '2014-06-01'
    sentencia = "SELECT date, gid, grid, ship_cargo, time_sec FROM marine_traffic.grid_time_shipcargo_daily WHERE date='"+fecha+"'::date LIMIT 10;"
    file_log.write("fecha consulta: "+fecha+"\n")
    file_log.write("Va a ejecutar .... "+sentencia+"\n")
    cursor_con = conexion.cursor()
    cursor_cont = 0
    print "antes de execute"
    try:
        print "entra en el try para ejecutar"
	#num_rows = int(cursor_con.rowcount)
        cursor_con.execute(sentencia)
        #resultis = cur.fetchall()
	
        # resultados consulta = data
        data = numpy.array([tuple(row) for row in cursor_con])
        data_date = numpy.array(data[:,0],dtype='S10')
        data_lat = numpy.array(data[:,1],dtype='i4')
        data_lon = numpy.array(data[:,2],dtype='i4')
        data_shipcargo = numpy.array(data[:,3],dtype='i4')
        data_timesec = numpy.array(data[:,4],dtype='f8')
        #data_timesec2 = numpy.array(data[:,3],dtype='S15')
        print "data_date: {}".format(data_date)
        print "data_lat: {}".format(data_lat)
        print "data_lon: {}".format(data_lon)
        print "data_shipcargo: {}".format(data_shipcargo)
        print "data_timesec: {}".format(data_timesec)
        #print "data_timesec2: {}".format(data_timesec2)
        print "resultado array: {}".format(data)
        
        unique_time = numpy.unique(data_date)
        unique_lat = numpy.unique(data_lat)
        unique_lon = numpy.unique(data_lon)

        print "vamos a ordenar"
        print "data_date: {}".format(unique_time)
        print "data_lat: {}".format(unique_lat)
        print "data_lon: {}".format(unique_lon)
        print "data_shipcargo: {}".format(numpy.unique(data_shipcargo))
        print "data_timesec: {}".format(numpy.unique(data_timesec))
        
        # Definir dimensiones
        ndim_time = numpy.size(unique_time)
        ndim_lat = numpy.size(unique_lat)
        ndim_lon = numpy.size(unique_lon)
        print "dimensioens: tiempo: {} latitude: {}, longitud: {}".format(ndim_time, ndim_lat, ndim_lon)
        
        time = ncfile.createDimension('time', ndim_time) 
        lat = ncfile.createDimension('lat',ndim_lat)
        lon = ncfile.createDimension('lon',ndim_lon)
        

         # Definir variables
        times = ncfile.createVariable('time','S1',('time',))
        latitudes = ncfile.createVariable('latitude','f8',('lat',))
        longitudes = ncfile.createVariable('longitude','f8',('lon',))

        # Variable 3D para almacenar los datos
        vel_t00 = ncfile.createVariable('vel_t00','f8',('time','lat','lon'))

        # Inicializar dimensiones
        times = numpy.asarray(unique_time)
        latitudes = numpy.asarray(unique_lat)
        longitudes = numpy.asarray(unique_lon)
     
        print "times: {}".format(times[:])
        #print 'times =\n',times[:]
        print "latitudes: {}".format(latitudes[:])
        print "longitudes: {}".format(longitudes[:])
 

        # Empezar a escribir variables
        row = data[0]
        row_date = row[0]
        print "primer fila: {}".format(row)
        print "primera fila, primera columna: {}".format(row_date)
        #indice_time = unique_time.index(row[0])[0]
        indice_time = numpy.where(times[0] == repr(row_date))
        print "TIEMPO: {} índice {}".format(repr(row[0]),indice_time)        

        row_lat = row[1]
        print " primera fila, segunda columna {}".format(row_lat)
        indice_lat = numpy.where(latitudes == row_lat)
        print " indice lat: {}".format(indice_lat[0])
        # Asignar variables
 
        row5 = data[4]
        row5_lat = row5[1]
        indice_lat5 = numpy.where(latitudes == row5_lat)
        print "fila 5: {}, índce lat: {}".format(row5,indice_lat5[0])
 

        indice_time5 = numpy.where(numpy.asarray(data_timesec) == row5[4])
        print "indice time5 {}".format(indice_time5[0])      
        indice_time5 = numpy.where(numpy.asarray(numpy.unique(data_timesec)) == row5[4])
        print "indice ordenado time5 {}".format(indice_time5[0])      


        ncfile.close()
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

