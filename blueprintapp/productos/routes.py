from flask import request, render_template, redirect, url_for, Blueprint, flash
from flask_login import login_required
from blueprintapp.app import db
from blueprintapp.productos.models import Producto
from blueprintapp.categorias.models import Categoria
from blueprintapp.proveedores.models import Proveedor

bp_producto = Blueprint("bp_producto", __name__, template_folder="templates")


@bp_producto.route("/")
@login_required
def index():
    productos = Producto.query.order_by(Producto.nombre).all()
    return render_template("producto/index.html", productos=productos)


@bp_producto.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        categorias = Categoria.query.all()
        proveedores = Proveedor.query.all()
        return render_template(
            "producto/create.html", categorias=categorias, proveedores=proveedores
        )
    elif request.method == "POST":
        producto = Producto(
            codigo_interno=request.form.get("codigo_interno"),
            nombre=request.form.get("nombre"),
            marca=request.form.get("marca"),
            descripcion=request.form.get("descripcion"),
            precio=float(request.form.get("precio_normal") or 0),
            precio_compra=float(request.form.get("precio_compra")),
            precio_normal=float(request.form.get("precio_normal")),
            precio_live=float(request.form.get("precio_live")),
            stock_actual=int(request.form.get("stock_actual")),
            stock_minimo=int(request.form.get("stock_minimo")),
            categoria_id=int(request.form.get("categoria_id")),
            proveedor_id=int(request.form.get("proveedor_id")),
            imagen=request.form.get("imagen"),
            estado=request.form.get("estado"),
        )
        db.session.add(producto)
        db.session.commit()
        flash("Producto registrado correctamente", "success")
        return redirect(url_for("bp_producto.index"))


@bp_producto.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    producto = Producto.query.get_or_404(id)
    if request.method == "GET":
        categorias = Categoria.query.all()
        proveedores = Proveedor.query.all()
        return render_template(
            "producto/edit.html",
            producto=producto,
            categorias=categorias,
            proveedores=proveedores,
        )

    elif request.method == "POST":
        producto.codigo_interno = request.form.get("codigo_interno")
        producto.nombre = request.form.get("nombre")
        producto.marca = request.form.get("marca")
        producto.descripcion = request.form.get("descripcion")
        producto.precio = float(request.form.get("precio_normal") or 0)
        producto.precio_compra = float(request.form.get("precio_compra"))
        producto.precio_normal = float(request.form.get("precio_normal"))
        producto.precio_live = float(request.form.get("precio_live"))
        producto.stock_actual = int(request.form.get("stock_actual"))
        producto.stock_minimo = int(request.form.get("stock_minimo"))
        producto.categoria_id = int(request.form.get("categoria_id"))
        producto.proveedor_id = int(request.form.get("proveedor_id"))
        producto.imagen = request.form.get("imagen")
        producto.estado = request.form.get("estado")

        db.session.commit()
        flash("Producto actualizado correctamente", "success")
        return redirect(url_for("bp_producto.index"))


@bp_producto.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    producto = Producto.query.get_or_404(id)
    if producto.detalles or producto.compras:
        producto.estado = "Inactivo"
        flash("El producto ya tiene movimientos. Se marco como Inactivo para conservar el historial.", "warning")
        db.session.commit()
        return redirect(url_for("bp_producto.index"))
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado correctamente.", "info")
    return redirect(url_for("bp_producto.index"))
