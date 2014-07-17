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
import urllib2 as urllib
import calendar
import time as tt

# Variables de sistema
HOME_PATH = '/home/aisuser/'
APP_PATH = HOME_PATH + 'netcdf/'
BASE_PATH = HOME_PATH + 'netcdf/'
LOG = HOME_PATH + "logs/netcdf_ais.log"
LOCK = APP_PATH + "netcdf_ais.lock"
LOG_ERROR_FILE = HOME_PATH + "logs/netcdf_ais.err"
NC_PATH = HOME_PATH + 'created_netcdf/'

# Configuración logging
log_error = logging.getLogger('netcdf_ais')
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

date_ayer = date - datetime.timedelta(days=1)
fecha_ayer = date_ayer.strftime("%Y-%m-%d")
year = date_ayer.year
month = date_ayer.strftime('%m')
day = date_ayer.day

# NOTA: eliminar version final 
fecha_ayer = '2014-06-25'

# Fichero log
file_log = open(LOG,'w+')
file_log.write("-+- START " + fecha + "-+-\n")

# Fichero netcdf salida
nc_name_file = NC_PATH + fecha_ayer + "_mt.nc"
ncfile = Dataset(nc_name_file, 'w');

#Conexion ddbb
opciones_db = " dbname=ais user=postgres password=+mngp0st+ port=5432 host=172.16.135.92"

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
 
    # Nota: ahora mismo la dimensión de tiempo es solo 1 ya que se obtienen los datos para todo un día. 
    # TODO: datos horarios a lo largo de un día
    sentencia = "SELECT extract(epoch from date) date, latitude, longitude, ship_cargo, time_sec FROM marine_traffic.grid_time_shipcargo_daily WHERE date='"+fecha_ayer+"'::date AND ship_cargo = 30 limit 10"
    sentencia = "SELECT extract(epoch from date) date, latitude, longitude, ship_cargo, time_sec FROM marine_traffic.grid_time_shipcargo_daily WHERE date='"+fecha_ayer+"'::date AND (ship_cargo = 30 or ship_cargo = 0) limit 10"
    #sentencia = "SELECT extract(epoch from date) date, latitude, longitude, ship_cargo, time_sec FROM marine_traffic.grid_time_shipcargo_daily WHERE date='"+fecha_ayer+"'::date AND ship_cargo = 30"
    file_log.write("fecha consulta: "+fecha+"\n")
    file_log.write("Va a ejecutar .... "+sentencia+"\n")
    cursor_con = conexion.cursor()
    cursor_cont = 0
    try:
        cursor_con.execute(sentencia)
	
        # resultados consulta = data
        data = numpy.array([tuple(row) for row in cursor_con])
        data_date = numpy.array(data[:,0],dtype='f8') # numpy array con todos los valores del campo date
        data_lat = numpy.array(data[:,1],dtype='f8')
        data_lon = numpy.array(data[:,2],dtype='f8')
        data_shipcargo = numpy.array(data[:,3],dtype='i4')
        data_timesec = numpy.array(data[:,4],dtype='f8')
        # Comrpobación: imprimir arrays numpy para las dimensiones y variable ship_cargo
        print "data_date: {}".format(data_date)
        print "data_lat: {}".format(data_lat)
        print "data_lon: {}".format(data_lon)
        print "data_shipcargo: {}".format(data_shipcargo)
        print "data_timesec: {}".format(data_timesec)
        print "resultado array entero (data): {}".format(data)

        # Calcular valores únicos para los índices de las dimensiones
        unique_time = numpy.unique(data_date)
        unique_lat = numpy.unique(data_lat)
        unique_lon = numpy.unique(data_lon)

        print "Valores índices dimensiones y variables"
        print "data_date: {}".format(unique_time)
        print "data_lat: {}".format(unique_lat)
        print "data_lon: {}".format(unique_lon)
        print "data_shipcargo: {}".format(numpy.unique(data_shipcargo))
        print "data_timesec: {}".format(numpy.unique(data_timesec))
        
        # Definir dimensiones (número de valores únicos)
        ndim_time = numpy.size(unique_time)
        ndim_lat = numpy.size(unique_lat)
        ndim_lon = numpy.size(unique_lon)
        print "***dimensiones: tiempo: {} latitude: {}, longitud: {}".format(ndim_time, ndim_lat, ndim_lon)
        
        time = ncfile.createDimension('time', ndim_time) 
        lat = ncfile.createDimension('lat',ndim_lat)
        lon = ncfile.createDimension('lon',ndim_lon)
        
         # Definir variables
        times = ncfile.createVariable('time','f8',('time',))
        latitudes = ncfile.createVariable('latitude','f8',('lat',))
        longitudes = ncfile.createVariable('longitude','f8',('lon',))

        # Atributos variables dimensiones
        times.units = 'seconds since 1970-01-01 00:00:00'
        latitudes.units = 'degrees_north'
        longitudes.units = 'degrees_east'
        
        # Variables 3Dimensiones para almacenar los datos.
        # Una variable por cada tipos valido: sc0, sc30, sc37, sc40, sc50, sc53, sc60, sc70, sc80
        sc0 = ncfile.createVariable('sc0_unspecified','f8',('time','lat','lon'))
        sc30 = ncfile.createVariable('sc30_fisher','f8',('time','lat','lon'))
        sc37 = ncfile.createVariable('sc37_yachts','f8',('time','lat','lon'))
        sc40 = ncfile.createVariable('sc40_hsc','f8',('time','lat','lon'))
        sc50 = ncfile.createVariable('sc50_tug','f8',('time','lat','lon'))
        sc53 = ncfile.createVariable('sc53_aid','f8',('time','lat','lon'))
        sc60 = ncfile.createVariable('sc60_passenger','f8',('time','lat','lon'))
        sc70 = ncfile.createVariable('sc70_cargo','f8',('time','lat','lon'))
        sc80 = ncfile.createVariable('sc80_tanker','f8',('time','lat','lon'))

        # Atributos variables
        sc0.units = 's' 
        sc30.units = 's' 
        sc37.units = 's' 
        sc40.units = 's' 
        sc50.units = 's' 
        sc53.units = 's' 
        sc60.units = 's' 
        sc70.units = 's' 
        sc80.units = 's' 
        
        # Inicializar dimensiones
        tims = numpy.asarray(unique_time)
        times[:] = tims
        lats = numpy.asarray(unique_lat)
        latitudes[:] = lats
        lons = numpy.asarray(unique_lon)
        longitudes[:] = lons     

        print "times: {}".format(times[:])
        #print 'times =\n',times[:]
        print "latitudes: {}".format(latitudes[:])
        print "longitudes: {}".format(longitudes[:])
 

        #Inicializar arrays variables con NaN
        vsc0 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc30 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc37 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc40 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc50 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc53 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc60 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc70 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        vsc80 = numpy.empty((ndim_time, ndim_lat, ndim_lon),dtype='f8')
        #sc30[:] = float(numpy.nan)
        vsc0.fill(float(numpy.NAN))
        vsc30.fill(float(numpy.NAN))
        vsc37.fill(float(numpy.NAN))
        vsc40.fill(float(numpy.NAN))
        vsc50.fill(float(numpy.NAN))
        vsc53.fill(float(numpy.NAN))
        vsc60.fill(float(numpy.NAN))
        vsc70.fill(float(numpy.NAN))
        vsc80.fill(float(numpy.NAN))

        # Asignar variables
        nrow = 0;
        for row in data:
            row_date = row[0]
            row_lat = row[1]
            row_lon = row[2]
            row_shipcargo = row[3]
            row_value = row[4]
     
            # Encontrar índices
            #indice_time = numpy.where(times == row_date.isoformat())[0]
            indice_time = numpy.where(times == row_date)[0]
            indice_lat = numpy.where(latitudes == row_lat)[0]
            indice_lon = numpy.where(longitudes == row_lon)[0]
  
            print "fila ({}) [{}] - idate {}, ilat {}, ilon {}".format(nrow, row, indice_time, indice_lat, indice_lon)
            if row_shipcargo == 0: 
                vsc0[indice_time, indice_lat, indice_lon] = row_value  
            elif row_shipcargo == 30: 
                vsc30[indice_time, indice_lat, indice_lon] = row_value         
                #var_sc30[indice_time, indice_lat, indice_lon] = row_value         
            elif row_shipcargo == 37: 
                vsc37[indice_time, indice_lat, indice_lon] = row_value        
            elif row_shipcargo == 40: 
                vsc40[indice_time, indice_lat, indice_lon] = row_value        
            elif row_shipcargo == 50: 
                vsc50[indice_time, indice_lat, indice_lon] = row_value        
            elif row_shipcargo == 53: 
                vsc53[indice_time, indice_lat, indice_lon] = row_value        
            elif row_shipcargo == 60: 
                vsc60[indice_time, indice_lat, indice_lon] = row_value        
            elif row_shipcargo == 70: 
                vsc70[indice_time, indice_lat, indice_lon] = row_value        
            else: #row_shipcargo == 80: 
                vsc80[indice_time, indice_lat, indice_lon] = row_value        

            nrow = nrow + 1

        # Imprimir netcdf
        print "Imprimir dimensiones"
        print ncfile.dimensions

        #ncfile.sync()
        sc0[:,:,:] = vsc0[:,:,:]
        sc0[:] = vsc0;
        sc30[:,:,:] = vsc30[:,:,:]
        sc30[:] = vsc30;
        sc37[:,:,:] = vsc37[:,:,:]
        sc37[:] = vsc37;
        sc40[:,:,:] = vsc40[:,:,:]
        sc40[:] = vsc40;
        sc50[:,:,:] = vsc50[:,:,:]
        sc50[:] = vsc50;
        sc53[:,:,:] = vsc53[:,:,:]
        sc53[:] = vsc53;
        sc60[:,:,:] = vsc60[:,:,:]
        sc60[:] = vsc60;
        sc70[:,:,:] = vsc70[:,:,:]
        sc70[:] = vsc70;
        sc80[:,:,:] = vsc80[:,:,:]
        sc80[:] = vsc80;
        print "imrpimir variables"
        print ncfile.variables
        print " ** ImpRIMIR vairiables sc30:"
        print ncfile.variables['sc30_fisher'][:]

        print "imrpimir dimensiones. latitudes"
        print ncfile.variables['latitude'][:]
        print "imrpimir dimensiones"
        for dimobj in ncfile.dimensions.values():
	    print dimobj
        
        ncfile.close()

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

