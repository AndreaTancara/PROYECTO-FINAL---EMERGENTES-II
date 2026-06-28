from datetime import datetime

from blueprintapp.app import db


class Gasto(db.Model):
    __tablename__ = "gastos"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    descripcion = db.Column(db.String(220), nullable=False)
    monto = db.Column(db.Float, nullable=False, default=0.0)
    tipo = db.Column(db.String(80), nullable=False, default="Repartidor")

    usuario = db.relationship("User", backref="gastos")
