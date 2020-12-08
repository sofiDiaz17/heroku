from flask import Flask, render_template, request, json, url_for, redirect,send_from_directory
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename
from pathlib import Path 
from PyPDF2 import PdfFileReader
import os
import Modelo as Modelo
import ModeloT as ModeloT
import Include.Modelo as Modelo
import time
import re
app = Flask(__name__)

app.config['UPLOAD_PATH'] = 'uploads'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.pdf']
app.config['UPLOAD_FOLDER'] = '../UPLOADS'

app.config['UPLOAD_PATH2'] = 'ArchivosPDF'
app.config['UPLOAD_EXTENSIONS2'] = ['.pdf']


@app.route("/")
def index():
    return "<h1>Hola TIN701 Bases de Datos!</h1>"

@app.route("/g")
def grafica():
    return render_template("grafica.html")





@app.route("/p", methods=['POST','GET'])
def project():
    return render_template("proyecto.html")

@app.route("/in", methods=['POST','GET'])
def inicial():
    return render_template("index.html")




@app.route("/a", methods=['POST','GET'])
def akats():
    return render_template("tarea.html")


@app.route('/N',methods= ['POST', 'GET']) 
def N():

        f= request.files['a'] 
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return "<h1>Archivo Ninja subido exitosamente</h1>"                  


@app.route("/chuc", methods=['POST','GET'])
def ne():
        try:
            
            x=0
            for key, value in request.form.items(): 
                print("key: {0}, value: {1}".format(key, value))
                if x==0:
                    _n = "{0}".format(value)
                elif x==1:
                    _r = "{0}".format(value)
                elif x==2:
                    _a = "{0}".format(value)
                print ("ciclo " + str(x))
                x=x+1
            
          


            if _n and _r and _a:
                return ModeloT.insertarEventoN(_n,_r,_a)
            else:
                return json.dumps({'html':'<span>Datos faltantes de los ninjas</span>'})
        except Exception as e:
            return json.dumps({'error':str(e)})
        finally:
            print("Lets go!")    

		

#@app.route('/re',methods=['POST','GET'])
#def res():
        #try:
           # _u = request.args.get('Usuario')
            #_e = request.args.get('Evento')
            #if _u and _e:
                #return Modelo.insertarEvento(_u, _e)
            #else:
                #return json.dumps({'html':'<span>Datos faltantes</span>'})
        #except Exception as e:
            #return json.dumps({'error':str(e)})
        #finally:
            #print("Lets go!")

#if __name__ == "__main__":
    #app.run()




def guardarArchivo(_archivo):
        if _archivo.filename != '':
            file_ext=os.path.splitext(_archivo.filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS2']:
            return False
        _archivo.save(os.path.join(app.config['UPLOAD_PATH2']), _archivo.filename)   
        return True

def extraerDatos(_nombrearchivo):
    pdf_reader=PdfFileReader(os.path.join(app.config['UPLOAD_PATH2'], _nombrearchivo.file))
    output_file_path= Path.cwd() / "TextoParaParseo.txt"
    with output_file_path.open(mode='w') as output_file:
        title= pdf_reader.documentInfo.title
        num_pages = pdf_reader.getNumPages()
        output_file.write(f"{title}\\nNumber of pages:{title}\\n\\n")
        for page in pdf_reader.pages:
            text=page.extractText()
            output_file.write(text)
    print('abriendo archivo...')
    time.sleep(3)
    _textoaparsear=open('TextoParaParseo.txt', 'r')
    _contenido=_textoaparsear.read()
    print("Contenido",_contenido)
    return _contenido

def ParseoTexto(_texto):
    _patron= (r"(\d{4}-\d{2})\n"
        r"Serial No:\n"
        r"(\w+)\n"
        r"Date:\n"
        r"(\d{2}/\d{2}/\d{4})\n" 
        r"B \$ W Total\n" 
        r"(\d+,\d+|\d+)\n" 
        r"Colour Total\n" 
        r"(\d+,\d+|\d+)")
    _todos=re.findall(_patron,_texto,re.MULTILINE)
    return _todos    

@app.route('/pro', methods= ['POST','GET'])
def archivo ():
    try:
        _eventos=Modelo.selectALLLecturas()


        #1 recibir archivo
        if request.method == 'POST':
            _a=request.files['Archivo']

        #validar el tipo de archivo y guardar en servidor

        if guardarArchivo(_a):
            print("si se guardo")
          
            
            _datos=extraerDatos(_a.filename)
           
            _encontrados=ParseoTexto(_datos)
            #5,.Cargarlo en la BD
            Modelo.InsertarLecturas(_encontrados)
     
        
        return render_template('1carga.html',eventos =_eventos)
    except Exception as e:
        print(str(e))
        return render_template('1carga.html')





@app.route("/ipro" ,methods = ['POST','GET'])
def inicialopro():
    return render_template("inicial.html")


if __name__ == "__main__":
    app.run()   





