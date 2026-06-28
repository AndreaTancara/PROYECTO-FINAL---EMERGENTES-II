from flask import request, render_template, redirect, url_for, Blueprint, flash
from blueprintapp.app import db
from blueprintapp.decorators import admin_required
from blueprintapp.roles.models import Role  # Importa tu modelo Role que creamos antes
from flask_login import login_required

# from blueprintapp.decorators import admin_required # Descomenta esto cuando lo tengas listo

bp_role = Blueprint("bp_role", __name__, template_folder="templates")


@bp_role.route("/")
@login_required
@admin_required
def index():
    roles = Role.query.all()
    return render_template("rol/index.html", roles=roles)


@bp_role.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    if request.method == "GET":
        return render_template("rol/create.html")

    elif request.method == "POST":
        nuevo_rol = Role(nombre_rol=request.form.get("nombre_rol"))
        db.session.add(nuevo_rol)
        db.session.commit()
        return redirect(url_for("bp_role.index"))


@bp_role.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required  # <--- ESTO ES LO QUE REALMENTE PROTEGE TU SISTEMA
# @admin_required
def edit(id):
    rol = Role.query.get_or_404(id)
    if request.method == "GET":
        return render_template("rol/edit.html", rol=rol)

    elif request.method == "POST":
        rol.nombre_rol = request.form.get("nombre_rol")
        db.session.commit()
        return redirect(url_for("bp_role.index"))


@bp_role.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete(id):
    rol = Role.query.get_or_404(id)
    if rol.usuarios:
        flash("No se puede eliminar un rol con usuarios asignados.", "warning")
        return redirect(url_for("bp_role.index"))
    db.session.delete(rol)
    db.session.commit()
    return redirect(url_for("bp_role.index"))
