from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from blueprintapp.app import db
from blueprintapp.pedidos.models import Pedido
from blueprintapp.pagos.models import Pago

bp_pago = Blueprint("bp_pago", __name__, template_folder="templates")


@bp_pago.route("/")
@login_required
def index():
    pagos = Pago.query.order_by(Pago.fecha.desc()).all()
    return render_template("pago/index.html", pagos=pagos)


@bp_pago.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        pedidos = Pedido.query.filter(Pedido.saldo_pendiente > 0).order_by(Pedido.fecha.desc()).all()
        return render_template("pago/create.html", pedidos=pedidos)

    try:
        pedido_id = int(request.form.get("pedido_id"))
        monto = float(request.form.get("monto"))
    except (TypeError, ValueError):
        flash("Complete correctamente los datos del pago.", "danger")
        return redirect(url_for("bp_pago.create"))
    metodo = request.form.get("metodo")

    pedido = Pedido.query.get_or_404(pedido_id)
    if monto <= 0:
        flash("El monto debe ser mayor a cero.", "danger")
        return redirect(url_for("bp_pago.create"))
    if monto > pedido.saldo_pendiente:
        flash("El pago no puede ser mayor al saldo pendiente.", "danger")
        return redirect(url_for("bp_pago.create"))

    pago = Pago(pedido_id=pedido_id, monto=monto, metodo=metodo)
    db.session.add(pago)

    pedido.saldo_pendiente = round(max(0.0, pedido.saldo_pendiente - monto), 2)
    if pedido.saldo_pendiente <= 0:
        pedido.saldo_pendiente = 0.0
        pedido.estado = "Pagado"
    elif pedido.estado == "Reservado":
        pedido.estado = "Confirmado"

    db.session.commit()
    flash("Pago registrado correctamente", "success")
    return redirect(url_for("bp_pago.index"))


@bp_pago.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    pago = Pago.query.get_or_404(id)
    pedido = pago.pedido
    if pedido:
        pedido.saldo_pendiente = round(pedido.saldo_pendiente + pago.monto, 2)
        if pedido.estado == "Pagado" and pedido.saldo_pendiente > 0:
            pedido.estado = "Confirmado"
    db.session.delete(pago)
    db.session.commit()
    flash("Pago eliminado", "info")
    return redirect(url_for("bp_pago.index"))
