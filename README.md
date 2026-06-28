# NexVolt ERP

Sistema web desarrollado con Python y Flask para la gestion de inventario, ventas, pedidos, pagos, entregas, envios y reportes de un negocio de ventas por TikTok Live y WhatsApp.

## Tecnologias

- Python
- Flask con patron Application Factory
- Blueprints
- SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-Bcrypt
- SQLite
- Bootstrap
- Font Awesome
- ReportLab

## Modulos principales

- Autenticacion de usuarios
- Roles y usuarios
- Dashboard con metricas
- Productos e inventario
- Compras de stock por factura
- Clientes
- Pedidos con varios productos
- Pagos, adelantos y saldos pendientes
- Entregas locales
- Envios nacionales
- Gastos
- Catalogo/categorias
- Proveedores
- Reportes PDF y Excel

## Ejecucion local

```bash
pip install -r requirements.txt
python seed.py
python run.py
```

Luego abrir:

```text
http://127.0.0.1:5000
```

## Usuario de prueba

```text
Usuario: admin
Password: admin123
```

## Despliegue en Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn run:app
```

## Base de datos

El proyecto incluye una base SQLite de prueba en:

```text
instance/bd_nexvolt.db
```
