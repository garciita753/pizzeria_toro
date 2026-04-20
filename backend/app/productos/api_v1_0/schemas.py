from marshmallow import fields

from app.ext import ma
from app.tamanos.api_v1_0.schemas import TamanoSchema


class CategoriaSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    activo = fields.Bool()


class ProductoSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    descripcion = fields.Str(allow_none=True)
    precio_base = fields.Float(required=True)
    activo = fields.Bool()
    categoria_id = fields.Int(required=True)
    categoria = fields.Nested(CategoriaSchema, dump_only=True)
   # stock = fields.Integer()

class ProductoTamanoSchema(ma.Schema):
    producto_id = fields.Int(required=True)
    tamano_id = fields.Int(required=True)
    precio = fields.Float(required=True)

    tamano = fields.Nested(TamanoSchema, dump_only=True)

