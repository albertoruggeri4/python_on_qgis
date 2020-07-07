#########  ESERCIZIO 1:
'''Scrivere una UNICA funzione in cui viene interrogato il DEM andando ad aggiungere ad ogni csv il valore di quota corrispondente alle coordinate indicate,
successivamente trasformare i csv in shapefile. Gli shapefile finali dovranno avere tutti gli attributi presenti nei csv iniziali con aggiunta la quota.
Sarà quindi necessario ripetere il procedimento su tutti i file della cartella utilizzando il ciclo glob. 
ATTENZIONE il DEM ha un sistema di riferimento differente da quello delle coordinate dei csv, 
sarà quindi necessario riproiettarlo (questo lo potete fare all'esterno della funzione). '''


##import delle librerie utili allo svolgimento dell'esercizio

import gdal       #libreria di traduttori per formati di dati geospaziali raster e vettoriali
import os         #libreria che permette di comunicare con il sistema operativo
import csv        #libreria per poter lavorare con i file in formato csv
import glob       #libreria utile per poter recuperare file/percorsi
import ogr, osr 


## settaggio della Working Directory, ovvero la cartella di lavoro
os.chdir("C:/LAB_2")




######   Prima parte: CAMBIO SISTEMA DI RIFERIEMNTO DEL RASTER in WGS84    #####

#caricamento dem originale attraverso la funzione gdal.Open
dataset =gdal.Open('dem_lombardia_100m_ED32N.tif')

#creazione del nome del nuovo raster
raster_r = 'dem_lombardia_100m_WGS84_32N.tif'
#creazione finale del raster attraverso la funzione gdal.Warp che prende come parametri (raster in uscita, raster originale, nuovo SR)
gdal.Warp(raster_r, dataset, dstSRS = 'EPSG:32632')

#chiudo il file che era stato aperto per concludere l'operazione
dataset = None

######   Seconda parte:            ###################

#creazione di una funzione add_q() che prendendo come parametri un dem ed un csv_file, aggiunge la quota dal dem al file csv
def add_q (dem, csv_file):
    csvfile_read = open (csv_file)                              #apertura file csv
    reader = csv.DictReader(csvfile_read, delimiter =',')       #lettura attraverso DictReader  che funziona come un normale lettore Reader ma associa le informazioni di ciascuna riga a un dictcui chiavi sono fornite dal parametro facoltativo fieldnames 
    
    raster = gdal.Open(dem)                                     #apertura file dem
    gt = raster.GetGeoTransform()                               #estrazione geoTransform
    band = raster.GetRasterBand(1)                              #lettura della band come un array
    arr = band.ReadAsArray()
    #print(arr)
    
    lista = []                                                  #creazione lista vuota da riempire in seguito durante il ciclo for
    for row in reader:                                          #Ciclo FOR per il csv_file all'interno del quale andremo ad aggiungere la colonna quota e la riempiremo con la quota estratta dal dem
        
        list_row=[]                                             #creazione lista vuota da riempire in seguito durante il ciclo for
        
        utm_x = float(row['xcoord'])                            #estrazione della xcoord, in float perchè con dict reader abbiamo valori in str
        utm_y = float(row['ycoord'])                            #estrazione della ycoord
        px = int((utm_x-gt[0])/gt[1])                           #calcolo della X px in riferimento alla coord del csv. Al valore di geotrans prendiamo il valore zero che viene sottrratto ad ogni valore del punto
        py = int((utm_y-gt[3])/gt[5])                           #calcolo della Y px in riferimento alla coord del csv
        #print(utm_x,utm_y)
        #print(px,py)
        
        
        
        ###quota###
        quota = band.ReadAsArray(px,py, 1, 1)                   #quota è uguale al valore sulla banda, letta come un array, ma con le particolarità di prendere la coord px e py e con estensione 1 e 1
                                                                #se avessi messo 3 e 3 avrebbe preso un gruppo di punti
        #print(quota)                                           #tipologia array che posso trasformare in seguito in int
        quota_int = int(quota)                                  #trasformazione quota in int
        
        #andiamo a riempire la nuova list_row con tutti gli elementi del csv    
        list_row.append(row['COD_REG'])
        list_row.append(row['COD_CM'])
        list_row.append(row['COD_PRO'])
        list_row.append(row['PRO_COM'])
        list_row.append(row['COMUNE'])
        list_row.append(row['NOME_TED'])
        list_row.append(row['FLAG_CM'])
        list_row.append(row['SHAPE_Leng'])
        list_row.append(row['SHAPE_Area'])
        list_row.append(row['xcoord'])
        list_row.append(row['ycoord'])
        list_row.append(quota_int)
        
        lista.append(list_row)                                  #andiamo ad aggiungere tutti questi valori alla lista che abbiamo creato fuori dal ciclo for
        #print(lista) 
    
    
    #### CREARE ADESSO IL NUOVO FILE CSV ###
    name = csv_file.split('.')[0]+'_quota.csv'                  #creazione nome del nuovo csv, con la funzione split che separa il nome al "punto" in posizione slicing [0], ovvero al primo punto
    csv_out = open(name, 'w')                                   #apriamo il nuovo csv pronto per essere scritto ('w')
    
    #adesso devo definire i campi
    fields = ['COD_REG', 'COD_CM', 'COD_PRO', 'PRO_COM', 'COMUNE', 'NOME_TED', 'FLAG_CM', 'SHAPE_Leng', 'SHAPE_Area', 'xcoord', 'ycoord', 'Quota']
    writer = csv.writer(csv_out)
    writer.writerow(fields)
    writer.writerows(lista)
    
    #infine chiudo i file
    csv_out.close()
    csvfile_read.close()
    #raster = None
    
    
        
    #come per il raster dobbiamo utilizzare un driver 
    driver = ogr.GetDriverByName('ESRI shapefile')
    
    #apro il file questa volta con la funzione CreateDataSource
    shapefile = driver.CreateDataSource(name.split('.')[0] + '_punti_quotati.shp')
    
    
    #open csv che ci servirà per le features (se vedi ?? nei sugg è perchè non hai importato il modulo)
    csvfile = open(name)
    reader = csv.DictReader(csvfile, delimiter = ',')
    # si può fare in un'unica riga:
    # reader = csv.DictReader(open("coordinate_header.csv",delimiter = ',')
    
    
    #create the spatial reference, uso osr --> SR 
    SR =osr.SpatialReference() #creato 
    SR.ImportFromEPSG(32632) #assegnato al csv
    #SR impostiamo uguale ai nostri raster in UTM
    
    #Creare il layer - (name, SR, tipologia shape(puntuale, lineare, poligonale)) wkb=wellknowbase
    layer =shapefile.CreateLayer(name.split('.')[0] + '_punti_quotati.shp', SR, ogr.wkbPoint)
    
    
    # Aggiungiamo i campi dello shp a cui siamo interessati...ogr per creare un campo esterno che poi inserisco in layer  
    
    
    # Definisco nome e tipologia dei vari campi della tabella attributi e li creo
    layer.CreateField(ogr.FieldDefn('Cod_reg', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('Cod_cm', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('Cod_pro', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('Pro_com', ogr.OFTInteger))
    name_field = ogr.FieldDefn('Comune', ogr.OFTString)
    name_field.SetWidth(34) # Definisco lunghezza massima della stringa
    layer.CreateField(name_field)
    layer.CreateField(ogr.FieldDefn('Nome_Ted', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('Flag_cm', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('Shape_Leng', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('Shape_Area', ogr.OFTReal))
    name_field_1 = ogr.FieldDefn('xcoord', ogr.OFTReal)
    layer.CreateField(name_field_1)
    layer.CreateField(ogr.FieldDefn('ycoord', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('Quota', ogr.OFTInteger))
    
    
    
    #creare le features di ogni riga
    for row in reader: # per ogni riga del csv fai i seguenti comandi:
        layer_defn = layer.GetLayerDefn() # estraggo la definizione del layer
        
        feature = ogr.Feature(layer_defn)
        feature.SetField('Cod_reg', row['COD_REG'])
        feature.SetField('Cod_cm', row['COD_CM'])
        feature.SetField('Cod_pro', row['COD_PRO'])
        feature.SetField('Pro_com', row['PRO_COM'])
        feature.SetField('Comune', row['COMUNE'])
        feature.SetField('Nome_Ted', row['NOME_TED'])
        feature.SetField('Flag_cm', row['FLAG_CM'])
        feature.SetField('Shape_Leng', row['SHAPE_Leng'])
        feature.SetField('Shape_Area', row['SHAPE_Area'])
        feature.SetField('xcoord', row['xcoord'])
        feature.SetField('ycoord', row['ycoord'])
        feature.SetField('Quota', row['Quota'])
        
        
        #create the WKT for the feature using Py string formatting
        wkt = "POINT(%f %f)"%  (float(row['xcoord']), float(row['ycoord'])) # scrivo la geometria in linguaggio wkt
        #print(wkt)
        #point - %f %f --- inserisce in float le coordinate 
        point =ogr.CreateGeometryFromWkt(wkt)
        feature.SetGeometry(point)
    
    
        #chiudo i file
        layer.CreateFeature(feature)
        feature = None 
    
    shapefile = None

### applico un ciclo for per chiamare tutti i file .csv presenti nella mia Working Directory ed il file dem 
for file in glob.glob('*csv'):
    dem='dem_lombardia_100m_WGS84_32N.tif'  
    add_q(dem, file)
    
