from turtle import update
from flask import Flask
from flask import render_template , request , redirect, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os
from flask import send_from_directory, url_for

app = Flask(__name__)
app.secret_key="9767"
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'empleados'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/')
def index():
    sql =  "SELECT * FROM `empleados`;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template('empleados/index.html' , empleados=empleados)

@app.route('/uploads/<nombrefoto>')
def uploads(nombrefoto):
    return send_from_directory(app.config['CARPETA'],nombrefoto)


@app.route("/destroy/<int:id>")
def destroy(id):
    conn=mysql.connect()
    cursor=conn.cursor()

    cursor.execute("SELECT foto from empleados WHERE id=%s", id)
    fila = cursor.fetchall()  
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    cursor.execute("DELETE FROM empleados WHERE id=%s", (id))
    conn.commit()
    return redirect('/')

@app.route("/edit/<int:id>")
def edit(id): 
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s",(id))
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template('empleados/edit.html' , empleados=empleados)
 
@app.route("/update" , methods=['POST'])
def update():
    id =  request.form['txtId']
    _nombre =request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    sql= "UPDATE empleados SET nombre=%s  , correo=%s WHERE id=%s;"
    datos = (_nombre, _correo,id)
    conn=mysql.connect()
    cursor=conn.cursor()
    now = datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    
    if _foto.filename !='':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto from empleados WHERE id=%s", id)
        fila = cursor.fetchall()  
       
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto , id))
        
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')

@app.route("/create")
def create():
    return render_template('empleados/create.html')

@app.route("/store", methods=['POST'])
def storage():
    _nombre =request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    if _nombre == '' or _correo == '' or _foto =='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))

    now = datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)


    sql =  "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    
    datos = (_nombre, _correo, nuevoNombreFoto)
    
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)

    