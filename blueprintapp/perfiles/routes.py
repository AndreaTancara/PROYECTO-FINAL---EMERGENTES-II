from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

# Importamos bcrypt desde tu app
from blueprintapp.app import db, bcrypt
from blueprintapp.pedidos.models import Pedido

bp_perfil = Blueprint("bp_perfil", __name__, template_folder="templates")


@bp_perfil.route("/perfil")
@login_required
def ver_perfil():
    # Asumiendo que en tu modelo Pedido tienes la relación o el campo usuario_id
    mis_pedidos = Pedido.query.filter_by(usuario_id=current_user.id).all()
    return render_template("perfil/perfil.html", pedidos=mis_pedidos)


@bp_perfil.route("/perfil/cambiar-password", methods=["POST"])
@login_required
def cambiar_password():
    current_pw = request.form.get("current_pw")
    new_pw = request.form.get("new_pw")

    # Validación con bcrypt: comparamos el hash almacenado con la contraseña ingresada
    if not bcrypt.check_password_hash(current_user.password_hash, current_pw):
        flash("La contraseña actual es incorrecta.", "danger")
        return redirect(url_for("bp_perfil.ver_perfil"))

    # Generamos el nuevo hash usando bcrypt
    # Nota: .decode('utf-8') es importante para convertir el resultado a string
    current_user.password_hash = bcrypt.generate_password_hash(new_pw).decode("utf-8")

    db.session.commit()
    flash("Contraseña actualizada correctamente.", "success")
    return redirect(url_for("bp_perfil.ver_perfil"))
