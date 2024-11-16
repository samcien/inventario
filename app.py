from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql

# Instalar PyMySQL como MySQLdb
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:AKyrBPvsEBisWlYuXzKJLveoICTXTvMO@junction.proxy.rlwy.net:48189/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Definición de modelos (usuarios, articulos, inventario, transacciones)

class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.Enum('Cajero', 'Gerente'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Articulo(db.Model):
    id_articulo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

class Inventario(db.Model):
    id_inventario = db.Column(db.Integer, primary_key=True)
    id_articulo = db.Column(db.Integer, db.ForeignKey('articulo.id_articulo'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    ultima_actualizacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    articulo = db.relationship('Articulo', backref=db.backref('inventario', lazy=True))

class Transaccion(db.Model):
    id_transaccion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_articulo = db.Column(db.Integer, db.ForeignKey('articulo.id_articulo'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

    usuario = db.relationship('Usuario', backref=db.backref('transacciones', lazy=True))
    articulo = db.relationship('Articulo', backref=db.backref('transacciones', lazy=True))

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# Rutas de la API

#ruta raiz
@app.route('/')
def home():
    return jsonify({'message': '¡El servidor está funcionando correctamente!'})


# Crear un usuario
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    nuevo_usuario = Usuario(nombre=data['nombre'], rol=data['rol'], email=data['email'], password=data['password'])
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({'message': 'Usuario creado exitosamente'}), 201

# Obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{'id_usuario': u.id_usuario, 'nombre': u.nombre, 'rol': u.rol, 'email': u.email} for u in usuarios])

# Crear un artículo
@app.route('/articulos', methods=['POST'])
def crear_articulo():
    data = request.get_json()
    nuevo_articulo = Articulo(nombre=data['nombre'], descripcion=data.get('descripcion'), precio=data['precio'])
    db.session.add(nuevo_articulo)
    db.session.commit()
    return jsonify({'message': 'Artículo creado exitosamente'}), 201

# Obtener todos los artículos
@app.route('/articulos', methods=['GET'])
def obtener_articulos():
    articulos = Articulo.query.all()
    return jsonify([{'id_articulo': a.id_articulo, 'nombre': a.nombre, 'descripcion': a.descripcion, 'precio': str(a.precio)} for a in articulos])

# Crear una transacción
@app.route('/transacciones', methods=['POST'])
def crear_transaccion():
    data = request.get_json()
    articulo = Articulo.query.get(data['id_articulo'])
    if not articulo:
        return jsonify({'message': 'Artículo no encontrado'}), 404
    usuario = Usuario.query.get(data['id_usuario'])
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    total = articulo.precio * data['cantidad']
    nueva_transaccion = Transaccion(id_usuario=data['id_usuario'], id_articulo=data['id_articulo'], cantidad=data['cantidad'], total=total)
    db.session.add(nueva_transaccion)
    db.session.commit()
    return jsonify({'message': 'Transacción creada exitosamente'}), 201

# Obtener todas las transacciones
@app.route('/transacciones', methods=['GET'])
def obtener_transacciones():
    transacciones = Transaccion.query.all()
    return jsonify([{
        'id_transaccion': t.id_transaccion,
        'usuario': t.usuario.nombre,
        'articulo': t.articulo.nombre,
        'cantidad': t.cantidad,
        'total': str(t.total),
        'fecha': t.fecha
    } for t in transacciones])

# Actualizar un artículo
@app.route('/articulos/<int:id>', methods=['PUT'])
def actualizar_articulo(id):
    articulo = Articulo.query.get(id)
    if not articulo:
        return jsonify({'message': 'Artículo no encontrado'}), 404
    data = request.get_json()
    articulo.nombre = data['nombre']
    articulo.descripcion = data.get('descripcion', articulo.descripcion)
    articulo.precio = data['precio']
    db.session.commit()
    return jsonify({'message': 'Artículo actualizado exitosamente'}), 200

# Eliminar un artículo
@app.route('/articulos/<int:id>', methods=['DELETE'])
def eliminar_articulo(id):
    articulo = Articulo.query.get(id)
    if not articulo:
        return jsonify({'message': 'Artículo no encontrado'}), 404
    db.session.delete(articulo)
    db.session.commit()
    return jsonify({'message': 'Artículo eliminado exitosamente'}), 200

if __name__ == "__main__":
    app.run(debug=True)
