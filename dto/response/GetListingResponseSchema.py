from marshmallow import Schema, fields, validate, ValidationError, validates, pre_dump
from flask_marshmallow import Marshmallow

USERNAME_INVALID = "Invalid username"
PASSWORD_INVALID = "Password is not correct"
import json

ma = Marshmallow()


class DescriptionSchema(Schema):
    english = fields.String()
    bahasa = fields.String()


# Define a schema for the nested "address" object
class GetListingResponseSchema(ma.Schema):
    id = fields.String()
    title = fields.String()
    # description = fields.Nested(DescriptionSchema, required=True)
    # imageUrls = fields.Nested(fields.Str, required=True)
    status = fields.String()

    class Meta:
        fields = (
            "id",
            "title",
            "description",
            "imageUrls",
            "status",
            "rowCreated",
            "rowUpdated",
        )
