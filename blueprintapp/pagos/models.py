from datetime import datetime
from blueprintapp.app import db

class Pago(db.Model):
    __tablename__ = "pagos"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"<Pago {self.id} - Pedido {self.pedido_id} - {self.monto}>"
