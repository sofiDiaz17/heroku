from flask import Flask, render_template, request, json, url_for, redirect,send_from_directory, session, g
from flaskext.mysql import MySQL
import data as Modelo
import jinja2
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from datetime import date, timedelta
import datetime
#  from dateutil.relativedelta import relativedelta
import pytesseract
from PIL import Image
#from cv2 import cv2
import os
from werkzeug.utils import secure_filename
import re
#from tkinter import messagebox
from decimal import Decimal
import requests, uuid
import json
import hashlib
import pdfkit
import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
import comprobacionfacial as Comp



KEYF = "4e341ff775bf4ee18e3a726fc1b5de7b"

# This endpoint will be used in all examples in this quickstart.
ENDPOINTF = "https://faceorange.cognitiveservices.azure.com/"
face_client=FaceClient(ENDPOINTF, CognitiveServicesCredentials(KEYF))




pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = './.apt/usr/bin/tesseract'




app = Flask(__name__)
@app.errorhandler(404)

def not_found(e):
    return render_template("404.html")
app.secret_key = 'claveultrasecretadeapp'

MYDIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['UPLOAD_FOLDER5'] ='./static/Contratos'
app.config['UPLOAD_FOLDER4'] ='./static/Selfie'
app.config['UPLOAD_FOLDER3'] ='./static/Comprobante'
app.config['UPLOAD_FOLDER2'] ='./static/INEATRAS'
app.config['UPLOAD_FOLDER1'] ='./static/INEDELANTE'

#app.config['UPLOAD_FOLDER'] = "cuponera\\uploads"
app.config['UPLOAD_EXTENSIONS'] = ['png', 'jpg', 'jpeg']

endpoint="https://cuponeravision.cognitiveservices.azure.com/"
subscription_key="4d0c7d3a1a4c4aebabb6df39c33dd9eb"
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

@app.route('/index')
def landing():
    return render_template ("index.html")

@app.route('/error')
def error():
    return render_template ("error.html")

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.correo=session['user']
        userF = Modelo.buscarUser(session['user'])
        if userF:
            g.user=userF
        else:
            g.user=" "
        fotoB = Modelo.fotoUser(session['user'])
        if fotoB:
            g.foto =fotoB[0][0]
        else:
            g.foto=" "
        BIT = Modelo.buscarBIT(session['user'])
        if userF:
            g.BIT=BIT[0][0]
        else:
            g.BIT=" "
        
@app.route('/registro',methods=['GET','POST'])
def registro():
    if request.method=='POST':
        phone=request.form['phone']
        corre=request.form['email']
        contra=request.form['password']
        contra2=request.form['re_password']
        img=request.form['img']
        print(img)
        if contra == contra2:
            salt = uuid.uuid4().hex
            sPass=hashlib.sha512(contra.encode('utf-8')  + salt.encode('utf-8')).hexdigest()
            print(salt)
            print(sPass)
            if phone and corre and contra:
                crear=Modelo.crearUsr(corre,sPass,salt,phone,img)
                if crear:
                    Modelo.entities(corre,'Registro','Se creo usuario')
                    errorLog="Se creo el usuario, inicia sesion"
                    return redirect(url_for('login'))
            else:
                Modelo.entities(corre,'Registro.Fail','No se pudo crear usuario')
                return render_template('registro.html')
        else:
            errorLog="Las contraseñas no concuerdan"
            return render_template('registro.html',errorLog=errorLog)
    return render_template('registro.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if g.user:
        return redirect(url_for('perfil'))
    if request.method=='POST':
        session.pop('user', None)
        user=request.form['correo']
        password=request.form['contraseña']
        if(user and password):
            usuario=Modelo.validarUsuario(user,password)
            print(usuario)
            if usuario==3:
                session['user']=user
                return redirect(url_for('call_center'))
            else:
                if usuario==1:              
                    session['user']=user
                    Modelo.entities(user,'Login','El usuario hace login')
                    return redirect(url_for('perfil'))
                elif usuario==2:
                    session['user']=user
                    Modelo.entities(user,'Login','El usuario hace login')
                    return redirect(url_for('perfil'))     
                else:
                    errorLog="Los datos no concuerdan"
                    Modelo.entities(user,'Login.Fail.NotFound','Error de datos al iniciar sesion')
                    return render_template('loginD.html',errorLog=errorLog)
    return render_template('loginD.html')



@app.route('/perfil',methods=['GET','POST'])
def perfil():
    if not g.user:
        return redirect(url_for('login'))
    try:
        estado=Modelo.estadoOnboarding(session['user'])
        if estado:
            userOnBoard=estado[0][0]
            maxExp= Modelo.expDate(session['user'])
            dataP= Modelo.puntosUsuario(session['user'])
            acumP=Modelo.puntfal(session['user'])
            b=Modelo.bitsUser(session['user'])
            bips=b[0][0]
            
            busquedaN= Modelo.SelectNombre(session['user'])
            busquedaEm= Modelo.SelectCorreo(session['user'])
            busquedaFe= Modelo.SelectFecha(session['user'])
            busquedaCu= Modelo.SelectCurp(session['user'])
           
            #print(userOnBoard)
            #print(bips) 
            if bips==0:
                bips=1
            r=Modelo.rewardsUsr(bips)
            #print(r)
            try:
                date_= maxExp[0][0].strftime("%d/%m/%Y")
            except:
                date_="- No hay fecha registrada"
            puntos = 0
            puntosF = 0 
            try:
                for data in dataP:
                    puntos = puntos + data[0]
            except:
                puntos = 0
            try:
                for dataf in acumP:
                    puntosF = puntosF + dataf[0]
            except:
                puntosF = 0 
            dataU = Modelo.dataUsuario(session['user'])
            num_calificar=Modelo.Num_CALIFICAR(session['user'])
            calificar=Modelo.CALIFICAR(session['user'])
            Modelo.entities(session['user'],'ProfileLoad','Se cargo el perfil del usuario')
            #print(dataU)
            front = Modelo.CHECKFront(session['user'])
            print(front)
            back=Modelo.CHECKBack(session['user'])
            print(back)
            imgdom=Modelo.CHECKDom(session['user'])  
            print(imgdom)
            selfie=Modelo.CHECKSelf(session['user'])
            print(selfie)
            llenado=0
            if front:
                llenado=llenado+1
            if back:
                    llenado=llenado+1
            if imgdom:
                    llenado=llenado+1
            if selfie:
                    llenado=llenado+1
            incompleto=True
            if llenado==4:
                incompleto=False

            contr=Modelo.CHECKContr(session['user'])
            if contr:
                print('cont')
            else:
                incompleto=True

            print(incompleto)
            llenadoB=(llenado*100)/4
            print(llenadoB)
            print(calificar)
            #QUERY DE TELEFONO Y DIRECCIÓN 
            direccion=Modelo.SelectDireccion(session['user'])
            telefono=Modelo.SelectTelefono(session['user'])
            return render_template('perfil_cliente.html',incompleto=incompleto,onboarding=userOnBoard,puntos=puntos, 
            expiracion=date_,puntosF=puntosF,nivel=r[0][0], tabla=dataU,num_calificar=num_calificar, calificar=calificar,
            frontINE=front,backINE=back,imgdom=imgdom,selfie=selfie,llenado=llenado,bar=llenadoB,telefono=telefono,
            direccion=direccion,nombre=busquedaN,email=busquedaEm,fechanaci=busquedaFe,curp=busquedaCu)
        else:
            Modelo.entities(session['user'],'UserOnBoarding.Fail','Ocurrio un error con el proceso de OnBoarding del usuario')
            errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
            return redirect(url_for('error'))
        
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'ProfileLoad.Fail.NotFound','Error al cargar el perfil del usuario')
        errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
        return redirect(url_for('error'))


@app.route('/rewards',methods=['GET','POST'])
def rewards():
    if not g.user:
        return redirect(url_for('login'))
    try:
        estado=Modelo.estadoOnboarding(session['user'])
        if estado:
            userOnBoard=estado[0][0]
            dataP= Modelo.puntosUsuario(session['user'])
            acumP=Modelo.puntfal(session['user'])
            b=Modelo.bitsUser(session['user'])
            bips=b[0][0]
            if bips==0:
                bips=1
            r=Modelo.rewardsUsr(bips)
            nextLvl=Modelo.nextLvl(r[0][0])
            bipsPer=(int(bips)*100)/int(nextLvl[0][6])
            faltan=int(nextLvl[0][6])-int(bips)
            puntos = 0
            puntosF = 0 
            try:
                for data in dataP:
                    puntos = puntos + data[0]
            except:
                puntos = 0
            try:
                for dataf in acumP:
                    puntosF = puntosF + dataf[0]
            except:
                puntosF = 0 
            num_calificar=Modelo.Num_CALIFICAR(session['user'])
            Modelo.entities(session['user'],'RewardsLoad','Se cargo el perfil de rewards')
            return render_template('rewardsD.html',onboarding=userOnBoard,puntos=puntos,puntosF=puntosF,
            nivel=r[0][0],nivelN=r[0][1],r1=r[0][2],r2=r[0][3],r3=r[0][4],r4=r[0][5],bips=bips,bipsPer=bipsPer,
            faltan=faltan,nlvl=nextLvl[0][1],rNL1=nextLvl[0][2],rNL2=nextLvl[0][3],num_calificar=num_calificar)
        else:
            Modelo.entities(session['user'],'RewardsLoad.Fail','No se cargaron los rewards')
            errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
            return redirect(url_for('error'))
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'RewardsLoad.Fail','No se cargaron los rewards')
        errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
        return redirect(url_for('error'))


"""@app.route('/historial')
def historial():
    if not g.user:
        return redirect(url_for('login'))
    try:
        estado=Modelo.estadoOnboarding(session['user'])
        userOnBoard=estado[0][0]
        dataU = Modelo.dataUsuario(session['user'])
        Modelo.entities(session['user'],'HistoryLoad','Se cargo el historial del usuario')
        return render_template('historial.html',onboarding=userOnBoard, tabla=dataU)
    except:
        try:
            Modelo.entities(session['user'],'HistoryLoad','Se cargo el historial del usuario')
            vac="No se ha registrado ningún movimiento aún"
            return render_template('historial.html',vac=vac)
        except  Exception as e: 
            print(str(e))
            Modelo.entities(session['user'],'HistoryLoad.Fail.NotFound','Error al cargar el historial del usuario')
            errorLog="Algo salio mal al cargar tu historial, vuelva a intentarlo"
            return render_template('perfil.html',errorLog=errorLog)"""


@app.route('/conversion')
def conversion():
    if not g.user:
        return redirect(url_for('login'))
    try:
        Modelo.entities(session['user'],'ConversionLoad','Se cargo la pagina de conversiones')
        return render_template('conversion.html')
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'ConversionLoad.Fail.NotFound','Error al cargar la pagina de conversiones')
        errorLog="Algo salio mal al cargar las conversiones, vuelva a intentarlo"
        return redirect(url_for('error'))

@app.route('/catalogo')
def catalogo():
    if not g.user:
        return redirect(url_for('login'))
    try:
        b=Modelo.bitsUser(session['user'])
        bips=b[0][0]
        if int(bips) < 1000:
            data=Modelo.catalogo(7)
        elif int(bips) > 999 and int(bips) < 2000:
            data=Modelo.catalogo(10)
        elif int(bips) > 1999 and int(bips) < 3000:
            data=Modelo.catalogo(13)
        elif int(bips) > 2999 and int(bips) < 4000:
            data=Modelo.catalogo(20)
        elif int(bips) >= 4000:
            data=Modelo.catalogo(25)
        print(data)
        num_calificar=Modelo.Num_CALIFICAR(session['user'])
        Modelo.entities(session['user'],'CatalogLoad','Se cargo la pagina de catalogo')
        return render_template('catalogo.html',num_calificar=num_calificar,data=data)
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'CatalogLoad.Fail.NotFound','Error al cargar la pagina de catalogo')
        errorLog="Algo salio mal al cargar el catalogo, vuelva a intentarlo"
        return redirect(url_for('error'))



def guardarArch(file):
    try:
        filename = secure_filename(file.filename)
        file.save(os.path.join(MYDIR + "/" + app.config['UPLOAD_FOLDER'], filename))
        #file.save(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
        return True
    except Exception as e:
        print(str(e))  
        return False  

def extraerInfo(filename):
    try:
        #img = Image.open(os.path.join(MYDIR + "/" + app.config['UPLOAD_FOLDER'], filename))
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        texto = pytesseract.image_to_string(img,lang='spa')
        Modelo.entities(session['user'],'GetTextFromImage','El programa extrajo el texto de la foto')
        return texto
    except:
        Modelo.entities(session['user'],'GetTextFromImage.Fail','El programa no pudo leer la foto')
        return False

def parsearFolio(info):
    foliorex= r"REFERENCIA (\d+)"
    foliorex2 = r"RECEIPT : ([A-Za-z0-9]+)"
    try:
        folio=re.findall(foliorex,info, re.MULTILINE)
        if folio:
            Modelo.entities(session['user'],'GetFolioFromImage','Se encontro el folio')
            return folio[0]
        else:
            folio=re.findall(foliorex2,info, re.MULTILINE)
            if folio:
                Modelo.entities(session['user'],'GetFolioFromImage','Se encontro el folio')
                return folio[0]
            else:
                Modelo.entities(session['user'],'GetFolioFromImage.Fail','No se encontro ningun folio')
                return False
    except:
        Modelo.entities(session['user'],'GetFolioFromImage.Fail','No se encontro ningun folio')
        return False

def parsearDate(info):
    fecharex= r"(\d{2}/[A-Za-z0-9]+/\d{2,})"
    try:
        fecha=re.findall(fecharex,info, re.MULTILINE)
        if fecha:
            Modelo.entities(session['user'],'GetDateFromImage','Se encontro la fecha')
            return fecha[0]
        else:
            Modelo.entities(session['user'],'GetDateFromImage.Fail','No se encontro ninguna fecha')
            return False
    except:
        Modelo.entities(session['user'],'GetDateFromImage.Fail','No se encontro ninguna fecha')
        return False

def parsearMonto(info):
    montorex= r"IMPORTE ([0-9].+)"
    montorex2 = r"^TOTAL ([0-9].+)"
    try:
        monto=re.findall(montorex,info, re.MULTILINE)
        if monto:
            Modelo.entities(session['user'],'GetMontoFromImage','Se encontro el monto')
            return monto[0]
        else:
            monto=re.findall(montorex2,info, re.MULTILINE)
            if monto:
                Modelo.entities(session['user'],'GetMontoFromImage','Se encontro el monto')
                return monto[0]
            else:
                Modelo.entities(session['user'],'GetMontoFromImage.Fail','No se encontro ningun monto')
                return False
    except:
        Modelo.entities(session['user'],'GetMontoFromImage.Fail','No se encontro ningun monto')
        return False

@app.route('/form',methods=['GET','POST'])
def form():
    if request.method=='POST':
        print("analizando data de foto")
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            save=guardarArch(file)
            if save: 
                Modelo.entities(session['user'],'SavePicture','El usuario subio una foto y se guardo')
                info=extraerInfo(filename)
                if info:
                        Modelo.entities(session['user'],'AnalizePicture','Se analizo la foto del usuario')
                        folio=parsearFolio(info)
                        mont=parsearMonto(info)
                        date=parsearDate(info)
                        if not folio:
                            folio=""
                        if not mont:
                            mont=0
                        if date:
                            try:
                                fecha=datetime.datetime.strptime(date, "%d/%b/%Y").strftime('%Y-%m-%d')
                            except:
                                try:
                                    fecha=datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
                                except:
                                    fecha=""
                        else:
                            fecha=""
                        data=[folio,mont,fecha,filename]
                        v=json.dumps(data,ensure_ascii=False)
                        return v
                else:
                    Modelo.entities(session['user'],'AnalizePicture.Fail','No se pudo analizar la foto')
                    return json.dumps(False)
            else:
                Modelo.entities(session['user'],'SavePicture.Fail','No se pudo guardar el archivo')
                return json.dumps(False)
    

@app.route('/recibos',methods=['GET','POST'])
def recibos():
    if not g.user:
        return redirect(url_for('login'))
    estado=Modelo.estadoOnboarding(session['user'])
    userOnBoard=estado[0][0]
    num_calificar=Modelo.Num_CALIFICAR(session['user'])

    return render_template('uploadAn.html',onboarding=userOnBoard,num_calificar=num_calificar)

@app.route('/subirRecibo',methods=['GET','POST'])
def subirRecibo():
    if request.method=='POST':
        data=request.get_json()
        folio = data['folio']
        monto = data['monto']
        fecha = data['fechaCom']
        rubro = data['rubro']
        archivo = data['archivo']

        today=datetime.datetime.now()
        d1 = today.strftime("%Y-%m-%d")
        ddd=datetime.datetime.strptime(d1, '%Y-%m-%d').date()
        #print(d1)
        d2=(ddd-timedelta(days=7)).strftime("%Y-%m-%d")

        #print(d2)
        if fecha > d1 or fecha < d2:
            errorLog="La fecha no es valida. (Recuerde que los recibos tienen solo una semana de validez)"
            print(errorLog)
            return json.dumps(False)
        else:
            if folio and monto and fecha and rubro and archivo:
                b=Modelo.bitsUser(session['user'])
                bips=b[0][0]
                guardar=Modelo.crearPurch(folio,session['user'],monto,fecha,rubro,archivo,bips)
                if guardar:
                    Modelo.entities(session['user'],'SavePurchaseInDB','Se guardo una compra en la base de datos')
                    print('se subio la data')
                    return json.dumps(True)
                else:
                    Modelo.entities(session['user'],'SavePurchaseInDB.Fail','No se pudo guardar en la base de datos')
                    errorLog="Revise los datos"
                    return json.dumps(False)

@app.route('/getObj',methods=['GET','POST'])
def getObj():
    if request.method=='POST':
            print("analizando data de foto")
            file = request.files['file']
            try:
                detect_objects_results_local = computervision_client.detect_objects_in_stream(file)
                Modelo.entities(session['user'],'ObjectDetect','Se corrio el API')
            except Exception as e:
                print(str(e))
                Modelo.entities(session['user'],'ObjectDetect.Fail','No se pudo correr el API')
                return json.dumps(False) 
            print("Detecting objects in local image:")
            if len(detect_objects_results_local.objects) == 0:
                Modelo.entities(session['user'],'ObjectDetect.Fail','No se detecto ningun objeto')
                print("No objects detected.")
                return json.dumps(False)
            else:
                Modelo.entities(session['user'],'ObjectDetect','Se detecto un objeto')
                for object in detect_objects_results_local.objects:
                    print("object at location {}".format(object.object_property))

                    headers = {
                        'Ocp-Apim-Subscription-Key': "36897135dcf04893864e79b62e0d3aec",
                        'Ocp-Apim-Subscription-Region':'eastus',
                        'Content-type': 'application/json',
                        'X-ClientTraceId': str(uuid.uuid4())
                    }
                    
                    body = [{
                        'text' : object.object_property
                    }]
                    try:
                        requestt = requests.post("https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=en&to=es",  headers=headers, json=body)
                        response = requestt.json()
                        print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
                        data=json.dumps(response,ensure_ascii=False)
                        Modelo.entities(session['user'],'Translate','Se traducio el objeto')
                        return data
                    except Exception as e:
                        print(str(e))
                        Modelo.entities(session['user'],'Translate.Fail','No se pudo traducir el objeto')
                        return json.dumps(False) 

@app.route('/getObjDB',methods=['GET','POST'])
def getObjDB():
    if request.method=='POST':
        data=request.get_json()
        nombre=data['nombre']
        try:
            data=Modelo.buscarObj(nombre)
            Modelo.entities(session['user'],'BuscarObjeto','Se busca el objeto en la base de datos')
            if data:
                Modelo.entities(session['user'],'ObjectFound','Se encontro el objeto en la base de datos')
                return json.dumps(data,ensure_ascii=False)
            else:
                Modelo.entities(session['user'],'ObjectFound.Fail','No se encontro el objeto en la base de datos')
                return json.dumps(False)
        except Exception as e:
            Modelo.entities(session['user'],'BuscarObjeto.Fail','No se pudo buscar el objeto')
            print(str(e))
            return json.dumps(False)

@app.route('/comprar',methods=['GET','POST'])
def comprar():
    if request.method=="POST":
        print("el usuario compra")
        data=request.get_json()
        compra=data['compra']
        objeto=data['objeto']
        print(compra)
        print(objeto)
        b=Modelo.bitsUser(session['user'])
        bips=b[0][0]
        base=Modelo.comprar(session['user'],compra,objeto,bips)
        if base:
            return json.dumps(True)
        else:
            return json.dumps(False)

@app.route('/OnBoard',methods=['GET','POST'])
def OnBoard():
    if request.method=='POST':
        data=request.get_json()
        estado=data['estado']
        try:
            data=Modelo.setEstadoOnboarding(session['user'],estado)
            if data:
                if estado==4:
                    Modelo.entities(session['user'],'OnBoardingEnd','El usuario completo el OnBoarding')
                elif estado==5:
                    Modelo.entities(session['user'],'OnBoardingReward','El usuario vio el OnBoard de reward')
                else:
                    Modelo.entities(session['user'],'ChangeState','El usuario completo una fase del OnBoarding')
                return json.dumps(data,ensure_ascii=False)
            else:
                Modelo.entities(session['user'],'ChangeState.Fail','No se pudo cambiar el estado del OnBoarding')
                return json.dumps(False)
        except Exception as e:
            Modelo.entities(session['user'],'ChangeState.Fail','No se pudo cambiar el estado del OnBoarding')
            print(str(e))
            return json.dumps(False)

@app.route('/close')
def close():
    try:
        Modelo.entities(session['user'],'CloseSession','El usuario cerro sesion')
        session.clear()
        return redirect(url_for('login'))
    except:
        Modelo.entities(session['user'],'CloseSession.Fail','El usuario no pudo cerrar sesion')
        errorLog="Algo salio mal al cerrar la sesion"
        return render_template('perfil.html',errorLog=errorLog)

@app.route('/')
def inicio():
    return redirect(url_for('login'))

'''Diego'''

@app.route('/404')
def error404():
    return render_template('404.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/devoluciones_reembolsos')
def devoluciones_reembolsos():
    userD=Modelo.USERDATA(session['user'])
    print(userD)
    if userD[0][18]!=1:
        return redirect(url_for('onboarding'))
    else:
        tickets=Modelo.tickets_tod(session['user'])
        _ticketactivos=Modelo.Ttickets(session['user'])
        _tickettotal=Modelo.Ttickett(session['user'])
        _ticketfinal=Modelo.Tticketf(session['user'])
        num_calificar=Modelo.Num_CALIFICAR(session['user'])
    
    return render_template('devoluciones_reembolsos.html', tickets = tickets,tta= _ticketactivos[0][0],ttt= _tickettotal[0][0],ttf= _ticketfinal[0][0],num_calificar=num_calificar)

@app.route('/ticket', methods=['GET','POST'])
def ticket():
    if request.method == 'POST':
        SERCHT = request.form['SERCHT']
        _SERCHT = Modelo.BUSTI(SERCHT)
        tickets=Modelo.tickets_tod(session['user'])
        #_ticketactivos=Modelo.Ttickets(session['user'])
        #_tickettotal=Modelo.Ttickett(session['user'])
        #_ticketfinal=Modelo.Tticketf(session['user'])
        #_DATAUSER=Modelo.DATOUSER(session['user'])
        num_calificar=Modelo.Num_CALIFICAR(session['user'])
        return render_template('ticket.html',tickets = tickets, SERCHTIK=_SERCHT[0][0],SERCHTIK1=_SERCHT[0][1],SERCHTIK2=_SERCHT[0][2],SERCHTIK3=_SERCHT[0][3],SERCHTIK4=_SERCHT[0][4],SERCHTIK5=_SERCHT[0][5],SERCHTIK6=_SERCHT[0][6],num_calificar=num_calificar)
    return redirect('mis_pedidos')

@app.route('/editar', methods=['GET','POST'])
def editar():
    if request.method == 'POST':
        data=request.get_json()
        print("#############")
        print(data)
        editicket1=data['editicket']
        ediestado1=data['ediestado']
        ediproducto1=data['ediproducto']
        edidireccion1=data['edidireccion']
        edirazon1=data['edirazon']
        _editarticket = Modelo.editart(editicket1, ediestado1, ediproducto1, edidireccion1, edirazon1)
        print(editicket1)
        print("°°°°°°°°°°°°°°°")
        if _editarticket:
            return json.dumps("bien")
        return json.dumps("algo")
    
@app.route('/borrar', methods=['GET','POST'])
def borrar():
    if request.method == 'POST':
        data=request.get_json()
        borrid=data['borrid']
        _borrarticket = Modelo.borrarticket(borrid)
        print(_borrarticket)
        if _borrarticket:
            return json.dumps(True)
        return json.dumps("algo")


@app.route('/compras',methods=['GET','POST'])
def compras():
    dataP= Modelo.puntosUsuario(session['user'])
    puntos = 0
    try:
        for data in dataP:
            puntos=puntos+data[0]
    except:
         puntos = 0
    try:
        Modelo.entities(session['user'],'TesterLoad','Se cargo la pagina de tester')
        estado=Modelo.estadoOnboarding(session['user'])
        userOnBoard=estado[0][0]
        num_calificar=Modelo.Num_CALIFICAR(session['user'])
        return render_template('compras.html',puntos=puntos,onboarding=userOnBoard,num_calificar=num_calificar)
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'TesterLoad.Fail.NotFound','Error al cargar el tester')
        errorLog="Algo salio mal al cargar el tester, vuelva a intentarlo"
        return redirect(url_for('error'))

@app.route('/devolver', methods=['GET', 'POST'])
def devolver():
    if request.method == 'POST':
        data=request.get_json()
        obj=data['objeto']
        razon=data['razon']
        domicilio=data['domicilio']
        sub=Modelo.insertarDevolucion(session['user'],obj,razon,domicilio)
        if sub:
            return json.dumps("bien")
        else:
            return json.dumps("mal")
    

@app.route('/mis_pedidos', methods=['GET', 'POST'])
def mis_pedidos():
    #_username=Modelo.nomuser(session['user'])
    #Modelo.pasos(session['user'],'P.PEDIDOS', 'USUARIO VE SUS PEDIDOS')
    calificar=Modelo.CALIFICAR(session['user'])
    num_calificar=Modelo.Num_CALIFICAR(session['user'])
    dataU = Modelo.pedidos(session['user'])
    return render_template('mis_pedidos.html',calificar=calificar,num_calificar=num_calificar,tabla=dataU)


@app.route('/calificar', methods=['GET','POST'])
def calificar():
    if request.method == 'POST':
        #Modelo.pasos(session['user'],'CALIFICAR', 'USUARIO CALIFICA A PERSONAL DE CC')
        data=request.get_json()
        ide_call=data['id_call']
        print("#############")
        print(ide_call)
        califica=data['cali']
        print("#############")
        print(califica)
        b=Modelo.bitsUser(session['user'])
        bips=b[0][0]
        CALI_ASE = Modelo.CALI_ASESOR(ide_call,califica,bips,session['user'])
        
        if CALI_ASE:
            return json.dumps(True)
        return json.dumps("algo")





"DIEGO CALL CENTER"

@app.route('/call_center')
def call_center():
    #Modelo.pasos(session['user'],'P.LISTA_CLIENTES', 'CC VE A LOS CLIENTES QUE TIENE QUE LLAMAR')
    _allinfos = Modelo.all_info()
    _ranking=Modelo.game(session['user'])
    #print(_allinfos)
    return render_template('call_center.html', _allinfos = _allinfos,_ranking=_ranking[0][0])


@app.route('/call_sc', methods=['GET','POST'])
def call_sc():
    if request.method == 'POST':
        llamando_a = request.form['llamando_a']
        #Modelo.pasos(session['user'],'P.LLAMADAS', 'CC LLAMA Y VE EL ANALISIS DE LA LLAMADA')
        #time.sleep(1)
        #_inicio_llamada = Modelo.llamada()
        _analisis_llamada = Modelo.analisis()
        _allinfos = Modelo.all_info()
        llam_ticket = Modelo.llam_ticket(llamando_a)    
        return render_template('call_sc.html', _analisis_llamada =_analisis_llamada,llamando_a=llamando_a,llam_ticket=llam_ticket)


@app.route('/tcs_usuario', methods=['GET','POST'])
def tsc_usuario():
    if request.method == 'POST':
        #Modelo.pasos(session['user'],'P.TICKET POR USUARIO', 'CC VE LA LISTA DE LOS TICKETS DE UN CLIENTE')
        #_username=Modelo.nomuser(session['user'])
        corre_tcs = request.form['corre_tcs']
        print(corre_tcs)
        tickets=Modelo.tickets_tod(corre_tcs)
        ticketsfeel=Modelo.tickets_todfell(corre_tcs)
        _ticketactivos=Modelo.Ttickets(corre_tcs)
        _tickettotal=Modelo.Ttickett(corre_tcs)
        _ticketfinal=Modelo.Tticketf(corre_tcs)
        #_DATAUSER=Modelo.DATOUSER(corre_tcs)
        return render_template('tcs_usuario.html', ticketsfeel=ticketsfeel, tickets = tickets,tta= _ticketactivos[0][0],ttt= _tickettotal[0][0],ttf= _ticketfinal[0][0])


@app.route('/add_llamada', methods=['GET','POST'])
def add_llamada():
    if request.method == 'POST':
        #Modelo.pasos(session['user'],'GUARDAR LLAMADA', 'CC GUARDA EL ANALISIS DE LA LLAMADA')
        data=request.get_json()
        #print(data)
        mensaje=data['texto_llamada']
        senti=data['sentimiento']
        pos=data['positivo']
        neutra=data['neutral']
        nega=data['negativo']
        clieb=data['cliente']
        tick=data['ticket_c']
        dat_llam=Modelo.anali_llama(mensaje, senti, pos, neutra, nega, clieb, tick, session['user'])
        if dat_llam:
            return json.dumps(True)
        return json.dumps("algo")

@app.route('/onboarding')
def onboarding():
    Modelo.listo(session['user'])
    return render_template('onboarding.html')


@app.route('/mi_perfil')
def mi_perfil():
    #Modelo.pasos(session['user'],'P.RANKING', 'CC VE LOS RANKINGS Y SU CALIFICACION')
    tickets=Modelo.tickets_tod(session['user'])
    _ticketactivos=Modelo.Ttickets(session['user'])
    _tickettotal=Modelo.Ttickett(session['user'])
    _ticketfinal=Modelo.Tticketf(session['user'])
    #_username=Modelo.nomuser(session['user'])
    _ranking=Modelo.game(session['user'])
    _ran_call=Modelo.r_call()
    _ran_ticket=Modelo.r_ticket5()
    #_DATAUSER=Modelo.DATOUSER(session['user'])
    _trofeos=Modelo.trafeos(session['user'])
    _stars = Modelo.stars(session['user'])
    print(_trofeos)
    return render_template('mi_perfil.html', tickets = tickets,tta= _ticketactivos[0][0],ttt= _tickettotal[0][0],ttf= _ticketfinal[0][0], _ranking=_ranking,_ran_call=_ran_call,_ran_ticket=_ran_ticket,_trofeos=_trofeos,_stars=_stars[0][1])

@app.route('/edi_tc', methods=['GET','POST'])
def edi_tc():
    if request.method == 'POST':
        #Modelo.pasos(session['name'],'P.EDICION DE TICKET CC', 'CC EDITA UN TICKET DE UN USUARIO')
        SERCHT = request.form['SERCHT']
        _SERCHT = Modelo.BUSTI(SERCHT)
        #print(_SERCHT)
        #_username=Modelo.nomuser(session['user'])
        tickets=Modelo.tickets_tod(session['user'])
        _ticketactivos=Modelo.Ttickets(session['user'])
        _tickettotal=Modelo.Ttickett(session['user'])
        _ticketfinal=Modelo.Tticketf(session['user'])
        return render_template('edi_tc.html', tickets = tickets,tta= _ticketactivos[0][0],ttt= _tickettotal[0][0],ttf= _ticketfinal[0][0], SERCHTIK=_SERCHT[0][0],SERCHTIK1=_SERCHT[0][1],SERCHTIK2=_SERCHT[0][2],SERCHTIK3=_SERCHT[0][3],SERCHTIK4=_SERCHT[0][4],SERCHTIK5=_SERCHT[0][5],SERCHTIK6=_SERCHT[0][6])
    return redirect('mis_pedidos')



" R & B"
    

@app.route('/IDR',methods= ['POST','GET'])
def IDR():
   print("si llego")
   #busqueda= Modelo.buscarU(session['user'])
   files = request.files.getlist('files[]')

   #errors = {}
   success = False

   for file in files:
      if file:
         filename = secure_filename(file.filename)
         _nombrearchivo=filename
         Modelo.IngresarIDetras(session['user'],_nombrearchivo)
         
         file.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename))
         success = True

      if success:
         resp = json.dumps({'message' : 'Files successfully uploaded'})
         _urline="./static/INEATRAS\\"+filename
         bandera=Modelo.ImagenATextoINEAtras(session['user'],_urline)
         if bandera == 1:
            print('NOINE')
            resp = json.dumps({'response' : 'No es una INE'})
            #Modelo.entities(busqueda,'uploadINETR','Subio su INE DETRAS')
            return resp
         elif bandera == 2: 
            print('INEYAREGISTRADA')
            resp = json.dumps({'response' : 'Esa INE ya esta registrada'})
            #Modelo.entities(busqueda,'uploadINETR','No se pudo, ine ya registrada')
            return resp
         elif bandera == 3: 
            print ('INE SE GUARDA')
            resp = json.dumps({'response' : 'INE registrada exitosamente'})
            #Modelo.entities(busqueda,'uploadINETR','Subio su INE DETRAS')
            return resp
         else:
            resp = json.dumps({'response' : 'Imgen no legible'})
            #Modelo.entities(busqueda,'uploadINETR','No se pudo leer imagen')
            return resp
         resp.status_code = 201
         
         return resp

@app.route('/ID',methods= ['POST','GET'])
def ID():
   print("si llego")
   #print(session['user'])
   #busqueda= Modelo.buscarU(session['user'])

   files = request.files.getlist('files[]')

   #errors = {}
   success = False

   for file in files:
       if file:
          filename = secure_filename(file.filename)
          _nombrearchivo=filename
          sub=Modelo.IngresarIDelante(session['user'],_nombrearchivo)
          if sub:
              print("Se guardo")
       try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER1'], filename))
            success = True
            print(os.path.join(app.config['UPLOAD_FOLDER1'], filename))
       except Exception as e:
            print(str(e))


       if success:
         #resp = json.jsonify({'message' : 'Files successfully uploaded'})
         _nombrearchivo=filename
         _urline="./static/INEDELANTE\\"+filename
         #Modelo.ImagenATextoINE(busqueda,_urline)
         bandera=Modelo.ImagenATextoINE(session['user'],_urline)
         if bandera == 1:
            print('NOINE')
            resp = json.dumps({'response' : 'No es una INE'})
            Modelo.entities(session['user'],'uploadINE','Documento no es una INE')
            return resp
         elif bandera == 2: 
            print('INEYAREGISTRADA')
            resp = json.dumps({'response' : 'Esa INE ya esta registrada'})
            Modelo.entities(session['user'],'uploadINE','Documento invalido, INE ya registrada')
            return resp
         elif bandera == 3: 
            print ('SEREGISTRA')
            resp = json.dumps({'response' : 'INE registrada exitosamente'})
            Modelo.entities(session['user'],'uploadINE','Subio su INE DELANTE')
            return resp
         else:
            resp = json.dumps({'response' : 'Imgen no legible'})
            Modelo.entities(session['user'],'uploadINE','Imagen lo legible')
            return resp

         #Modelo.IngresarIDelante(_nombrearchivo)
         resp.status_code = 201
         return resp

       

@app.route('/COMP',methods= ['POST','GET'])
def COMP():
   print("si llego")
   #busqueda= Modelo.buscarU(session['user'])
   files = request.files.getlist('files[]')

   #errors = {}
   success = False

   for file in files:
      if file:
         filename = secure_filename(file.filename)
         _nombrearchivo=filename
         Modelo.IngresarComprobante(session['user'],_nombrearchivo)
         
         file.save(os.path.join(app.config['UPLOAD_FOLDER3'], filename))
         success = True

      if success:
         resp = json.dumps({'message' : 'Files successfully uploaded'})
         _urline="./static/Comprobante\\"+filename
         bandera= Modelo.ImagenATextoDomicilio(session['user'],_urline)
         if bandera == 1:
            print('NComprobante')
            resp = json.dumps({'response' : 'Documento invalido'})
            #Modelo.entities(busqueda,'uploadCompr','Comprobante inválido')
            return resp
         elif bandera == 0: 
            print('Comprobante valido')
            resp = json.dumps({'response' : 'Comprobante valido'})
            #Modelo.entities(busqueda,'uploadCompr','Subio su comprobante de domicilio')
            return resp
         else:
            resp = json.dumps({'response' : 'Imgen no legible'})
            #Modelo.entities(busqueda,'uploadCompr','No se pudo leer imagen')
            return resp
         resp.status_code = 201
         return resp


@app.route('/SELF',methods= ['POST','GET'])
def SELF():
   print("si llego a la selfie")
   #busqueda= Modelo.buscarU(session['user'])

   files = request.files.getlist('files[]')

   #errors = {}
   success = False

   for file in files:
      if file:
         filename = secure_filename(file.filename)
         _nombrearchivo=filename
         ine=Modelo.SelectIneArchivo(session['user'])
         if ine == False:
             return json.dumps({'response' : 'No subio su INE'})
         _urlComp="./static/INEDELANTE\\"+ ine
         file.save(os.path.join(app.config['UPLOAD_FOLDER4'], filename))
         success = True

      if success:
         resp = json.dumps({'message' : 'Files successfully uploaded'})
         _urline="./static/Selfie\\"+filename
         bandera=Comp.Comprobacion(_urlComp,_urline)
         if bandera == 1:
            print('NOINE')
            resp = json.dumps({'response' : 'Documento Valido'})
            Modelo.IngresarSelfie(session['user'],_nombrearchivo)
            Modelo.entities(session['user'],'uploadSelfie','Subio su Selfie')
            return resp
         elif bandera == 2:
            resp = json.dumps({'response' : 'No hay rostros'})
            Modelo.entities(session['user'],'NoUploadSelfie','No se pudo leer imagen')
            return resp
         elif bandera == 0:
            resp = json.dumps({'response' : 'No hay coincidencia'})
            Modelo.entities(session['user'],'NoUploadSelfie','No se pudo leer imagen')
            return resp
         #resp.status_code = 201
         
         return resp

"""
@app.route('/SELF',methods= ['POST','GET'])
def SELF():
        print("si llego a la sefie")
        #busqueda= Modelo.buscarU(session['user'])
        files = request.files.getlist('files[]')
	
       # errors = {}
        success = False
      
        for file in files:
         if file:
            filename = secure_filename(file.filename)
            _nombrearchivo=filename
            Modelo.IngresarSelfie(session['user'],_nombrearchivo)
            file.save(os.path.join(app.config['UPLOAD_FOLDER4'], filename))
            success = True

        if success:
            resp = json.dumps({'message' : 'Files successfully uploaded'})
            #resp.status_code = 201            
            #Modelo.entities(busqueda,'busqueda','Subio su selfie')
            return resp
"""



@app.route('/B',methods= ['POST','GET'])
def B():
        f=request.files['archi']
        filename= secure_filename(f.filename)
        usuario=f.save(os.path.join(app.config['UPLOAD_FOLDER5'],filename))
        user=request.form['archi']
        if usuario == True:
           session['user'] = user 
           Modelo.entities(user, 'subir contrato', 'Se subio el contrato exitosamente')
           #return redirect(url_for('logeado'))
        else:
            errorlog= "Te faltan campos"
            Modelo.entities(user, 'Error al subir contrato', 'No se pudo subir el contrato')
            return render_template('perfil.html', errorlog = errorlog) 




@app.route('/uploadContract',methods= ['POST','GET'])
def uploadContract():
        print("se llego al subidor")
        #busqueda= Modelo.buscarU(session['user'])

        files = request.files.getlist('files[]')
	
        #errors = {}
        success = False
      
        for file in files:
         if file:
            filename = secure_filename(file.filename)
            _nombrearchivo=filename
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER5'], filename))
                success = True
            except Exception as e:
                print(str(e))

        if success:
            resp = json.dumps({'message' : 'Contrato subido con exito'})
            _nombrearchivo=filename
            _urline="./static/Contratos\\"+filename
            #resp.status_code = 201
            Modelo.entities(session['user'],'uploadContract','Subio contrato exitosamente')
            ll=Modelo.RegistroContrato(session['user'],_nombrearchivo)
            if ll:
                print("se registra")
                return json.dumps(True)
            else:
                print("ALGO SALIO MAL")
                return False
            return resp

@app.route("/misdatos",methods=['GET', 'POST'] )
def misdatos():
   #busqueda= Modelo.buscarU(session['user'])
   _name=Modelo.SelectNombre(session['user'])
   _rfc=Modelo.SelectCurp(session['user'])
   _email=session['user']
   _direccion=Modelo.SelectDireccion(session['user'])
   _fechanacimiento=Modelo.SelectFecha(session['user'])
   #Modelo.CrearPDF(_name,_rfc,_email,_direccion,_fechanacimiento)
   #Modelo.EnviarCorreoContrato(_name,_email)
   try:
      busquedaN= Modelo.SelectNombre(session['user'])
      busquedaEm= Modelo.SelectCorreo(session['user'])
      busquedaDI= Modelo.SelectDireccion(session['user'])
      busquedaFe= Modelo.SelectFecha(session['user'])
      busquedaCu= Modelo.SelectCurp(session['user'])

      return render_template("misdatosdb.html",nombre=busquedaN,email=busquedaEm,direccion=busquedaDI,fechanaci=busquedaFe,curp=busquedaCu) 
   except Exception as e:
       print(e)
       return redirect(url_for('subdocumentos'))
           



@app.route("/subdocumentos",methods=['GET', 'POST'] )
def subdocumentos():
   #busqueda= Modelo.buscarU(session['user'])
   
   front = Modelo.CHECKFront(session['user'])
   print(front)
   back=Modelo.CHECKBack(session['user'])
   print(back)
   imgdom=Modelo.CHECKDom(session['user'])  
   print(imgdom)
   selfie=Modelo.CHECKSelf(session['user'])
   print(selfie)
   llenado=0
   if front:
       llenado=llenado+1
   if back:
        llenado=llenado+1
   if imgdom:
        llenado=llenado+1
   if selfie:
        llenado=llenado+1

   llenadoB=(llenado*100)/4
   Modelo.entities(session['user'],'documentos','Entro a mis documentos')
   return render_template("documentosdb.html",frontINE=front,backINE=back,imgdom=imgdom,selfie=selfie,llenado=llenado,bar=llenadoB) 


@app.route("/sendContract",methods=['GET', 'POST'] )
def sendContract():
   _email= session['user']
   #env=Enviroment(loader=FileSystemLoader("templates"))
   #template=env.get_template("contrato.html")
   _name= Modelo.SelectNombre(session['user'])
   _direccion= Modelo.SelectDireccion(session['user'])
   _fechanacimiento= Modelo.SelectFecha(session['user'])
   _rfc= Modelo.SelectCurp(session['user'])
   
   #print("Hola")
   if((_name is not None) and (_direccion is not None) ):
       Crear=Modelo.CrearPDF(_name,_rfc,_email,_direccion,_fechanacimiento)
       Enviar=Modelo.EnviarCorreoContrato(_name,_email)
       if Crear and Enviar:
           return json.dumps(True)
       else:
           return json.dumps(False) 

      
   else:
      print("esta vacío")
      return json.dumps(False)


def Comprobacion(_urlIne,_urlSelfie):
    target_image_file_names = [_urlIne]
    # The source photos contain this person
    source_image_file_name1 = open(_urlSelfie,"rb")
    #source_image_file_name2 = open("pelon.jpeg","rb")

    # Detect face(s) from source image 1, returns a list[DetectedFaces]
    # We use detection model 2 because we are not retrieving attributes.
    detected_faces1 = face_client.face.detect_with_stream(source_image_file_name1 , detectionModel='detection_02')
    # Add the returned face's face ID
    source_image1_id = detected_faces1[0].face_id
    print('{} face(s) detected from image {}.'.format(len(detected_faces1), source_image_file_name1))

    # Detect face(s) from source image 2, returns a list[DetectedFaces]
    #detected_faces2 = face_client.face.detect_with_stream(source_image_file_name2, detectionModel='detection_02')
    # Add the returned face's face ID
    #source_image2_id = detected_faces2[0].face_id
    #print('{} face(s) detected from image {}.'.format(len(detected_faces2), source_image_file_name2))

    # List for the target face IDs (uuids)
    detected_faces_ids = []
    # Detect faces from target image url list, returns a list[DetectedFaces]
    for image_file_name in target_image_file_names:
        # We use detection model 2 because we are not retrieving attributes.
        print(image_file_name)
        image_file_name = open(image_file_name,"rb")
        detected_faces = face_client.face.detect_with_stream(image_file_name, detectionModel='detection_02')
        # Add the returned face's face ID
        detected_faces_ids.append(detected_faces[0].face_id)
        print('{} face(s) detected from image {}.'.format(len(detected_faces), image_file_name))

        # Verification example for faces of the same person. The higher the confidence, the more identical the faces in the images are.
    # Since target faces are the same person, in this example, we can use the 1st ID in the detected_faces_ids list to compare.
    verify_result_same = face_client.face.verify_face_to_face(source_image1_id, detected_faces_ids[0])
    print('Faces from {} & {} are of the same person, with confidence: {}'
        .format(source_image_file_name1, target_image_file_names[0], verify_result_same.confidence)
        if verify_result_same.is_identical
           
        else 'Faces from {} & {} are of a different person, with confidence: {}'
            .format(source_image_file_name1, target_image_file_names[0], verify_result_same.confidence))

    print(verify_result_same.confidence)
    if verify_result_same.confidence >.5:
        bandera=1
        return bandera
    else:
        bandera=0
        return bandera










if __name__ == "__main__":
    app.run(debug=True)
