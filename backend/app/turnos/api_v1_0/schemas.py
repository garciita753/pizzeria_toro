from marshmallow import fields, Schema, validates, ValidationError
from app.ext import ma

class TurnoSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    usuario_id = fields.Int(required=True)

    apertura = fields.DateTime(dump_only=True)
    cierre = fields.DateTime(allow_none=True)

    monto_inicio = fields.Float(required=True)
    monto_cierre = fields.Float(allow_none=True)

    abierto = fields.Boolean(dump_only=True)