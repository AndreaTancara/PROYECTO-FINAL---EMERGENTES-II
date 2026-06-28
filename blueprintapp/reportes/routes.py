from datetime import datetime, time
from io import BytesIO

from flask import Blueprint, Response, render_template, request
from flask_login import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import func

from blueprintapp.app import db
from blueprintapp.categorias.models import Categoria
from blueprintapp.clientes.models import Cliente
from blueprintapp.pedidos.models import DetallePedido, Pedido
from blueprintapp.productos.models import Producto

bp_reporte = Blueprint("bp_reporte", __name__, template_folder="templates")


def _parse_date(value, fallback=None):
    if not value:
        return fallback
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return fallback


def _filtros():
    return {
        "fecha_inicio": request.args.get("fecha_inicio", ""),
        "fecha_fin": request.args.get("fecha_fin", ""),
        "cliente_id": request.args.get("cliente_id", type=int),
        "producto_id": request.args.get("producto_id", type=int),
    }


def _datos_reportes():
    filtros = _filtros()
    fecha_inicio = _parse_date(filtros["fecha_inicio"])
    fecha_fin = _parse_date(filtros["fecha_fin"])
    cliente_id = filtros["cliente_id"]
    producto_id = filtros["producto_id"]

    pedidos_query = Pedido.query
    if fecha_inicio:
        pedidos_query = pedidos_query.filter(Pedido.fecha >= datetime.combine(fecha_inicio, time.min))
    if fecha_fin:
        pedidos_query = pedidos_query.filter(Pedido.fecha <= datetime.combine(fecha_fin, time.max))
    if cliente_id:
        pedidos_query = pedidos_query.filter(Pedido.cliente_id == cliente_id)

    ventas_producto_query = (
        db.session.query(
            Producto.nombre,
            func.coalesce(func.sum(DetallePedido.cantidad), 0),
            func.coalesce(func.sum(DetallePedido.subtotal), 0.0),
        )
        .join(DetallePedido, DetallePedido.producto_id == Producto.id)
        .join(Pedido, Pedido.id == DetallePedido.pedido_id)
    )
    ventas_categoria_query = (
        db.session.query(
            Categoria.nombre,
            func.coalesce(func.sum(DetallePedido.cantidad), 0),
            func.coalesce(func.sum(DetallePedido.subtotal), 0.0),
        )
        .join(Producto, Producto.categoria_id == Categoria.id)
        .join(DetallePedido, DetallePedido.producto_id == Producto.id)
        .join(Pedido, Pedido.id == DetallePedido.pedido_id)
    )
    if producto_id:
        ventas_producto_query = ventas_producto_query.filter(Producto.id == producto_id)
    if fecha_inicio:
        ventas_producto_query = ventas_producto_query.filter(Pedido.fecha >= datetime.combine(fecha_inicio, time.min))
        ventas_categoria_query = ventas_categoria_query.filter(Pedido.fecha >= datetime.combine(fecha_inicio, time.min))
    if fecha_fin:
        ventas_producto_query = ventas_producto_query.filter(Pedido.fecha <= datetime.combine(fecha_fin, time.max))
        ventas_categoria_query = ventas_categoria_query.filter(Pedido.fecha <= datetime.combine(fecha_fin, time.max))

    ventas = pedidos_query.order_by(Pedido.fecha.desc()).all()
    return {
        "ventas": ventas,
        "ventas_por_cliente": (
            db.session.query(Cliente.nombre_completo, func.count(Pedido.id), func.coalesce(func.sum(Pedido.total), 0.0))
            .join(Pedido, Pedido.cliente_id == Cliente.id)
            .group_by(Cliente.id)
            .order_by(func.sum(Pedido.total).desc())
            .all()
        ),
        "ventas_por_producto": (
            ventas_producto_query.group_by(Producto.id).order_by(func.sum(DetallePedido.subtotal).desc()).all()
        ),
        "ventas_por_categoria": (
            ventas_categoria_query.group_by(Categoria.id).order_by(func.sum(DetallePedido.subtotal).desc()).all()
        ),
        "stock_actual": Producto.query.order_by(Producto.stock_actual.asc(), Producto.nombre.asc()).all(),
        "adelantos": sum(v.adelanto or 0 for v in ventas),
        "saldos": sum(v.saldo_pendiente or 0 for v in ventas),
        "filtros": filtros,
    }


@bp_reporte.route("/")
@login_required
def index():
    datos = _datos_reportes()
    return render_template(
        "reporte/index.html",
        **datos,
        clientes=Cliente.query.order_by(Cliente.nombre_completo).all(),
        productos=Producto.query.order_by(Producto.nombre).all(),
    )


@bp_reporte.route("/export/excel")
@login_required
def export_excel():
    datos = _datos_reportes()
    html = render_template("reporte/export.xls.html", **datos)
    return Response(
        html,
        mimetype="application/vnd.ms-excel",
        headers={"Content-Disposition": "attachment; filename=reportes_nexvolt.xls"},
    )


@bp_reporte.route("/export/pdf")
@login_required
def export_pdf():
    datos = _datos_reportes()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 45
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Reporte NexVolt")
    y -= 25
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, y, f"Adelantos: Bs {datos['adelantos']:.2f}    Saldos pendientes: Bs {datos['saldos']:.2f}")
    y -= 25
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, "Ventas por fecha")
    y -= 18
    pdf.setFont("Helvetica", 8)
    for venta in datos["ventas"][:32]:
        cliente = venta.cliente.nombre_completo if venta.cliente and venta.cliente.nombre_completo else (venta.cliente.telefono if venta.cliente else "---")
        line = f"{venta.fecha.strftime('%d/%m/%Y')} | {cliente[:28]} | {venta.estado} | Bs {venta.total:.2f}"
        pdf.drawString(40, y, line)
        y -= 13
        if y < 50:
            pdf.showPage()
            y = height - 45
            pdf.setFont("Helvetica", 8)
    pdf.save()
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reportes_nexvolt.pdf"},
    )
