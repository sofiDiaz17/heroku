from flask import Flask, render_template, request, json, session, g
from flaskext.mysql import MySQL
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import hashlib
import requests, uuid
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from array import array
from PIL import Image
import sys
import time
import requests
import json
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from io import BytesIO
import time
import re
import smtplib
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import pathlib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64 

import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


KEY = '7ee7446ab0c44ec9b79e2baaa14ba40b'
ENDPOINT = 'https://ekkos02.cognitiveservices.azure.com/'

_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))
text_recognition_url = ENDPOINT + "/vision/v3.1/read/analyze"

app = Flask(__name__)

app.config["DEBUG"] = True
app.config['MYSQL_DATABASE_USER'] = 'sepherot_sofia'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zueTmwnaGI3X'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_sofiaBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL(app)


def validarUsuario( _email, _password):
    try:
        if _email and _password:
            #print("En el modelo")
            conn=mysql.connect()
            cursor = conn.cursor()
            query = "SELECT * FROM CUsers WHERE Email = %s"
            try:
                cursor.execute(query,(_email))
                data= cursor.fetchall()
                print(data)
                salt=data[0][4]
                sPass=hashlib.sha512(_password.encode('utf-8')  + salt.encode('utf-8')).hexdigest()
                if data and data [0][14] == "CALL_CENTER":
                    return 3
                else:
                    if data and data [0][3] == sPass:
                        print(data[0][15])
                        if len(data[0][15])>0:
                            return 1
                        else:
                            return 2
                        return True 
                    else: 
                        return False
            except Exception as e:
                return e 
            cursor.close()
            conn.close()
        else:
            return json.dumps ({'html': '<span> Te faltan datos </span>'})            
    except Exception as e:
        return json.dumps ({'error': str(e)})

    
def crearUsr(_correo, _contraseña,_salt,_cel,_img):
    try:
        if _correo and _contraseña and _cel:
            conn = mysql.connect()
            cursor = conn.cursor()
            query="INSERT INTO CUsers (email, password, salt, Phone, OnBoardingState, BipTips,BIT) VALUES (%s, %s, %s,%s,0,0,%s);"
            try:
                cursor.execute(query, (_correo,_contraseña,_salt,_cel,_img))
              
                return True
            except Exception as e:
                print(str(e))
                return False
            cursor.close() 
            conn.close()
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        return json.dumps({'error':str(e)})



def buscarUser(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT * FROM CUsers WHERE email = %s"
        try:
            cursor.execute(query, (_user))
            data = cursor.fetchall()
            if data:
                return data[0][5]
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def fotoUser(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT Selfie FROM CUsers WHERE email = %s"
        try:
            cursor.execute(query, (_user))
            data = cursor.fetchall()
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e
        finally:
            cursor.close() 
            conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def buscarBIT(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT BIT FROM CUsers WHERE email = %s"
        try:
            cursor.execute(query, (_user))
            data = cursor.fetchall()
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e
        finally:
            cursor.close() 
            conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def dataUsuario(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT invoice, amount, date, categoryName, points, expiration,statusName FROM T_Movements, C_Categories, C_Status WHERE user=%s and expiration > CURRENT_DATE and category = categoryId and status = statusId"
        try:
            cursor.execute(query, (_user))
            data = cursor.fetchall()
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def puntosUsuario(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT points FROM T_Movements where expiration > CURRENT_DATE and status=2 and user=%s"
        try:
            cursor.execute(query, (_user))
            data = cursor.fetchall()
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def expDate(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT expiration FROM T_Movements where user = %s  and expiration > CURRENT_DATE and status=2 ORDER BY T_Movements.expiration ASC LIMIT 1"
        try:
            cursor.execute(query, (_user))
            data = cursor.fetchall()
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})
    

def puntfal(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT points FROM T_Movements where status=1 and user= %s"
        cursor.execute(query,_user)
        data = cursor.fetchall()
        try:
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def bitsUser(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        queryBip="SELECT Biptips FROM CUsers where email = %s"
        cursor.execute(queryBip,_user)        
        data = cursor.fetchall()
        try:
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e 
        cursor.close() 
        conn.close()        
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def rewardsUsr(_bips):
    if _bips:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT * FROM C_Levels WHERE levelBipTips <= %s ORDER BY levelId DESC LIMIT 1"
        cursor.execute(query,_bips)
        data = cursor.fetchall()
        try:
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e 
        cursor.close() 
        conn.close()        
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})
 
        
def nextLvl(_level):
    if _level:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT * FROM C_Levels where levelId = %s + 1"
        cursor.execute(query,_level)
        data = cursor.fetchall()
        try:
            if data:
                return data
            else:
                return False
        except Exception as e:
            return e 
        cursor.close() 
        conn.close()        
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})

def crearPurch(folio, user, monto, fecha,  rubro, arch, bips):
    conn = mysql.connect()
    cursor = conn.cursor()
    if rubro == '1':
        puntos=int(float(monto))*0.13
    elif rubro == '2' or rubro == '3':
        puntos=int(float(monto))*0.10
    elif rubro == '4':
        puntos=int(float(monto))*0.5
    else:
        puntos=int(float(monto))*0.15
    date_object=datetime.datetime.strptime(fecha, "%Y-%m-%d")
    if int(bips) < 1000:
        exp=date_object+relativedelta(days=+7)
    elif int(bips) > 999 and int(bips) < 2000:
        exp=date_object+relativedelta(days=+10)
    elif int(bips) > 1999 and int(bips) < 3000:
        exp=date_object+relativedelta(days=+14)
    elif int(bips) > 2999 and int(bips) < 4000:
        exp=date_object+relativedelta(days=+20)
    elif int(bips) >= 4000:
        exp=date_object+relativedelta(days=+24)
    query="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, %s, %s, %s, %s ,%s, %s, 1)"
    try:
        done=cursor.execute(query, (folio, user, monto,fecha, rubro,puntos,exp, arch))
        if done:
            today=datetime.datetime.now()
            d1 = today.strftime("%Y-%m-%d")
            ddd=datetime.datetime.strptime(d1, '%Y-%m-%d').date()
            expR=ddd+relativedelta(years=+1)

            if int(bips) + 300 >= 4000:
                id="regalo1500"+user
                points=1500
                doc="regalo1500"
                try:
                    queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                
            elif int(bips) + 300 >= 3000:
                id="regalo1000"+user
                points=1000
                doc="regalo1000"
                try:
                    queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                
            elif int(bips) + 300 >= 2000:
                id="regalo700"+user
                points=700
                doc="regalo700"
                try:
                    queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))

            elif int(bips) + 300 >= 1000:
                id="regalo500"+user
                points=500
                doc="regalo500"
                try:
                    queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                


            queryBips="UPDATE CUsers SET Biptips = Biptips + 300 WHERE email = %s"
            doneBip=cursor.execute(queryBips, (user))
            if doneBip:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(str(e))
        return False
    cursor.close() 
    conn.close()


def insertarDevolucion(user,objeto,razon,domicilio):
    conn = mysql.connect()
    cursor = conn.cursor()
    query="Insert into S_C_REFUND1 (EMAIL_R, PRODUCT_R, REASON_R, ADRRESS, STATUS_R) values (%s,%s,%s,%s,1)"
    try:
        cursor.execute(query,(user,objeto,razon,domicilio))
        return True
    except Exception as e:
        print(str(e))
        return False


def pedidos(user):
    conn = mysql.connect()
    cursor = conn.cursor()
    query="SELECT amountPurchase, datePurchase, objetoPurchase, objectPictures, objectName FROM T_Purchases, C_Catalog WHERE objectName = objetoPurchase AND user = %s"
    try:
        cursor.execute(query,user)
        data = cursor.fetchall()
        if data:
            return data
        else:
            return False
    except Exception as e:
        return e
    cursor.close() 
    conn.close()


def catalogo(cant):
    conn = mysql.connect()
    cursor = conn.cursor()
    query="SELECT * FROM C_Catalog LIMIT %s"
    try:
        cursor.execute(query,cant)
        data = cursor.fetchall()
        if data:
            return data
        else:
            return False
    except Exception as e:
        return e
    cursor.close() 
    conn.close()

def buscarObj(_nombre):
    conn = mysql.connect()
    cursor = conn.cursor()
    query="SELECT * FROM C_Catalog where objectName = %s"
    try:
        cursor.execute(query,_nombre)
        data = cursor.fetchall()
        if data:
            return data
        else:
            return False
    except Exception as e:
        return e
    cursor.close() 
    conn.close()

def estadoOnboarding(user):
    conn = mysql.connect()
    cursor = conn.cursor()
    query="Select OnBoardingState from CUsers where email = (%s)"
    try:
        cursor.execute(query, (user))
        data = cursor.fetchall()
        if data:
            return data
        else:
            return False
    except Exception as e:
        print(str(e))
        return False
    cursor.close() 
    conn.close()

def setEstadoOnboarding(user,estado):
    conn = mysql.connect()
    cursor = conn.cursor()
    query="Update CUsers set OnBoardingState = %s where email= %s"
    try:
        done=cursor.execute(query, (estado, user))
        if done:
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False
    cursor.close() 
    conn.close()


def comprar(user, compra,objeto,bips):
    conn = mysql.connect()
    cursor = conn.cursor()
    selectPuntos="SELECT points FROM T_Movements where expiration > CURRENT_DATE and status=2 and user=%s"
    cursor.execute(selectPuntos, (user))
    puntos = cursor.fetchall()
    print("los puntos del usuario son:")
    print(puntos)
    pns=0
    try:
        for data in puntos:
            pns = pns + data[0]
            print(data)
    except:
        pns = 0
    print(pns)
    resta = pns - int(compra)
    print(resta)
    
    datosViejos="SELECT * FROM T_Movements where user = %s  and expiration > CURRENT_DATE and status=2 ORDER BY T_Movements.expiration ASC LIMIT 1"
    try:
        cursor.execute(datosViejos, (user))
        dv = cursor.fetchall()
    except Exception as e:
        print(str(e))
        return False
    print(dv)
    today=datetime.datetime.now()
    d1 = today.strftime("%Y-%m-%d")
    category=dv[0][5]
    expR=dv[0][7]

    updatePuntos="UPDATE T_Movements set status=5 where expiration > CURRENT_DATE and status=2 and user=%s"
    try:
        cursor.execute(updatePuntos, (user))
    except Exception as e:
        print(str(e))
        return False

    compraRest="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, status) values (%s, %s, 0, %s, %s, %s ,%s, 2)"
    try:
        cursor.execute(compraRest, ("Restantes",user,d1,category,resta,expR))
    except Exception as e:
        print(str(e))
        return False
        
    

    compraReg="Insert into T_Purchases (amountPurchase, user, objetoPurchase) values (%s,%s,%s)"
    try:
        cursor.execute(compraReg, (int(compra),user,objeto))
        today=datetime.datetime.now()
        d1 = today.strftime("%Y-%m-%d")
        ddd=datetime.datetime.strptime(d1, '%Y-%m-%d').date()
        expR=ddd+relativedelta(years=+1)

        if int(bips) + 150 >= 4000:
            id="regalo1500"+user
            points=1500
            doc="regalo1500"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))
                
        elif int(bips) + 150 >= 3000:
            id="regalo1000"+user
            points=1000
            doc="regalo1000"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))
                
        elif int(bips) + 150 >= 2000:
            id="regalo700"+user
            points=700
            doc="regalo700"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))

        elif int(bips) + 150 >= 1000:
            id="regalo500"+user
            points=500
            doc="regalo500"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))
                


        queryBips="UPDATE CUsers SET Biptips = Biptips + 150 WHERE email = %s"
        doneBip=cursor.execute(queryBips, (user))
        if doneBip:
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False




def entities(user,stage,info):
    conn = mysql.connect()
    cursor = conn.cursor()
    query="Insert into T_Entities (user, stage, stageinfo) values (%s, %s, %s)"
    try:
        done=cursor.execute(query, (user, stage, info))
        if done:
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False
    cursor.close() 
    conn.close()



"B & R"

def CrearPDF(_name,_rfc, _email,_direccion,_fechanacimiento):
    
    prueba = pathlib.Path("Contrato_OrangeJuice.pdf")
    if prueba.exists ():
        print ("File exist")
        os.remove(".\Contrato_OrangeJuice.pdf")
    else:
        print("NO EXISTE")
            
    if _name and _rfc and _email and _direccion and _fechanacimiento:
        _Nombre= _name
        _NombreArchivo="Contrato_OrangeJuice.pdf" 
        _TituloDocumento="Contrato Orange Juice"
        _SubtituloDocumento=_Nombre
        _curp=_rfc
        _FechaNacimiento=_fechanacimiento
        _Direccion=_direccion
        _Email=_email
        c=canvas.Canvas(_NombreArchivo)
        c.setTitle(_TituloDocumento)
        c.setLineWidth(.3)
        c.setFont('Helvetica',20)
        #print(_FechaNacimiento)
        textLines = ['Este es el contrato de: ', _Nombre ,'Quien poseé el CURP: ', _curp ,'Su fecha de nacimiento es: ', str(_FechaNacimiento) ,'Su estado civil es; ', '' ,'Su dirección es: ', _Direccion,'Correo electrónico:',_Email,' ' ,'textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto']

        c.drawCentredString(300,760,_TituloDocumento)
        c.setFont('Helvetica',14)
        c. drawCentredString(290,720,_SubtituloDocumento)
        text = c.beginText(60,720)
        text.setFont("Helvetica", 10)
        contador = 0    
        for line in textLines:
            contador = contador +1
            #print("Prueba", + contador)
            text.textLine(line)
        c.drawText(text)
        c.drawCentredString(300,80,_Nombre)
        c.line(200,100,400,100)
        c.save()
        #bandera=1
        return True
    else:
        print("error")
        #return json.dumps({'html':'<span>Datos faltantes</span>'})
        #bandera=0
        return False
    
       
       
def EnviarCorreoContrato(_name,_email):
    nombre=_name
    destinatario=_email
    usuraio='ekkoscorp@gmail.com'
    archivo= '.\Contrato_OrangeJuice.pdf'
    #message ='Bienvenido al Sistema de puntos Ekkos!'
    Asunto = 'Inscripción Orange Juice Points'
    mensaje = MIMEMultipart("plain")#estandar
    mensaje["Subject"]=Asunto
    mensaje["From"]=usuraio
    mensaje["To"]=destinatario
    
    html=f"""
    <html>
    <body>
        Hola <i>{nombre}</i> <i>{destinatario}</i></br>
        Bienvenido a <b>Orange Juice Points System</b>
        Ingresa al link siguiente para subir tu contrato.
        http://127.0.0.1:5000

    </body>
    </html>
    """
    parte_html=MIMEText(html,"html")

    mensaje.attach(parte_html)
    
    
    adjunto=MIMEBase("application","octect-stream")
    adjunto.set_payload(open(archivo,"rb").read())
    #print("Lo encontré")
    encode_base64(adjunto)

    adjunto.add_header("content-Disposition",f"attachment; filename={archivo}")
    mensaje.attach(adjunto)
    mensaje_final= mensaje.as_string()
    server =smtplib.SMTP('smtp.gmail.com')
    server.starttls()
    server.login(usuraio,'EkkosC0rp')

    #print("Inicio seción")
    #server.sendmail('ekkoscorp@gmail.com','robertoxd27@gmail.com', message)
    server.sendmail(usuraio,destinatario,mensaje_final)
    server.quit()
    print("Correo enviado exitosamente!")
    return True



def IngresarIDelante(busqueda,_nombrearchivo):
    try:

        usuario=busqueda
        if _nombrearchivo and busqueda:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="CUsers"
   
            sqlCreateSP="UPDATE "+ _TABLA +" SET IneFront ='"+ _nombrearchivo +"' WHERE Email = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return True
            else:
                return False
            cursor.close()
            conn.close()
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})


def ImagenATextoINE(usuario,_urline):
    bandera1=0
    headers = {'Ocp-Apim-Subscription-Key': KEY,'Content-Type': 'application/octet-stream'}
    with open(_urline, 'rb') as f:
        data = f.read()
    response = requests.post(
        text_recognition_url, headers=headers, data=data)

    #operation_url = response.headers["Operation-Location"]

    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
   
        time.sleep(1)
        if ("analyzeResult" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'failed'):
            poll = False
    
    contador= ' '
    if analysis['status'] == "succeeded":
        #print(analysis["analyzeResult"]["readResults"][0]["lines"])
        for l in analysis["analyzeResult"]["readResults"][0]["lines"]:
            #print(l["text"])
            contador=contador+ '\n' + l["text"]
                
    #print(contador)
    #import re
    bandera=""
    bandera = (r"INSTITUTO NACIONAL ELECTORAL\n"
	r"([a-zA-Z0-9]+.+)")
    bandera = re.findall(bandera, contador, re.MULTILINE)
    if len(bandera) >0:
        print("Si es una INE")
        if usuario:
            conn = mysql.connect()
            cursor = conn.cursor()
            regex = (r"FECHA DE NACIMIENTO\n"
            r"(\w+)\n"
            r"(\d{2}/\d{2}/\d{4})\n"
            r"(\w+)\n"
            r"SEXO H\n"
            r"([a-zA-Z0-9]+.+)\n")

            regex2 = (r"FECHA DE NACIMIENTO\n"
            r"(\w+)\n"
            r"(\d{2}/\d{2}/\d{4})\n"
            r"(\w+)\n"
            r"SEXO M\n"
            r"([a-zA-Z0-9]+.+)\n")

            domicilio = (r"DOMICILIO\n"
            r"([a-zA-Z0-9]+.+)\n"
            r"([a-zA-Z0-9]+.+)")

            curp = (r"CURP ([a-zA-Z0-9]+.+)\n")

            ApellidoPat = (r"FECHA DE NACIMIENTO\n"
            r"(\w+)")

            fechareg=(r"(\d{2}/\d{2}/\d{4})\n")

            ApellidoPat = re.findall(ApellidoPat, contador, re.MULTILINE)
            curp = re.findall(curp, contador, re.MULTILINE)
            matches = re.findall(regex, contador, re.MULTILINE)
            matches2 = re.findall(regex2, contador, re.MULTILINE)
            domicilio = re.findall(domicilio, contador, re.MULTILINE)
            ff=re.findall(fechareg, contador, re.MULTILINE)
            print(contador)
            print(domicilio)
            print(ApellidoPat)
            print(matches)
            print(curp)
            #print(ff)
            try:
                fecha=matches[0][1]
                fecha2=fecha[6:10]+"-"+fecha[3:5]+"-"+fecha[0:2]
            except:
                fecha=matches2[0][1]
                fecha2=fecha[6:10]+"-"+fecha[3:5]+"-"+fecha[0:2]
                
            #print(fecha2)
            domicilio2=domicilio[0][0]
            domicilio2=domicilio2+ " " +domicilio[0][1]
            curp=curp[0]
            try:
                Nombre=matches[0][0]+" "+matches[0][2]+" "+matches[0][3]
            except:
                Nombre=matches2[0][0]+" "+matches2[0][2]+" "+matches2[0][3]

            print(Nombre)
            print(curp)
            print(domicilio2)
            _TABLA="CUsers"
            query= "SELECT * FROM CUsers WHERE Name ='"+Nombre+"'"
            try: 
                cursor.execute(query)
                data = cursor.fetchall()
                if data:
                    cursor.close()
                    conn.close()
                   
                    rfc=data[0][8]

                    if rfc == curp:
                        bandera1=2
                        print("INE invalida, persona ya registrada")
                        #usuario=busqueda
                        conn = mysql.connect()
                        cursor = conn.cursor()
                        sqlCreateSP="UPDATE "+ _TABLA +" SET IneFront =''  WHERE Email = '"+usuario+"'"
                        cursor.execute(sqlCreateSP)
                        conn.commit()
                        cursor.close()
                        conn.close()
                        return bandera1
                    else:
                        try:
                                if usuario:            
                                    conn = mysql.connect()
                                    cursor = conn.cursor()
                                    sqlCreateSP="UPDATE "+ _TABLA +" SET Name ='"+ Nombre +"',  CURP = '"+ curp +"',  BirthDate = '"+ fecha2 +"',  Address = '"+ domicilio2 +"' WHERE Email = '"+usuario+"'"
                                    cursor.execute(sqlCreateSP)                                    
                                    bandera1=3
                                    return bandera1
                                else:
                                    return json.dumps({'html':'<span>Datos faltantes</span>'})
                        except Exception as e:
                            print(json.dumps({'error':str(e)}))
                            return json.dumps({'error':str(e)})
                        finally:
                            cursor.close()
                            conn.close()
                            return bandera1
                    
                   
                else:
                    cursor.close()
                    conn.close()
                    #usuario=busqueda
                    if usuario:            
                        conn = mysql.connect()
                        cursor = conn.cursor()
                        sqlCreateSP="UPDATE "+ _TABLA +" SET Name ='"+ Nombre +"',  CURP = '"+ curp +"',  BirthDate = '"+ fecha2 +"',  Address = '"+ domicilio2 +"' WHERE Email = '"+usuario+"'"
                        cursor.execute(sqlCreateSP)
                        data=cursor.fetchall()                       
                        conn.commit()
                        cursor.close()
                        conn.close()
                        bandera1 = 3
                        
                        return bandera1
                        
                    return bandera1

                    
            except Exception as e:
                print(str(e))
                cursor.close()
                conn.close()
                return e
        else: 
            print("Te faltan datos")
            return json.dumps ({'html': '<span> Te faltan datos </span>'})

    else:
        print("No es una INE, documento invalido")
        #usuario=busqueda
        conn = mysql.connect()
        cursor = conn.cursor()
        _TABLA="CUsers"
        sqlCreateSP="UPDATE "+ _TABLA +" SET IneFront =''  WHERE Email = '"+usuario+"'"
        cursor.execute(sqlCreateSP)
        conn.commit()
        cursor.close() 
        conn.close()
        #os.remove(_urline)
        bandera1=1
        return bandera1



def IngresarIDetras(usuario,_nombrearchivo):
    try:
        #   _usuario = request.args.get('Usuario')
        #   _evento = request.args.get('Evento')
        usuario
        if _nombrearchivo and usuario:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="CUsers"
            sqlCreateSP="UPDATE "+ _TABLA +" SET IneBack ='"+ _nombrearchivo +"' WHERE Email = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()



def ImagenATextoINEAtras(busqueda,_urline):
    bandera1=0
    headers = {'Ocp-Apim-Subscription-Key': KEY,'Content-Type': 'application/octet-stream'}
    with open(_urline, 'rb') as f:
        data = f.read()
    response = requests.post(
        text_recognition_url, headers=headers, data=data)

    #operation_url = response.headers["Operation-Location"]

    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
   
        time.sleep(1)
        if ("analyzeResult" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'failed'):
            poll = False

    contador= ' '
    if analysis['status'] == "succeeded":
        #print(analysis["analyzeResult"]["readResults"][0]["lines"])
        for l in analysis["analyzeResult"]["readResults"][0]["lines"]:
            #print(l["text"])
            contador=contador+ '\n' + l["text"]
                    
    
    bandera=""
    bandera = (r"INE\n"
	r"([a-zA-Z0-9]+.+)")

    bandera = re.findall(bandera, contador, re.MULTILINE)
    print(bandera)
    if len(bandera) >0:
        print("Si es una INE")
        if busqueda:
            conn = mysql.connect()
            cursor = conn.cursor()
            regex = (r"INSTITUTO NACIONAL ELECTORAL\n"
            r"(\w+)")

            matches = re.findall(regex, contador, re.MULTILINE)
            print(matches)
            idatras=matches[0]
            print(idatras)
            _TABLA="CUsers"
            query= "SELECT * FROM CUsers WHERE IdBack ='"+idatras+"'"

            try: 
                cursor.execute(query)
                data = cursor.fetchall()
                if data:
                    cursor.close()
                    conn.close()
                    
                    bandera1=2
                    print("INE invalida, persona ya registrada")
                    usuario=busqueda
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    
                    sqlCreateSP="UPDATE "+ _TABLA +" SET IneBack =''  WHERE Email = '"+usuario+"'"
                    cursor.execute(sqlCreateSP)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    os.remove(_urline)
                    return bandera1
                    
                    
                else:
                    usuario=busqueda
                              
                    #print("paso 1 ideatras")
                    conn = mysql.connect()
                    #print("paso 2 ideatras")
                    cursor = conn.cursor()
                   
                    sqlCreateSP="UPDATE "+ _TABLA +" SET IdBack ='"+ idatras +"' WHERE Email = '"+usuario+"'"
                    cursor.execute(sqlCreateSP)                    
                    bandera1=3
                    return bandera1
            except Exception as e:
                print(e)
                cursor.close()
                conn.close()
                return e
        else: 
                return json.dumps ({'html': '<span> Te faltan datos </span>'})

    else:
        print("No es una INE, documento invalido")
        usuario=busqueda
        conn = mysql.connect()
        cursor = conn.cursor()
        sqlCreateSP="UPDATE "+ _TABLA +" SET IneBack =''  WHERE Email = '"+usuario+"'"
        cursor.execute(sqlCreateSP)
        conn.commit()
        cursor.close()
        conn.close()
        os.remove(_urline)
        bandera1=1
        return bandera1


def IngresarComprobante(busqueda,_nombrearchivo):
    try:
        usuario=busqueda
        if _nombrearchivo and busqueda:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="CUsers"
  
            sqlCreateSP="UPDATE "+ _TABLA +" SET ProofAddress ='"+ _nombrearchivo +"' WHERE Email = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            cursor.close()
            conn.close()
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(str(e))
        return json.dumps({'error':str(e)})
        



def ImagenATextoDomicilio(usuario,_urline):
    headers = {'Ocp-Apim-Subscription-Key': KEY,'Content-Type': 'application/octet-stream'}
    with open(_urline, 'rb') as f:
        data = f.read()
    response = requests.post(
        text_recognition_url, headers=headers, data=data)

    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()
   
        time.sleep(1)
        if ("analyzeResult" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'failed'):
            poll = False
    
    contador= ' '
    if analysis['status'] == "succeeded":
        #print(analysis["analyzeResult"]["readResults"][0]["lines"])
        for l in analysis["analyzeResult"]["readResults"][0]["lines"]:
            #print(l["text"])
            contador=contador+ '\n' + l["text"]
                 
                
    #print(contador)
    bandera=""
    bandera =  r"Domicilio ([a-zA-Z0-9]+.+)"
    bandera2=""
    bandera2= (r"([a-zA-Z0-9]+.+)\n"
	r"Direccion:\n"
	r"([a-zA-Z0-9]+.+)")
    bandera = re.findall(bandera, contador, re.MULTILINE)
    bandera2 = re.findall(bandera2, contador, re.MULTILINE)
    if not bandera and not bandera2:
        return 1
    print(bandera)
    bandera=bandera[0]
    print(bandera2)
    
    print(" ")
    if len(bandera) >0 or len(bandera2)>0 :
        print("Entro")
        if len(bandera2) == 0:
            direccion=bandera
        else:
            direccion=bandera2[0][0]+bandera2[0][1]
        
        
        print(direccion)
        try:
            
            if usuario:            
                conn = mysql.connect()
                print("paso 2")
                cursor = conn.cursor()
                _TABLA="CUsers"
                sqlCreateSP="UPDATE "+ _TABLA +" SET Address ='"+ direccion +"' WHERE Email = '"+usuario+"'"
                cursor.execute(sqlCreateSP)
                bandera1=0
                cursor.close()
                conn.close()
                return bandera1
            else:
                print("no ve usuario")
                return json.dumps({'html':'<span>Datos faltantes</span>'})
        except Exception as e:
            print(str(e))
            return json.dumps({'error':str(e)})
            
    else:
        print("No reconoce Domicilio")
        conn = mysql.connect()
        cursor = conn.cursor()
        sqlCreateSP="UPDATE "+ _TABLA +" SET ProofAddress =''  WHERE Email = '"+usuario+"'"
        cursor.execute(sqlCreateSP)
        conn.commit()
        cursor.close()
        conn.close()
        os.remove(_urline)
        bandera1=1
        return bandera1



    
def IngresarSelfie(usuario,_nombrearchivo):
    try:
       
        if _nombrearchivo and usuario:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="CUsers"
            sqlCreateSP="UPDATE "+ _TABLA +" SET Selfie ='"+ _nombrearchivo +"' WHERE Email = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
            else:
                return json.dumps({'error':str(data[0])})
            cursor.close()
            conn.close()
        else:
            print("NO VE DATA")
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(str(e))
        return json.dumps({'error':str(e)})



def SelectNombre(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT Name FROM CUsers WHERE Email ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                nombre=data[0][0]
                return nombre
            else:
                return False
        except Exception as e:
            return e
            
        cursor.close()
        conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})  
    
def SelectCorreo(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT Email FROM CUsers WHERE Email ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                correo=data[0][0]
                return correo
            else:
                return False
        except Exception as e:
            return e
        cursor.close()
        conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'}) 

def SelectDireccion(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT Address FROM CUsers WHERE Email ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                direccion=data[0][0]
                return direccion
            else:
                return False
        except Exception as e:
            return e
        cursor.close()
        conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})

def SelectFecha(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT BirthDate FROM CUsers WHERE Email ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                fechanaci=data[0][0]
                return fechanaci
            else:
                return False
        except Exception as e:
            return e
        cursor.close()
        conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})

def SelectCurp(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT CURP FROM CUsers WHERE Email ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                curp=data[0][0]
                return curp
            else:
                return False
        except Exception as e:
            return e
        cursor.close()
        conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})


def RegistroContrato(usuario,filen):
    try:
        
        if usuario:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="CUsers"
            sqlCreateSP="UPDATE "+ _TABLA +" SET ContractState = '"+filen+"'  WHERE Email = '"+usuario+"'"
            
            try:
                cursor.execute(sqlCreateSP)
                today=datetime.datetime.now()
                d1 = today.strftime("%Y-%m-%d")
                ddd=datetime.datetime.strptime(d1, '%Y-%m-%d').date()
                expR=ddd+relativedelta(years=+1)
                id="regalo300"+usuario
                points=300
                doc="regalo300"
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,usuario,d1,points,expR,doc))
                return True
            except Exception as e:
                print(str(e))
                return False
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
        conn.close()

'''Diego'''

def Ttickets(correo):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT COUNT(EMAIL_R) FROM S_C_REFUND1 WHERE STATUS_R = 2 and EMAIL_R = %s',correo)
    tta = cur.fetchall()
    return tta

def Ttickett(correo):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT COUNT(EMAIL_R) FROM S_C_REFUND1 WHERE STATUS_R = 1 and  EMAIL_R = %s',correo)
    ttt = cur.fetchall() 
    return ttt

def Tticketf(correo):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT COUNT(EMAIL_R) FROM S_C_REFUND1 WHERE STATUS_R = 0 and EMAIL_R = %s',correo)
    ttf = cur.fetchall()
    return ttf

def tickets_tod(correo):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM S_C_REFUND1 WHERE STATUS_R in (1, 2) AND EMAIL_R = %s ORDER BY ID_REFUND DESC',correo)
    tickets = cur.fetchall()
    return tickets

def BUSTI(SERCHT):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM S_C_REFUND1 WHERE ID_REFUND = %s', SERCHT)
    ENCON = cursor.fetchall()
    return ENCON

def USERDATA(user):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM CUsers WHERE Email = %s', user)
    ENCON = cursor.fetchall()
    return ENCON

def editart(editicket1, ediestado1, ediproducto1, edidireccion1, edirazon1):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE S_C_REFUND1 SET PRODUCT_R = %s, REASON_R = %s, ADRRESS = %s WHERE ID_REFUND = %s;', (ediproducto1,edirazon1,edidireccion1,editicket1)) 
    return True
   

def borrarticket(Borrar):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE S_C_REFUND1 SET STATUS_R = 5 WHERE ID_REFUND =  %s;', Borrar)
    return True

def CALI_ASESOR(ide_call,califica,bips,user):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE S_C_CALL SET CALIFICATIO_CALL = %s WHERE ID_CALL =  %s;', (califica, ide_call))
    today=datetime.datetime.now()
    d1 = today.strftime("%Y-%m-%d")
    ddd=datetime.datetime.strptime(d1, '%Y-%m-%d').date()
    expR=ddd+relativedelta(years=+1)

    if int(bips) + 150 >= 4000:
            id="regalo1500"+user
            points=1500
            doc="regalo1500"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))
                
    elif int(bips) + 150 >= 3000:
            id="regalo1000"+user
            points=1000
            doc="regalo1000"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))
                
    elif int(bips) + 150 >= 2000:
            id="regalo700"+user
            points=700
            doc="regalo700"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))

    elif int(bips) + 150 >= 1000:
            id="regalo500"+user
            points=500
            doc="regalo500"
            try:
                queryRegalo="Insert into T_Movements (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
            except Exception as e:
                print(str(e))
                


    queryBips="UPDATE CUsers SET Biptips = Biptips + 150 WHERE email = %s"
    doneBip=cursor.execute(queryBips, (user))
    if doneBip:
            return True
    else:
            return False
    return True

def Num_CALIFICAR(user):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT COUNT(ID_CALL) FROM `S_C_CALL` WHERE NAME_C = %s AND CALIFICATIO_CALL IS NULL',user)
    Num_CALIFICAR1 = cur.fetchall()
    return Num_CALIFICAR1

'''
def nomuser(user):
    cur1 = mysql.get_db().cursor()
    cur1.execute('SELECT NAME FROM S_C_USER WHERE NAME = %s',user)
    nomre = cur1.fetchall()
    return nomre'''

def all_info():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT Selfie, EMAIL, COUNT(EMAIL_R), Phone, Name FROM S_C_REFUND1, CUsers WHERE EMAIL_R = EMAIL AND (STATUS_R=1 OR STATUS_R=2) GROUP BY NAME ORDER BY COUNT(EMAIL_R) DESC')
    allinf = cursor.fetchall()
    return allinf


def llamada():
    
    speech_key, service_region = "e21c5662cc5c4e7aa983ba12c67f6a90", "eastus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,language="es-MX")
    print("Se ha iniciado la grabación de la llamada...")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    
    #result = 2
    return result.text
    #return result


def analisis():
    document = llamada()
    ta_credential = AzureKeyCredential("669021d295c9482e96114324804b22c8")
    text_analytics_client = TextAnalyticsClient(endpoint="https://text-a-powe-client.cognitiveservices.azure.com/", credential=ta_credential)
    client = text_analytics_client
    documents = [document]
    response = client.analyze_sentiment(documents = documents)[0]
    print("Document Sentiment: {}".format(response.sentiment))
    print("Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
        response.confidence_scores.positive,
        response.confidence_scores.neutral, 
        response.confidence_scores.negative,
    ))
    respuestas = [response.sentiment, response.confidence_scores.positive, response.confidence_scores.neutral, response.confidence_scores.negative, document]
    
    #respuestas= 3
    return respuestas


'''
def DATOUSER(CORREUSER):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM S_C_USER WHERE EMAIL = %s', CORREUSER)
    datuse = cursor.fetchall()
    return datuse
    '''



def anali_llama(mensaje, senti, pos, neutra, nega, clieb, tick, user):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('Insert into S_C_CALL (NAME_C, ID_TICKET_C, CALL_TEXT, SENTIMENT, NUM_PO, NUM_NEU, NUM_NEG, USER_CALL_CENTER) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (clieb,tick,mensaje,senti,pos,neutra,nega,user))

    conn1 = mysql.connect()
    cursor1 = conn1.cursor()
    cursor1.execute('UPDATE S_C_REFUND1 SET STATUS_R = 2 WHERE ID_REFUND =  %s;', tick)
    return True



def listo(user):
    cur = mysql.get_db().cursor()
    cur.execute('UPDATE CUsers SET Status = 1 WHERE Email = %s',user)
    listo1 = cur.fetchall()
    return listo1

def llam_ticket(llamando_a):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT ID_REFUND,PRODUCT_R FROM `S_C_REFUND1` WHERE STATUS_R in (1, 2) AND EMAIL_R = %s',llamando_a)
    listo1 = cur.fetchall()
    return listo1


def game(user):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(ID_CALL) FROM S_C_CALL WHERE USER_CALL_CENTER = %s ',user)
    gameinf = cursor.fetchall()
    return gameinf


def r_call():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT USER_CALL_CENTER, COUNT(ID_CALL) FROM `S_C_CALL` GROUP BY USER_CALL_CENTER ORDER BY COUNT(ID_CALL) DESC')
    ran_call = cur.fetchall()
    return ran_call

def r_ticket5():
    cur = mysql.get_db().cursor()
    cur.execute('SELECT ADVISER, COUNT(ID_REFUND) FROM `S_C_REFUND1` WHERE STATUS_R=5 GROUP BY ADVISER ORDER BY COUNT(ID_REFUND) DESC')
    ra_ticket5 = cur.fetchall()
    return ra_ticket5


def trafeos(user):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM T_S_C_TROPHY WHERE USER_CC = %s',user)
    ra_ticket5 = cur.fetchall()
    return ra_ticket5

def stars(user):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT USER_CALL_CENTER, AVG(CALIFICATIO_CALL) FROM `S_C_CALL` WHERE USER_CALL_CENTER= %s',user)
    all_stars = cur.fetchall()
    return all_stars

def tickets_todfell(correo):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM S_C_REFUND1 INNER JOIN S_C_CALL ON ID_REFUND = ID_TICKET_C  WHERE STATUS_R in (1, 2) AND EMAIL_R = %s ORDER BY ID_REFUND DESC',correo)
    tickets = cur.fetchall()
    return tickets


def CALIFICAR(user):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM `S_C_CALL` WHERE NAME_C = %s AND CALIFICATIO_CALL IS NULL',user)
    CALIFICAR1 = cur.fetchall()
    return CALIFICAR1

def CHECKContr(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        frontINE="SELECT ContractState FROM CUsers WHERE Email = %s"
        try:
            cursor.execute(frontINE, (user))
            data = cursor.fetchone()
            if data:
                if data[0] != '': 
                  return True
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
     
    try:
        cursor.execute(CHECKFront, (user))
    except Exception as e:
        print(str(e))
        return False
   



def CHECKFront(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        frontINE="SELECT IneFront FROM CUsers WHERE Email = %s"
        try:
            cursor.execute(frontINE, (user))
            data = cursor.fetchone()
            if data:
                if data[0] != '': 
                  return True
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
     
    try:
        cursor.execute(CHECKFront, (user))
    except Exception as e:
        print(str(e))
        return False
   

def CHECKBack(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        backINE="SELECT IneBack FROM CUsers WHERE Email = %s"
        try:
            cursor.execute(backINE, (user))
            data = cursor.fetchone()
            if data[0] != '':
               return True
            else:
                return False
                             
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
     
    try:
        cursor.execute(CHECKBack, (user))
    except Exception as e:
        print(str(e))
        return False
   
def CHECKDom(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        address="SELECT ProofAddress FROM `CUsers` WHERE Email = %s"
        
        try:
            cursor.execute(address, (user))
            data = cursor.fetchone()
            if data[0] != '':
               return True
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
     
    try:
        cursor.execute(CHECKDom, (user))
    except Exception as e:
        print(str(e))
        return False
   
def CHECKSelf(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        selfieq="SELECT Selfie FROM CUsers WHERE Email = %s"
        try:
            cursor.execute(selfieq, (user))
            data = cursor.fetchone()
            if data:
                if data[0] != '': 
                  return True
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
     
    try:
        cursor.execute(CHECKSelf, (user))
    except Exception as e:
        print(str(e))
        return False
   
def SelectTelefono(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT Phone FROM CUsers WHERE Email ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                curp=data[0][0]
                return curp
            else:
                return False
        except Exception as e:
            return e
        cursor.close()
        conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})
            

def SelectIneArchivo(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT IneFront FROM CUsers WHERE Email ='"+user+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                status=data[0][0]
                return status
            else:
                return False
        except Exception as e:
            print(e)
            return False
            cursor.close()
            conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})