from flask import request, render_template, redirect, url_for, Blueprint, flash
from flask_login import login_required
from blueprintapp.app import db
from blueprintapp.proveedores.models import Proveedor

bp_proveedor = Blueprint("bp_proveedor", __name__, template_folder="templates")


@bp_proveedor.route("/")
@login_required
def index():
    proveedores = Proveedor.query.all()
    return render_template("proveedor/index.html", proveedores=proveedores)


@bp_proveedor.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("proveedor/create.html")
    elif request.method == "POST":
        prov = Proveedor(
            nombre_empresa=request.form.get("nombre_empresa"),
            contacto=request.form.get("contacto"),
            telefono=request.form.get("telefono"),
            whatsapp=request.form.get("whatsapp"),
            correo=request.form.get("correo"),
            direccion=request.form.get("direccion"),
            observaciones=request.form.get("observaciones"),
        )
        db.session.add(prov)
        db.session.commit()
        return redirect(url_for("bp_proveedor.index"))


@bp_proveedor.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    proveedor = Proveedor.query.get_or_404(id)
    if request.method == "GET":
        return render_template("proveedor/edit.html", proveedor=proveedor)

    elif request.method == "POST":
        proveedor.nombre_empresa = request.form.get("nombre_empresa")
        proveedor.contacto = request.form.get("contacto")
        proveedor.telefono = request.form.get("telefono")
        proveedor.whatsapp = request.form.get("whatsapp")
        proveedor.correo = request.form.get("correo")
        proveedor.direccion = request.form.get("direccion")
        proveedor.observaciones = request.form.get("observaciones")

        db.session.commit()
        return redirect(url_for("bp_proveedor.index"))


@bp_proveedor.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    prov = Proveedor.query.get_or_404(id)
    if prov.productos:
        flash("No se puede eliminar un proveedor con productos asociados.", "warning")
        return redirect(url_for("bp_proveedor.index"))
    db.session.delete(prov)
    db.session.commit()
    flash("Proveedor eliminado correctamente.", "info")
    return redirect(url_for("bp_proveedor.index"))
