from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.turnos.models import Turno
from app.users.models import Usuario
from .schemas import TurnoSchema
from sqlalchemy import func
from app.pedidos.models import Pedido, DetallePedido, DetalleMitad
from app.productos.models import Producto
from app.factura.models import Factura
from app.movimientos.models import MovimientoStock
turnos_v1_0_bp = Blueprint('turnos_v1_0_bp', __name__)
api = Api(turnos_v1_0_bp)

turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)


class TurnosListResource(Resource):

    @jwt_required()
    def get(self):
        turnos = Turno.query.order_by(Turno.id.desc()).all()
        return {
            "success": True,
            "data": turnos_schema.dump(turnos),
            "count": len(turnos)
        }, 200

    @jwt_required()
    def post(self):
        payload = request.get_json() or {}
        usuario_id   = payload.get("usuario_id")
        monto_inicio = payload.get("monto_inicio", 0)

        if usuario_id is None:
            return {"success": False, "message": "usuario_id es requerido"}, 400

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return {"success": False, "message": "Usuario no encontrado"}, 404

        turno_abierto = Turno.query.filter_by(usuario_id=usuario_id, cierre=None).first()
        if turno_abierto:
            return {
                "success": False,
                "message": "El usuario ya tiene un turno abierto",
                "data": turno_schema.dump(turno_abierto)
            }, 400

        try:
            turno = Turno(usuario_id=usuario_id, monto_inicio=float(monto_inicio))
            db.session.add(turno)
            db.session.commit()
            return {
                "success": True,
                "message": "Turno creado",
                "data": turno_schema.dump(turno)
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": "Error al crear turno", "error": str(e)}, 500


class TurnoResource(Resource):

    @jwt_required()
    def get(self, turno_id):
        turno = Turno.query.get(turno_id)
        if not turno:
            return {"success": False, "message": "Turno no encontrado"}, 404
        return {"success": True, "data": turno_schema.dump(turno)}, 200

    @jwt_required()
    def put(self, turno_id):
        turno = Turno.query.get(turno_id)
        if not turno:
            return {"success": False, "message": "Turno no encontrado"}, 404

        data = request.get_json() or {}

        if "monto_inicio" in data:
            try:
                turno.monto_inicio = float(data["monto_inicio"])
            except:
                return {"success": False, "message": "monto_inicio invalido"}, 400

        if "monto_cierre" in data:
            try:
                turno.monto_cierre = float(data["monto_cierre"])
            except:
                return {"success": False, "message": "monto_cierre invalido"}, 400

        if "cierre" in data:
            turno.cierre = data["cierre"]

        db.session.commit()
        return {
            "success": True,
            "message": "Turno actualizado",
            "data": turno_schema.dump(turno)
        }, 200

    @jwt_required()
    def delete(self, turno_id):
        turno = Turno.query.get(turno_id)
        if not turno:
            return {"success": False, "message": "Turno no encontrado"}, 404
        db.session.delete(turno)
        db.session.commit()
        return {"success": True, "message": "Turno eliminado"}, 200


class TurnoCerrarResource(Resource):

    @jwt_required()
    def post(self, turno_id):
        turno = Turno.query.get(turno_id)
        if not turno:
            return {"success": False, "message": "Turno no encontrado"}, 404
        if not turno.abierto:
            return {"success": False, "message": "Turno ya está cerrado"}, 400

        data = request.get_json() or {}
        monto_cierre = data.get("monto_cierre")
        if monto_cierre is None:
            return {"success": False, "message": "monto_cierre es requerido"}, 400

        try:
            turno.cerrar(float(monto_cierre))
            return {
                "success": True,
                "message": "Turno cerrado",
                "data": turno_schema.dump(turno)
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": "Error al cerrar turno", "error": str(e)}, 500


class TurnosAbiertosResource(Resource):

    @jwt_required()
    def get(self):
        turnos = Turno.query.filter_by(cierre=None).all()
        return {
            "success": True,
            "data": turnos_schema.dump(turnos),
            "count": len(turnos)
        }, 200


class TurnoResumenResource(Resource):
   

    @jwt_required()
    def get(self, turno_id):
        turno = Turno.query.get(turno_id)
        if not turno:
            return {'success': False, 'error': 'Turno no encontrado'}, 404

        
        pedidos = Pedido.query.filter_by(turno_id=turno_id).all()
        pedidos_activos = [p for p in pedidos if p.estado.nombre != 'cancelado']

        
        facturas = Factura.query.filter(
            Factura.pedido_id.in_([p.id for p in pedidos_activos]),
            Factura.anulada == False
        ).all()

        total_vendido  = sum(f.total    for f in facturas)
        total_subtotal = sum(f.subtotal for f in facturas)
        total_impuesto = sum(f.impuesto for f in facturas)

        
        ventas_productos = {}

        for pedido in pedidos_activos:
            for detalle in pedido.detalles:

                if detalle.combo_id:
                    continue  

                if detalle.is_mitad:
                    for mitad in detalle.mitades:
                        pid = mitad.producto_id
                        if pid not in ventas_productos:
                            ventas_productos[pid] = {
                                'producto_id': pid,
                                'nombre':    mitad.producto.nombre if mitad.producto else f'Producto {pid}',
                                'categoria': mitad.producto.categoria.nombre if mitad.producto else '',
                                'tamanos':   {}
                            }
                        tamano_nombre = detalle.tamano.nombre if detalle.tamano else 'Sin tamaño'
                        key = f'{tamano_nombre} (mitad)'
                        if key not in ventas_productos[pid]['tamanos']:
                            ventas_productos[pid]['tamanos'][key] = {'cantidad': 0, 'subtotal': 0}
                        ventas_productos[pid]['tamanos'][key]['cantidad'] += detalle.cantidad
                        ventas_productos[pid]['tamanos'][key]['subtotal'] += round(detalle.subtotal / 2, 2)

                elif detalle.producto_id:
                    pid = detalle.producto_id
                    if pid not in ventas_productos:
                        ventas_productos[pid] = {
                            'producto_id': pid,
                            'nombre':    detalle.producto.nombre if detalle.producto else f'Producto {pid}',
                            'categoria': detalle.producto.categoria.nombre if detalle.producto else '',
                            'tamanos':   {}
                        }
                    tamano_nombre = detalle.tamano.nombre if detalle.tamano else 'Sin tamaño'
                    if tamano_nombre not in ventas_productos[pid]['tamanos']:
                        ventas_productos[pid]['tamanos'][tamano_nombre] = {'cantidad': 0, 'subtotal': 0}
                    ventas_productos[pid]['tamanos'][tamano_nombre]['cantidad'] += detalle.cantidad
                    ventas_productos[pid]['tamanos'][tamano_nombre]['subtotal'] += detalle.subtotal


        pizzas  = [v for v in ventas_productos.values() if v['categoria'].lower() == 'pizzas']
        bebidas = [v for v in ventas_productos.values() if v['categoria'].lower() == 'bebidas']
        otros   = [v for v in ventas_productos.values()
                   if v['categoria'].lower() not in ('pizzas', 'bebidas')]


        combos_vendidos = {}  

        for pedido in pedidos_activos:
            for detalle in pedido.detalles:
                if not detalle.combo_id:
                    continue
                cid = detalle.combo_id
                if cid not in combos_vendidos:
                    nombre = detalle.combo.nombre if detalle.combo else f'Combo {cid}'
                    combos_vendidos[cid] = {
                        'combo_id': cid,
                        'nombre':   nombre,
                        'cantidad': 0,
                        'subtotal': 0.0,
                    }
                combos_vendidos[cid]['cantidad'] += detalle.cantidad
                combos_vendidos[cid]['subtotal'] += detalle.subtotal

        combos_lista = sorted(
            combos_vendidos.values(),
            key=lambda x: x['subtotal'],
            reverse=True
        )

        from app.productos.models import Producto as Prod
        inventario_bebidas = []
        for prod in Prod.query.filter_by(activo=True).all():
            if prod.categoria.nombre.lower() != 'bebidas':
                continue
            vendidas = sum(
                t['cantidad']
                for v in bebidas
                if v['producto_id'] == prod.id
                for t in v['tamanos'].values()
            )
            inventario_bebidas.append({
                'producto_id':  prod.id,
                'nombre':       prod.nombre,
                'vendidas':     vendidas,
                'stock_actual': prod.stock if prod.stock is not None else 0,
            })


        try:
            
            movimientos_stock = (
                MovimientoStock.query
                .filter_by(turno_id=turno_id)
                .order_by(MovimientoStock.fecha.asc())
                .all()
            )
            movimientos_lista = [
                {
                    'id':              m.id,
                    'producto_nombre': m.producto.nombre if m.producto else '—',
                    'usuario_nombre':  m.usuario.nombre  if m.usuario  else '—',
                    'cantidad':        m.cantidad,
                    'stock_anterior':  m.stock_anterior,
                    'stock_nuevo':     m.stock_nuevo,
                    'fecha':           m.fecha.isoformat(),
                }
                for m in movimientos_stock
            ]
        except Exception:
            
            movimientos_lista = []

        
        extras_ingredientes = {}

        for pedido in pedidos_activos:
            for detalle in pedido.detalles:
                for extra in detalle.extras:
                    iid = extra.ingrediente_id
                    if iid not in extras_ingredientes:
                        nombre = extra.ingrediente.nombre if extra.ingrediente else f'Ingrediente {iid}'
                        extras_ingredientes[iid] = {
                            'ingrediente_id': iid,
                            'nombre':         nombre,
                            'cantidad':       0,
                            'ingreso':        0.0,
                        }
                    extras_ingredientes[iid]['cantidad'] += extra.cantidad
                    extras_ingredientes[iid]['ingreso']  += round(
                        extra.cantidad * extra.precio_extra, 2
                    )

        top_extras = sorted(
            extras_ingredientes.values(),
            key=lambda x: x['ingreso'],
            reverse=True
        )

        ventas_por_hora = {}
        for pedido in pedidos_activos:
            if pedido.fecha is None:
                continue
            hora = pedido.fecha.strftime('%H')
            if hora not in ventas_por_hora:
                ventas_por_hora[hora] = {'hora': int(hora), 'pedidos': 0, 'subtotal': 0.0}
            ventas_por_hora[hora]['pedidos']  += 1
            ventas_por_hora[hora]['subtotal'] += round(
                sum(d.subtotal for d in pedido.detalles), 2
            )

        ventas_por_hora_lista = sorted(ventas_por_hora.values(), key=lambda x: x['hora'])


        return {
            'success': True,
            'data': {

                'turno_id':     turno.id,
                'usuario':      turno.usuario.nombre if turno.usuario else '',
                'apertura':     turno.apertura.isoformat(),
                'cierre':       turno.cierre.isoformat() if turno.cierre else None,
                'monto_inicio': turno.monto_inicio,
                'monto_cierre': turno.monto_cierre,

                'total_pedidos':  len(pedidos_activos),
                'total_facturas': len(facturas),
                'total_subtotal': round(total_subtotal, 2),
                'total_impuesto': round(total_impuesto, 2),
                'total_vendido':  round(total_vendido,  2),

                'pizzas':  pizzas,
                'bebidas': bebidas,
                'otros':   otros,

                'combos': combos_lista,

                'inventario_bebidas': inventario_bebidas,

                'movimientos_stock': movimientos_lista,

                'top_extras': top_extras,

                'ventas_por_hora': ventas_por_hora_lista,
            }
        }, 200


api.add_resource(TurnoResumenResource,   '/api/v1.0/turnos/<int:turno_id>/resumen', endpoint='turno_resumen')
api.add_resource(TurnosListResource,     '/api/v1.0/turnos',                        endpoint='turnos_list')
api.add_resource(TurnoResource,          '/api/v1.0/turnos/<int:turno_id>',         endpoint='turno_detail')
api.add_resource(TurnoCerrarResource,    '/api/v1.0/turnos/<int:turno_id>/cerrar',  endpoint='turno_cerrar')
api.add_resource(TurnosAbiertosResource, '/api/v1.0/turnos/abiertos',               endpoint='turnos_abiertos')