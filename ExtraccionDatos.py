import os
import re
from os import listdir
from os.path import isfile, join
import PyPDF2
from datetime import datetime
import numpy as np
import mysql.connector

def extraer_delito(texto, lista_delitos):
    texto_minuscula = texto.lower()
    for delito in lista_delitos:
        patron = r'\b' + re.escape(delito.lower()) + r'\b'
        if re.search(patron, texto_minuscula):
            return delito
    return "No encontrado"

lista_delitos = [
    "delito de homicidio", "delito de asesinato", "delito de aborto", "delito de lesiones", 
    "delito de riña tumultuaria", "delito de lesión al feto", "delito de detención ilegal", 
    "delito de secuestro", "delito de amenazas", "delito de coacciones", "delito de tortura", 
    "delito de trata de seres humanos", "delito de agresión sexual", "delito de acoso sexual",
    "delito de omisión del deber de socorro", "delito de allanamiento de morada", "delito de calumnia", 
    "delito de injurias", "delito de hurto", "delito de robo", "delito de extorsión", 
    "delito de estafa", "delito de daños en propiedad ajena", "delito contra la salud pública", 
    "delito contra la seguridad vial", "delito de abuso sexual"
]

def extraer_id_cendoj(texto):
    m = re.search('\d{20}', texto)
    return int(m.group(0)) if m else 0

def extraer_organo(texto):
    m = re.search('Órgano:.*', texto)
    if m:
        organo = m.group(0).replace('Órgano:', '').strip()
        partes = organo.split(".")
        return partes[0].strip(), partes[1].strip() if len(partes) > 1 else np.nan
    return np.nan, np.nan

def extraer_sede(texto):
    m = re.search('Sede:.*', texto)
    return m.group(0).replace('Sede:', '').strip() if m else "No encontrado"

def extraer_seccion(texto):
    m = re.search('Sección:.*', texto)
    return int(m.group(0).replace('Sección:', '').strip()) if m else "No encontrado"

def extraer_fecha(texto):
    m = re.search(r'Fecha:\s*(\d{2}/\d{2}/\d{4})', texto)
    return datetime.strptime(m.group(1), '%d/%m/%Y').strftime('%Y-%m-%d') if m else "No encontrado"

def extraer_recurso_n(texto):
    m = re.search('Nº de Recurso:.*', texto)
    return m.group(0).replace('Nº de Recurso:', '').strip() if m else "No encontrado"

def extraer_juez(texto):
    m = re.search('Ponente:.*', texto)
    return m.group(0).replace('Ponente:', '').strip() if m else "No encontrado"

def extraer_letrado(texto):
    m = re.search('Letrad[oa] de la Administración de Justicia:.*', texto)
    return m.group(0).replace('Letrado de la Administración de Justicia:', '').replace('Letrada de la Administración de Justicia:', '').strip() if m else "No encontrado"

def procesar_archivo_sentencia():
    ruta = r"ProyectoPSP/PDF"
    solo_archivos = [f for f in listdir(ruta) if isfile(join(ruta, f))]
    for nombre_archivo in solo_archivos:
        ruta_archivo = join(ruta, nombre_archivo)
        texto = ""
        with open(ruta_archivo, "rb") as f:
            lector = PyPDF2.PdfReader(f)
            for pagina in range(len(lector.pages)):
                texto += lector.pages[pagina].extract_text() + "\n"

        id_cendoj = extraer_id_cendoj(texto)
        tribunal, sala = extraer_organo(texto)
        sede = extraer_sede(texto)
        seccion = extraer_seccion(texto)
        fecha = extraer_fecha(texto)
        recurso_n = extraer_recurso_n(texto)
        juez = extraer_juez(texto)
        letrado = extraer_letrado(texto)
        delito = extraer_delito(texto, lista_delitos)

        if os.path.isfile(ruta_archivo):
            os.remove(ruta_archivo)
        
        datos_sentencia = (id_cendoj, tribunal, sala, sede, seccion, fecha, recurso_n, juez, letrado, delito)
        print(datos_sentencia)
        
        insertar_datos(datos_sentencia, texto)
        
def insertar_datos(datos_sentencia, texto_completo):
    conexion = mysql.connector.connect(host='localhost', user='root', password='pirineus', 
                                       database='sentencias')
    cursor = conexion.cursor()
    consulta = """INSERT INTO sentencias (cendoj_id, tribunal, sala, sede, seccion, 
                fecha, recurso_n, juez, letrado, delito, texto_completo)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(consulta, datos_sentencia + (texto_completo,))
    conexion.commit()
    cursor.close()
    conexion.close()

if __name__ == "__main__":
    procesar_archivo_sentencia()
