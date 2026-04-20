from marshmallow import fields

from app.ext import ma


class TamanoSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
