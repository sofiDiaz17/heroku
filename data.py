from flask import Flask, render_template, request, json, session, g
from flaskext.mysql import MySQL
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import hashlib
import requests, uuid


app = Flask(__name__)

app.config["DEBUG"] = True
app.config['MYSQL_DATABASE_USER'] = 'sepherot_sofia'
app.config['MYSQL_DATABASE_PASSWORD'] = 'zueTmwnaGI3X'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_sofiaBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL(app)

def crearUsr(_correo, _contraseña,_salt,_nombre,_img):
    try:
        if _correo and _contraseña and _nombre:
            conn = mysql.connect()
            cursor = conn.cursor()
            query="INSERT INTO C_Users (email, password, salt, name, picture, onBoardState, BipTips) VALUES (%s, %s, %s, %s, %s,0,0);"
            try:
                cursor.execute(query, (_correo,_contraseña,_salt,_nombre,_img))
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
        query="SELECT * FROM C_Users WHERE email = %s"
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

def fotoUser(_user):
    if _user:
        conn = mysql.connect()
        cursor = conn.cursor()
        query="SELECT picture FROM C_Users WHERE email = %s"
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
                    regaloSet=cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                
            elif int(bips) + 300 >= 3000:
                id="regalo1000"+user
                points=1000
                doc="regalo1000"
                try:
                    queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    regaloSet=cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))
                
            elif int(bips) + 300 >= 2000:
                id="regalo700"+user
                points=700
                doc="regalo700"
                try:
                    queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    regaloSet=cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
                except Exception as e:
                    print(str(e))

            elif int(bips) + 300 >= 1000:
                id="regalo500"+user
                points=500
                doc="regalo500"
                try:
                    queryRegalo="Insert into T_Purchas (invoice, user, amount, date, category, points, expiration, file, status) values (%s, %s, 0, %s, 6, %s ,%s, %s, 2)"
                    regaloSet=cursor.execute(queryRegalo, (id,user,d1,points,expR,doc))
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

