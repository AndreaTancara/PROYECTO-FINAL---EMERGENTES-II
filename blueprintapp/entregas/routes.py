from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from blueprintapp.app import db
from blueprintapp.entregas.models import Entrega
from blueprintapp.pedidos.models import Pedido

bp_entrega = Blueprint("bp_entrega", __name__, template_folder="templates")

ESTADOS_ENTREGA = ["Programada", "Preparando", "En Ruta", "Entregada", "Cancelada"]
LUGARES_RAPIDOS = ["6 de Marzo", "Faro Murillo", "Obelisco", "Paqueteria"]


@bp_entrega.route("/")
@login_required
def index():
    entregas = Entrega.query.order_by(Entrega.fecha_entrega, Entrega.hora).all()
    return render_template("entrega/index.html", entregas=entregas)


@bp_entrega.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        pedidos = Pedido.query.filter(Pedido.estado.notin_(["Cancelado", "Entregado"]))
        pedidos = pedidos.order_by(Pedido.fecha.desc()).all()
        return render_template("entrega/create.html", pedidos=pedidos, lugares=LUGARES_RAPIDOS, estados=ESTADOS_ENTREGA)

    pedido_id = int(request.form.get("pedido_id"))
    try:
        fecha_entrega = datetime.strptime(request.form.get("fecha_entrega"), "%Y-%m-%d").date()
        hora = datetime.strptime(request.form.get("hora"), "%H:%M").time()
    except (TypeError, ValueError):
        flash("La fecha y la hora de entrega no son validas.", "danger")
        return redirect(url_for("bp_entrega.create"))

    pedido = Pedido.query.get_or_404(pedido_id)
    estado = request.form.get("estado") if request.form.get("estado") in ESTADOS_ENTREGA else "Programada"
    entrega = Entrega(
        pedido_id=pedido_id,
        fecha_entrega=fecha_entrega,
        hora=hora,
        lugar=request.form.get("lugar_personalizado") or request.form.get("lugar"),
        responsable=request.form.get("responsable"),
        estado=estado,
        observaciones=request.form.get("observaciones"),
    )
    db.session.add(entrega)
    _sincronizar_estado_pedido(pedido, estado)
    db.session.commit()
    flash("Entrega registrada correctamente", "success")
    return redirect(url_for("bp_entrega.index"))


@bp_entrega.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    entrega = Entrega.query.get_or_404(id)
    if request.method == "GET":
        return render_template("entrega/edit.html", entrega=entrega, lugares=LUGARES_RAPIDOS, estados=ESTADOS_ENTREGA)

    try:
        entrega.fecha_entrega = datetime.strptime(request.form.get("fecha_entrega"), "%Y-%m-%d").date()
        entrega.hora = datetime.strptime(request.form.get("hora"), "%H:%M").time()
    except (TypeError, ValueError):
        flash("La fecha y la hora de entrega no son validas.", "danger")
        return redirect(url_for("bp_entrega.edit", id=id))

    entrega.lugar = request.form.get("lugar_personalizado") or request.form.get("lugar")
    entrega.responsable = request.form.get("responsable")
    entrega.estado = request.form.get("estado") if request.form.get("estado") in ESTADOS_ENTREGA else entrega.estado
    entrega.observaciones = request.form.get("observaciones")
    if entrega.pedido:
        _sincronizar_estado_pedido(entrega.pedido, entrega.estado)
    db.session.commit()
    flash("Entrega actualizada correctamente", "success")
    return redirect(url_for("bp_entrega.index"))


@bp_entrega.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    entrega = Entrega.query.get_or_404(id)
    db.session.delete(entrega)
    db.session.commit()
    flash("Entrega eliminada", "info")
    return redirect(url_for("bp_entrega.index"))


def _sincronizar_estado_pedido(pedido, estado_entrega):
    if estado_entrega == "Entregada":
        pedido.estado = "Entregado"
    elif estado_entrega == "En Ruta":
        pedido.estado = "En Ruta"
    elif pedido.estado not in ["Cancelado", "Entregado"]:
        pedido.estado = "Preparando"
