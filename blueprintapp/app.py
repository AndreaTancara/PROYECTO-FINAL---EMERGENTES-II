from flask import Flask
from blueprintapp.extensions import db, login_manager, bcrypt, migrate
from blueprintapp.usuarios.models import User
from blueprintapp.roles.models import Role
from blueprintapp.categorias.models import Categoria
from blueprintapp.productos.models import Producto
from blueprintapp.clientes.models import Cliente
from blueprintapp.pedidos.models import Pedido
from blueprintapp.proveedores.models import Proveedor
from blueprintapp.pagos.models import Pago
from blueprintapp.entregas.models import Entrega
from blueprintapp.envios.models import Envio
from blueprintapp.compras.models import CompraStock
from blueprintapp.gastos.models import Gasto


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object("blueprintapp.config.Config")

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registro de Blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .proveedores.routes import bp_proveedor
    from .categorias.routes import bp_categoria
    from .clientes.routes import bp_cliente
    from .productos.routes import bp_producto
    from .pedidos.routes import bp_pedido
    from blueprintapp.pagos.routes import bp_pago
    from blueprintapp.entregas.routes import bp_entrega
    from blueprintapp.envios.routes import bp_envio
    from blueprintapp.reportes.routes import bp_reporte
    from blueprintapp.compras.routes import bp_compra
    from blueprintapp.gastos.routes import bp_gasto
    from blueprintapp.roles.routes import bp_role
    from blueprintapp.usuarios.routes import bp_usuario
    from blueprintapp.perfiles.routes import bp_perfil  # Importa el blueprint

    app.register_blueprint(bp_perfil)
    app.register_blueprint(bp_usuario, url_prefix="/usuarios")
    app.register_blueprint(bp_role, url_prefix="/roles")
    app.register_blueprint(bp_categoria, url_prefix="/categorias")
    app.register_blueprint(bp_cliente, url_prefix="/clientes")
    app.register_blueprint(bp_pedido, url_prefix="/pedidos")
    app.register_blueprint(bp_producto, url_prefix="/productos")
    app.register_blueprint(bp_pago, url_prefix="/pagos")
    app.register_blueprint(bp_entrega, url_prefix="/entregas")
    app.register_blueprint(bp_envio, url_prefix="/envios")
    app.register_blueprint(bp_reporte, url_prefix="/reportes")
    app.register_blueprint(bp_compra, url_prefix="/compras")
    app.register_blueprint(bp_gasto, url_prefix="/gastos")
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(bp_proveedor, url_prefix="/proveedores")

    return app
