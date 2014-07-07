#! /usr/bin/env python

import csv
filesource = 'nombre_fichero.csv'
with open(filesource, 'rb') as f:
    reader = csv.reader(f, delimiter=';', quotechar='"')
    for row in reader:
        q = "INSERT INTO nombre_tabla " + \
            "(campo1, campo2, campo3) " + \
            "VALUES ('%s', '%s', '%s')" % (tuple(row[0:3]))
        # instruccion de ejecucion


