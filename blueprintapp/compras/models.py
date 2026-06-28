from datetime import datetime

from blueprintapp.app import db


class CompraStock(db.Model):
    __tablename__ = "compras_stock"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    factura = db.Column(db.String(80), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.Float, nullable=False, default=0.0)
    gasto_compra = db.Column(db.Float, nullable=False, default=0.0)
    observaciones = db.Column(db.Text)

    producto = db.relationship("Producto", back_populates="compras")

    @property
    def total_compra(self):
        return round((self.cantidad * self.costo_unitario) + self.gasto_compra, 2)
