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
                if data and data [0][3] == sPass:
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
            query="INSERT INTO CUsers (email, password, salt, Phone, OnBoardingState, BipTips) VALUES (%s, %s, %s,%s,0,0);"
            try:
                cursor.execute(query, (_correo,_contraseña,_salt,_cel))
                today=datetime.datetime.now()
                d1 = today.strftime("%Y-%m-%d")
                ddd=datetime.datetime.strptime(d1, '%Y-%m-%d').date()
                expR=ddd+relativedelta(years=+1)
                id="regalo300"+_correo
                points=300
                doc="regalo300"
                queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                cursor.execute(queryRegalo, (id,_correo,d1,points,expR,doc))
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


def loginUser(_correo, _contraseña):
    try:
        if _correo and _contraseña:
            conn = mysql.connect()
            cursor = conn.cursor()
            query="SELECT * FROM C_Users WHERE email = %s"
            try:
                cursor.execute(query, (_correo))
                data = cursor.fetchall()
                print(data)
                salt=data[0][2]
                password=data[0][1]
                sPass=hashlib.sha512(_contraseña.encode('utf-8')  + salt.encode('utf-8')).hexdigest()
                if data and password == sPass:
                    return True
                else:
                    return False
            except Exception as e:
                 return e
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

def dataUsuario(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT invoice, amount, date, categoryName, points, expiration,statusName FROM T_Purchas, C_Categories, C_Status WHERE user=%s and expiration > CURRENT_DATE and category = categoryId and status = statusId"
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
        query="SELECT points FROM T_Purchas where expiration > CURRENT_DATE and status=2 and user=%s"
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
        query="SELECT expiration FROM T_Purchas where user = %s  and expiration > CURRENT_DATE and status=2 ORDER BY T_Purchas.expiration ASC LIMIT 1"
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
        query="SELECT points FROM T_Purchas where status=1 and user= %s"
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
        queryBip="SELECT BipTips FROM C_Users where email = %s"
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
    query="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, %s, %s, %s, %s ,%s, %s, 1)"
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
                    queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                
            elif int(bips) + 300 >= 3000:
                id="regalo1000"+user
                points=1000
                doc="regalo1000"
                try:
                    queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                
            elif int(bips) + 300 >= 2000:
                id="regalo700"+user
                points=700
                doc="regalo700"
                try:
                    queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))

            elif int(bips) + 300 >= 1000:
                id="regalo500"+user
                points=500
                doc="regalo500"
                try:
                    queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                


            queryBips="UPDATE C_Users SET BipTips = BipTips + 300 WHERE email = %s"
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
    query="Select onBoardState from C_Users where email = (%s)"
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
    query="Update C_Users set onBoardState = %s where email= %s"
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

            domicilio = (r"DOMICILIO\n"
            r"([a-zA-Z0-9]+.+)\n"
            r"([a-zA-Z0-9]+.+)")

            curp = (r"CURP ([a-zA-Z0-9]+.+)\n")

            ApellidoPat = (r"FECHA DE NACIMIENTO\n"
            r"(\w+)")

            ApellidoPat = re.findall(ApellidoPat, contador, re.MULTILINE)
            curp = re.findall(curp, contador, re.MULTILINE)
            matches = re.findall(regex, contador, re.MULTILINE)
            domicilio = re.findall(domicilio, contador, re.MULTILINE)
            
            """print(domicilio)
            print(ApellidoPat)
            print(matches)
            print(curp)"""

            fecha=matches[0][1]
            fecha2=fecha[6:10]+"-"+fecha[3:5]+"-"+fecha[0:2]
            domicilio2=domicilio[0][0]
            domicilio2=domicilio2+ " " +domicilio[0][1]
            curp=curp[0]
            Nombre=matches[0][0]+" "+matches[0][2]+" "+matches[0][3]
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
                              
                    print("paso 1 ideatras")
                    conn = mysql.connect()
                    print("paso 2 ideatras")
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
