from datetime import date, datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from blueprintapp.app import db
from blueprintapp.gastos.models import Gasto

bp_gasto = Blueprint("bp_gasto", __name__, template_folder="templates")


@bp_gasto.route("/")
@login_required
def index():
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = date(hoy.year, hoy.month, 1)
    gastos = Gasto.query.order_by(Gasto.fecha.desc(), Gasto.id.desc()).all()

    def total_desde(fecha):
        return db.session.query(func.coalesce(func.sum(Gasto.monto), 0.0)).filter(Gasto.fecha >= fecha).scalar() or 0.0

    return render_template(
        "gasto/index.html",
        gastos=gastos,
        total_dia=total_desde(hoy),
        total_semana=total_desde(inicio_semana),
        total_mes=total_desde(inicio_mes),
    )


@bp_gasto.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("gasto/create.html")
    try:
        fecha = datetime.strptime(request.form.get("fecha"), "%Y-%m-%d").date()
        monto = float(request.form.get("monto") or 0)
    except (TypeError, ValueError):
        flash("Complete correctamente los datos del gasto.", "danger")
        return redirect(url_for("bp_gasto.create"))

    gasto = Gasto(
        fecha=fecha,
        usuario_id=current_user.id,
        descripcion=request.form.get("descripcion"),
        monto=monto,
        tipo=request.form.get("tipo") or "Repartidor",
    )
    db.session.add(gasto)
    db.session.commit()
    flash("Gasto registrado correctamente.", "success")
    return redirect(url_for("bp_gasto.index"))


@bp_gasto.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    gasto = Gasto.query.get_or_404(id)
    if request.method == "GET":
        return render_template("gasto/edit.html", gasto=gasto)
    try:
        gasto.fecha = datetime.strptime(request.form.get("fecha"), "%Y-%m-%d").date()
        gasto.monto = float(request.form.get("monto") or 0)
    except (TypeError, ValueError):
        flash("Complete correctamente los datos del gasto.", "danger")
        return redirect(url_for("bp_gasto.edit", id=id))
    gasto.tipo = request.form.get("tipo") or "Repartidor"
    gasto.descripcion = request.form.get("descripcion")
    db.session.commit()
    flash("Gasto actualizado correctamente.", "success")
    return redirect(url_for("bp_gasto.index"))


@bp_gasto.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):
    gasto = Gasto.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    flash("Gasto eliminado correctamente.", "info")
    return redirect(url_for("bp_gasto.index"))
