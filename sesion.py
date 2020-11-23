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
from dateutil.relativedelta import relativedelta
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





#pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = './.apt/usr/bin/tesseract'




app = Flask(__name__)
app.secret_key = 'claveultrasecretadeapp'

MYDIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = "uploads"


#app.config['UPLOAD_FOLDER'] = "cuponera\\uploads"
app.config['UPLOAD_EXTENSIONS'] = ['png', 'jpg', 'jpeg']

endpoint="https://cuponeravision.cognitiveservices.azure.com/"
subscription_key="4d0c7d3a1a4c4aebabb6df39c33dd9eb"
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


@app.route('/index')
def landing():
    return render_template ("index.html")


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = Modelo.buscarUser(session['user'])
        fotoB = Modelo.fotoUser(session['user'])
        g.foto =fotoB[0][0]
        
@app.route('/registro',methods=['GET','POST'])
def registro():
    if request.method=='POST':
        nombre=request.form['name']
        corre=request.form['email']
        contra=request.form['password']
        contra2=request.form['re_password']
        img=request.form['img']

        if contra == contra2:
            salt = uuid.uuid4().hex
            sPass=hashlib.sha512(contra.encode('utf-8')  + salt.encode('utf-8')).hexdigest()
            print(salt)
            print(sPass)
            if nombre and corre and contra:
                crear=Modelo.crearUsr(corre,sPass,salt,nombre,img)
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
            usuario=Modelo.loginUser(user,password)
            if usuario:
                session['user']=user
                Modelo.entities(user,'Login','El usuario hace login')
                return redirect(url_for('perfil'))
            else:
                errorLog="Los datos no concuerdan"
                Modelo.entities(user,'Login.Fail.NotFound','Error de datos al iniciar sesion')
                return render_template('login.html',errorLog=errorLog)
    return render_template('login.html')



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
            if bips==0:
                bips=1
            r=Modelo.rewardsUsr(bips)
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
            Modelo.entities(session['user'],'ProfileLoad','Se cargo el perfil del usuario')
            return render_template('perfil.html',onboarding=userOnBoard,puntos=puntos, expiracion=date_,puntosF=puntosF,nivel=r[0][0] )
        else:
            Modelo.entities(session['user'],'UserOnBoarding.Fail','Ocurrio un error con el proceso de OnBoarding del usuario')
            errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
            return render_template('login.html',errorLog=errorLog)
        
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'ProfileLoad.Fail.NotFound','Error al cargar el perfil del usuario')
        errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
        return render_template('login.html',errorLog=errorLog)


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
            Modelo.entities(session['user'],'RewardsLoad','Se cargo el perfil de rewards')
            return render_template('rewards.html',onboarding=userOnBoard,puntos=puntos,puntosF=puntosF,
            nivel=r[0][0],nivelN=r[0][1],r1=r[0][2],r2=r[0][3],r3=r[0][4],r4=r[0][5],bips=bips,bipsPer=bipsPer,
            faltan=faltan,nlvl=nextLvl[0][1],rNL1=nextLvl[0][2],rNL2=nextLvl[0][3])
        else:
            Modelo.entities(session['user'],'RewardsLoad.Fail','No se cargaron los rewards')
            errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
            return render_template('login.html',errorLog=errorLog)
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'RewardsLoad.Fail','No se cargaron los rewards')
        errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
        return render_template('login.html',errorLog=errorLog)


@app.route('/historial')
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
            return render_template('perfil.html',errorLog=errorLog)


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
        return render_template('perfil.html',errorLog=errorLog)

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
        
        Modelo.entities(session['user'],'CatalogLoad','Se cargo la pagina de catalogo')
        return render_template('catalogo.html',data=data)
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'CatalogLoad.Fail.NotFound','Error al cargar la pagina de catalogo')
        errorLog="Algo salio mal al cargar el catalogo, vuelva a intentarlo"
        return render_template('perfil.html',errorLog=errorLog)

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
        img = Image.open(os.path.join(MYDIR + "/" + app.config['UPLOAD_FOLDER'], filename))
        #img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'],filename))
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
    if request.method=='POST':
            folio = request.form['folio']
            monto = request.form['monto']
            fecha = request.form['fechaCom']
            rubro = request.form['rubro']
            archivo = request.form['archivo']

            today=datetime.datetime.now()
            d1 = today.strftime("%Y-%m-%d")
            ddd=datetime.datetime.strptime(d1, '%Y-%m-%d').date()
            #print(d1)
            d2=(ddd-timedelta(days=7)).strftime("%Y-%m-%d")
            #print(d2)
            if fecha > d1 or fecha < d2:
                errorLog="La fecha no es valida. (Recuerde que los recibos tienen solo una semana de validez)"
                return render_template('uploadAn.html',errorLog=errorLog)
            else:
                if folio and monto and fecha and rubro and archivo:
                    b=Modelo.bitsUser(session['user'])
                    bips=b[0][0]
                    guardar=Modelo.crearPurch(folio,session['user'],monto,fecha,rubro,archivo,bips)
                    if guardar:
                        Modelo.entities(session['user'],'SavePurchaseInDB','Se guardo una compra en la base de datos')
                        print('se subio la data')
                        return redirect(url_for('perfil'))
                    else:
                        Modelo.entities(session['user'],'SavePurchaseInDB.Fail','No se pudo guardar en la base de datos')
                        errorLog="Revise los datos"
                        return render_template('uploadAn.html',errorLog=errorLog)
    estado=Modelo.estadoOnboarding(session['user'])
    userOnBoard=estado[0][0]
    return render_template('uploadAn.html',onboarding=userOnBoard)

@app.route('/tester',methods=['GET','POST'])
def tester():
    dataP= Modelo.puntosUsuario(session['user'])
    puntos = 0
    try:
        for data in dataP:
            puntos = puntos + data[0]
    except:
        puntos = 0
    try:
        Modelo.entities(session['user'],'TesterLoad','Se cargo la pagina de tester')
        estado=Modelo.estadoOnboarding(session['user'])
        userOnBoard=estado[0][0]
        return render_template('fotoTest.html',puntos=puntos,onboarding=userOnBoard)
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'TesterLoad.Fail.NotFound','Error al cargar el tester')
        errorLog="Algo salio mal al cargar el tester, vuelva a intentarlo"
        return render_template('perfil.html',errorLog=errorLog)


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
                        'Ocp-Apim-Subscription-Key': "a17af57ca4ca4ec2ab4930bce9967c13",
                        'Ocp-Apim-Subscription-Region':'southcentralus',
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

@app.route('/OnBoard',methods=['GET','POST'])
def OnBoard():
    if request.method=='POST':
        data=request.get_json()
        estado=data['estado']
        try:
            data=Modelo.setEstadoOnboarding(session['user'],estado)
            if data:
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


if __name__ == "__main__":
    app.run(debug=True)
    
