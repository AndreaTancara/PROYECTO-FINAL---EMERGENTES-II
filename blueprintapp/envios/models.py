from blueprintapp.app import db

class Envio(db.Model):
    __tablename__ = "envios"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    cliente_nombre = db.Column(db.String(120))
    telefono = db.Column(db.String(30))
    empresa_transporte = db.Column(db.String(120))
    numero_guia = db.Column(db.String(80))
    ciudad_destino = db.Column(db.String(120))
    estado_envio = db.Column(db.String(80), default="Pendiente")

    def __repr__(self):
        return f"<Envio {self.id} - Pedido {self.pedido_id} - {self.estado_envio}>"
