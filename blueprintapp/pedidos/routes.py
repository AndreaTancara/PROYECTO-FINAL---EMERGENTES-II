from flask import flash, request, render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from blueprintapp.app import db
from blueprintapp.pedidos.models import DetallePedido, Pedido
from blueprintapp.clientes.models import Cliente
from datetime import datetime, timezone

from blueprintapp.productos.models import Producto

bp_pedido = Blueprint("bp_pedido", __name__, template_folder="templates")

ESTADOS_PEDIDO = [
    "Reservado",
    "Confirmado",
    "Pagado",
    "Preparando",
    "En Ruta",
    "Entregado",
    "Cancelado",
]


@bp_pedido.route("/")
@login_required
def index():
    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template("pedido/index.html", pedidos=pedidos)


@bp_pedido.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        clientes = Cliente.query.all()
        productos = Producto.query.filter(Producto.stock_actual > 0).all()
        return render_template(
            "pedido/create.html",
            clientes=clientes,
            productos=productos,
            estados=ESTADOS_PEDIDO,
        )

    try:
        cliente_id = int(request.form.get("cliente_id"))
        adelanto = float(request.form.get("adelanto") or 0)
        estado = request.form.get("estado") if request.form.get("estado") in ESTADOS_PEDIDO else "Reservado"
        observaciones = request.form.get("observaciones")
    except (TypeError, ValueError):
        flash("Por favor complete los datos básicos del pedido.", "danger")
        return redirect(url_for("bp_pedido.create"))

    producto_ids = request.form.getlist("producto_id")
    cantidades = request.form.getlist("cantidad")
    precios = request.form.getlist("precio_venta")
    descuentos = request.form.getlist("descuento_item")

    line_items = []
    total = 0.0
    descuento_total = 0.0

    for idx, producto_id in enumerate(producto_ids):
        if not producto_id:
            continue

        try:
            cantidad = int(cantidades[idx])
            precio_venta = float(precios[idx])
            descuento_item = float(descuentos[idx] or 0)
        except (IndexError, TypeError, ValueError):
            continue

        if cantidad <= 0 or precio_venta < 0:
            continue

        producto = Producto.query.get(producto_id)
        if not producto:
            flash(f"Producto inválido en la línea {idx + 1}.", "danger")
            return redirect(url_for("bp_pedido.create"))

        if producto.stock_actual < cantidad:
            flash(f"Stock insuficiente para {producto.nombre}.", "danger")
            return redirect(url_for("bp_pedido.create"))

        subtotal = round(precio_venta * cantidad - descuento_item, 2)
        if subtotal < 0:
            subtotal = 0.0

        line_items.append({
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": precio_venta,
            "descuento_item": descuento_item,
            "subtotal": subtotal,
        })
        total += subtotal
        descuento_total += descuento_item

    if not line_items:
        flash("Debe agregar al menos un producto válido al pedido.", "danger")
        return redirect(url_for("bp_pedido.create"))

    total = round(total, 2)
    descuento_total = round(descuento_total, 2)

    if adelanto > total:
        flash("El adelanto no puede ser mayor al total.", "danger")
        return redirect(url_for("bp_pedido.create"))

    saldo_pendiente = round(total - adelanto, 2)
    if saldo_pendiente == 0:
        estado = "Pagado"

    try:
        nuevo_pedido = Pedido(
            cliente_id=cliente_id,
            usuario_id=current_user.id,
            estado=estado,
            descuento=descuento_total,
            adelanto=adelanto,
            saldo_pendiente=saldo_pendiente,
            total=total,
            observaciones=observaciones,
        )
        db.session.add(nuevo_pedido)
        db.session.flush()

        for item in line_items:
            detalle = DetallePedido(
                pedido_id=nuevo_pedido.id,
                producto_id=item["producto"].id,
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                descuento_item=item["descuento_item"],
                subtotal=item["subtotal"],
            )
            db.session.add(detalle)
            item["producto"].stock_actual -= item["cantidad"]

        db.session.commit()
        flash("Pedido registrado con éxito", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al registrar: " + str(e), "danger")

    return redirect(url_for("bp_pedido.index"))


@bp_pedido.route("/view/<int:id>")
@login_required
def view(id):
    pedido = Pedido.query.get_or_404(id)
    return render_template("pedido/view.html", pedido=pedido)


@bp_pedido.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    pedido = Pedido.query.get_or_404(id)
    if request.method == "GET":
        return render_template(
            "pedido/edit.html",
            pedido=pedido,
            estados=ESTADOS_PEDIDO,
            clientes=Cliente.query.order_by(Cliente.nombre_completo).all(),
            productos=Producto.query.order_by(Producto.nombre).all(),
        )

    try:
        cliente_id = int(request.form.get("cliente_id"))
        adelanto = float(request.form.get("adelanto") or 0)
        estado = request.form.get("estado") if request.form.get("estado") in ESTADOS_PEDIDO else pedido.estado
    except (TypeError, ValueError):
        flash("Complete correctamente los datos del pedido.", "danger")
        return redirect(url_for("bp_pedido.edit", id=id))

    producto_ids = request.form.getlist("producto_id")
    cantidades = request.form.getlist("cantidad")
    precios = request.form.getlist("precio_venta")
    descuentos = request.form.getlist("descuento_item")

    for detalle in pedido.detalles:
        if detalle.producto:
            detalle.producto.stock_actual += detalle.cantidad

    line_items = []
    total = 0.0
    descuento_total = 0.0

    for idx, producto_id in enumerate(producto_ids):
        if not producto_id:
            continue
        try:
            cantidad = int(cantidades[idx])
            precio_venta = float(precios[idx])
            descuento_item = float(descuentos[idx] or 0)
        except (IndexError, TypeError, ValueError):
            continue
        if cantidad <= 0 or precio_venta < 0:
            continue
        producto = Producto.query.get(producto_id)
        if not producto:
            continue
        if producto.stock_actual < cantidad:
            db.session.rollback()
            flash(f"Stock insuficiente para {producto.nombre}.", "danger")
            return redirect(url_for("bp_pedido.edit", id=id))
        subtotal = max(0.0, round(precio_venta * cantidad - descuento_item, 2))
        line_items.append((producto, cantidad, precio_venta, descuento_item, subtotal))
        total += subtotal
        descuento_total += descuento_item

    if not line_items:
        db.session.rollback()
        flash("Debe mantener al menos un producto en el pedido.", "danger")
        return redirect(url_for("bp_pedido.edit", id=id))

    total = round(total, 2)
    if adelanto > total:
        db.session.rollback()
        flash("El adelanto no puede ser mayor al total.", "danger")
        return redirect(url_for("bp_pedido.edit", id=id))

    DetallePedido.query.filter_by(pedido_id=pedido.id).delete()
    pedido.cliente_id = cliente_id
    pedido.estado = estado
    pedido.observaciones = request.form.get("observaciones")
    pedido.descuento = round(descuento_total, 2)
    pedido.adelanto = adelanto
    pedido.total = total
    pedido.saldo_pendiente = round(total - adelanto, 2)
    if pedido.saldo_pendiente == 0:
        pedido.estado = "Pagado"

    for producto, cantidad, precio_venta, descuento_item, subtotal in line_items:
        db.session.add(
            DetallePedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=precio_venta,
                descuento_item=descuento_item,
                subtotal=subtotal,
            )
        )
        producto.stock_actual -= cantidad

    db.session.commit()
    flash("Pedido actualizado correctamente", "success")
    return redirect(url_for("bp_pedido.view", id=id))


@bp_pedido.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    pedido = Pedido.query.get_or_404(id)
    for detalle in pedido.detalles:
        if detalle.producto:
            detalle.producto.stock_actual += detalle.cantidad
    db.session.delete(pedido)
    db.session.commit()
    return redirect(url_for("bp_pedido.index"))
