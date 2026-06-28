from blueprintapp.app import db


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(120), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(30))
    whatsapp = db.Column(db.String(30))
    correo = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    observaciones = db.Column(db.Text)

    productos = db.relationship("Producto", backref="proveedor", lazy=True)

    def __repr__(self):
        return f"<PROVEEDOR: {self.nombre_empresa}>"
