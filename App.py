from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jona25a25.'
app.config['MYSQL_DB'] = 'creationsanysDB'

mysql = MySQL(app)

# Clave secreta para mensajes flash
app.secret_key = 'mysecretkey'

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        # Insertar en la base de datos
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO clientes (nombre, correo, telefono, direccion) 
                VALUES (%s, %s, %s, %s)
            """, (nombre, correo, telefono, direccion))
            mysql.connection.commit()
            flash(f'¡Bienvenido, {nombre}!', 'success')
            return redirect(url_for('catalogo'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cur.close()
    return render_template('registro.html')


# Ruta para mostrar el catálogo
@app.route('/catalogo')
def catalogo():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    return render_template('catalogo.html', productos=productos)

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    # Lógica para agregar al carrito (por ejemplo, guardar el producto seleccionado en la sesión)
    return redirect(url_for('formulario_pedido'))
#formulario pedido
@app.route('/formulario_pedido', methods=['GET', 'POST'])
def formulario_pedido():
    if request.method == 'POST':
        # Lógica para guardar el pedido
        fecha = request.form['fecha']
        color = request.form['color']
        # Guardar en la base de datos u otra lógica
        return redirect(url_for('pedido_agendado'))
    return render_template('formulario_pedido.html')

@app.route('/pedido_agendado')
def pedido_agendado():
    return render_template('pedido_agendado.html')

# Ruta para confirmar pedido
@app.route('/confirmar_pedido', methods=['GET', 'POST'])
def confirmar_pedido():
    id_cliente = 1  # Cambia esto por el ID del cliente autenticado
    cur = mysql.connection.cursor()

    # Obtener el nombre del cliente
    cur.execute("SELECT nombre FROM clientes WHERE id_cliente = %s", (id_cliente,))
    cliente = cur.fetchone()
    if not cliente:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('registro'))
    nombre_cliente = cliente[0]

    if request.method == 'POST':
        fecha_pedido = datetime.now().date()
        fecha_entrega = request.form['fecha_entrega']

        # Validar fecha de entrega
        fecha_minima = fecha_pedido + timedelta(days=3)
        if datetime.strptime(fecha_entrega, '%Y-%m-%d').date() < fecha_minima:
            flash('La fecha de entrega debe ser al menos 3 días después de hoy.', 'danger')
            return redirect(url_for('confirmar_pedido'))

        # Guardar datos del pedido en la sesión para el resumen
        session['pedido_resumen'] = {
            'id_cliente': id_cliente,
            'nombre_cliente': nombre_cliente,
            'fecha_pedido': fecha_pedido.strftime('%Y-%m-%d'),
            'fecha_entrega': fecha_entrega
        }
        return redirect(url_for('resumen_pedido'))

    cur.close()
    return render_template('confirmar_pedido.html', nombre_cliente=nombre_cliente)


# Ruta para mostrar el resumen del pedido
@app.route('/resumen_pedido', methods=['GET', 'POST'])
def resumen_pedido():
    if 'pedido_resumen' not in session:
        flash('No hay un pedido para mostrar.', 'danger')
        return redirect(url_for('confirmar_pedido'))

    pedido_resumen = session['pedido_resumen']

    if request.method == 'POST':
        # Guardar el pedido en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO pedidos (id_cliente, fecha_pedido, fecha_entrega, estado) 
            VALUES (%s, %s, %s, 'pendiente')
        """, (pedido_resumen['id_cliente'], pedido_resumen['fecha_pedido'], pedido_resumen['fecha_entrega']))
        mysql.connection.commit()
        cur.close()

        # Limpiar la sesión después de guardar
        session.pop('pedido_resumen', None)
        flash('Pedido confirmado. Muchas gracias por tu compra.', 'success')
        return redirect(url_for('pedido_detalle'))

    return render_template('resumen_pedido.html', pedido=pedido_resumen)

# Ruta para ver detalle del pedido
@app.route('/pedido_detalle')
def pedido_detalle():
    id_cliente = 1  # Cambia esto por el ID del cliente autenticado
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_pedido, p.fecha_pedido, p.fecha_entrega, p.estado
        FROM pedidos p 
        WHERE p.id_cliente = %s
    """, (id_cliente,))
    detalles = cur.fetchall()
    cur.close()
    return render_template('pedido_detalle.html', detalles=detalles)

# Configuración para ejecutar el servidor
if __name__ == '__main__':
    app.run(port=3000, debug=True)
