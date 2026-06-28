from datetime import datetime
from blueprintapp.app import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(120))
    telefono = db.Column(db.String(30), nullable=False)
    ciudad = db.Column(db.String(80))
    direccion = db.Column(db.String(200))
    referencia = db.Column(db.String(200))
    tipo_cliente = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    observaciones = db.Column(db.Text)
    email = db.Column(db.String(100))

    pedidos = db.relationship("Pedido", backref="cliente", lazy=True)

    def __repr__(self):
        return f"<CLIENTE: {self.nombre_completo}>"
