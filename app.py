from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('base_datos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            telefono TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_correo TEXT,
            partido TEXT NOT NULL,
            fecha TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            FOREIGN KEY (cliente_correo) REFERENCES clientes(correo)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# Formulario para agregar cliente
@app.route('/agregar_cliente', methods=['GET', 'POST'])
def agregar_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        conn = sqlite3.connect('base_datos.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre, correo, telefono) VALUES (?, ?, ?)", 
                       (nombre, correo, telefono))
        conn.commit()
        conn.close()
        # Redirige a reservas con el correo como parámetro GET
        return redirect(url_for('agregar_reserva', correo=correo))
    return render_template('clientes.html')  

# Ver lista de clientes
@app.route('/clientes')
def ver_clientes():
    conn = sqlite3.connect('base_datos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, correo, telefono FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return render_template('ver_clientes.html', clientes=clientes)

# Eliminar cliente
@app.route('/eliminar_cliente/<string:correo>')
def eliminar_cliente(correo):
    conn = sqlite3.connect('base_datos.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE cliente_correo = ?", (correo,))
    cursor.execute("DELETE FROM clientes WHERE correo = ?", (correo,))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_clientes'))

# Formulario para agregar reserva
@app.route('/agregar_reserva', methods=['GET', 'POST'])
def agregar_reserva():
    if request.method == 'POST':
        correo = request.form['correo']
        partido = request.form['partido']
        fecha = request.form['fecha']
        cantidad = request.form['cantidad']
        # No guardes aún en la base de datos, primero confirma
        return render_template('confirmar_reserva.html', correo=correo, partido=partido, fecha=fecha, cantidad=cantidad)
    return render_template('reservas.html')

@app.route('/confirmar_reserva', methods=['POST'])
def confirmar_reserva():
    correo = request.form['correo']
    partido = request.form['partido']
    fecha = request.form['fecha']
    cantidad = request.form['cantidad']
    # Aquí sí guardas en la base de datos
    conn = sqlite3.connect('base_datos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reservas (cliente_correo, partido, fecha, cantidad) VALUES (?, ?, ?, ?)", 
                   (correo, partido, fecha, cantidad))
    conn.commit()
    conn.close()
    # Aquí puedes redirigir a una página de pago o de éxito
    return render_template('pago.html', correo=correo, partido=partido, fecha=fecha, cantidad=cantidad)

# Ver lista de reservas
@app.route('/reservas')
def ver_reservas():
    conn = sqlite3.connect('base_datos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, cliente_correo, partido, fecha, cantidad FROM reservas")
    reservas = cursor.fetchall()
    conn.close()
    return render_template('ver_reservas.html', reservas=reservas)

# Eliminar reserva
@app.route('/eliminar_reserva/<int:reserva_id>')
def eliminar_reserva(reserva_id):
    conn = sqlite3.connect('base_datos.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_reservas'))
@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

if __name__ == '__main__':
    app.run(debug=True)