from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from blueprintapp.extensions import db, bcrypt
from blueprintapp.auth import auth_bp
from blueprintapp.usuarios.models import User
from blueprintapp.roles.models import Role


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        # VERIFICACIÓN CON BCRYPT (Debe coincidir con cómo se registró)
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash("¡Bienvenido al sistema!", "success")
            return redirect(url_for("main_bp.index"))

        flash("Nombre de usuario o contraseña incorrectos", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))
