from functools import wraps
from flask import flash, redirect, url_for  # Importamos flash y redirect
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Mantenemos tu misma lógica de validación
        if (
            not current_user.is_authenticated
            or current_user.rol is None
            or current_user.rol.nombre_rol != "Administrador"
        ):
            # En lugar de abort(403), usamos flash y redirect
            flash("Acceso denegado: Se requieren permisos de administrador.", "danger")
            return redirect(
                url_for("main_bp.index")
            )  # Cambia 'main.index' por tu ruta de inicio real

        return f(*args, **kwargs)

    return decorated_function
