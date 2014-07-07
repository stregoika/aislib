from netCDF4 import Dataset
import numpy as np

__author__ = 'slora'

#openning file in append mode
nc = Dataset('/home/slora/opendap/observational/drifter/surface_drifter/test/drifter_svp014-scb_svp009/L1/2013/dep0001_drifter-svp014_scb-svp009_L1_2013-12-02.nc', mode='a')
print nc.variables

#selecting the indexes for the measure that will be changed based on a latitude value
select = np.nonzero(nc.variables['LAT'][:] == 44.4811)

#modifying qc values for select index
nc.variables['QC_LAT'][select] = 4
nc.variables['QC_LON'][select] = 4
nc.variables['QC_PSPEED'][select] = 4

#closing the file
nc.close()


