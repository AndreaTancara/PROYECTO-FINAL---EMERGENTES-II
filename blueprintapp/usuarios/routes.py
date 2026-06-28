from flask import flash, redirect, render_template, Blueprint, request, url_for
from flask_login import login_required
from sqlalchemy import func
from blueprintapp.app import bcrypt
from blueprintapp.decorators import admin_required
from blueprintapp.roles.models import Role
from blueprintapp.usuarios.models import User
from blueprintapp.productos.models import Producto
from blueprintapp.clientes.models import Cliente
from blueprintapp.pedidos.models import Pedido
from blueprintapp.categorias.models import Categoria
from blueprintapp.extensions import db
from werkzeug.security import (
    generate_password_hash,
)  # Importa esto arriba en tu archivo

# Usamos 'bp_usuario' como el nombre del blueprint
bp_usuario = Blueprint("bp_usuario", __name__, template_folder="templates")


# La ruta '/' cargará el dashboard directamente al iniciar sesión
@bp_usuario.route("/")
@admin_required
@login_required
def index():
    # Realizamos la consulta de ventas aquí para mostrarla en el dashboard
    suma_ventas = db.session.query(func.sum(Pedido.total)).scalar() or 0.0
    return render_template(
        "usuario/index.html",  # Ubicación del archivo en blueprintapp/usuarios/templates/usuario/index.html
        usuarios=User.query.all(),
        total_usuarios=User.query.count(),
        total_cat=Categoria.query.count(),
        total_prod=Producto.query.count(),
        total_clientes=Cliente.query.count(),
        total_pedidos=Pedido.query.count(),
        total_ventas=suma_ventas,
    )


@bp_usuario.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        rol_id = request.form.get("rol_id")

        if User.query.filter_by(username=username).first():
            flash("El nombre de usuario ya existe", "danger")
            return redirect(url_for("bp_usuario.create"))

        # --- CORRECCIÓN AQUÍ ---
        # Usamos bcrypt, generamos el hash y lo decodificamos a string
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        nuevo_usuario = User(
            username=username, password_hash=hashed_password, rol_id=rol_id
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Usuario creado exitosamente por el administrador", "success")
        return redirect(url_for("bp_usuario.index"))

    roles = Role.query.all()
    return render_template("usuario/create.html", roles=roles)


# Aquí irán tus rutas de edición de usuarios (ej. @bp_usuario.route("/edit/<int:id>")...)
@bp_usuario.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit(id):
    usuario = User.query.get_or_404(id)
    if request.method == "POST":
        usuario.username = request.form.get("username")
        usuario.rol_id = request.form.get("rol_id")  # Asignamos el nuevo rol

        nueva_password = request.form.get("password")
        if nueva_password:  # Solo si el usuario escribió algo
            usuario.set_password(nueva_password)

        db.session.commit()
        flash("Usuario actualizado exitosamente", "success")
        return redirect(url_for("bp_usuario.index"))

    # IMPORTANTE: Debes enviar los roles para que el <select> funcione
    roles = Role.query.all()
    return render_template("usuario/edit.html", usuario=usuario, roles=roles)


# --- RUTA PARA ELIMINAR USUARIO ---
@bp_usuario.route("/delete/<int:id>", methods=["POST"])
@admin_required
@login_required
def delete(id):
    usuario = User.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado correctamente", "danger")
    return redirect(url_for("bp_usuario.index"))
