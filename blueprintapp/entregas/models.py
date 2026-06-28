from datetime import date, time
from blueprintapp.app import db

class Entrega(db.Model):
    __tablename__ = "entregas"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    lugar = db.Column(db.String(120), nullable=False)
    responsable = db.Column(db.String(120))
    estado = db.Column(db.String(40), nullable=False, default="Programada")
    observaciones = db.Column(db.Text)

    def __repr__(self):
        return f"<Entrega {self.id} - Pedido {self.pedido_id} - {self.fecha_entrega} {self.hora}>"
