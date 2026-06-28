"""nexvolt erp inventory sales

Revision ID: 9f2c1a7b4e10
Revises: 5cad1e7038d4
Create Date: 2026-06-18
"""
from alembic import op
import sqlalchemy as sa


revision = "9f2c1a7b4e10"
down_revision = "5cad1e7038d4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("proveedores") as batch_op:
        batch_op.add_column(sa.Column("whatsapp", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("correo", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("direccion", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("observaciones", sa.Text(), nullable=True))

    with op.batch_alter_table("clientes") as batch_op:
        batch_op.add_column(sa.Column("telefono", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("ciudad", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("direccion", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("referencia", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("tipo_cliente", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("fecha_registro", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("observaciones", sa.Text(), nullable=True))

    with op.batch_alter_table("productos") as batch_op:
        batch_op.add_column(sa.Column("codigo_interno", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("marca", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("descripcion", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("precio_compra", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("precio_normal", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("precio_live", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("stock_minimo", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("imagen", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("estado", sa.String(length=30), nullable=True))
        batch_op.create_unique_constraint("uq_productos_codigo_interno", ["codigo_interno"])

    op.execute("UPDATE proveedores SET correo = COALESCE(correo, email)")
    op.execute("UPDATE clientes SET telefono = COALESCE(telefono, 'Sin telefono')")
    op.execute("UPDATE clientes SET fecha_registro = COALESCE(fecha_registro, CURRENT_TIMESTAMP)")
    op.execute("UPDATE productos SET codigo_interno = COALESCE(codigo_interno, 'PROD-' || id)")
    op.execute("UPDATE productos SET precio_compra = COALESCE(precio_compra, precio)")
    op.execute("UPDATE productos SET precio_normal = COALESCE(precio_normal, precio)")
    op.execute("UPDATE productos SET precio_live = COALESCE(precio_live, precio)")
    op.execute("UPDATE productos SET stock_minimo = COALESCE(stock_minimo, 5)")
    op.execute("UPDATE productos SET estado = COALESCE(estado, 'Activo')")

    with op.batch_alter_table("pedidos") as batch_op:
        batch_op.add_column(sa.Column("estado", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("descuento", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("adelanto", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("saldo_pendiente", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("observaciones", sa.Text(), nullable=True))

    op.execute("UPDATE pedidos SET estado = COALESCE(estado, 'Reservado')")
    op.execute("UPDATE pedidos SET descuento = COALESCE(descuento, 0)")
    op.execute("UPDATE pedidos SET adelanto = COALESCE(adelanto, 0)")
    op.execute("UPDATE pedidos SET saldo_pendiente = COALESCE(saldo_pendiente, total)")

    with op.batch_alter_table("detalle_pedidos") as batch_op:
        batch_op.add_column(sa.Column("descuento_item", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("subtotal", sa.Float(), nullable=True))

    op.execute("UPDATE detalle_pedidos SET descuento_item = COALESCE(descuento_item, 0)")
    op.execute("UPDATE detalle_pedidos SET subtotal = COALESCE(subtotal, cantidad * precio_unitario)")

    op.create_table(
        "pagos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("metodo", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "entregas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("fecha_entrega", sa.Date(), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("lugar", sa.String(length=120), nullable=False),
        sa.Column("responsable", sa.String(length=120), nullable=True),
        sa.Column("estado", sa.String(length=40), nullable=False, server_default="Programada"),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "envios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("empresa_transporte", sa.String(length=120), nullable=True),
        sa.Column("numero_guia", sa.String(length=80), nullable=True),
        sa.Column("ciudad_destino", sa.String(length=120), nullable=True),
        sa.Column("estado_envio", sa.String(length=80), nullable=True),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("envios")
    op.drop_table("entregas")
    op.drop_table("pagos")
    with op.batch_alter_table("detalle_pedidos") as batch_op:
        batch_op.drop_column("subtotal")
        batch_op.drop_column("descuento_item")
    with op.batch_alter_table("pedidos") as batch_op:
        batch_op.drop_column("observaciones")
        batch_op.drop_column("saldo_pendiente")
        batch_op.drop_column("adelanto")
        batch_op.drop_column("descuento")
        batch_op.drop_column("estado")
    with op.batch_alter_table("productos") as batch_op:
        batch_op.drop_constraint("uq_productos_codigo_interno", type_="unique")
        batch_op.drop_column("estado")
        batch_op.drop_column("imagen")
        batch_op.drop_column("stock_minimo")
        batch_op.drop_column("precio_live")
        batch_op.drop_column("precio_normal")
        batch_op.drop_column("precio_compra")
        batch_op.drop_column("descripcion")
        batch_op.drop_column("marca")
        batch_op.drop_column("codigo_interno")
    with op.batch_alter_table("clientes") as batch_op:
        batch_op.drop_column("observaciones")
        batch_op.drop_column("fecha_registro")
        batch_op.drop_column("tipo_cliente")
        batch_op.drop_column("referencia")
        batch_op.drop_column("direccion")
        batch_op.drop_column("ciudad")
        batch_op.drop_column("telefono")
    with op.batch_alter_table("proveedores") as batch_op:
        batch_op.drop_column("observaciones")
        batch_op.drop_column("direccion")
        batch_op.drop_column("correo")
        batch_op.drop_column("whatsapp")
