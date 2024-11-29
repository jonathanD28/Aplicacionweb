from flask import Flask, make_response, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import pdfkit
import os
from datetime import datetime

app = Flask(__name__)


# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jona25a25.'
app.config['MYSQL_DB'] = 'creationsanysDB'

mysql = MySQL(app)

# Clave secreta para mensajes flash
app.secret_key = 'mi_clave_secreta'

path_to_wkhtmltopdf = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)


# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registro de usuarios
# Ruta para registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        
        # Insertar nuevo cliente en la base de datos y recuperar el ID
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO clientes (nombre, correo, telefono, direccion) 
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, telefono, direccion))
        mysql.connection.commit()
        
        # Obtener el ID del cliente insertado
        cur.execute("SELECT LAST_INSERT_ID()")
        id_cliente = cur.fetchone()[0]
        cur.close()
        
        # Guardar el ID del cliente y el nombre en la sesión
        session['id_cliente'] = id_cliente
        session['nombre_usuario'] = nombre
        session['usuario_registrado'] = True  # Marca al usuario como registrado
        
        flash("Registro exitoso. Ahora puedes agregar productos al carrito.", "success")
        return redirect(url_for('catalogo'))
    return render_template('registro.html')



# Ruta para mostrar el catálogo
@app.route('/catalogo')
def catalogo():
    lista_productos = obtener_productos() 
    return render_template('catalogo.html', productos=lista_productos)

def obtener_productos():
    return [
        {'id_producto': 1, 'nombre_producto': 'Ramo Feliz Cumpleaños', 'descripcion': '6 rosas (color a elección) con Listón y 2 mariposas', 'precio': 11.00, 'categoria': 'rosa', 'imagen': 'ramofelizcumple.jpeg'},
        {'id_producto': 2, 'nombre_producto': 'Ramo Temático Carro', 'descripcion': '6 rosas (color a elección) con carrito hotwheels', 'precio': 10.00, 'categoria': 'rosa', 'imagen': 'ramoHotwheels.jpeg'},
        {'id_producto': 3, 'nombre_producto': 'Ramo Corazón', 'descripcion': '6 rosas (color a elección) y 2 mariposas', 'precio': 10.00, 'categoria': 'rosa', 'imagen': 'ramo6rosas.jpeg'},
        {'id_producto': 4, 'nombre_producto': 'Ramo Luces LED', 'descripcion': '13 rosas (color a elección), Corona pequeña y 2 mariposas y Luz LED', 'precio': 22.00, 'categoria': 'rosa', 'imagen': 'ramoluzled.jpeg'},
        {'id_producto': 5, 'nombre_producto': 'Mini Ramo', 'descripcion': '3 rosas (color a elección), Mariposa', 'precio': 6.00, 'categoria': 'rosa', 'imagen': 'ramo3rosas.jpeg'},
        {'id_producto': 6, 'nombre_producto': 'Mini Corona', 'descripcion': 'Color dorado y plateado (metálica)', 'precio': 1.75, 'categoria': 'accesorio', 'imagen': 'coronapequeña.jpeg'},
        {'id_producto': 7, 'nombre_producto': 'Letras LED', 'descripcion': '4 o 3 fotos, Frase, Fecha, Corazones', 'precio': 10.00, 'categoria': 'accesorio', 'imagen': 'ramoluzled.jpeg'},
        {'id_producto': 8, 'nombre_producto': 'Corona Metálica Mediana', 'descripcion': 'Dorada con perlita', 'precio': 2.00, 'categoria': 'accesorio', 'imagen': 'coronamediana.jpeg'},
        {'id_producto': 9, 'nombre_producto': 'Corona Metálica Grande', 'descripcion': 'Corona de metal grande con perlitas', 'precio': 3.00, 'categoria': 'accesorio', 'imagen': 'coronametalica.jpeg'},
        {'id_producto': 10, 'nombre_producto': 'Ramo Peluche', 'descripcion': 'Peluche, Carta, Listón con frase, 2 mariposas', 'precio': 20.00, 'categoria': 'rosa', 'imagen': 'ramo6rosas.jpeg'},
    ]
def obtener_producto(id_producto):
    productos = obtener_productos()
    for producto in productos:
        if producto['id_producto'] == id_producto:
            return producto
    return None
print("Using wkhtmltopdf from:", path_to_wkhtmltopdf)

# Ruta para agregar productos al carrito
@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'usuario_registrado' not in session:
        flash("Debes registrarte antes de agregar productos al carrito.", "error")
        return redirect(url_for('registro'))

    id_producto = request.form.get('id_producto')
    cantidad = int(request.form.get('cantidad', 1))
    
    # Simula el carrito
    if 'carrito' not in session:
        session['carrito'] = []
    
    # Agregar el producto al carrito
    session['carrito'].append({'id_producto': id_producto, 'cantidad': cantidad})
    flash("Producto agregado al carrito.", "success")
    
    # Redirige al usuario a la página de detalles del pedido
    return redirect(url_for('pedido_detalle'))

# Ruta para ver el carrito
@app.route('/ver_carrito')
def ver_carrito():
    carrito = session.get('carrito', [])
    if not carrito:
        flash("Tu carrito está vacío.", "warning")
    return render_template('carrito.html', carrito=carrito)

@app.route('/pedido_detalle', methods=['GET', 'POST'])
def pedido_detalle():
    carrito = session.get('carrito', [])
    
    if not carrito:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for('catalogo'))  # Regresa al catálogo si no hay productos
    
    if request.method == 'POST':
        # Recibir la fecha de entrega y color seleccionados
        fecha_entrega = request.form.get('fecha_entrega')
        color = request.form.get('color')
        
        # Guardar los detalles del pedido en la sesión
        pedido_resumen = {
            'productos': carrito,
            'fecha_entrega': fecha_entrega,
            'color': color
        }
        session['pedido_resumen'] = pedido_resumen
        flash("Detalles del pedido guardados. Puedes confirmar tu pedido.", "success")
        return redirect(url_for('confirmar_pedido'))
    
    # Aquí pasamos los productos del carrito para que se muestren en el formulario
    return render_template('pedido_detalle.html', carrito=carrito)

@app.route('/confirmar_pedido', methods=['GET', 'POST'])
def confirmar_pedido():
    if 'pedido_resumen' not in session:
        flash("No hay detalles del pedido para confirmar.", "error")
        return redirect(url_for('catalogo'))
    
    # Obtener los detalles del pedido desde la sesión
    pedido_resumen = session['pedido_resumen']
    
    # Obtener el ID del cliente desde la sesión
    id_cliente = session.get('id_cliente')
    if not id_cliente:
        flash("Error: No se pudo identificar al cliente. Por favor, regístrate de nuevo.", "error")
        return redirect(url_for('registro'))

    # Aquí procesas el pedido en la base de datos (guardar en la tabla de pedidos)
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO pedidos (id_cliente, fecha_pedido, fecha_entrega, color, estado) 
        VALUES (%s, %s, %s, %s, 'pendiente')
    """, (id_cliente, datetime.now(), pedido_resumen['fecha_entrega'], pedido_resumen['color']))
    mysql.connection.commit()
    cur.close()
    
    # Limpiar la sesión
    session.pop('carrito', None)
    session.pop('pedido_resumen', None)
    
    flash("Pedido confirmado. Muchas gracias por tu compra.", "success")
    return redirect(url_for('pedido_agendado'))


# Ruta para mostrar el resumen del pedido
@app.route('/resumen_pedido', methods=['GET', 'POST'])
def resumen_pedido():
    carrito = session.get('carrito', [])
    fecha_entrega = session.get('fecha_entrega', '')
    
    if not carrito:
        flash('No hay productos en el carrito.', 'danger')
        return redirect(url_for('ver_carrito'))

    if request.method == 'POST':
        # Guardar el pedido en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO pedidos (id_cliente, fecha_pedido, fecha_entrega, estado) 
            VALUES (%s, %s, %s, 'pendiente')
        """, (session['id_usuario'], datetime.now(), fecha_entrega))
        mysql.connection.commit()
        cur.close()

        # Limpiar la sesión después de guardar
        session.pop('carrito', None)
        session.pop('fecha_entrega', None)
        flash('Pedido confirmado. Muchas gracias por tu compra.', 'success')
        return redirect(url_for('pedido_detalle'))

    return render_template('resumen_pedido.html', carrito=carrito, fecha_entrega=fecha_entrega)

@app.route('/pedido_agendado')
def pedido_agendado():
    return render_template('pedido_agendado.html')

@app.route('/generar_pdf', methods=['GET'])
def generar_pdf():
    # Datos para la plantilla PDF
    pedido_resumen = session.get('pedido_resumen', {})
    nombre_cliente = session.get('nombre_usuario', 'Cliente')
    fecha_pedido = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # O ajusta según tu lógica
    fecha_entrega = pedido_resumen.get('fecha_entrega', 'N/A')
    productos = []

    for item in pedido_resumen.get('productos', []):
        producto = obtener_producto(int(item['id_producto']))
        productos.append({
            'nombre_producto': producto['nombre_producto'],
            'cantidad': item['cantidad'],
            'precio': producto['precio']
        })

    # Renderizar el HTML para PDF
    rendered = render_template('factura.html', nombre_cliente=nombre_cliente,
                               fecha_pedido=fecha_pedido, fecha_entrega=fecha_entrega, productos=productos)
    
    # Generar el PDF
    try:
        pdf = pdfkit.from_string(rendered, False, configuration=config)
        # Guardar el PDF en un archivo para verificar
        with open('factura.pdf', 'wb') as f:
            f.write(pdf)
        print("PDF generado exitosamente.")
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return str(e)
    
    # Enviar el PDF como respuesta
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=factura.pdf'
    return response



# Configuración para ejecutar el servidor
if __name__ == '__main__':
    app.run(port=3000, debug=True)
