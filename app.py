from flask import Flask, flash, render_template,request, url_for, redirect, session
from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1Jptyvdtnma'
app.config['MYSQL_DB'] = 'Cafeteria'
app.secret_key = 'contraseña'

mysql = MySQL(app)

#Vista General -----------------------------------------------------------------------------    
#Inicio Cafeteria
@app.route('/')
def inicio():
    return render_template('index.html')

#Menu publico
@app.route('/menu')
def menu():
    cur = mysql.connection.cursor()
    postre="'postre'";comida="'comida'"; bebida="'bebida'"
    cur.execute('SELECT Nombre, Precio FROM Producto where Categoria =(%s)'%(postre))    
    postre = cur.fetchall()
    cur.execute('SELECT Nombre, Precio FROM Producto where Categoria =(%s)'%(comida))    
    comida = cur.fetchall()
    cur.execute('SELECT Nombre, Precio FROM Producto where Categoria =(%s)'%(bebida))    
    bebida = cur.fetchall()
    return render_template('menu.html', comida=comida,bebida=bebida,postre=postre)

#Fichas publicadas
@app.route('/fichas')
def fichas():
    cur = mysql.connection.cursor()
    listo="'Listo'"
    cur.execute('SELECT idFicha, Cliente FROM Ficha where Estado =(%s)'%(listo))    
    listo = cur.fetchall()
    return render_template('fichas.html', listo=listo)

#Ingresar
@app.route('/login')
def login():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1001"):
            return redirect(url_for('users'))
        elif (usuario=="1002"):
            return redirect(url_for('admin'))
        else: 
            return redirect(url_for('cocin'))
    else:
        return render_template('ingresa.html')

#Cerrar Sesion
@app.route('/salir')
def salir():
    session.clear()
    return render_template('index.html')

#Validar Datos
@app.route('/ingresar', methods=['POST'])
def ingresar():
    if  request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        usuario=usuario.strip()
        if usuario=="1001" or usuario=="1002" or usuario=="1003":
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM Usuario WHERE CI= {0}'.format(usuario))
            dato = cur.fetchall()[0];categoria= dato[2]
            dato= dato[1]
            mysql.connection.commit()
            session["usuario"]= usuario
            if dato == contraseña:
                if categoria=='Administrador':
                    return redirect(url_for('users'))
                else :
                    if categoria=='Cajero':
                        cur.execute('select count(idDia) from Dia')
                        ext=cur.fetchone()[0]
                        if ext==0:
                            return redirect(url_for('com'))
                        else: 
                            return redirect(url_for('admin'))
                    else:
                        return redirect(url_for('cocin'))
            else :
                session.clear()
                flash('Contraseña Incorrecta')
                return redirect(url_for('login'))
        else :
           flash('El usuario no existe')
           return redirect(url_for('login'))

#Usuario Administrador -----------------------------------------------------------------------------    
#General
@app.route('/users')
def users():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1001"):
            cur = mysql.connection.cursor()
            cur.execute('SELECT CI, Contraseña, Categoria FROM Usuario')    
            usuarios = cur.fetchall()
            return render_template('usuarios.html', usuarios=usuarios)
        elif (usuario=="1002"):
            return redirect(url_for('admin'))
        else: 
            return redirect(url_for('cocin'))
    else:
        return render_template('ingresa.html')

#Cambiar contraseña
@app.route('/camr', methods=['POST'])
def camr():
    if  request.method == 'POST':
        ci = request.form['ci']
        ct=request.form['categoria']
    return render_template('cambiar.html', ci=ci,ct=ct)

@app.route('/cambiarC', methods=['POST'])
def cambiar():
    if  request.method == 'POST':
        usuario = request.form['usuario']
        nueva=request.form['nueva']
        nueva="'"+nueva+"'"
        cur = mysql.connection.cursor()
        cur.execute('UPDATE Usuario SET Contraseña={0} WHERE CI= {1}'.format(nueva,usuario))
        flash('Cambiado correctamente')
        mysql.connection.commit()
        return redirect(url_for('users'))

#Ver dias y ganancia
@app.route('/dias')
def dias():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1001"):

           cur = mysql.connection.cursor()
           cur.execute('SELECT * FROM Dia')
           dias = cur.fetchall()
           return render_template('dias.html', dias=dias)

        elif (usuario=="1002"):
            return redirect(url_for('admin'))
        else: 
            return redirect(url_for('cocin'))
    else:
        return render_template('ingresa.html')

#Usuario Cajero -----------------------------------------------------------------------------    
# Comenzar
@app.route('/com')
def com():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1002"):
            return render_template('comenzar.html')
        elif (usuario=="1001"):
            return redirect(url_for('users'))
        else: 
            return redirect(url_for('cocin'))
    else:
        return render_template('ingresa.html')

#Ingresar Fecha
@app.route('/com2', methods=['POST'])
def com2():
    if  request.method == 'POST':
         fecha = request.form['fecha'] 
         fecha=fecha
         cur= mysql.connection.cursor()
         cur.execute('INSERT INTO Dia(Fecha,Ganancia) VALUES (%s,%s)',(fecha,-1))
         mysql.connection.commit()
    return redirect(url_for('admin'))

#General
@app.route('/admin')
def admin():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1002"):
            cur = mysql.connection.cursor()
            cur.execute('SELECT max(idDia) as  idDia FROM Dia ')
            idDia=cur.fetchone()[0]
            cur.execute('SELECT Fecha,Ganancia FROM Dia where idDia =(%s)'%(idDia))
            data=cur.fetchall()[0]
            if data[1]==-1 :
                cur = mysql.connection.cursor()
                cur.execute('select count(idFicha) from Ficha')
                dat=cur.fetchone()[0]
                if dat==0:
                    ficha=1
                else:
                    cur.execute('SELECT max(idFicha) as  idFicha FROM Ficha ')
                    ficha=cur.fetchone()[0]
                    cur.execute('SELECT Total FROM Ficha where idFicha={0}'.format(ficha))
                    total = cur.fetchone()[0]
                    if total!= 0:
                        ficha=ficha+1
            
                postre="'postre'";comida="'comida'"; bebida="'bebida'"; proceso="'Proceso'";total=0
                cur.execute('SELECT idProducto,Nombre, Precio FROM Producto where Categoria =(%s)'%(postre))    
                postre = cur.fetchall()
                cur.execute('SELECT idProducto,Nombre, Precio FROM Producto where Categoria =(%s)'%(comida))    
                comida = cur.fetchall()
                cur.execute('SELECT idProducto,Nombre, Precio FROM Producto where Categoria =(%s)'%(bebida))    
                bebida = cur.fetchall()
                cur.execute('SELECT idProducto,idFicha, Cantidad FROM Pedido where Estado =(%s)'%(proceso))    
                proceso=cur.fetchall(); pedido= 'P:'
                for i in proceso:
                    cur.execute('SELECT Nombre, Precio FROM Producto where idProducto =(%s)'%(i[0]))  
                    data=cur.fetchall()[0]  ;pedido='{0} - {1} {2}'.format(pedido,i[2],data[0])+'\n'
                    total=total + (data[1]*i[2])
                cur.execute('SELECT max(idDia) as  idDia FROM Dia ')
                idDia=cur.fetchone()[0]
                cur.execute('SELECT idDia,Fecha FROM Dia where idDia =(%s)'%(idDia))
                dia=cur.fetchall()[0]
                idDia=dia[0]; fecha=dia[1]
                return render_template('admin.html',ficha=ficha,postre=postre,comida=comida,bebida=bebida,proceso=proceso,total=total,pedido=pedido,idDia=idDia,fecha=fecha)
            else:
                return redirect(url_for('com'))           
        elif (usuario=="1001"):
            return redirect(url_for('users'))
        else: 
            return redirect(url_for('cocin'))
    else:
        return render_template('ingresa.html')

#Añadir pedido
@app.route('/fich', methods=['POST'])
def fich():
    if  request.method == 'POST':
        cantidad= request.form['cantidad']
        cantidad=int(cantidad)
        idProducto=request.form['idProducto']
        ficha=request.form['ficha']
        idDia=request.form['dia']
        cur = mysql.connection.cursor()
        cur.execute('select count(idProducto) from Producto WHERE idProducto= {0}'.format(idProducto))
        idd=cur.fetchone()[0]
        if idd !=0 and cantidad>0:
            cur.execute('select count(idFicha) from Ficha WHERE idFicha= {0}'.format(ficha))
            fit=cur.fetchone()[0]
            c="'No'"; estado="Proceso"
            orden="INSERT INTO Ficha(idDia,Cliente,Total,Estado) VALUES ("+idDia+","+c+",0,"+c+")"
            if fit == 0:
                cur.execute('{0}'.format(orden))
                mysql.connection.commit()
            cur.execute('INSERT INTO Pedido(idProducto,idFicha,Cantidad,Estado) VALUES (%s,%s,%s,%s)',(idProducto,ficha,cantidad,estado))
            mysql.connection.commit()
            flash('Añadido correctamente')
        else:
            flash('Datos incorrectos')
    return redirect(url_for('admin'))

#Cancelar pedidos
@app.route('/borrar')
def delt():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1002"):
            cur = mysql.connection.cursor()
            estado2="'Proceso'"
            cur.execute('DELETE FROM Pedido WHERE Estado = {0}'.format(estado2))
            mysql.connection.commit()
            return redirect(url_for('admin'))
        elif (usuario=="1001"):
            return redirect(url_for('users'))
        else: 
            return redirect(url_for('cocin'))
    else:
        return render_template('ingresa.html')

#Añadir ficha
@app.route('/fich2', methods=['POST'])
def fich2():
    if  request.method == 'POST':
        cliente= request.form['cliente']
        ficha=request.form['fich']
        idDia=request.form['dia']
        total=request.form['total']
        cur = mysql.connection.cursor()
        cur.execute('select count(idFicha) from Ficha WHERE idFicha= {0}'.format(ficha))
        idd=cur.fetchone()[0]
        if idd ==0:
            flash("Debes añadir productos")
        else:
            estado="'Confirmado'"; cliente="'"+cliente+"'";estado2="'Proceso'"
            cur.execute('UPDATE Ficha SET idDia={0}, Cliente={1},Total={2},Estado={3} WHERE idFicha= {4}'.format(idDia,cliente,total,estado,ficha))
            mysql.connection.commit()
            cur.execute('UPDATE Pedido SET Estado={0} WHERE Estado= {1}'.format(estado,estado2))
            mysql.connection.commit()
            flash('Ficha Añadida')
    return redirect(url_for('admin'))

#Cerrar caja
@app.route('/conf', methods=['POST'])
def comf():
    if  request.method == 'POST':
        idDia= request.form['idDia']
        cur = mysql.connection.cursor()
        cur.execute(' SELECT SUM(Total) from Ficha where idDia= {0}'.format(idDia))
        total=cur.fetchone()[0]
        if total==None:
            total=0
        estado2="'Proceso'"
        cur.execute('DELETE FROM Pedido WHERE Estado = {0}'.format(estado2))
        mysql.connection.commit()
        return render_template('cerrarcaja.html', total=total,idDia=idDia)

@app.route('/conf2', methods=['POST'])
def comf2():
    if  request.method == 'POST':
        total= request.form['total']
        idDia= request.form['idDia']
        cur = mysql.connection.cursor()
        cur.execute('UPDATE Dia SET Ganancia={0} WHERE idDia= {1}'.format(total,idDia))
        mysql.connection.commit()
        return redirect(url_for('salir'))

#Usuario Cocinero -----------------------------------------------------------------------------    
#General
@app.route('/cocin')
def cocin():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1003"):
            cur = mysql.connection.cursor()
            confirmado="'Confirmado'"
            cur.execute('SELECT idFicha, Cliente FROM Ficha where Estado =(%s)'%(confirmado))    
            confirmado = cur.fetchall()
            listo="'Listo'"
            cur.execute('SELECT idFicha, Cliente FROM Ficha where Estado =(%s)'%(listo))    
            listo = cur.fetchall()
            return render_template('cocin.html',confirmado=confirmado,listo=listo)
        elif (usuario=="1002"):
            return redirect(url_for('admin'))
        else: 
            return redirect(url_for('users'))
    else:
        return render_template('ingresa.html')

#Ver pedidos
@app.route('/ver', methods=['POST'])
def ver():
    if  request.method == 'POST':
        idFicha= request.form['idFicha']
        cur = mysql.connection.cursor()
        cur.execute('SELECT idProducto,Cantidad FROM Pedido where idFicha =(%s)'%(idFicha))    
        ped=cur.fetchall(); pedido= 'P:'
        for i in ped:
            cur.execute('SELECT Nombre, Precio FROM Producto where idProducto =(%s)'%(i[0]))  
            data=cur.fetchall()[0]  ;pedido='{0} | {1} {2}'.format(pedido,i[1],data[0])+'\n'
        flash(pedido)
        return render_template('verpedido.html')

#Cambiar estado de comida
@app.route('/estado/<estad>/<idFicha>')
def estado(estad,idFicha):
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1003"):
            cur = mysql.connection.cursor()
            estado="'"+estad+"'"
            cur.execute('UPDATE Ficha SET Estado={0} WHERE idFicha= {1}'.format(estado,idFicha))
            mysql.connection.commit()
            return redirect(url_for('cocin'))
        elif (usuario=="1002"):
            return redirect(url_for('admin'))
        else: 
            return redirect(url_for('users'))
    else:
        return render_template('ingresa.html')

#Ver menu para editar
@app.route('/cambmenu')
def cambmenu():
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1003"):
            cur = mysql.connection.cursor()
            postre="'postre'";comida="'comida'"; bebida="'bebida'"
            cur.execute('SELECT idProducto, Nombre, Precio FROM Producto where Categoria =(%s)'%(postre))    
            postre = cur.fetchall()
            cur.execute('SELECT idProducto, Nombre, Precio FROM Producto where Categoria =(%s)'%(comida))    
            comida = cur.fetchall()
            cur.execute('SELECT idProducto, Nombre, Precio FROM Producto where Categoria =(%s)'%(bebida))    
            bebida = cur.fetchall()
            return render_template('cambiarmenu.html', comida=comida,bebida=bebida,postre=postre)
        elif (usuario=="1002"):
            return redirect(url_for('admin'))
        else: 
            return redirect(url_for('users'))
    else:
        return render_template('ingresa.html')

#Editar Producto o añadir
@app.route('/editmenu/<accion>/<nombre>/<precio>/<categoria>', methods=['POST'])
def editMenu(accion,nombre,precio,categoria):
    if  request.method == 'POST':
        boton=""
        idProducto= request.form['idProducto']
        if accion=="nuevo":
            boton="Agregar"
            return render_template('editmenu.html',boton=boton,idProducto=idProducto,accion=accion)
        else:
            boton="Cambiar"
            return render_template('editmenu.html',boton=boton,idProducto=idProducto,producto=nombre,precio=precio,categoria=categoria,accion=accion)

@app.route('/edit2', methods=['POST'])
def edit2():
    if  request.method == 'POST':
        idProducto= request.form['idProducto']
        producto=request.form['producto']
        precio=request.form['precio']
        categoria=request.form['categoria']
        categoria=categoria.lower();categoria=categoria.strip()
        acc=request.form['acc']
        boton=request.form['boton']
        cur = mysql.connection.cursor()
        idProducto=int(idProducto); precio=float(precio)

        if  precio>0 and (categoria=="bebida" or categoria=="comida" or categoria=="postre"):
            if idProducto == 0:
                cur.execute('INSERT INTO Producto(Categoria,Nombre,Precio) VALUES (%s,%s,%s)',(categoria,producto,precio))
                mysql.connection.commit()
                return redirect(url_for('cambmenu'))
            else:
                categoria="'"+categoria+"'";producto="'"+producto+"'"
                cur.execute('UPDATE Producto SET Categoria={0},Nombre={1},Precio={2} WHERE idProducto= {3}'.format(categoria,producto,precio,idProducto))
                mysql.connection.commit()
                return redirect(url_for('cambmenu'))
        else:
            flash("La categoria no existe o el precio es menor a 0")
            return render_template('editmenu.html',boton=boton,idProducto=idProducto,producto=producto,precio=precio,categoria=categoria,accion=acc)

#EliminarProducto
@app.route('/borr/<idProducto>')
def borr(idProducto):
    if "usuario" in session:
        usuario = session["usuario"]
        if(usuario=="1003"):
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM Producto WHERE idProducto = {0}'.format(idProducto))
            mysql.connection.commit()
            return redirect(url_for('cambmenu'))
        elif (usuario=="1002"):
            return redirect(url_for('admin'))
        else: 
            return redirect(url_for('users'))
    else:
        return render_template('ingresa.html')

if __name__=='__main__':
    app.run(port=3000, debug=True)