from marshmallow import fields

from app.ext import ma


class UsuariosSchema(ma.Schema):
    id = fields.Int()
    nombre = fields.Str(required=True)
    correo = fields.Email(required=True)
    rol = fields.Str()
    active = fields.Boolean()
    cedula = fields.Str()
    codigo = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)