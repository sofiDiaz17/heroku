from os import name
from flask import Flask, render_template, request, json, url_for, redirect,send_from_directory, g, session
import os
#from PyPDF2 import PdfFileReader
from werkzeug.utils import secure_filename
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import Modelo as Modelo
import data as Modelo2
import time
import re
import jinja2
import ctypes
import pdfkit

app = Flask(__name__)
app.config['UPLOAD_FOLDER5'] ='./static/Contratos'
app.config['UPLOAD_FOLDER4'] ='./static/Selfie'
app.config['UPLOAD_FOLDER3'] ='./static/Comprobante'
app.config['UPLOAD_FOLDER2'] ='./static/INEATRAS'
app.config['UPLOAD_FOLDER'] ='./static/INEDELANTE'
app.config['UPLOAD_EXTENSIONS'] = '.pdf', '.png' , '.jpeg'
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.before_request
def before_request():
   g.user = None
   if 'user' in session:
      g.user = Modelo.buscarU(session['user'])

@app.route("/")
def index():
  
   return render_template("./inicialekko.html")
   
#busqueda= Modelo.buscarU(session['user'])

#env=Enviroment(loader=FileSystemLoader("templates"))
#template=env.get_template("contrato.html")
#busquedaN= Modelo.SelectNombre(session['user'])
#busquedaDI= Modelo.SelectDireccion(session['user'])
#busquedaFe= Modelo.SelectFecha(session['user'])
#busquedaCu= Modelo.SelectCurp(session['user'])
#usuario={
# 'name': busquedaN,
# 'address': busquedaNI,
#'curp1':busquedaFe,
#'date':
# }

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
        print("si llego")
        busqueda= Modelo.buscarU(session['user'])

        files = request.files.getlist('files[]')
	
        #errors = {}
        success = False
      
        for file in files:
         if file:
            filename = secure_filename(file.filename)
            _nombrearchivo=filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER5'], filename))
            success = True

        if success:
            resp = json.jsonify({'message' : 'Files successfully uploaded'})
            _nombrearchivo=filename
            _urline="./static/Contratos\\"+filename
            resp.status_code = 201
            Modelo.entities(busqueda,'uploadContract','Subio contrato exitosamente')
            Modelo.RegistroContrato(busqueda)
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
         #print(_nombrearchivo)
         sub=Modelo2.IngresarIDelante(session['user'],_nombrearchivo)
         if sub:
            #redirect(url_for('subdocumentos')) 
            print("Se guardo")           
         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
         success = True

      if success:
         #resp = json.jsonify({'message' : 'Files successfully uploaded'})
         _nombrearchivo=filename
         _urline="./static/INEDELANTE\\"+filename
         #Modelo.ImagenATextoINE(busqueda,_urline)
         bandera=Modelo2.ImagenATextoINE(session['user'],_urline)
         if bandera == 1:
            print('NOINE')
            resp = json.jsonify({'response' : 'No es una INE'})
            Modelo.entities(session['user'],'uploadINE','Documento no es una INE')
            return resp
         elif bandera == 2: 
            print('INEYAREGISTRADA')
            resp = json.jsonify({'response' : 'Esa INE ya esta registrada'})
            Modelo.entities(session['user'],'uploadINE','Documento invalido, INE ya registrada')
            return resp
         elif bandera == 3: 
            print ('SEREGISTRA')
            resp = json.jsonify({'response' : 'INE registrada exitosamente'})
            Modelo.entities(session['user'],'uploadINE','Subio su INE DELANTE')
            return resp
         else:
            resp = json.jsonify({'response' : 'Imgen no legible'})
            Modelo.entities(session['user'],'uploadINE','Imagen lo legible')
            return resp

         #Modelo.IngresarIDelante(_nombrearchivo)
         resp.status_code = 201
         return resp
  
  
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
         Modelo2.IngresarIDetras(session['user'],_nombrearchivo)
         
         file.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename))
         success = True

      if success:
         resp = json.jsonify({'message' : 'Files successfully uploaded'})
         _urline="./static/INEATRAS\\"+filename
         bandera=Modelo2.ImagenATextoINEAtras(session['user'],_urline)
         if bandera == 1:
            print('NOINE')
            resp = json.jsonify({'response' : 'No es una INE'})
            #Modelo.entities(busqueda,'uploadINETR','Subio su INE DETRAS')
            return resp
         elif bandera == 2: 
            print('INEYAREGISTRADA')
            resp = json.jsonify({'response' : 'Esa INE ya esta registrada'})
            #Modelo.entities(busqueda,'uploadINETR','No se pudo, ine ya registrada')
            return resp
         elif bandera == 3: 
            print ('INE SE GUARDA')
            resp = json.jsonify({'response' : 'INE registrada exitosamente'})
            #Modelo.entities(busqueda,'uploadINETR','Subio su INE DETRAS')
            return resp
         else:
            resp = json.jsonify({'response' : 'Imgen no legible'})
            #Modelo.entities(busqueda,'uploadINETR','No se pudo leer imagen')
            return resp
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
         Modelo2.IngresarComprobante(session['user'],_nombrearchivo)
         
         file.save(os.path.join(app.config['UPLOAD_FOLDER3'], filename))
         success = True

      if success:
         resp = json.jsonify({'message' : 'Files successfully uploaded'})
         _urline="./static/Comprobante\\"+filename
         bandera= Modelo2.ImagenATextoDomicilio(session['user'],_urline)
         if bandera == 1:
            print('NComprobante')
            resp = json.jsonify({'response' : 'Documento invalido'})
            #Modelo.entities(busqueda,'uploadCompr','Comprobante inválido')
            return resp
         elif bandera == 0: 
            print('Comprobante valido')
            resp = json.jsonify({'response' : 'Comprobante valido'})
            #Modelo.entities(busqueda,'uploadCompr','Subio su comprobante de domicilio')
            return resp
         else:
            resp = json.jsonify({'response' : 'Imgen no legible'})
            #Modelo.entities(busqueda,'uploadCompr','No se pudo leer imagen')
            return resp
         resp.status_code = 201
         return resp

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
            Modelo2.IngresarSelfie(session['user'],_nombrearchivo)
            file.save(os.path.join(app.config['UPLOAD_FOLDER4'], filename))
            success = True

        if success:
            resp = json.jsonify({'message' : 'Files successfully uploaded'})
            resp.status_code = 201            
            #Modelo.entities(busqueda,'busqueda','Subio su selfie')
            return resp



@app.route("/misdatos",methods=['GET', 'POST'] )
def misdatos():
   busqueda= Modelo.buscarU(session['user'])
   _name=Modelo.SelectNombre(busqueda)
   _rfc=Modelo.SelectCurp(busqueda)
   _email=busqueda
   _direccion=Modelo.SelectDireccion(busqueda)
   _fechanacimiento=Modelo.SelectFecha(busqueda)
   #Modelo.CrearPDF(_name,_rfc,_email,_direccion,_fechanacimiento)
   #Modelo.EnviarCorreoContrato(_name,_email)
   try:
      busquedaN= Modelo.SelectNombre(session['user'])
      busquedaEm= Modelo.SelectCorreo(session['user'])
      busquedaDI= Modelo.SelectDireccion(session['user'])
      busquedaFe= Modelo.SelectFecha(session['user'])
      busquedaCu= Modelo.SelectCurp(session['user'])

      return render_template("./datos.html",nombre=busquedaN,email=busquedaEm,direccion=busquedaDI,fechanaci=busquedaFe,curp=busquedaCu) 
   except:
      print("error")    



@app.route("/registro",methods=['GET', 'POST'])
def insertarEventoP():
    if request.method == 'POST':
        _email=request.form.get('DEmail')
        _password=request.form.get('DPassword')
        usuario = Modelo.insertarEventoP(_email,_password)
        
        user=request.form['DEmail']
        if usuario == True:
           session['user'] = user 
           Modelo.entities(user, 'registrarse', 'El usuario se registro')
           Modelo.CorreoRegistro(_email)
           return redirect(url_for('index'))
        else:
            errorlog= "Te faltan campos"
            Modelo.entities(user, 'Error al registrarse', 'El usuario se registro')
            return render_template('registro1.html', errorlog = errorlog)
     
               
    return render_template ("./registro1.html")

              
@app.route("/actualizar")
def actualizarPass():
    if request.method == 'POST':
        _email=request.form.get('DEmailA')
        _password=request.form.get('DPasswordA')
        #usuario=Modelo.actualizarM(_email,_password)
        usuario=True
        user=request.form['DEmailA']
        if usuario == True:
           session['user'] = user 
           Modelo.entities(user, 'registrarse', 'El usuario se registro')
           #Modelo.EnviarCorreo(_name,_email)
           return redirect(url_for('index'))
        else:
            errorlog= "Te faltan campos"
            Modelo.entities(user, 'Error al registrarse', 'No pudo registrarse')
            return render_template('registro.html', errorlog = errorlog)

    return render_template("./actualizar.html")


@app.route("/login",methods=['GET', 'POST'])
def log():
   
   if g.user:
         return redirect(url_for('logeadobien'))
   if request.method=='POST':
         session.pop('user', None)
         user=request.form['LEmail']
         password= request.form['LPassword']
         print(user,password)
         if (user and password):
            print("A buscar")
            usuario= Modelo2.validarUsuario(user,password)
            if usuario == True:
               session['user'] = user
               #numloggins=Modelo.SelectLoggins(user) 
               numloggins=1
               Modelo.entities(user, 'Login', 'El usuario hizo log')
               if(numloggins ==0):
                  Modelo.RegistroLogin(user)
                  
                  return redirect(url_for('onbo'))
                 
               else:
                  Modelo.RegistroLogin(user)
                  return redirect(url_for('subdocumentos'))
         else:
               errorlog = "Tus datos son incorrectos"
               Modelo.entities(user, 'Login.Fail.NotFound', "Ingreso mal sus datos")
               return render_template('login1.html',errorlog = errorlog)   
   return render_template('login1.html')
 

@app.route("/logeado")
def logea():

  
   try:
      busqueda= Modelo.buscarU(session['user'])
      Modelo.entities(busqueda,'contrato','El usuario entro al apartado de contrato')
      return render_template("./perfil1.html",usuarioactual=busqueda) 
   except:
      print("error")   

@app.route("/didocumentos",methods=['GET', 'POST'] )
def subdocumentos():
   #busqueda= Modelo.buscarU(session['user'])
   Modelo.entities(session['user'],'documentos','Entro a mis documentos')
   return render_template("./documentos.html")   


@app.route("/actualizar")
def ActualizarEventoP():

   return render_template("./actualizar.html")

@app.route("/cerrar")
def cerrar():
   busqueda= Modelo.buscarU(session['user'])
   Modelo.entities(busqueda,'Logout','El usuario cerro sesión')
   session.pop("user",None)
   return redirect(url_for("index"))

@app.route("/onbo",methods=['GET', 'POST'] )
def onbo():
   busqueda= Modelo.buscarU(session['user'])
   Modelo.entities(busqueda,'onboarding','El usuario vio la guia')
  
   
   return render_template("./guia.html")     
   
@app.route("/profile",methods=['GET', 'POST'] )
def logeadobien():

   #busqueda= Modelo.buscarU(session['user'])
   #medalla1= Modelo.SelectLoggins(session['user'])
   #medalla2= Modelo.SelectStatus(session['user'])
   #medalla3= Modelo.SelectContrato(session['user'])
   #Modelo.entities(busqueda,'logeado','El usuario hizo login')
   return render_template("./profile1.html")   
  
@app.route("/sendContract",methods=['GET', 'POST'] )
def sendContract():
   
   _email= Modelo.buscarU(session['user'])
   #env=Enviroment(loader=FileSystemLoader("templates"))
   #template=env.get_template("contrato.html")
   _name= Modelo.SelectNombre(session['user'])
   _direccion= Modelo.SelectDireccion(session['user'])
   _fechanacimiento= Modelo.SelectFecha(session['user'])
   _rfc= Modelo.SelectCurp(session['user'])
   
   print("Hola")
   if((_name is not None) and (_direccion is not None) ):
      print("value")
      Modelo.CrearPDF(_name,_rfc,_email,_direccion,_fechanacimiento)
      Modelo.EnviarCorreoContrato(_name,_email)
      
   else:
      print("esta vacío")

   
   
   





if __name__ == "__main__":
    app.run()   
