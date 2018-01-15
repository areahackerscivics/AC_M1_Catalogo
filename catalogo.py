#!/usr/bin/env python
# encoding: utf-8

import sys, os
import datetime
#from datetime import datetime
from datetime import timedelta
import urllib
from pymongo import MongoClient#Libreria Mongodb
parent_dir=os.getcwd()
path= os.path.dirname(parent_dir)
sys.path.append(path)
import xml.dom.minidom
from xml.dom.minidom import parse


#Conexion a MongoDB
from conexionMongo import *
conexion = getConexion()
client = MongoClient(conexion)
tdb = getDB()
db = client[tdb]
coleccion = getColcatalogo()
catsdb = db[coleccion]

def calculoCatalogo(filename,anyo,mes):

    datafile=os.path.join("AC_M1_Catalogo","FILES","filename") #ruta crontab linux

    DOMTree = xml.dom.minidom.parse(datafile)

    coleccion = DOMTree.documentElement

    #Se extrae el nombre de cada uno de los datasets
    datasets = coleccion.getElementsByTagName('dcat:dataset')
    #Se extrae la fecha en la que se publicó el catálogo
    datafechaAct=coleccion.getElementsByTagName('dct:modified').item(0).firstChild.nodeValue


    #Se inicializa el diccionario con los nombres de las temas (categorías)
    #como aparecen en el xml
    dicc = {
        'ciencia tecnologia': 0,
        'comercio': 0,
        'cultura ocio': 0,
        'demografia': 0,
        'deporte': 0,
        'economia': 0,
        'educacion': 0,
        'empleo': 0,
        'energia': 0,
        'hacienda': 0,
        'industria': 0,
        'legislacion justicia': 0,
        'medio ambiente': 0,
        'medio rural': 0,
        'salud': 0,
        'sector publico': 0,
        'seguridad': 0,
        'sociedad bienestar': 0,
        'transporte': 0,
        'turismo': 0,
        'urbanismo infraestructuras': 0,
        'vivienda': 0
    }

    for dataset in datasets:
        temas = dataset.getElementsByTagName('dcat:theme')
        for tema in temas:
            url =  tema.getAttribute('rdf:resource')
            catBruto = (url.split('/'))[-1]
            categoria = catBruto.replace('-', ' ')

            dicc[categoria] = dicc.get(categoria, 0) + 1

    result = []
    keys = dicc.keys()
    keys.sort()
    today=datetime.date.today()
    for categoria in keys:
        result.append( {'categoria': categoria, 'numDatasets': dicc[categoria]} )
        catdb={
                "anyo":anyo,
                "mes":mes,
                "datos":result,
                "FechaUpdateCatalogo":datafechaAct
                }
    try:
        catsdb.insert_one(catdb)#Almacenar catalogo
        print str(today),":Insertado con exito "
    except:
        print str(today),":Este registro ya existe "

def getCatalogoBLL():
    DAY = timedelta(1)
    today=datetime.date.today()-DAY
    anyo=today.strftime("%Y")
    mes=today.strftime("%m")
    """Devuelve el número de datasets por categoría.

     Retorna  un array con el nombre de la categoría con el número de
     datasets publicados por el ayuntamiento de valencia por categorías

     Nota: Se detectó que puede existir el mismo dataset en más de
     una categoría
    """

    filename = 'catalogo_' + anyo + '_' + mes + '.rdf'
    datafile=os.path.join("AC_M1_Catalogo","FILES","filename") #ruta crontab linux

    if os.path.isfile(datafile):
        return calculoCatalogo(filename,anyo,mes )
    else:
        #Si el año y el mes actuales son los mismos que los de la petición, nos descargamos el nuevo rdf de la web del ayuntamiento y realizamos el cálculo.
        testfile = urllib.URLopener()
        testfile.retrieve("http://gobiernoabierto.valencia.es/wp-content/themes/viavansi-ogov/proxyFile.php?url=http://gobiernoabierto.valencia.es/va/catalogo.rdf", 'FILES/'+filename)
        return calculoCatalogo(filename,anyo,mes)
getCatalogoBLL()
