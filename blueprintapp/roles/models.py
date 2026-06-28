from blueprintapp.app import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)
