from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import func

from blueprintapp.app import db
from blueprintapp.compras.models import CompraStock
from blueprintapp.productos.models import Producto

bp_compra = Blueprint("bp_compra", __name__, template_folder="templates")


@bp_compra.route("/")
@login_required
def index():
    compras = CompraStock.query.order_by(CompraStock.fecha.desc(), CompraStock.id.desc()).all()
    inversion = db.session.query(
        func.coalesce(func.sum(CompraStock.cantidad * CompraStock.costo_unitario), 0.0)
    ).scalar() or 0.0
    gastos = db.session.query(func.coalesce(func.sum(CompraStock.gasto_compra), 0.0)).scalar() or 0.0
    return render_template("compra/index.html", compras=compras, inversion=inversion, gastos=gastos)


@bp_compra.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        productos = Producto.query.order_by(Producto.nombre).all()
        return render_template("compra/create.html", productos=productos)

    try:
        producto_id = int(request.form.get("producto_id"))
        fecha = datetime.strptime(request.form.get("fecha"), "%Y-%m-%d").date()
        cantidad = int(request.form.get("cantidad"))
        costo_unitario = float(request.form.get("costo_unitario") or 0)
        gasto_compra = float(request.form.get("gasto_compra") or 0)
    except (TypeError, ValueError):
        flash("Complete correctamente los datos de la compra.", "danger")
        return redirect(url_for("bp_compra.create"))

    producto = Producto.query.get_or_404(producto_id)
    compra = CompraStock(
        producto_id=producto_id,
        fecha=fecha,
        factura=request.form.get("factura"),
        cantidad=cantidad,
        costo_unitario=costo_unitario,
        gasto_compra=gasto_compra,
        observaciones=request.form.get("observaciones"),
    )
    producto.stock_actual += cantidad
    producto.precio_compra = costo_unitario
    db.session.add(compra)
    db.session.commit()
    flash("Ingreso de stock registrado correctamente.", "success")
    return redirect(url_for("bp_compra.index"))


@bp_compra.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    compra = CompraStock.query.get_or_404(id)
    if request.method == "GET":
        productos = Producto.query.order_by(Producto.nombre).all()
        return render_template("compra/edit.html", compra=compra, productos=productos)

    producto_anterior = compra.producto
    cantidad_anterior = compra.cantidad
    try:
        producto_id = int(request.form.get("producto_id"))
        fecha = datetime.strptime(request.form.get("fecha"), "%Y-%m-%d").date()
        cantidad = int(request.form.get("cantidad"))
        costo_unitario = float(request.form.get("costo_unitario") or 0)
        gasto_compra = float(request.form.get("gasto_compra") or 0)
    except (TypeError, ValueError):
        flash("Complete correctamente los datos de la compra.", "danger")
        return redirect(url_for("bp_compra.edit", id=id))

    if producto_anterior:
        producto_anterior.stock_actual = max(0, producto_anterior.stock_actual - cantidad_anterior)

    producto_nuevo = Producto.query.get_or_404(producto_id)
    producto_nuevo.stock_actual += cantidad
    producto_nuevo.precio_compra = costo_unitario

    compra.producto_id = producto_id
    compra.fecha = fecha
    compra.factura = request.form.get("factura")
    compra.cantidad = cantidad
    compra.costo_unitario = costo_unitario
    compra.gasto_compra = gasto_compra
    compra.observaciones = request.form.get("observaciones")
    db.session.commit()
    flash("Compra actualizada y stock recalculado.", "success")
    return redirect(url_for("bp_compra.index"))


@bp_compra.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    compra = CompraStock.query.get_or_404(id)
    if compra.producto:
        compra.producto.stock_actual = max(0, compra.producto.stock_actual - compra.cantidad)
    db.session.delete(compra)
    db.session.commit()
    flash("Compra eliminada y stock ajustado.", "info")
    return redirect(url_for("bp_compra.index"))
