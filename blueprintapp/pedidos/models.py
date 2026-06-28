from datetime import datetime, timezone
from blueprintapp.app import db


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    estado = db.Column(db.String(30), nullable=False, default="Reservado")
    descuento = db.Column(db.Float, default=0.0)
    adelanto = db.Column(db.Float, default=0.0)
    saldo_pendiente = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    observaciones = db.Column(db.Text)

    detalles = db.relationship(
        "DetallePedido", backref="pedido", lazy=True, cascade="all, delete-orphan"
    )
    pagos = db.relationship("Pago", backref="pedido", lazy=True, cascade="all, delete-orphan")
    entregas = db.relationship("Entrega", backref="pedido", lazy=True, cascade="all, delete-orphan")
    envios = db.relationship("Envio", backref="pedido", lazy=True, cascade="all, delete-orphan")

    @property
    def total_pagado(self):
        return round((self.adelanto or 0) + sum(pago.monto for pago in self.pagos), 2)

    @property
    def saldo_actual(self):
        return round(max(0.0, self.total - self.total_pagado), 2)

    @property
    def esta_pagado(self):
        return self.saldo_actual == 0.0

    def __repr__(self):
        return f"<Pedido ID: {self.id} | Cliente ID: {self.cliente_id} | Estado: {self.estado}>"


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedidos"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    descuento_item = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, nullable=False)

    producto = db.relationship("Producto", back_populates="detalles")
