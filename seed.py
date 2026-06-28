from blueprintapp.app import create_app
from blueprintapp.extensions import bcrypt, db
from blueprintapp.roles.models import Role
from blueprintapp.usuarios.models import User

app = create_app()

with app.app_context():
    admin_role = Role.query.filter_by(nombre_rol="Administrador").first()
    if not admin_role:
        admin_role = Role(nombre_rol="Administrador")
        db.session.add(admin_role)
        db.session.flush()

    vendedor_role = Role.query.filter_by(nombre_rol="Vendedor").first()
    if not vendedor_role:
        db.session.add(Role(nombre_rol="Vendedor"))

    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", rol_id=admin_role.id)
        admin.password_hash = bcrypt.generate_password_hash("admin123").decode("utf-8")
        db.session.add(admin)
    else:
        admin.rol_id = admin_role.id

    db.session.commit()
    print("Base de datos inicializada. Usuario: admin / Clave: admin123")
