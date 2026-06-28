"""operaciones nexvolt

Revision ID: b7d8a32f4c91
Revises: 9f2c1a7b4e10
Create Date: 2026-06-18
"""
from alembic import op
import sqlalchemy as sa


revision = "b7d8a32f4c91"
down_revision = "9f2c1a7b4e10"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("clientes") as batch_op:
        batch_op.alter_column("nombre_completo", existing_type=sa.String(length=120), nullable=True)

    with op.batch_alter_table("envios") as batch_op:
        batch_op.add_column(sa.Column("cliente_nombre", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("telefono", sa.String(length=30), nullable=True))

    op.create_table(
        "compras_stock",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("factura", sa.String(length=80), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("costo_unitario", sa.Float(), nullable=False),
        sa.Column("gasto_compra", sa.Float(), nullable=False),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "gastos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("descripcion", sa.String(length=220), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("tipo", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("gastos")
    op.drop_table("compras_stock")
    with op.batch_alter_table("envios") as batch_op:
        batch_op.drop_column("telefono")
        batch_op.drop_column("cliente_nombre")
    with op.batch_alter_table("clientes") as batch_op:
        batch_op.alter_column("nombre_completo", existing_type=sa.String(length=120), nullable=False)
