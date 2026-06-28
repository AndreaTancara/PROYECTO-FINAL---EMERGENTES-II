# Librerias a usar en el modulo
from flask import request, render_template, redirect, url_for, Blueprint, flash
from flask_login import login_required

# Referencia a la base de datos
from blueprintapp.app import db

# Modelos con los que interactura el modulo
from blueprintapp.categorias.models import Categoria

bp_categoria = Blueprint("bp_categoria", __name__, template_folder="templates")


@bp_categoria.route("/")
@login_required
def index():
    categorias = Categoria.query.all()
    return render_template("categoria/index.html", categorias=categorias)


@bp_categoria.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("categoria/create.html")
    elif request.method == "POST":
        nombre = request.form.get("nombre")
        # Solo guardamos nombre
        categoria = Categoria(nombre=nombre)
        db.session.add(categoria)
        db.session.commit()
        return redirect(url_for("bp_categoria.index"))


@bp_categoria.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method == "GET":
        return render_template("categoria/edit.html", categoria=categoria)
    elif request.method == "POST":
        categoria.nombre = request.form.get("nombre")
        db.session.commit()
        return redirect(url_for("bp_categoria.index"))


# --- OPERACIÓN ELIMINAR ---
@bp_categoria.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.productos:
        flash("No se puede eliminar un catalogo con productos asociados.", "warning")
        return redirect(url_for("bp_categoria.index"))
    db.session.delete(categoria)  # Eliminamos el registro
    db.session.commit()
    flash("Catalogo eliminado correctamente.", "info")
    return redirect(url_for("bp_categoria.index"))
