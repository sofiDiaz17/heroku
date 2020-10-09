from flask import Flask, render_template, request, json, session, g
from flaskext.mysql import MySQL
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta


app = Flask(__name__)

app.config["DEBUG"] = True
app.config['MYSQL_DATABASE_USER'] = 'sepherot_sofia'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zueTmwnaGI3X'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_sofiaBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL(app)

def loginUser(_correo, _contraseña):
    try:
        if _correo and _contraseña:
            conn = mysql.connect()
            cursor = conn.cursor()
            query="SELECT * FROM C_Users WHERE correo = %s"
            try:
                cursor.execute(query, (_correo))
                data = cursor.fetchall()
                print(data)
                if data and data[0][1] == _contraseña:
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
        query="SELECT * FROM C_Users WHERE correo = %s"
        try:
            cursor.execute(query, (_user))
            data = cursor.fetchall()
            if data:
                return data[0][3]
            else:
                return False
        except Exception as e:
            return e
        cursor.close() 
        conn.close()
    else:
        return json.dumps({'html':'<span>Datos faltantes</span>'})


def dataUsuario(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT folio, monto, fecha, nombreR, puntos, expiracion,nombreE FROM T_Purchas, C_Rubro, C_Status WHERE usuario=%s and expiracion > CURRENT_DATE and rubro = id_rubro and estado = id_estado"
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
        query="SELECT puntos FROM T_Purchas where expiracion > CURRENT_DATE and estado=2 and usuario=%s"
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
        query="SELECT expiracion FROM T_Purchas where usuario = %s  and expiracion > CURRENT_DATE and estado=2 ORDER BY T_Purchas.expiracion ASC LIMIT 1"
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
    
def crearPurch(folio, user, monto, fecha,  rubro, arch):
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
    exp=date_object+relativedelta(months=+2)
    query="Insert into T_Purchas (folio, usuario, monto, fecha, rubro, puntos, expiracion, comprobante, estado) values (%s, %s, %s, %s, %s, %s ,%s, %s, 1)"
    try:
        done=cursor.execute(query, (folio, user, monto,fecha, rubro,puntos,exp, arch))
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
    query="Insert into Entities (user, stage, stageinfo) values (%s, %s, %s)"
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

