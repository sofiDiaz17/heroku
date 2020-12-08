from flask import Flask, render_template, request, json, url_for, redirect,send_from_directory
import os
import smtplib
import bcrypt
import getpass
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64 
from flaskext.mysql import MySQL
import re
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import pathlib

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

KEY = '7ee7446ab0c44ec9b79e2baaa14ba40b'
ENDPOINT = 'https://ekkos02.cognitiveservices.azure.com/'

_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))
text_recognition_url = ENDPOINT + "/vision/v3.1/read/analyze"

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MYSQL_DATABASE_USER'] = 'sepherot_roberto'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Fe2zrCW7b3'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_robertoBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL(app)




def EnviarCorreoContrato(_name,_email):
    nombre=_name
    destinatario=_email
    usuraio='ekkoscorp@gmail.com'
    archivo= '.\Contrato_Ekkos.pdf'
    #message ='Bienvenido al Sistema de puntos Ekkos!'
    Asunto = 'Inscripción Ekkos Points'
    mensaje = MIMEMultipart("plain")#estandar
    mensaje["Subject"]=Asunto
    mensaje["From"]=usuraio
    mensaje["To"]=destinatario
    
    html=f"""
    <html>
    <body>
        Hola <i>{nombre}</i> <i>{destinatario}</i></br>
        Bienvenido a <b>Ekkos Points System</b>
        Ingresa al link siguiente para subir tu contrato.
        http://127.0.0.1:5000/logeado

    </body>
    </html>
    """
    parte_html=MIMEText(html,"html")

    mensaje.attach(parte_html)
    
    
    adjunto=MIMEBase("application","octect-stream")
    adjunto.set_payload(open(archivo,"rb").read())
    print("Lo encontré")
    encode_base64(adjunto)

    adjunto.add_header("content-Disposition",f"attachment; filename={archivo}")
    mensaje.attach(adjunto)
    mensaje_final= mensaje.as_string()
    server =smtplib.SMTP('smtp.gmail.com')
    server.starttls()
    server.login(usuraio,'EkkosC0rp')

    print("Inicio seción")
    #server.sendmail('ekkoscorp@gmail.com','robertoxd27@gmail.com', message)
    server.sendmail(usuraio,destinatario,mensaje_final)
    server.quit()
    print("Correo enviado exitosamente!")

def insertarEventoP(_email,_password):
    try:
       
        if _email and _password:
            conn = mysql.connect()
            cursor = conn.cursor()
            print("paso 1")
            _TABLA="T_UserPoints"
            sqlDropProcedure="DROP PROCEDURE IF EXISTS InsertUsers;"
            print("paso 2")
            cursor.execute(sqlDropProcedure)
            print("paso 3")
            sqlCreateSP="CREATE PROCEDURE InsertUsers(IN UEmail VARCHAR(50), IN UPass VARCHAR(50), IN UStatus INT(20)) INSERT INTO "+_TABLA+"(UEmail, UPass, UStatus) VALUES (UEmail, UPass, UStatus)"
            print("paso 4")
            cursor.execute(sqlCreateSP)
            print("paso 5")
            cursor.execute("CREATE TABLE IF NOT EXISTS `sepherot_robertoBD`.`"+_TABLA+"` (`UName` VARCHAR(50) NOT NULL, `UEmail` VARCHAR(50) NOT NULL , `UPass` VARCHAR(50) NOT NULL ,`UAdd` VARCHAR(50) NOT NULL,`UDATE` DATE NOT NULL,`URFC` VARCHAR(50) NOT NULL,`CStatus` VARCHAR(50) NOT NULL,`UStatus` INT(20),`Tiempo` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`IdUsers`)) ENGINE = InnoDB;")                    
            #cursor.execute("INSERT INTO `T_UserPoints` (`UName`,`UEmail`,`UPass`,`UAdd`,`UDATE`,`URFC`,`CStatus`) VALUES (%s, %s, %s, %s)",(_n, _l, _e, _p))
            print("paso 6")
            cursor.callproc('InsertUsers',(_email , _password,1))
            print("paso 7")
            data = cursor.fetchall()
            

            if len(data)==0:
                conn.commit()
                print("se registro")
                return json.dumps({'message':'Evento registrado correctamente !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            print("error")
            return json.dumps({'html':'<span>Datos faltantes</span>'})

    except Exception as e:
        print("error 2")
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})
    finally:
       cursor.close() 
       print("cierre")
       conn.close()

def validarUsuario( _email, _password):
    try:
        if _email and _password:
            conn=mysql.connect()
            cursor = conn.cursor()
            query = "SELECT * FROM T_UserPoints WHERE UEmail = %s"
            try:
                cursor.execute(query,(_email))
                data= cursor.fetchall()
                print(data)
                if data and data [0][3] == _password:
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

def entities(user, stage, info):
    try:
       
        conn=mysql.connect()
        cursor=conn.cursor()
        sql="INSERT INTO Entities (user, stage, stageinfo) values (%s, %s, %s)"
        query = cursor.execute(sql,(user, stage, info))
        conn.commit()
        if query:
            return True
        else:
            return False
    except Exception as e:
        print (str(e))
        return False
    conn.close()
    cursor.close()                
                     


def buscarU(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM T_UserPoints WHERE UEmail = %s"
        try: 
            cursor.execute(query,(_user))
            data = cursor.fetchall()
            if data:
                return data[0][2]
            else:
                return False
        except Exception as e:
            return e
        cursor.close()
        conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})       

def actualizarPass(_email,_password):
    try:
        #   _usuario = request.args.get('Usuario')
        #   _evento = request.args.get('Evento')
        if _email and _password:            
            print("paso 1")
            conn = mysql.connect()
            print("paso 2")
            cursor = conn.cursor()
            print("paso 3")
            _TABLA="T_UserPoints"
            print("paso 4")
            #sqlDropProcedure="DROP PROCEDURE IF EXISTS actualizarPost;"
            # #cursor.execute(sqlDropProcedure)
            sqlCreateSP="UPDATE "+ _TABLA +"   UPass ='"+ _password +"' WHERE UEmail = '"+_email+"'"
            print("paso 5")
            cursor.execute(sqlCreateSP)
            print("paso 6")
            #cursor.execute("INSERT INTO "+_TABLA+"(Usuario, Evento) VALUES (%s, %s)", (_usuario, _evento))            #cursor.callproc('actualizarPost',(_postulante))            data = cursor.fetchall()
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return redirect(url_for('logeado'))
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

def actualizarM(_name,_password,_rfc, _email,_direccion,_fechanacimiento,_estadocivil):
    try:
        #   _usuario = request.args.get('Usuario')
        #   _evento = request.args.get('Evento')
        if _name and _password and _rfc and _email and _direccion and _fechanacimiento and _estadocivil:            
            print("paso 1")
            conn = mysql.connect()
            print("paso 2")
            cursor = conn.cursor()
            print("paso 3")
            _TABLA="T_UserPoints"
            print("paso 4")
            #sqlDropProcedure="DROP PROCEDURE IF EXISTS actualizarPost;"
            # #cursor.execute(sqlDropProcedure)
            sqlCreateSP="UPDATE "+ _TABLA +" SET UName ='"+ _name +"',  UPass ='"+ _password +"', UAdd ='"+ _direccion +"',  UDate ='"+ _fechanacimiento +"',  URFC ='"+ _rfc +"',  CStatus ='"+ _estadocivil +"', UStatus = '2' WHERE UEmail = '"+_email+"'"
            print("paso 5")
            cursor.execute(sqlCreateSP)
            print("paso 6")
            #cursor.execute("INSERT INTO "+_TABLA+"(Usuario, Evento) VALUES (%s, %s)", (_usuario, _evento))            #cursor.callproc('actualizarPost',(_postulante))            data = cursor.fetchall()
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return redirect(url_for('logeado'))
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

def CrearPDF(_name,_rfc, _email,_direccion,_fechanacimiento):
    
    prueba = pathlib.Path("Contrato_Ekkos.pdf")
    if prueba.exists ():
        print ("File exist")
        os.remove(".\Contrato_Ekkos.pdf")
        print ("File not exist")
        if _name and _rfc and _email and _direccion and _fechanacimiento:
            #conn = mysql.connect()
            #cursor = conn.cursor()
            print("paso 1 pdf")
            _Nombre= _name
            _NombreArchivo="Contrato_Ekkos.pdf" 
            _TituloDocumento="Contrato Ekkos"
            _SubtituloDocumento=_Nombre
            _curp=_rfc
            _FechaNacimiento=_fechanacimiento
            _Direccion=_direccion
            _Email=_email
            print("paso 2")
            c=canvas.Canvas(_NombreArchivo)
            c.setTitle(_TituloDocumento)
            c.setLineWidth(.3)
            c.setFont('Helvetica',20)
            print("paso 3")
            print(_FechaNacimiento)
            textLines = ['Este es el contrato de: ', _Nombre ,'Quien poseé el CURP: ', _curp ,'Su fecha de nacimiento es: ', str(_FechaNacimiento) ,'Su estado civil es; ', '' ,'Su dirección es: ', _Direccion,'Correo electrónico:',_Email,' ' ,'textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto']

            print("paso 4")
            c.drawCentredString(300,760,_TituloDocumento)
            c.setFont('Helvetica',14)
            c. drawCentredString(290,720,_SubtituloDocumento)
            print("paso 5")
            text = c.beginText(60,720)
            print("paso5.1")
            text.setFont("Helvetica", 10)
            print("paso5.2")
            contador = 0    
            for line in textLines:
                contador = contador +1
                print("Prueba", + contador)
                text.textLine(line)
            print("paso 6")
            c.drawText(text)
            c.drawCentredString(300,80,_Nombre)
            c.line(200,100,400,100)
            print("paso 7")
            c.save()
            bandera=1
            return bandera
        else:
            print("error")
            return json.dumps({'html':'<span>Datos faltantes</span>'})
        bandera=0
        return bandera
    else:
        print ("File not exist")
        if _name and _rfc and _email and _direccion and _fechanacimiento:
            #conn = mysql.connect()
            #cursor = conn.cursor()
            print("paso 1 pdf")
            _Nombre= _name
            _NombreArchivo="Contrato_Ekkos.pdf" 
            _TituloDocumento="Contrato Ekkos"
            _SubtituloDocumento=_Nombre
            _curp=_rfc
            _FechaNacimiento=_fechanacimiento
            _Direccion=_direccion
            _Email=_email
            print("paso 2")
            c=canvas.Canvas(_NombreArchivo)
            c.setTitle(_TituloDocumento)
            c.setLineWidth(.3)
            c.setFont('Helvetica',20)
            print("paso 3")
            print(_FechaNacimiento)
            textLines = ['Este es el contrato de: ', _Nombre ,'Quien poseé el CURP: ', _curp ,'Su fecha de nacimiento es: ', str(_FechaNacimiento) ,'Su estado civil es; ', '' ,'Su dirección es: ', _Direccion,'Correo electrónico:',_Email,' ' ,'textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto','textotextotextotextotextotextotextotextotextotexto']

            print("paso 4")
            c.drawCentredString(300,760,_TituloDocumento)
            c.setFont('Helvetica',14)
            c. drawCentredString(290,720,_SubtituloDocumento)
            print("paso 5")
            text = c.beginText(60,720)
            print("paso5.1")
            text.setFont("Helvetica", 10)
            print("paso5.2")
            contador = 0    
            for line in textLines:
                contador = contador +1
                print("Prueba", + contador)
                text.textLine(line)
            print("paso 6")
            c.drawText(text)
            c.drawCentredString(300,80,_Nombre)
            c.line(200,100,400,100)
            print("paso 7")
            c.save()
            bandera=1
            return bandera
        else:
            print("error")
            return json.dumps({'html':'<span>Datos faltantes</span>'})
        print("cierre pdf")
       

def CorreoActualizar(_email):
    
    destinatario=_email
    usuraio='ekkoscorp@gmail.com'
    #message ='Bienvenido al Sistema de puntos Ekkos!'
    Asunto = 'Actualizar contraseña Ekkos Points'
    mensaje = MIMEMultipart("plain")#estandar
    mensaje["Subject"]=Asunto
    mensaje["From"]=usuraio
    mensaje["To"]=destinatario
    print("Parte 1")
    html=f"""
    <html>
    <body>
        Hola <i>{destinatario}</i></br>
        Para actualizar su contraseña de <b>Ekkos Points System</b>
        Ingresa al link para poder actualizar tu contraseña
        link
        
    </body>
    </html>
    """
    parte_html=MIMEText(html,"html")
    print("Parte 2")
    mensaje.attach(parte_html)
    server =smtplib.SMTP('smtp.gmail.com')
    server.starttls()
    server.login(usuraio,'EkkosC0rp')
    print("Parte 3")
    print("Inicio seción")
    #server.sendmail('ekkoscorp@gmail.com','robertoxd27@gmail.com', message)
    server.sendmail(usuraio,destinatario,mensaje.as_string())
    print("Parte 4")
    server.quit()
    print("cerrar sesión")
    
def CorreoRegistro(_email):
    
    destinatario=_email
    usuraio='ekkoscorp@gmail.com'
    #message ='Bienvenido al Sistema de puntos Ekkos!'
    Asunto = 'Registro en Ekkos Points'
    mensaje = MIMEMultipart("plain")#estandar
    mensaje["Subject"]=Asunto
    mensaje["From"]=usuraio
    mensaje["To"]=destinatario
    print("Parte 1")
    html=f"""
    <html>
    <body>
        Hola <i>{destinatario}</i></br>
        Bienvenido a <b>Ekkos Points System</b>
        Ingresa al link para poder iniciar sesión
        link
        
    </body>
    </html>
    """
    parte_html=MIMEText(html,"html")
    print("Parte 2")
    mensaje.attach(parte_html)
    server =smtplib.SMTP('smtp.gmail.com')
    server.starttls()
    server.login(usuraio,'EkkosC0rp')
    print("Parte 3")
    print("Inicio seción")
    #server.sendmail('ekkoscorp@gmail.com','robertoxd27@gmail.com', message)
    server.sendmail(usuraio,destinatario,mensaje.as_string())
    print("Parte 4")
    server.quit()
    print("cerrar sesión")

def ValidarPassword(_password):
    if 8<= len(_password)<=16:
        if re.search('[a-z]',_password)and re.search('[A-Z]',_password):
            if re.search('[0-9]',_password):
                if re.search('[$@#]',_password):
                    return True

    return False

def IngresarIDelante(busqueda,_nombrearchivo):
    try:
        #   _usuario = request.args.get('Usuario')
        #   _evento = request.args.get('Evento')
        usuario=busqueda
        if _nombrearchivo and busqueda:            
            #print("paso 1")
            conn = mysql.connect()
            #print("paso 2")
            cursor = conn.cursor()
            #print("paso 3")
            _TABLA="CUsers"
            #print("paso 4")
            #sqlDropProcedure="DROP PROCEDURE IF EXISTS actualizarPost;"
            # #cursor.execute(sqlDropProcedure)
            sqlCreateSP="UPDATE "+ _TABLA +" SET IneFront ='"+ _nombrearchivo +"' WHERE Email = '"+usuario+"'"
            #print("paso 5")
            cursor.execute(sqlCreateSP)
            #print("paso 6")
            #cursor.execute("INSERT INTO "+_TABLA+"(Usuario, Evento) VALUES (%s, %s)", (_usuario, _evento))            #cursor.callproc('actualizarPost',(_postulante))            data = cursor.fetchall()
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return redirect(url_for('subdocumentos'))
            else:
                return json.dumps({'error':str(data[0])})
            cursor.close()
            conn.close()
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})
    
        

def IngresarIDetras(busqueda,_nombrearchivo):
    try:
        #   _usuario = request.args.get('Usuario')
        #   _evento = request.args.get('Evento')
        usuario=busqueda
        if _nombrearchivo and busqueda:            
            print("paso 1")
            conn = mysql.connect()
            print("paso 2")
            cursor = conn.cursor()
            print("paso 3")
            _TABLA="CUsers"
            print("paso 4")
            #sqlDropProcedure="DROP PROCEDURE IF EXISTS actualizarPost;"
            # #cursor.execute(sqlDropProcedure)
            sqlCreateSP="UPDATE "+ _TABLA +" SET IDetras ='"+ _nombrearchivo +"' WHERE UEmail = '"+usuario+"'"
            print("paso 5")
            cursor.execute(sqlCreateSP)
            print("paso 6")
            #cursor.execute("INSERT INTO "+_TABLA+"(Usuario, Evento) VALUES (%s, %s)", (_usuario, _evento))            #cursor.callproc('actualizarPost',(_postulante))            data = cursor.fetchall()
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return redirect(url_for('subdocumentos'))
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





def SelectNombre(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                nombre=data[0][1]
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
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                correo=data[0][2]
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
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                direccion=data[0][4]
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
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                fechanaci=data[0][5]
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
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                curp=data[0][6]
                return curp
            else:
                return False
        except Exception as e:
            return e
            cursor.close()
            conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})


def SelectStatus(busqueda):
    if busqueda:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+busqueda+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                status=status[0][7]
                return status
            else:
                return False
        except Exception as e:
            return e
            cursor.close()
            conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})    


def RegistroLogin(user):
    try:
 
        usuario=user
        if user:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="T_UserPoints"
            sqlCreateSP="UPDATE "+ _TABLA +" SET Loggins = Loggins + 1  WHERE UEmail = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            print("paso 6")
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return redirect(url_for('subdocumentos'))
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
 
def RegistroContrato(busqueda):
    try:
        usuario=busqueda
        if usuario:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="T_UserPoints"
            sqlCreateSP="UPDATE "+ _TABLA +" SET Contract = 1  WHERE UEmail = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            print("paso 6")
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return redirect(url_for('subdocumentos'))
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
 
def SelectLoggins(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+user+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                loggins=data[0][13]
                return loggins
            else:
                return False
        except Exception as e:
            return e
            cursor.close()
            conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})

def SelectContrato(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+user+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                contrato=data[0][14]
                return contrato
            else:
                return False
        except Exception as e:
            return e
            cursor.close()
            conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})

"""def SelectStatus(user):
    if user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query= "SELECT * FROM T_UserPoints WHERE UEmail ='"+user+"'"
        try: 
            cursor.execute(query)
            data = cursor.fetchall()
            if data:
                status=data[0][7]
                return status
            else:
                return False
        except Exception as e:
            return e
            cursor.close()
            conn.close()
    else: 
            return json.dumps ({'html': '<span> Te faltan datos </span>'})"""

