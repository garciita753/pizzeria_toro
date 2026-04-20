from marshmallow import fields, Schema, validates, ValidationError
from app.ext import ma

class DetalleExtrasSchema(ma.Schema):
    id             = fields.Int(dump_only=True)
    detalle_id     = fields.Int()
    ingrediente_id = fields.Int(required=True)
    tamano_id      = fields.Int(allow_none=True)
    precio_extra   = fields.Float(dump_only=True)
    cantidad       = fields.Int()
    ingrediente    = fields.Method("get_ingrediente", dump_only=True)  

    def get_ingrediente(self, obj):
        return {"id": obj.ingrediente.id, "nombre": obj.ingrediente.nombre} \
               if obj.ingrediente else None

class DetalleMitadExtraSchema(ma.Schema):
    id               = fields.Int(dump_only=True)
    detalle_mitad_id = fields.Int(dump_only=True)
    ingrediente_id   = fields.Int(required=True)
    cantidad         = fields.Int(load_default=1)
    ingrediente      = fields.Method("get_ingrediente", dump_only=True)

    def get_ingrediente(self, obj):
        return {"id": obj.ingrediente.id, "nombre": obj.ingrediente.nombre} \
               if obj.ingrediente else None

class DetalleMitadSchema(ma.Schema):
    id          = fields.Int(dump_only=True)
    detalle_id  = fields.Int(dump_only=True)
    mitad       = fields.Int(required=True)        # 1 o 2
    producto_id = fields.Int(required=True)
    producto    = fields.Method("get_producto", dump_only=True)
    extras      = fields.List(fields.Nested(DetalleMitadExtraSchema), dump_only=True)

    def get_producto(self, obj):
        return {"id": obj.producto.id, "nombre": obj.producto.nombre} \
               if obj.producto else None


class DetallePedidoSchema(ma.Schema):
    id              = fields.Int(dump_only=True)
    pedido_id       = fields.Int(dump_only=True)
    producto_id     = fields.Int(allow_none=True)
    combo_id        = fields.Int(allow_none=True)
    tamano_id       = fields.Int(allow_none=True)
    cantidad        = fields.Int(required=True)
    precio_unitario = fields.Float()
    subtotal        = fields.Float(dump_only=True)
    is_mitad        = fields.Bool(dump_only=True)
    notas           = fields.Str(allow_none=True, dump_only=True)
    extras          = fields.List(fields.Nested(DetalleExtrasSchema),   dump_only=True)
    mitades         = fields.List(fields.Nested(DetalleMitadSchema),    dump_only=True)

    producto_nombre = fields.Method("get_producto_nombre", dump_only=True)
    tamano_nombre   = fields.Method("get_tamano_nombre",   dump_only=True)

    def get_producto_nombre(self, obj):
        """Si es mitad/mitad devuelve 'Charque / Hawaiana', si no el nombre normal."""
        if obj.is_mitad and obj.mitades:
            nombres = [m.producto.nombre for m in obj.mitades if m.producto]
            return " / ".join(nombres)
        return obj.producto.nombre if obj.producto else None

    def get_tamano_nombre(self, obj):
        return obj.tamano.nombre if obj.tamano else None

class PedidoSchema(ma.Schema):
    id                = fields.Int(dump_only=True)
    numero_turno      = fields.Int(dump_only=True)
    fecha             = fields.DateTime(dump_only=True)
    updated_at        = fields.DateTime(dump_only=True)
    estado_id         = fields.Int(dump_only=True)
    tipo_entrega_id   = fields.Int(required=True)
    direccion_entrega = fields.Str(allow_none=True)
    total             = fields.Float(dump_only=True)
    cliente_id        = fields.Int(required=True)
    usuario_id        = fields.Int(required=True)
    turno_id          = fields.Int(required=True)
    detalles          = fields.List(fields.Nested(DetallePedidoSchema), dump_only=True)

    estado       = fields.Method("get_estado",       dump_only=True)
    tipo_entrega = fields.Method("get_tipo_entrega", dump_only=True)

    def get_estado(self, obj):
        return {"id": obj.estado.id, "nombre": obj.estado.nombre} \
               if obj.estado else None

    def get_tipo_entrega(self, obj):
        return {"id": obj.tipo_entrega.id, "nombre": obj.tipo_entrega.nombre} \
               if obj.tipo_entrega else None

    @validates('tipo_entrega_id')
    def validate_tipo_entrega_id(self, value):
        from app.pedidos.models import TipoEntrega
        if not TipoEntrega.query.get(value):
            raise ValidationError(f"tipo_entrega_id {value} no existe")