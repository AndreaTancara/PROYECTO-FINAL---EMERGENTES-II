from datetime import date, datetime, time

from flask import render_template, request
from flask_login import login_required
from sqlalchemy import func

from blueprintapp.app import db
from blueprintapp.clientes.models import Cliente
from blueprintapp.entregas.models import Entrega
from blueprintapp.envios.models import Envio
from blueprintapp.pagos.models import Pago
from blueprintapp.pedidos.models import DetallePedido, Pedido
from blueprintapp.productos.models import Producto
from blueprintapp.main import main_bp


def _month_range(value):
    hoy = date.today()
    if not value:
        value = f"{hoy.year:04d}-{hoy.month:02d}"
    try:
        year, month = [int(part) for part in value.split("-")]
        start = datetime(year, month, 1)
    except (TypeError, ValueError):
        value = f"{hoy.year:04d}-{hoy.month:02d}"
        start = datetime(hoy.year, hoy.month, 1)
    if start.month == 12:
        end = datetime(start.year + 1, 1, 1)
    else:
        end = datetime(start.year, start.month + 1, 1)
    return value, start, end


@main_bp.route("/")
@login_required
def index():
    hoy = date.today()
    inicio_dia = datetime.combine(hoy, time.min)
    fin_dia = datetime.combine(hoy, time.max)
    mes_filtro, inicio_mes, fin_mes = _month_range(request.args.get("mes"))

    pedidos_mes_query = Pedido.query.filter(
        Pedido.fecha >= inicio_mes,
        Pedido.fecha < fin_mes,
        Pedido.estado != "Cancelado",
    )
    productos_bajos_query = Producto.query.filter(Producto.stock_actual <= Producto.stock_minimo)
    productos_top = (
        db.session.query(Producto.nombre, func.sum(DetallePedido.cantidad).label("total_vendido"))
        .join(DetallePedido)
        .join(Pedido, Pedido.id == DetallePedido.pedido_id)
        .filter(Pedido.fecha >= inicio_mes, Pedido.fecha < fin_mes, Pedido.estado != "Cancelado")
        .group_by(Producto.nombre)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .limit(5)
        .all()
    )

    return render_template(
        "main/index.html",
        mes_filtro=mes_filtro,
        total_productos=Producto.query.count(),
        total_clientes=Cliente.query.count(),
        total_pedidos=Pedido.query.count(),
        pedidos_mes=pedidos_mes_query.count(),
        productos_bajos=productos_bajos_query.count(),
        productos_bajos_lista=productos_bajos_query.order_by(Producto.stock_actual.asc()).limit(8).all(),
        total_pagos=db.session.query(func.coalesce(func.sum(Pago.monto), 0.0)).scalar() or 0.0,
        ventas_dia=(
            db.session.query(func.coalesce(func.sum(Pedido.total), 0.0))
            .filter(Pedido.fecha.between(inicio_dia, fin_dia), Pedido.estado != "Cancelado")
            .scalar()
            or 0.0
        ),
        ventas_mes=pedidos_mes_query.with_entities(func.coalesce(func.sum(Pedido.total), 0.0)).scalar() or 0.0,
        adelantos_mes=pedidos_mes_query.with_entities(func.coalesce(func.sum(Pedido.adelanto), 0.0)).scalar() or 0.0,
        saldos_mes=pedidos_mes_query.with_entities(func.coalesce(func.sum(Pedido.saldo_pendiente), 0.0)).scalar() or 0.0,
        pedidos_pendientes=Pedido.query.filter(Pedido.saldo_pendiente > 0).count(),
        entregas_pendientes=Entrega.query.filter(Entrega.fecha_entrega >= hoy).count(),
        envios_en_ruta=Envio.query.filter(
            Envio.estado_envio.in_(["Pendiente", "En Ruta", "En Camino", "En Proceso", "En transito"])
        ).count(),
        nombres_productos=[p[0] for p in productos_top],
        cantidades_vendidas=[p[1] for p in productos_top],
    )
