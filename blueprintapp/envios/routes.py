from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from blueprintapp.app import db
from blueprintapp.envios.models import Envio
from blueprintapp.pedidos.models import Pedido

bp_envio = Blueprint("bp_envio", __name__, template_folder="templates")
ESTADOS_ENVIO = ["Pendiente", "En transito", "Entregado", "Devuelto"]


@bp_envio.route("/")
@login_required
def index():
    envios = Envio.query.order_by(Envio.id.desc()).all()
    return render_template("envio/index.html", envios=envios)


@bp_envio.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        pedidos = Pedido.query.filter(Pedido.estado.notin_(["Cancelado", "Entregado"]))
        pedidos = pedidos.order_by(Pedido.fecha.desc()).all()
        return render_template("envio/create.html", pedidos=pedidos, estados=ESTADOS_ENVIO)

    pedido_id = int(request.form.get("pedido_id"))
    pedido = Pedido.query.get_or_404(pedido_id)
    envio = _llenar_envio(Envio(pedido_id=pedido_id), pedido)
    db.session.add(envio)
    _sincronizar_pedido(pedido, envio.estado_envio)
    db.session.commit()
    flash("Envio registrado correctamente", "success")
    return redirect(url_for("bp_envio.index"))


@bp_envio.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    envio = Envio.query.get_or_404(id)
    if request.method == "GET":
        return render_template("envio/edit.html", envio=envio, estados=ESTADOS_ENVIO)

    _llenar_envio(envio, envio.pedido)
    if envio.pedido:
        _sincronizar_pedido(envio.pedido, envio.estado_envio)
    db.session.commit()
    flash("Envio actualizado correctamente", "success")
    return redirect(url_for("bp_envio.index"))


@bp_envio.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    envio = Envio.query.get_or_404(id)
    db.session.delete(envio)
    db.session.commit()
    flash("Envio eliminado", "info")
    return redirect(url_for("bp_envio.index"))


def _llenar_envio(envio, pedido=None):
    envio.cliente_nombre = request.form.get("cliente_nombre")
    envio.telefono = request.form.get("telefono")
    envio.empresa_transporte = request.form.get("empresa_transporte")
    envio.numero_guia = request.form.get("numero_guia")
    envio.ciudad_destino = request.form.get("ciudad_destino")
    envio.estado_envio = request.form.get("estado_envio") if request.form.get("estado_envio") in ESTADOS_ENVIO else "Pendiente"
    if pedido and pedido.cliente:
        envio.cliente_nombre = envio.cliente_nombre or pedido.cliente.nombre_completo
        envio.telefono = envio.telefono or pedido.cliente.telefono
        envio.ciudad_destino = envio.ciudad_destino or pedido.cliente.ciudad
    return envio


def _sincronizar_pedido(pedido, estado_envio):
    if estado_envio == "Entregado":
        pedido.estado = "Entregado"
    elif pedido.estado not in ["Cancelado", "Entregado"]:
        pedido.estado = "En Ruta"
