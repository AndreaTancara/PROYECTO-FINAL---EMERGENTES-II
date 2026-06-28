from blueprintapp.app import db


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    codigo_interno = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    marca = db.Column(db.String(80))
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False)
    precio = db.Column(db.Float, nullable=False, default=0.0)
    precio_compra = db.Column(db.Float, nullable=False, default=0.0)
    precio_normal = db.Column(db.Float, nullable=False, default=0.0)
    precio_live = db.Column(db.Float, nullable=False, default=0.0)
    stock_actual = db.Column(db.Integer, default=0, nullable=False)
    stock_minimo = db.Column(db.Integer, default=0, nullable=False)
    imagen = db.Column(db.String(200))
    estado = db.Column(db.String(30), nullable=False, default="Activo")

    detalles = db.relationship("DetallePedido", back_populates="producto")
    compras = db.relationship("CompraStock", back_populates="producto", lazy=True)

    def __repr__(self):
        return f"<PRODUCTO: {self.nombre} - Stock: {self.stock_actual}>"
