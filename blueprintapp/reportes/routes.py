from datetime import datetime, time
from io import BytesIO

from flask import Blueprint, Response, render_template, request
from flask_login import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
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
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
        title="Reporte NexVolt",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BrandTitle", fontName="Helvetica-Bold", fontSize=18, textColor=colors.white))
    styles.add(ParagraphStyle(name="BrandSub", fontSize=8.5, textColor=colors.HexColor("#dbeafe")))
    styles.add(ParagraphStyle(name="SectionTitle", fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor("#0b2545"), spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="CellSmall", fontSize=7.2, leading=9))

    def p(value):
        return Paragraph(str(value or "---"), styles["CellSmall"])

    def money(value):
        return f"Bs {float(value or 0):,.2f}"

    def table(data, widths):
        tbl = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 7.4),
                    ("FONTSIZE", (0, 1), (-1, -1), 7.2),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d7e3f4")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fbff")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return tbl

    filtros = datos["filtros"]
    periodo = f"{filtros.get('fecha_inicio') or 'Inicio'} al {filtros.get('fecha_fin') or 'Actual'}"
    generado = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_ventas = sum(v.total or 0 for v in datos["ventas"])

    story = []
    header = Table(
        [
            [
                Paragraph("NexVolt ERP", styles["BrandTitle"]),
                Paragraph(f"Reporte comercial<br/>Generado: {generado}<br/>Periodo: {periodo}", styles["BrandSub"]),
            ]
        ],
        colWidths=[3.4 * inch, 3.7 * inch],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#061b34")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#0d6efd")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 12))

    resumen = Table(
        [
            ["Ventas", "Total vendido", "Adelantos", "Saldos pendientes"],
            [len(datos["ventas"]), money(total_ventas), money(datos["adelantos"]), money(datos["saldos"])],
        ],
        colWidths=[1.4 * inch, 1.9 * inch, 1.9 * inch, 1.9 * inch],
    )
    resumen.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf2ff")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0b2545")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0d6efd")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bfd7ff")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d7e3f4")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(resumen)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Ventas por fecha", styles["SectionTitle"]))
    ventas_rows = [["Fecha", "Cliente", "Estado", "Total"]]
    for venta in datos["ventas"][:45]:
        cliente = venta.cliente.nombre_completo if venta.cliente and venta.cliente.nombre_completo else (venta.cliente.telefono if venta.cliente else "---")
        ventas_rows.append([venta.fecha.strftime("%d/%m/%Y"), p(cliente[:38]), venta.estado, money(venta.total)])
    if len(ventas_rows) == 1:
        ventas_rows.append(["---", "Sin ventas para estos filtros", "---", money(0)])
    story.append(table(ventas_rows, [0.95 * inch, 3.15 * inch, 1.45 * inch, 1.55 * inch]))

    story.append(Paragraph("Ventas por producto", styles["SectionTitle"]))
    producto_rows = [["Producto", "Unidades", "Total"]]
    for nombre, unidades, total in datos["ventas_por_producto"][:18]:
        producto_rows.append([p(str(nombre)[:50]), unidades, money(total)])
    if len(producto_rows) == 1:
        producto_rows.append(["Sin datos", 0, money(0)])
    story.append(table(producto_rows, [4.4 * inch, 1.2 * inch, 1.5 * inch]))

    story.append(Paragraph("Ventas por categoria", styles["SectionTitle"]))
    categoria_rows = [["Categoria", "Unidades", "Total"]]
    for nombre, unidades, total in datos["ventas_por_categoria"][:14]:
        categoria_rows.append([p(str(nombre)[:45]), unidades, money(total)])
    if len(categoria_rows) == 1:
        categoria_rows.append(["Sin datos", 0, money(0)])
    story.append(table(categoria_rows, [4.4 * inch, 1.2 * inch, 1.5 * inch]))

    story.append(Paragraph("Stock actual", styles["SectionTitle"]))
    stock_rows = [["Codigo", "Producto", "Stock", "Minimo"]]
    for producto in datos["stock_actual"][:28]:
        stock_rows.append([producto.codigo_interno or "---", p(producto.nombre[:45]), producto.stock_actual, producto.stock_minimo])
    if len(stock_rows) == 1:
        stock_rows.append(["---", "Sin productos", 0, 0])
    story.append(table(stock_rows, [1.1 * inch, 3.8 * inch, 1.1 * inch, 1.1 * inch]))

    doc.build(story)
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reportes_nexvolt.pdf"},
    )
