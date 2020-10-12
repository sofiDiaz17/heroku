from flask import Flask, render_template, request, json, url_for, redirect,send_from_directory, session, g
from flaskext.mysql import MySQL
import data as Modelo
import jinja2
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



pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'



app = Flask(__name__)
app.secret_key = 'claveultrasecretadeapp'

app.config['UPLOAD_FOLDER'] = "cuponera\\uploads"
app.config['UPLOAD_EXTENSIONS'] = ['png', 'jpg', 'jpeg']

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = Modelo.buscarUser(session['user'])
        

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
    #dataU = Modelo.dataUsuario(session['user'])
    try:
        maxExp= Modelo.expDate(session['user'])
        dataP= Modelo.puntosUsuario(session['user'])
        try:
            date_= maxExp[0][0].strftime("%d/%m/%Y")
        except:
            date_="- No hay fecha registrada"
        puntos = 0
        try:
            for data in dataP:
                puntos = puntos + data[0]
        except:
            puntos = 0
        Modelo.entities(session['user'],'ProfileLoad','Se cargo el perfil del usuario')
        return render_template('perfil.html',puntos=puntos, expiracion=date_ )
    except Exception as e:
        print(str(e))
        Modelo.entities(session['user'],'ProfileLoad.Fail.NotFound','Error al cargar el perfil del usuario')
        errorLog="Algo salio mal al cargar perfil, vuelva a intentarlo"
        return render_template('login.html',errorLog=errorLog)


@app.route('/historial')
def historial():
    if not g.user:
        return redirect(url_for('login'))
    try:
        dataU = Modelo.dataUsuario(session['user'])
        Modelo.entities(session['user'],'HistoryLoad','Se cargo el historial del usuario')
        return render_template('historial.html', tabla=dataU)
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

def guardarArch(file):
    try:
        filename = secure_filename(file.filename)
        file.save(os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
        return True
    except Exception as e:
        print(str(e))  
        return False  

def extraerInfo(filename):
    try:
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
    if not g.user:
        return redirect(url_for('login'))
    if request.method=='POST':
        if request.form['analizar']:
            print("analizando data de foto")
            file = request.files['comprobante']
            if file:
                filename = secure_filename(file.filename)
                save=guardarArch(file)
            if save: 
                Modelo.entities(session['user'],'SavePicture','El usuario subio una foto y se guardo')
                try:
                    info=extraerInfo(filename)
                    if info:
                        Modelo.entities(session['user'],'AnalizePicture','Se analizo la foto del usuario')
                        folio=parsearFolio(info)
                        mont=parsearMonto(info)
                        date=parsearDate(info)
                        if folio:
                            session['fol']=folio
                        else:
                            session['fol']=""
                        if mont:
                            session['mon']=mont
                        else:
                            mont=0
                        if date:
                            try:
                                fecha=datetime.datetime.strptime(date, "%d/%b/%Y").strftime('%Y-%m-%d')
                                session['fec']=fecha
                            except:
                                try:
                                    fecha=datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
                                    session['fec']=fecha
                                except:
                                    fecha=""
                                    session['fec']=fecha
                        else:
                            session['fec']=""
                        session['arc']=filename
                        return redirect(url_for('form2'))
                except:
                    Modelo.entities(session['user'],'AnalizePicture.Fail','No se pudo analizar la foto')
            else:
                Modelo.entities(session['user'],'SavePicture.Fail','No se pudo guardar el archivo')
                errorLog="No se pudo guardar, intente de vuelta"
                return render_template('upload.html',errorLog=errorLog)
    return render_template('upload.html')

@app.route('/form2',methods=['GET','POST'])
def form2():
    if not g.user:
        return redirect(url_for('login'))
    if request.method=='POST':
        if request.form['ingresar']:
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
                return render_template('uploadAn.html',errorLog=errorLog,folio=session['fol'],monto=monto,fecha=session['fec'],archivo=session['arc'])
            else:
                if folio and monto and fecha and rubro and archivo:
                    guardar=Modelo.crearPurch(folio,session['user'],monto,fecha,rubro,archivo)
                    if guardar:
                        Modelo.entities(session['user'],'SavePurchaseInDB','Se guardo una compra en la base de datos')
                        print('se subio la data')
                        return redirect(url_for('perfil'))
                    else:
                        Modelo.entities(session['user'],'SavePurchaseInDB.Fail','No se pudo guardar en la base de datos')
                        errorLog="Revise los datos"
                        return render_template('uploadAn.html',errorLog=errorLog)
    try:
        monto=Decimal(session['mon'].replace(',',''))
    except:
        monto=0
    return render_template('uploadAn.html',folio=session['fol'],monto=monto,fecha=session['fec'],archivo=session['arc'])


@app.route('/close')
def close():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def inicio():
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
    
