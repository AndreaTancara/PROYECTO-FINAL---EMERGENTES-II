from flask import request, render_template, redirect, url_for, Blueprint, flash
from flask_login import login_required
from blueprintapp.app import db
from blueprintapp.clientes.models import Cliente

bp_cliente = Blueprint("bp_cliente", __name__, template_folder="templates")


@bp_cliente.route("/")
@login_required
def index():
    clientes = Cliente.query.order_by(Cliente.nombre_completo).all()
    return render_template("cliente/index.html", clientes=clientes)


@bp_cliente.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("cliente/create.html")
    elif request.method == "POST":
        cliente = Cliente(
            nombre_completo=request.form.get("nombre"),
            telefono=request.form.get("telefono"),
            ciudad=request.form.get("ciudad"),
            direccion=request.form.get("direccion"),
            referencia=request.form.get("referencia"),
            tipo_cliente=request.form.get("tipo_cliente"),
            observaciones=request.form.get("observaciones"),
            email=request.form.get("email"),
        )
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente registrado correctamente", "success")
        return redirect(url_for("bp_cliente.index"))


@bp_cliente.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == "GET":
        return render_template("cliente/edit.html", cliente=cliente)
    elif request.method == "POST":
        cliente.nombre_completo = request.form.get("nombre")
        cliente.telefono = request.form.get("telefono")
        cliente.ciudad = request.form.get("ciudad")
        cliente.direccion = request.form.get("direccion")
        cliente.referencia = request.form.get("referencia")
        cliente.tipo_cliente = request.form.get("tipo_cliente")
        cliente.observaciones = request.form.get("observaciones")
        cliente.email = request.form.get("email")
        db.session.commit()
        flash("Cliente actualizado correctamente", "success")
        return redirect(url_for("bp_cliente.index"))


@bp_cliente.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    cliente = Cliente.query.get_or_404(id)
    if cliente.pedidos:
        flash("No se puede eliminar un cliente con pedidos. Conserva el historial de ventas.", "warning")
        return redirect(url_for("bp_cliente.index"))
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado correctamente", "info")
    return redirect(url_for("bp_cliente.index"))
